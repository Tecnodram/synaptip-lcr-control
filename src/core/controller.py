from __future__ import annotations

import logging
from dataclasses import dataclass

from PySide6.QtCore import QObject, QThread, Signal, Slot

from instrument.serial_client import SerialClient, SerialClientError
from utils.helpers import MeasurementResult, format_log_line, parse_measurement_response


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class CommandRequest:
    command: str
    terminator: str
    expect_response: bool
    response_optional: bool = False


@dataclass(slots=True)
class MeasureRequest:
    """Parameters for a single FETC? measurement fetch."""

    terminator: str
    mode_assumption: str  # user-supplied label used for result field annotation


class SerialWorker(QObject):
    """Performs all serial I/O in a dedicated worker thread."""

    ports_ready = Signal(list)
    connected = Signal(str)
    disconnected = Signal()
    command_sent = Signal(str)
    response_ready = Signal(str)
    measurement_raw = Signal(str)  # raw response string from a Measure Once cycle
    error = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._client = SerialClient()

    @Slot()
    def refresh_ports(self) -> None:
        try:
            ports = self._client.list_ports()
            formatted = [f"{p.device} - {p.description}" for p in ports]
            self.ports_ready.emit(formatted)
        except SerialClientError as exc:
            self.error.emit(str(exc))
        except Exception as exc:  # defensive catch to protect UI loop
            self.error.emit(f"Unexpected port scan error: {exc}")

    @Slot(str, int, float)
    def connect_port(self, port: str, baud_rate: int, timeout_sec: float) -> None:
        try:
            self._client.open(port=port, baud_rate=baud_rate, timeout_sec=timeout_sec)
            self.connected.emit(port)
        except SerialClientError as exc:
            self.error.emit(str(exc))

    @Slot()
    def disconnect_port(self) -> None:
        try:
            self._client.close()
            self.disconnected.emit()
        except SerialClientError as exc:
            self.error.emit(str(exc))

    @Slot(str, str, bool, bool)
    def send(self, command: str, terminator: str, expect_response: bool, response_optional: bool) -> None:
        try:
            self._client.write_command(command=command, terminator=terminator)
            self.command_sent.emit(command)

            if expect_response:
                response = self._client.read_response(terminator=terminator)
                if response:
                    self.response_ready.emit(response)
                elif response_optional:
                    self.response_ready.emit("<no response>")
                else:
                    self.error.emit("Timeout or empty response")
        except SerialClientError as exc:
            self.error.emit(str(exc))

    @Slot(str)
    def do_measure(self, terminator: str) -> None:
        """
        Fetch one measurement using confirmed command: FETC?.

        Confirmed U2829C sequence:
            1. Send FETC?
            2. Read the comma-separated result line
        """
        try:
            self._client.write_command(command="FETC?", terminator=terminator)
            self.command_sent.emit("FETC?")

            response = self._client.read_response(terminator=terminator)
            if not response:
                self.error.emit("Fetch Measurement: no response after FETC?")
                return

            self.response_ready.emit(response)
            self.measurement_raw.emit(response)
        except SerialClientError as exc:
            self.error.emit(str(exc))


