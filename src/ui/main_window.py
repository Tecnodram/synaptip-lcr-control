from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QCloseEvent, QFont, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.controller import AppController, CommandRequest, MeasureRequest
from utils.helpers import (
    TERMINATOR_OPTIONS,
    MeasurementResult,
    get_mode_labels,
    normalize_terminator,
)


class MainWindow(QMainWindow):
    """Main UI window for SynAptIp LCR Control."""

    def __init__(self) -> None:
        super().__init__()
        self._controller = AppController()

        self.setWindowTitle("SynAptIp LCR Control")
        self.setWindowIcon(QIcon(str(self._asset_path("assets/icons/SynAptIp_LCR_Control.ico"))))
        self.setMinimumSize(1180, 780)
        self.resize(1240, 860)

        # Left panel widgets
        self._port_combo: QComboBox
        self._baud_combo: QComboBox
        self._timeout_spin: QDoubleSpinBox
        self._terminator_combo: QComboBox
        self._connect_btn: QPushButton
        self._disconnect_btn: QPushButton
        self._refresh_btn: QPushButton
        self._status_label: QLabel

        self._idn_btn: QPushButton
        self._identity_value_lbl: QLabel

        self._freq_spin: QDoubleSpinBox
        self._apply_freq_btn: QPushButton
        self._level_spin: QDoubleSpinBox
        self._apply_level_btn: QPushButton
        self._bias_on_btn: QPushButton
        self._bias_off_btn: QPushButton

        # Right panel widgets
        self._mode_input: QLineEdit
        self._fetch_measurement_btn: QPushButton
        self._primary_key_lbl: QLabel
        self._secondary_key_lbl: QLabel
        self._res_timestamp_lbl: QLabel
        self._res_raw_lbl: QLabel
        self._res_primary_lbl: QLabel
        self._res_secondary_lbl: QLabel
        self._res_status_lbl: QLabel

        self._trig_btn: QPushButton
        self._manual_input: QLineEdit
        self._expect_response_combo: QComboBox
        self._manual_send_btn: QPushButton

        # Bottom log widgets
        self._log_output: QTextEdit
        self._clear_log_btn: QPushButton

        self._build_ui()
        self._wire_events()
        self._set_connected_state(False, "")
        QTimer.singleShot(0, self._controller.refresh_ports)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    @staticmethod
    def _asset_path(relative_path: str) -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / relative_path
        return Path(__file__).resolve().parents[2] / relative_path

    def _build_ui(self) -> None:
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        title = QLabel("SynAptIp LCR Control")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.DemiBold))
        subtitle = QLabel("Instrument-style LCR control interface for EUCOL U2829C")
        subtitle.setStyleSheet("color: #4b5563;")
        root.addWidget(title)
        root.addWidget(subtitle)

        body = QHBoxLayout()
        body.setSpacing(12)
        left = self._build_left_panel()
        right = self._build_right_panel()
        body.addLayout(left, stretch=9)
        body.addLayout(right, stretch=11)
        root.addLayout(body, stretch=6)

        root.addWidget(self._build_log_panel(), stretch=4)

        self.setCentralWidget(central)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f7fb;
            }
            QGroupBox {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-top: 8px;
                font-weight: 600;
                background: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QPushButton {
                min-height: 30px;
                padding: 4px 10px;
            }
            QLineEdit, QComboBox, QDoubleSpinBox {
                min-height: 28px;
            }
            QTextEdit#sessionLog {
                background-color: #0b1220;
                color: #d7e3ff;
                border-radius: 6px;
                font-family: Consolas;
                font-size: 10.5pt;
            }
            """
        )

    def _build_left_panel(self) -> QVBoxLayout:
        left = QVBoxLayout()
        left.setSpacing(10)
        left.addWidget(self._build_connection_panel())
        left.addWidget(self._build_instrument_info_panel())
        left.addWidget(self._build_quick_control_panel())
        left.addStretch(1)
        return left

    def _build_right_panel(self) -> QVBoxLayout:
        right = QVBoxLayout()
        right.setSpacing(10)
        right.addWidget(self._build_measurement_panel())
        right.addWidget(self._build_diagnostics_panel())
        right.addStretch(1)
        return right

    def _build_connection_panel(self) -> QGroupBox:
        group = QGroupBox("Connection")
        gl = QGridLayout(group)
        gl.setHorizontalSpacing(10)
        gl.setVerticalSpacing(8)

        self._port_combo = QComboBox()
        self._port_combo.setEditable(True)
        self._port_combo.setPlaceholderText("Select or type COM port (e.g., COM4)")

        self._refresh_btn = QPushButton("Refresh Ports")

        self._baud_combo = QComboBox()
        self._baud_combo.setEditable(True)
        self._baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self._baud_combo.setCurrentText("115200")

        self._timeout_spin = QDoubleSpinBox()
        self._timeout_spin.setRange(0.1, 60.0)
        self._timeout_spin.setSingleStep(0.1)
        self._timeout_spin.setValue(1.0)
        self._timeout_spin.setSuffix(" s")

        self._terminator_combo = QComboBox()
        for label, value in TERMINATOR_OPTIONS:
            self._terminator_combo.addItem(label, value)
        self._terminator_combo.setCurrentText(r"\n")

        self._connect_btn = QPushButton("Connect")
        self._disconnect_btn = QPushButton("Disconnect")

        self._status_label = QLabel("Status: Disconnected")
        self._status_label.setStyleSheet("color: #991b1b; font-weight: 600;")

        gl.addWidget(QLabel("COM Port"), 0, 0)
        gl.addWidget(self._port_combo, 0, 1)
        gl.addWidget(self._refresh_btn, 0, 2)
        gl.addWidget(QLabel("Baud Rate"), 1, 0)
        gl.addWidget(self._baud_combo, 1, 1)
        gl.addWidget(QLabel("Timeout"), 1, 2)
        gl.addWidget(self._timeout_spin, 1, 3)
        gl.addWidget(QLabel("Terminator"), 2, 0)
        gl.addWidget(self._terminator_combo, 2, 1)
        gl.addWidget(self._connect_btn, 2, 2)
        gl.addWidget(self._disconnect_btn, 2, 3)
        gl.addWidget(self._status_label, 3, 0, 1, 4)

        return group

    def _build_instrument_info_panel(self) -> QGroupBox:
        group = QGroupBox("Instrument Info")
        gl = QGridLayout(group)
        gl.setHorizontalSpacing(10)
        gl.setVerticalSpacing(8)

        self._idn_btn = QPushButton("Read *IDN?")
        self._identity_value_lbl = QLabel("(not read yet)")
        self._identity_value_lbl.setWordWrap(True)
        self._identity_value_lbl.setStyleSheet("font-family: Consolas; color: #111827;")

        gl.addWidget(self._idn_btn, 0, 0)
        gl.addWidget(QLabel("Identity"), 1, 0)
        gl.addWidget(self._identity_value_lbl, 1, 1, 1, 3)

        return group

    def _build_quick_control_panel(self) -> QGroupBox:
        group = QGroupBox("Quick Instrument Control")
        gl = QGridLayout(group)
        gl.setHorizontalSpacing(10)
        gl.setVerticalSpacing(8)

        self._freq_spin = QDoubleSpinBox()
        self._freq_spin.setDecimals(3)
        self._freq_spin.setRange(1.0, 1000000.0)
        self._freq_spin.setValue(1000.0)
        self._freq_spin.setSuffix(" Hz")
        self._apply_freq_btn = QPushButton("Apply Frequency")

        self._level_spin = QDoubleSpinBox()
        self._level_spin.setDecimals(3)
        self._level_spin.setRange(0.001, 5.0)
        self._level_spin.setValue(0.5)
        self._level_spin.setSuffix(" V")
        self._apply_level_btn = QPushButton("Apply Level")

        self._bias_on_btn = QPushButton("DC Bias ON")
        self._bias_off_btn = QPushButton("DC Bias OFF")

        note = QLabel("Confirmed controls: FREQ, VOLT, BIAS ON/OFF.")
        note.setWordWrap(True)
        note.setStyleSheet("color: #6b7280; font-style: italic;")

        gl.addWidget(QLabel("Frequency"), 0, 0)
        gl.addWidget(self._freq_spin, 0, 1)
        gl.addWidget(self._apply_freq_btn, 0, 2)
        gl.addWidget(QLabel("AC Level"), 1, 0)
        gl.addWidget(self._level_spin, 1, 1)
        gl.addWidget(self._apply_level_btn, 1, 2)
        gl.addWidget(QLabel("DC Bias State"), 2, 0)
        gl.addWidget(self._bias_on_btn, 2, 1)
        gl.addWidget(self._bias_off_btn, 2, 2)
        gl.addWidget(note, 3, 0, 1, 3)

        return group

    def _build_measurement_panel(self) -> QGroupBox:
        group = QGroupBox("Measurement")
        gl = QGridLayout(group)
        gl.setHorizontalSpacing(12)
        gl.setVerticalSpacing(8)
        gl.setColumnStretch(1, 2)
        gl.setColumnStretch(3, 2)

        self._mode_input = QLineEdit()
        self._mode_input.setText("Z-θ (manual assumption)")
        self._mode_input.setPlaceholderText("e.g. Z-θ, L-Q, C-D")

        self._fetch_measurement_btn = QPushButton("Fetch Measurement")

        gl.addWidget(QLabel("Mode assumption"), 0, 0)
        gl.addWidget(self._mode_input, 0, 1)
        gl.addWidget(self._fetch_measurement_btn, 0, 2)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #e5e7eb;")
        gl.addWidget(sep, 1, 0, 1, 4)

        hdr = QLabel("Latest Measurement")
        hdr.setStyleSheet("font-weight: 600; color: #374151;")
        gl.addWidget(hdr, 2, 0, 1, 4)

        def _value_label(text: str = "—") -> QLabel:
            lbl = QLabel(text)
            lbl.setStyleSheet("font-family: Consolas; color: #111827; font-size: 10pt;")
            return lbl

        self._res_timestamp_lbl = _value_label()
        self._res_raw_lbl = _value_label()
        self._res_primary_lbl = _value_label()
        self._res_secondary_lbl = _value_label()
        self._res_status_lbl = _value_label()

        self._primary_key_lbl = QLabel("Primary value")
        self._secondary_key_lbl = QLabel("Secondary value")

        gl.addWidget(QLabel("Timestamp"), 3, 0)
        gl.addWidget(self._res_timestamp_lbl, 3, 1, 1, 3)
        gl.addWidget(QLabel("Raw response"), 4, 0)
        gl.addWidget(self._res_raw_lbl, 4, 1, 1, 3)
        gl.addWidget(self._primary_key_lbl, 5, 0)
        gl.addWidget(self._res_primary_lbl, 5, 1)
        gl.addWidget(self._secondary_key_lbl, 5, 2)
        gl.addWidget(self._res_secondary_lbl, 5, 3)
        gl.addWidget(QLabel("Status flag"), 6, 0)
        gl.addWidget(self._res_status_lbl, 6, 1)

        return group

    def _build_diagnostics_panel(self) -> QGroupBox:
        group = QGroupBox("Diagnostics / Manual Commands")
        gl = QGridLayout(group)
        gl.setHorizontalSpacing(10)
        gl.setVerticalSpacing(8)

        self._trig_btn = QPushButton("Send TRIG")
        self._manual_input = QLineEdit()
        self._manual_input.setPlaceholderText("Enter manual command")

        self._expect_response_combo = QComboBox()
        self._expect_response_combo.addItem("Expect response", True)
        self._expect_response_combo.addItem("No response expected", False)

        self._manual_send_btn = QPushButton("Send Command")

        gl.addWidget(self._trig_btn, 0, 0)
        gl.addWidget(QLabel("Manual command"), 1, 0)
        gl.addWidget(self._manual_input, 1, 1, 1, 2)
        gl.addWidget(self._expect_response_combo, 2, 0)
        gl.addWidget(self._manual_send_btn, 2, 1)

        note = QLabel(
            "Manual commands are for diagnostics/protocol exploration. "
            "For write commands, confirm success on the instrument front panel."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #6b7280; font-style: italic;")
        gl.addWidget(note, 3, 0, 1, 3)

        return group

    def _build_log_panel(self) -> QGroupBox:
        group = QGroupBox("Session Log")
        vl = QVBoxLayout(group)

        self._log_output = QTextEdit()
        self._log_output.setObjectName("sessionLog")
        self._log_output.setReadOnly(True)
        self._log_output.setPlaceholderText("Timestamped communication log appears here")

        self._clear_log_btn = QPushButton("Clear Log")

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._clear_log_btn)

        vl.addWidget(self._log_output)
        vl.addLayout(row)

        return group

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------

    def _wire_events(self) -> None:
        self._refresh_btn.clicked.connect(self._controller.refresh_ports)
        self._connect_btn.clicked.connect(self._on_connect_clicked)
        self._disconnect_btn.clicked.connect(self._controller.disconnect_port)

        self._idn_btn.clicked.connect(self._send_idn)

        self._apply_freq_btn.clicked.connect(self._apply_frequency)
        self._apply_level_btn.clicked.connect(self._apply_level)
        self._bias_on_btn.clicked.connect(self._bias_on)
        self._bias_off_btn.clicked.connect(self._bias_off)

        self._fetch_measurement_btn.clicked.connect(self._fetch_measurement)

        self._trig_btn.clicked.connect(self._send_trig)
        self._manual_send_btn.clicked.connect(self._send_manual)
        self._manual_input.returnPressed.connect(self._send_manual)

        self._clear_log_btn.clicked.connect(self._log_output.clear)

        self._controller.log_line.connect(self._append_log)
        self._controller.ports_updated.connect(self._on_ports_updated)
        self._controller.connection_changed.connect(self._set_connected_state)
        self._controller.identity_received.connect(self._on_identity_received)
        self._controller.measurement_result.connect(self._on_measurement_result)

    def _disconnect_controller_signals(self) -> None:
        for signal, slot in (
            (self._controller.log_line, self._append_log),
            (self._controller.ports_updated, self._on_ports_updated),
            (self._controller.connection_changed, self._set_connected_state),
            (self._controller.identity_received, self._on_identity_received),
            (self._controller.measurement_result, self._on_measurement_result),
        ):
            try:
                signal.disconnect(slot)
            except (RuntimeError, TypeError):
                pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _selected_terminator(self) -> str:
        data: Optional[str] = self._terminator_combo.currentData(Qt.ItemDataRole.UserRole)
        if isinstance(data, str):
            return data
        return normalize_terminator(self._terminator_combo.currentText())

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _on_connect_clicked(self) -> None:
        port_value = self._port_combo.currentText().strip()
        if " - " in port_value:
            port_value = port_value.split(" - ", 1)[0].strip()

        if not port_value:
            QMessageBox.warning(self, "Missing COM Port", "Please select or type a COM port.")
            return

        baud_text = self._baud_combo.currentText().strip()
        try:
            baud_rate = int(baud_text)
        except ValueError:
            QMessageBox.warning(self, "Invalid Baud Rate", "Please enter a valid integer baud rate.")
            return

        self._controller.connect_port(
            port=port_value,
            baud_rate=baud_rate,
            timeout_sec=float(self._timeout_spin.value()),
        )

    def _send_idn(self) -> None:
        self._controller.send_idn(self._selected_terminator())

    def _fetch_measurement(self) -> None:
        self._controller.fetch_measurement(
            MeasureRequest(
                terminator=self._selected_terminator(),
                mode_assumption=self._mode_input.text().strip(),
            )
        )

    def _apply_frequency(self) -> None:
        self._controller.set_frequency(self._freq_spin.value(), self._selected_terminator())

    def _apply_level(self) -> None:
        self._controller.set_level(self._level_spin.value(), self._selected_terminator())

    def _bias_on(self) -> None:
        self._controller.set_dc_bias_enabled(True, self._selected_terminator())

    def _bias_off(self) -> None:
        self._controller.set_dc_bias_enabled(False, self._selected_terminator())

    def _send_trig(self) -> None:
        self._controller.send_command(
            CommandRequest(
                command="TRIG",
                terminator=self._selected_terminator(),
                expect_response=True,
                response_optional=True,
            )
        )

    def _send_manual(self) -> None:
        command = self._manual_input.text().strip()
        if not command:
            return

        expect_response = bool(self._expect_response_combo.currentData(Qt.ItemDataRole.UserRole))
        self._controller.send_command(
            CommandRequest(
                command=command,
                terminator=self._selected_terminator(),
                expect_response=expect_response,
                response_optional=True,
            )
        )

    # ------------------------------------------------------------------
    # Slot handlers
    # ------------------------------------------------------------------

    def _on_identity_received(self, identity: str) -> None:
        self._identity_value_lbl.setText(identity if identity else "<empty identity response>")

    def _on_measurement_result(self, result: object) -> None:
        if not isinstance(result, MeasurementResult):
            return

        p_label, s_label = get_mode_labels(result.mode_assumption)
        self._primary_key_lbl.setText(p_label)
        self._secondary_key_lbl.setText(s_label)

        self._res_timestamp_lbl.setText(result.timestamp)
        self._res_raw_lbl.setText(result.raw_response)

        if result.primary_value is not None:
            self._res_primary_lbl.setText(f"{result.primary_value:.6g}")
        else:
            self._res_primary_lbl.setText("(parse error)")

        if result.secondary_value is not None:
            self._res_secondary_lbl.setText(f"{result.secondary_value:.6g}")
        else:
            self._res_secondary_lbl.setText("(parse error)")

        self._res_status_lbl.setText(result.status_flag if result.status_flag else "—")

    def _append_log(self, line: str) -> None:
        self._log_output.append(line)

    def _on_ports_updated(self, ports: list[str]) -> None:
        current = self._port_combo.currentText().strip()

        self._port_combo.blockSignals(True)
        self._port_combo.clear()
        self._port_combo.addItems(ports)

        if current:
            self._port_combo.setCurrentText(current)
        elif ports:
            if any(item.startswith("COM4") for item in ports):
                for index, item in enumerate(ports):
                    if item.startswith("COM4"):
                        self._port_combo.setCurrentIndex(index)
                        break
            else:
                self._port_combo.setCurrentIndex(0)

        self._port_combo.blockSignals(False)

    def _set_connected_state(self, connected: bool, port: str) -> None:
        self._connect_btn.setEnabled(not connected)
        self._disconnect_btn.setEnabled(connected)

        self._idn_btn.setEnabled(connected)
        self._fetch_measurement_btn.setEnabled(connected)

        self._apply_freq_btn.setEnabled(connected)
        self._apply_level_btn.setEnabled(connected)
        self._bias_on_btn.setEnabled(connected)
        self._bias_off_btn.setEnabled(connected)

        self._trig_btn.setEnabled(connected)
        self._manual_send_btn.setEnabled(connected)

        self._refresh_btn.setEnabled(not connected)
        self._port_combo.setEnabled(not connected)
        self._baud_combo.setEnabled(not connected)
        self._timeout_spin.setEnabled(not connected)
        self._terminator_combo.setEnabled(not connected)

        if connected:
            self._status_label.setText(f"Status: Connected ({port})")
            self._status_label.setStyleSheet("color: #166534; font-weight: 600;")
        else:
            self._status_label.setText("Status: Disconnected")
            self._status_label.setStyleSheet("color: #991b1b; font-weight: 600;")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            if hasattr(self, "_controller") and self._controller is not None:
                self._disconnect_controller_signals()
                self._controller.shutdown()
        finally:
            super().closeEvent(event)
