from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from datetime import datetime

from PySide6.QtCore import QObject, Signal

import serial
import serial.tools.list_ports

from services.csv_exporter import parse_measurement_triple
from services.unit_conversion import sanitize_step_hz


@dataclass(slots=True)
class ConnectionSettings:
    com_port: str
    baudrate: int
    timeout_s: float
    terminator: str


@dataclass(slots=True)
class SweepSettings:
    sample_id: str
    ac_voltage_v: float
    dc_bias_v: float
    frequency_start_hz: float
    frequency_stop_hz: float
    frequency_step_hz: float
    point_settle_delay_s: float
    measure_delay_s: float
    bias_settle_delay_s: float
    use_dc_bias: bool
    dc_bias_list_v: list[float] | None = None
    frequency_points_hz: list[float] | None = None


class ScanRunner(QObject):
    """Serial I/O helper for V2 sweeps using confirmed command paths."""

    log = Signal(str)
    measurement = Signal(dict)
    sweep_finished = Signal(dict)
    connected = Signal(bool, str)

    def __init__(self) -> None:
        super().__init__()
        self._serial: serial.Serial | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @staticmethod
    def list_ports() -> list[str]:
        ports = serial.tools.list_ports.comports()
        return [f"{port.device} - {port.description or 'Unknown device'}" for port in ports]

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def connect(self, settings: ConnectionSettings) -> None:
        self.disconnect()
        try:
            self._serial = serial.Serial(
                port=settings.com_port,
                baudrate=settings.baudrate,
                timeout=settings.timeout_s,
                write_timeout=settings.timeout_s,
            )
            self.connected.emit(True, settings.com_port)
            self._log(f"Connected to {settings.com_port}")
        except Exception as exc:
            self._serial = None
            self.connected.emit(False, "")
            self._log(f"Connection failed: {exc}")

    def disconnect(self) -> None:
        self.stop()
        if self._serial is None:
            return
        try:
            if self._serial.is_open:
                self._serial.close()
            self._log("Disconnected")
        except Exception as exc:
            self._log(f"Disconnect error: {exc}")
        finally:
            self._serial = None
            self.connected.emit(False, "")

    def send_confirmed_controls(
        self,
        frequency_hz: float,
        ac_voltage_v: float,
        dc_bias_v: float,
        bias_on: bool,
        terminator: str,
        run_optional_bias_queries: bool,
    ) -> None:
        self._write(f"FREQ {frequency_hz:g}", terminator)
        self._write(f"VOLT {ac_voltage_v:g}", terminator)
        self._write("BIAS ON" if bias_on else "BIAS OFF", terminator)
        self._write(f":BIAS:VOLTage {dc_bias_v:g}", terminator)

        if run_optional_bias_queries:
            self._query_optional_bias(terminator)

    def run_sweep(self, connection: ConnectionSettings, settings: SweepSettings) -> None:
        if self._thread and self._thread.is_alive():
            self._log("Sweep already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_sweep_worker,
            args=(connection, settings),
            daemon=True,
        )
        self._thread.start()

    def execute_command(
        self,
        connection: ConnectionSettings,
        command: str,
        expect_response: bool,
    ) -> str | None:
        """Run a manual diagnostics command using the active serial connection."""
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Command testing is disabled while sweep/measurement is running")

        if not self._serial or not self._serial.is_open:
            self._open_serial_direct(connection)
            if not self._serial or not self._serial.is_open:
                raise RuntimeError("No active serial connection")

        self._write(command, connection.terminator)
        if not expect_response:
            return None
        return self._read_response(connection.terminator, command)

    def measure_once(self, connection: ConnectionSettings, settings: SweepSettings) -> None:
        if self._thread and self._thread.is_alive():
            self._log("Measure Once skipped: sweep thread is already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._measure_once_worker, args=(connection, settings), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            # Avoid joining from the same worker thread, which raises RuntimeError.
            if threading.current_thread() is self._thread:
                self._log("Sweep stop requested")
                return
            self._thread.join(timeout=1.5)
            self._log("Sweep stop requested")

    def _run_sweep_worker(self, connection: ConnectionSettings, settings: SweepSettings) -> None:
        completed = False
        interrupted = False
        rows_collected = 0
        attempted_points = 0
        successful_points = 0
        failed_points = 0
        started_at = time.perf_counter()
        try:
            if not self._serial or not self._serial.is_open:
                self._open_serial_direct(connection)
                if not self._serial or not self._serial.is_open:
                    self._log("Sweep aborted: no active serial connection")
                    return

            frequency_points_hz = settings.frequency_points_hz or self._build_frequency_points_hz(settings)
            if not frequency_points_hz:
                self._log("Sweep aborted: no frequency points were generated")
                return

            bias_values = self._build_bias_values(settings)
            if not bias_values:
                self._log("Sweep aborted: bias plan is empty")
                return

            self._log(f"Run started: {len(frequency_points_hz)} frequencies x {len(bias_values)} bias points")

            for bias_value in bias_values:
                if self._stop_event.is_set():
                    self._log("Sweep interrupted by operator")
                    interrupted = True
                    return

                for current_hz in frequency_points_hz:
                    if self._stop_event.is_set():
                        self._log("Sweep interrupted by operator")
                        interrupted = True
                        return

                    try:
                        z_ohm, theta_deg, status, raw, measurement_ok = self._acquire_point(
                            connection=connection,
                            settings=settings,
                            frequency_hz=current_hz,
                            bias_value=bias_value,
                        )
                    except Exception as exc:
                        self._log(f"Measurement point exception at {current_hz:g} Hz: {exc}")
                        z_ohm, theta_deg, status, raw, measurement_ok = (
                            None,
                            None,
                            "FAILED_POINT_EXCEPTION",
                            f"<exception:{exc}>",
                            False,
                        )

                    if not measurement_ok:
                        self._log(
                            f"Measurement point failed at freq={current_hz:g} Hz, bias={bias_value:g} V"
                        )

                    row = {
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "sample_id": settings.sample_id,
                        "freq_hz": current_hz,
                        "dc_bias_v": bias_value if settings.use_dc_bias else 0.0,
                        "raw_response": raw,
                        "primary": z_ohm,
                        "secondary": theta_deg,
                        "status": status,
                        "ac_voltage_v": settings.ac_voltage_v,
                        "dc_bias_on": settings.use_dc_bias,
                        "z_ohm": z_ohm,
                        "theta_deg": theta_deg,
                        "measurement_ok": measurement_ok,
                    }
                    self.measurement.emit(row)
                    rows_collected += 1
                    attempted_points += 1

                    status_text = str(status or "")
                    z_text = "None" if z_ohm is None else f"{z_ohm:g}"
                    theta_text = "None" if theta_deg is None else f"{theta_deg:g}"
                    self._log(
                        f"[RUN] f={current_hz:g} Hz, bias={bias_value:g}, Z={z_text}, "
                        f"theta={theta_text}, status={status_text or '<none>'}"
                    )
                    if status_text and status_text != "0":
                        self._log(
                            f"[RUN] Non-zero status observed at f={current_hz:g} Hz, bias={bias_value:g}: {status_text}"
                        )

                    if measurement_ok and (not status_text or status_text == "0"):
                        successful_points += 1
                    else:
                        failed_points += 1

            completed = True
            self._log("Run completed")
        except Exception as exc:
            self._log(f"Sweep error: {exc}")
        finally:
            duration_s = time.perf_counter() - started_at
            self.sweep_finished.emit(
                {
                    "mode": "run",
                    "completed": completed,
                    "interrupted": interrupted,
                    "rows_collected": rows_collected,
                    "attempted_points": attempted_points,
                    "successful_points": successful_points,
                    "failed_points": failed_points,
                    "duration_s": duration_s,
                }
            )

    def _query_optional_bias(self, terminator: str) -> None:
        for command in (":BIAS?", ":BIAS:STAT?", ":BIAS:VOLT?"):
            try:
                response = self._query(command, terminator)
                self._log(f"{command} => {response}")
            except Exception as exc:
                self._log(f"Optional verification failed for {command}: {exc}")

    def _query(self, command: str, terminator: str) -> str:
        self._write(command, terminator)
        return self._read_response(terminator, command)

    def _read_response(self, terminator: str, command: str) -> str:
        if self._serial is None:
            raise RuntimeError("Not connected")
        raw = self._serial.read_until(expected=terminator.encode("ascii", errors="replace"))
        text = raw.decode("ascii", errors="replace").strip()
        self._log(f"Response to {command}: {text if text else '<empty>'}")
        return text

    def _write(self, command: str, terminator: str) -> None:
        if self._serial is None or not self._serial.is_open:
            raise RuntimeError("Serial port is not connected")
        payload = f"{command}{terminator}".encode("ascii", errors="replace")
        self._serial.write(payload)
        self._serial.flush()
        self._log(f"Sent: {command}")

    def _log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log.emit(f"[{stamp}] {message}")

    def _build_bias_values(self, settings: SweepSettings) -> list[float]:
        if not settings.use_dc_bias:
            return [settings.dc_bias_v]
        if settings.dc_bias_list_v:
            return settings.dc_bias_list_v
        return [settings.dc_bias_v]

    def _open_serial_direct(self, settings: ConnectionSettings) -> None:
        try:
            if self._serial and self._serial.is_open:
                return
            self._serial = serial.Serial(
                port=settings.com_port,
                baudrate=settings.baudrate,
                timeout=settings.timeout_s,
                write_timeout=settings.timeout_s,
            )
            self.connected.emit(True, settings.com_port)
            self._log(f"Connected to {settings.com_port}")
        except Exception as exc:
            self._serial = None
            self.connected.emit(False, "")
            self._log(f"Connection failed: {exc}")

    def _measure_once_worker(self, connection: ConnectionSettings, settings: SweepSettings) -> None:
        completed = False
        rows_collected = 0
        try:
            if not self._serial or not self._serial.is_open:
                self._open_serial_direct(connection)
                if not self._serial or not self._serial.is_open:
                    self._log("Measure Once aborted: no active serial connection")
                    return

            frequency_points_hz = settings.frequency_points_hz or [settings.frequency_start_hz]
            if not frequency_points_hz:
                self._log("Measure Once aborted: no frequency point was provided")
                return

            bias_values = self._build_bias_values(settings)
            if not bias_values:
                self._log("Measure Once aborted: no bias point was provided")
                return

            frequency_hz = float(frequency_points_hz[0])
            bias_value = float(bias_values[0])
            z_ohm, theta_deg, status, raw, measurement_ok = self._acquire_point(
                connection=connection,
                settings=settings,
                frequency_hz=frequency_hz,
                bias_value=bias_value,
            )

            if not measurement_ok:
                self._log("Measure Once failed")

            row = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "sample_id": settings.sample_id,
                "freq_hz": frequency_hz,
                "dc_bias_v": bias_value,
                "raw_response": raw,
                "primary": z_ohm,
                "secondary": theta_deg,
                "status": status,
                "ac_voltage_v": settings.ac_voltage_v,
                "dc_bias_on": settings.use_dc_bias,
                "z_ohm": z_ohm,
                "theta_deg": theta_deg,
                "measurement_ok": measurement_ok,
            }
            self.measurement.emit(row)
            rows_collected = 1
            completed = True
        except Exception as exc:
            self._log(f"Measure Once error: {exc}")
        finally:
            self.sweep_finished.emit(
                {
                    "mode": "measure_once",
                    "completed": completed,
                    "interrupted": False,
                    "rows_collected": rows_collected,
                }
            )

    @staticmethod
    def _build_frequency_points_hz(settings: SweepSettings) -> list[float]:
        start_hz = float(settings.frequency_start_hz)
        stop_hz = float(settings.frequency_stop_hz)
        step_hz = sanitize_step_hz(settings.frequency_step_hz)
        if step_hz <= 0 or start_hz >= stop_hz:
            return []

        points: list[float] = []
        current_hz = start_hz
        max_points = 500000
        while current_hz <= stop_hz + 1e-9:
            points.append(round(current_hz, 12))
            current_hz += step_hz
            if len(points) > max_points:
                break
        return points

    def _acquire_point(
        self,
        connection: ConnectionSettings,
        settings: SweepSettings,
        frequency_hz: float,
        bias_value: float,
    ) -> tuple[float | None, float | None, str, str, bool]:
        # Per-point sequence follows lab-confirmed acquisition order.
        self._write(f"FREQ {frequency_hz:g}", connection.terminator)
        self._write(f"VOLT {settings.ac_voltage_v:g}", connection.terminator)
        if settings.use_dc_bias:
            self._write("BIAS ON", connection.terminator)
            self._write(f":BIAS:VOLTage {bias_value:g}", connection.terminator)
            time.sleep(max(0.0, settings.bias_settle_delay_s))
        else:
            self._write("BIAS OFF", connection.terminator)

        time.sleep(max(0.0, settings.point_settle_delay_s))
        self._log("TRIG step: sending TRIG")
        self._write("TRIG", connection.terminator)
        time.sleep(max(0.0, settings.measure_delay_s))

        raw_response = self._query("FETC?", connection.terminator)
        if not raw_response:
            self._log("FETC? returned empty, attempting READ? fallback")
            raw_response = self._query("READ?", connection.terminator)

        if not raw_response:
            self._log("Acquisition error: empty response after FETC? and READ? fallback")
            return None, None, "FAILED_EMPTY", "<empty>", False

        z_ohm, theta_deg, status = parse_measurement_triple(raw_response)
        if z_ohm is None or theta_deg is None:
            self._log(f"Parsing failed for raw response: {raw_response}")
            status = status or "FAILED_PARSE"
            return z_ohm, theta_deg, status, raw_response, False

        return z_ohm, theta_deg, status or "0", raw_response, True