class AppController(QObject):
    """Coordinates UI events and background serial worker interactions."""

    log_line = Signal(str)
    ports_updated = Signal(list)
    connection_changed = Signal(bool, str)
    measurement_result = Signal(object)       # emits MeasurementResult
    identity_received = Signal(str)
    response_received = Signal(str)

    request_refresh_ports = Signal()
    request_connect = Signal(str, int, float)
    request_disconnect = Signal()
    request_send = Signal(str, str, bool, bool)
    request_measure = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._connected = False
        self._connected_port = ""
        self._is_shutting_down = False
        self._last_mode_assumption = ""  # cached at measure_once call time
        self._awaiting_idn = False

        self._worker_thread = QThread()
        self._worker = SerialWorker()
        self._worker.moveToThread(self._worker_thread)

        self.request_refresh_ports.connect(self._worker.refresh_ports)
        self.request_connect.connect(self._worker.connect_port)
        self.request_disconnect.connect(self._worker.disconnect_port)
        self.request_send.connect(self._worker.send)
        self.request_measure.connect(self._worker.do_measure)

        self._worker.ports_ready.connect(self._on_ports_ready)
        self._worker.connected.connect(self._on_connected)
        self._worker.disconnected.connect(self._on_disconnected)
        self._worker.command_sent.connect(self._on_command_sent)
        self._worker.response_ready.connect(self._on_response_ready)
        self._worker.measurement_raw.connect(self._on_measurement_raw)
        self._worker.error.connect(self._on_error)

    def _ensure_worker_thread_started(self) -> None:
        if self._is_shutting_down:
            return
        if self._worker_thread is not None and not self._worker_thread.isRunning():
            self._worker_thread.start()

    @Slot()
    def refresh_ports(self) -> None:
        self._ensure_worker_thread_started()
        self.request_refresh_ports.emit()

    @Slot(str, int, float)
    def connect_port(self, port: str, baud_rate: int, timeout_sec: float) -> None:
        self._ensure_worker_thread_started()
        self.log_line.emit(format_log_line(f"Connecting to {port} at {baud_rate} bps, timeout={timeout_sec:.2f}s"))
        self.request_connect.emit(port, baud_rate, timeout_sec)

    @Slot()
    def disconnect_port(self) -> None:
        if self._worker_thread is not None and self._worker_thread.isRunning():
            self.request_disconnect.emit()

    def send_command(self, request: CommandRequest) -> None:
        if not self._connected:
            self.log_line.emit(format_log_line("Error: Not connected to an instrument"))
            return
        self._ensure_worker_thread_started()
        self.request_send.emit(
            request.command,
            request.terminator,
            request.expect_response,
            request.response_optional,
        )

    def _send_confirmed_write(self, command: str, terminator: str) -> None:
        """Send a confirmed write command and log write-verification guidance."""
        self.send_command(
            CommandRequest(
                command=command,
                terminator=terminator,
                expect_response=False,
                response_optional=True,
            )
        )
        self.log_line.emit(
            format_log_line(
                "Write command sent. Serial response may be absent even when command succeeds; "
                "use the instrument front-panel display as current source of truth."
            )
        )

    def send_idn(self, terminator: str) -> None:
        """Request and publish instrument identity using *idn?."""
        if not self._connected:
            self.log_line.emit(format_log_line("Error: Not connected to an instrument"))
            return
        self._awaiting_idn = True
        self.send_command(
            CommandRequest(
                command="*idn?",
                terminator=terminator,
                expect_response=True,
                response_optional=False,
            )
        )

    def set_frequency(self, frequency_hz: float, terminator: str) -> None:
        """Confirmed command mapping: set_frequency(value) -> FREQ <value>."""
        self._send_confirmed_write(f"FREQ {frequency_hz:g}", terminator)

    def set_level(self, level_v: float, terminator: str) -> None:
        """Confirmed command mapping: set_level(value) -> VOLT <value>."""
        self._send_confirmed_write(f"VOLT {level_v:g}", terminator)

    def set_dc_bias_enabled(self, enabled: bool, terminator: str) -> None:
        """Confirmed command mapping: BIAS ON / BIAS OFF."""
        self._send_confirmed_write("BIAS ON" if enabled else "BIAS OFF", terminator)

    def fetch_measurement(self, request: MeasureRequest) -> None:
        """
        Fetch a single measurement line via FETC?, parse it, and emit a structured
        MeasurementResult via the measurement_result signal.
        """
        if not self._connected:
            self.log_line.emit(format_log_line("Error: Not connected to an instrument"))
            return
        self._ensure_worker_thread_started()
        self._last_mode_assumption = request.mode_assumption
        self.request_measure.emit(request.terminator)

    @Slot(list)
    def _on_ports_ready(self, ports: list[str]) -> None:
        self.ports_updated.emit(ports)
        self.log_line.emit(format_log_line(f"Detected {len(ports)} COM port(s)"))

    @Slot(str)
    def _on_connected(self, port: str) -> None:
        self._connected = True
        self._connected_port = port
        self.connection_changed.emit(True, port)
        self.log_line.emit(format_log_line(f"Connected to {port}"))

    @Slot()
    def _on_disconnected(self) -> None:
        was_connected = self._connected
        old_port = self._connected_port
        self._connected = False
        self._connected_port = ""
        self.connection_changed.emit(False, "")
        if was_connected:
            self.log_line.emit(format_log_line(f"Disconnected from {old_port}"))
        else:
            self.log_line.emit(format_log_line("Disconnected"))

    @Slot(str)
    def _on_command_sent(self, command: str) -> None:
        self.log_line.emit(format_log_line(f"Sent: {command}"))

    @Slot(str)
    def _on_response_ready(self, response: str) -> None:
        self.log_line.emit(format_log_line(f"Response: {response}"))
        self.response_received.emit(response)
        if self._awaiting_idn:
            self._awaiting_idn = False
            self.identity_received.emit(response)

    @Slot(str)
    def _on_measurement_raw(self, raw: str) -> None:
        """Parse a raw measurement response and emit a structured MeasurementResult."""
        result = parse_measurement_response(raw, self._last_mode_assumption)
        self.log_line.emit(
            format_log_line(
                f"Measurement: raw={raw!r}  "
                f"primary={result.primary_value}  "
                f"secondary={result.secondary_value}  "
                f"status={result.status_flag!r}"
            )
        )
        self.measurement_result.emit(result)

    @Slot(str)
    def _on_error(self, message: str) -> None:
        if self._awaiting_idn:
            self._awaiting_idn = False
        self.log_line.emit(format_log_line(f"Error: {message}"))

    def sweep_frequency(self, start_hz: float, stop_hz: float, steps: int) -> None:
        """Future automation placeholder."""
        raise NotImplementedError("sweep_frequency: not implemented yet")

    def export_csv(self, file_path: str) -> None:
        """Future export placeholder."""
        raise NotImplementedError("export_csv: not implemented yet")

    def _shutdown_worker_thread(self) -> None:
        worker_thread = getattr(self, "_worker_thread", None)
        if worker_thread is None or not worker_thread.isRunning():
            return

        # Graceful path: ask the event loop to quit and wait for a clean stop.
        worker_thread.quit()
        if worker_thread.wait(2000):
            return

        # Escalation path: only if graceful shutdown times out.
        LOGGER.warning("Worker thread did not stop after graceful quit; forcing termination")

        # Last resort only. terminate() can interrupt execution abruptly.
        worker_thread.terminate()
        if not worker_thread.wait(500):
            LOGGER.error("Worker thread did not stop after terminate() fallback")

    def shutdown(self) -> None:
        """Stop worker thread cleanly when app exits."""
        if self._is_shutting_down:
            return

        self._is_shutting_down = True

        worker_thread = getattr(self, "_worker_thread", None)
        if worker_thread is None:
            return

        try:
            if worker_thread.isRunning():
                self.request_disconnect.emit()
        except Exception:
            pass
        finally:
            self._shutdown_worker_thread()
