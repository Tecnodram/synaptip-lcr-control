from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import serial
import serial.tools.list_ports


class SerialClientError(RuntimeError):
    """Raised when serial communication fails in a recoverable way."""


@dataclass(slots=True)
class PortInfo:
    """Simple representation used by the UI layer."""

    device: str
    description: str


class SerialClient:
    """Low-level serial wrapper for the EUCOL U2829C connection workflow."""

    def __init__(self) -> None:
        self._conn: Optional[serial.Serial] = None

    @property
    def is_connected(self) -> bool:
        return bool(self._conn and self._conn.is_open)

    def list_ports(self) -> list[PortInfo]:
        ports = serial.tools.list_ports.comports()
        results = [
            PortInfo(device=port.device, description=port.description or "Unknown device")
            for port in ports
        ]
        results.sort(key=lambda p: p.device)
        return results

    def open(self, port: str, baud_rate: int, timeout_sec: float) -> None:
        if self.is_connected:
            self.close()

        try:
            self._conn = serial.Serial(
                port=port,
                baudrate=baud_rate,
                timeout=timeout_sec,
                write_timeout=timeout_sec,
            )
        except (serial.SerialException, OSError, ValueError) as exc:
            self._conn = None
            raise SerialClientError(f"Unable to open {port}: {exc}") from exc

    def close(self) -> None:
        if not self._conn:
            return

        try:
            if self._conn.is_open:
                self._conn.close()
        except serial.SerialException as exc:
            raise SerialClientError(f"Error while closing serial port: {exc}") from exc
        finally:
            self._conn = None

    def write_command(self, command: str, terminator: str) -> None:
        if not self.is_connected or not self._conn:
            raise SerialClientError("Cannot write command: no active serial connection")

        try:
            payload = f"{command}{terminator}".encode("ascii", errors="replace")
            self._conn.write(payload)
            self._conn.flush()
        except serial.SerialException as exc:
            raise SerialClientError(f"Failed sending command '{command}': {exc}") from exc

    def read_response(self, terminator: str) -> str:
        if not self.is_connected or not self._conn:
            raise SerialClientError("Cannot read response: no active serial connection")

        expected = terminator.encode("ascii", errors="replace")

        try:
            data = self._conn.read_until(expected=expected)
        except serial.SerialException as exc:
            raise SerialClientError(f"Read failed: {exc}") from exc

        return data.decode("ascii", errors="replace").strip()

    def fetch_measurement(self, terminator: str) -> str:
        """Fetch a single measurement using confirmed command: FETC?."""
        self.write_command(command="FETC?", terminator=terminator)
        return self.read_response(terminator=terminator)

    def set_frequency(self, frequency_hz: float) -> None:
        """Set measurement frequency in Hz using confirmed command: FREQ <value>."""
        command = f"FREQ {frequency_hz:g}"
        self.write_command(command=command, terminator="\n")

    def set_measurement_mode(self, mode: str) -> None:
        """Set measurement mode (e.g. 'Z-\u03b8', 'L-Q', 'C-D').  NOT YET IMPLEMENTED."""
        raise NotImplementedError("set_measurement_mode: U2829C command not yet discovered")

    def set_level(self, level_v: float) -> None:
        """Set AC test level in volts using confirmed command: VOLT <value>."""
        command = f"VOLT {level_v:g}"
        self.write_command(command=command, terminator="\n")

    def set_speed(self, speed: str) -> None:
        """Set measurement speed (e.g. 'SLOW', 'MED', 'FAST').  NOT YET IMPLEMENTED."""
        raise NotImplementedError("set_speed: U2829C command not yet discovered")

    def set_range(self, range_setting: str) -> None:
        """Set measurement range (e.g. 'AUTO', '1K', '10K').  NOT YET IMPLEMENTED."""
        raise NotImplementedError("set_range: U2829C command not yet discovered")

    def set_dc_bias_enabled(self, enabled: bool) -> None:
        """Enable/disable DC bias using confirmed commands: BIAS ON / BIAS OFF."""
        command = "BIAS ON" if enabled else "BIAS OFF"
        self.write_command(command=command, terminator="\n")

    def set_dc_bias_value(self, bias_v: float) -> None:
        """Set DC bias voltage in volts. Command is not confirmed for U2829C yet."""
        raise NotImplementedError("set_dc_bias_value: U2829C command not yet discovered")

    # -------------------------------------------------------------------------
    # Future architecture placeholders
    # -------------------------------------------------------------------------

    def sweep_frequency(self, start_hz: float, stop_hz: float, steps: int) -> None:
        """Future sweep API placeholder."""
        raise NotImplementedError("sweep_frequency: not implemented yet")

    def export_csv(self, file_path: str) -> None:
        """Future export API placeholder."""
        raise NotImplementedError("export_csv: not implemented yet")
