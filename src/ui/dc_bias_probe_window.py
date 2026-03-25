from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QCloseEvent, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.controller import AppController, CommandRequest
from utils.helpers import TERMINATOR_OPTIONS, format_log_line, normalize_terminator


class DcBiasProbeWindow(QMainWindow):
    """Experimental utility for probing U2829C DC bias command behavior."""

    def __init__(self) -> None:
        super().__init__()
        self._controller = AppController()
        self._sequence_steps: list[dict[str, object]] = []
        self._sequence_running = False
        self._sequence_name = ""
        self._sequence_on_finished: Optional[Callable[[], None]] = None
        self._pending_response_context: Optional[str] = None

        self.setWindowTitle("SynAptIp DC Bias Probe")
        self.setWindowIcon(QIcon(str(self._asset_path("assets/icons/SynAptIp_DC_Bias_Probe.ico"))))
        self.setMinimumSize(1360, 900)
        self.resize(1480, 980)

        self._port_combo: QComboBox
        self._baud_combo: QComboBox
        self._timeout_spin: QDoubleSpinBox
        self._terminator_combo: QComboBox
        self._connect_btn: QPushButton
        self._disconnect_btn: QPushButton
        self._refresh_btn: QPushButton
        self._status_label: QLabel
        self._identity_value_lbl: QLabel

        self._bias_settle_spin: QDoubleSpinBox
        self._measure_delay_spin: QDoubleSpinBox
        self._bias_voltage_spin: QDoubleSpinBox
        self._sweep_values_input: QLineEdit
        self._candidate_input: QLineEdit

        self._preset_combo: QComboBox
        self._load_preset_btn: QPushButton
        self._run_preset_btn: QPushButton
        self._preset_summary: QTextEdit

        self._idn_btn: QPushButton
        self._fetch_once_btn: QPushButton
        self._probe_queries_btn: QPushButton
        self._bias_on_btn: QPushButton
        self._bias_off_btn: QPushButton
        self._set_bias_voltage_btn: QPushButton
        self._measure_with_bias_btn: QPushButton
        self._run_sweep_btn: QPushButton
        self._error_query_btn: QPushButton
        self._send_candidate_btn: QPushButton

        self._results_output: QTextEdit
        self._log_output: QTextEdit
        self._save_log_btn: QPushButton
        self._clear_log_btn: QPushButton
        self._clear_results_btn: QPushButton

        self._build_ui()
        self._wire_events()
        self._load_selected_preset(initial=True)
        self._set_connected_state(False, "")
        QTimer.singleShot(0, self._controller.refresh_ports)

    @staticmethod
    def _asset_path(relative_path: str) -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / relative_path
        return Path(__file__).resolve().parents[2] / relative_path

    def _build_ui(self) -> None:
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(12)

        root.addWidget(self._build_header())

        top = QHBoxLayout()
        top.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(10)
        left.addWidget(self._build_connection_group())
        left.addWidget(self._build_parameters_group())

        right = QVBoxLayout()
        right.setSpacing(10)
        right.addWidget(self._build_actions_group())

        top.addLayout(left, 9)
        top.addLayout(right, 11)
        root.addLayout(top, stretch=4)
        root.addWidget(self._build_output_splitter(), stretch=6)

        self.setCentralWidget(central)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f3f6fb;
            }
            QWidget#probeHeader {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f172a,
                    stop:0.55 #1d4ed8,
                    stop:1 #0b5cab
                );
                border-radius: 14px;
            }
            QLabel#headerEyebrow {
                color: #bfdbfe;
                font-size: 10pt;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QLabel#headerTitle {
                color: #f8fafc;
                font-size: 20pt;
                font-weight: 700;
            }
            QLabel#headerSubtitle {
                color: #dbeafe;
                font-size: 10.5pt;
            }
            QLabel#headerBadge {
                color: #082f49;
                background: #fef3c7;
                border-radius: 10px;
                padding: 4px 10px;
                font-weight: 700;
            }
            QLabel#headerNote {
                color: #fef3c7;
                font-size: 10pt;
            }
            QGroupBox {
                border: 1px solid #d1d5db;
                border-radius: 10px;
                margin-top: 8px;
                font-weight: 700;
                background: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }
            QPushButton {
                min-height: 32px;
                padding: 5px 11px;
            }
            QPushButton#primaryAction {
                background-color: #0f62fe;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 700;
            }
            QPushButton#primaryAction:disabled {
                background-color: #93c5fd;
                color: #eff6ff;
            }
            QLineEdit, QComboBox, QDoubleSpinBox {
                min-height: 30px;
            }
            QTextEdit#presetSummary {
                background-color: #f8fafc;
                border: 1px solid #dbe3ef;
                border-radius: 8px;
                font-family: Consolas;
                font-size: 10pt;
            }
            QTextEdit#probeResults {
                background-color: #081c15;
                color: #d1fae5;
                border-radius: 8px;
                font-family: Consolas;
                font-size: 10.5pt;
            }
            QTextEdit#sessionLog {
                background-color: #0b1220;
                color: #d7e3ff;
                border-radius: 8px;
                font-family: Consolas;
                font-size: 10.5pt;
            }
            """
        )

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("probeHeader")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        logo_label = QLabel()
        logo_label.setFixedSize(92, 92)
        logo_pixmap = QPixmap(str(self._asset_path("assets/icons/SynAptIp_DC_Bias_Probe.ico")))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaled(76, 76, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        eyebrow = QLabel("SYNAPTIP TECHNOLOGIES")
        eyebrow.setObjectName("headerEyebrow")
        title = QLabel("SynAptIp DC Bias Probe")
        title.setObjectName("headerTitle")
        subtitle = QLabel(
            "Version 2 experimental workstation for DC bias validation, preset-driven testing, and sweep-style lab probing"
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("headerSubtitle")

        badge_row = QHBoxLayout()
        badge_row.setSpacing(8)
        badge = QLabel("Experimental Validation Tool")
        badge.setObjectName("headerBadge")
        note = QLabel("Confirmed operational controls stay isolated in SynAptIp LCR Control.")
        note.setObjectName("headerNote")
        badge_row.addWidget(badge)
        badge_row.addWidget(note, stretch=1)

        text_col.addWidget(eyebrow)
        text_col.addWidget(title)
        text_col.addWidget(subtitle)
        text_col.addLayout(badge_row)

        layout.addWidget(logo_label)
        layout.addLayout(text_col, stretch=1)

        return header

    def _build_connection_group(self) -> QGroupBox:
        group = QGroupBox("Connection / Settings")
        gl = QGridLayout(group)
        gl.setHorizontalSpacing(12)
        gl.setVerticalSpacing(9)

        self._port_combo = QComboBox()
        self._port_combo.setEditable(True)
        self._port_combo.setPlaceholderText("Select or type COM port (for example COM4)")

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
        self._connect_btn.setObjectName("primaryAction")
        self._disconnect_btn = QPushButton("Disconnect")

        self._status_label = QLabel("Status: Disconnected")
        self._status_label.setStyleSheet("color: #991b1b; font-weight: 700;")

        self._idn_btn = QPushButton("IDN")
        self._identity_value_lbl = QLabel("(not read yet)")
        self._identity_value_lbl.setWordWrap(True)
        self._identity_value_lbl.setStyleSheet("font-family: Consolas; color: #111827;")

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
        gl.addWidget(QLabel("Identity"), 4, 0)
        gl.addWidget(self._identity_value_lbl, 4, 1, 1, 3)

        return group

    def _build_parameters_group(self) -> QGroupBox:
        group = QGroupBox("Experimental Parameters")
        gl = QGridLayout(group)
        gl.setHorizontalSpacing(12)
        gl.setVerticalSpacing(9)

        self._bias_settle_spin = QDoubleSpinBox()
        self._bias_settle_spin.setRange(0.0, 10.0)
        self._bias_settle_spin.setSingleStep(0.05)
        self._bias_settle_spin.setValue(0.30)
        self._bias_settle_spin.setSuffix(" s")

        self._measure_delay_spin = QDoubleSpinBox()
        self._measure_delay_spin.setRange(0.0, 10.0)
        self._measure_delay_spin.setSingleStep(0.05)
        self._measure_delay_spin.setValue(0.20)
        self._measure_delay_spin.setSuffix(" s")

        self._bias_voltage_spin = QDoubleSpinBox()
        self._bias_voltage_spin.setDecimals(3)
        self._bias_voltage_spin.setRange(-20.0, 20.0)
        self._bias_voltage_spin.setSingleStep(0.1)
        self._bias_voltage_spin.setValue(0.5)
        self._bias_voltage_spin.setSuffix(" V")

        self._sweep_values_input = QLineEdit("-1.0,-0.5,0.0,0.5,1.0")
        self._sweep_values_input.setPlaceholderText("Comma-separated voltages")

        self._candidate_input = QLineEdit()
        self._candidate_input.setPlaceholderText("Manual experimental command, for example :DCBIAS:VOLT 0.500")

        self._send_candidate_btn = QPushButton("Send Candidate Once")

        note = QLabel(
            "Experimental presets do not claim any DC bias numeric syntax is confirmed. "
            "All candidate commands are logged and should be validated against the instrument front panel."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #6b7280; font-style: italic;")

        gl.addWidget(QLabel("Bias settle delay"), 0, 0)
        gl.addWidget(self._bias_settle_spin, 0, 1)
        gl.addWidget(QLabel("Measure delay"), 0, 2)
        gl.addWidget(self._measure_delay_spin, 0, 3)
        gl.addWidget(QLabel("Candidate bias voltage"), 1, 0)
        gl.addWidget(self._bias_voltage_spin, 1, 1)
        gl.addWidget(QLabel("Short sweep voltages"), 1, 2)
        gl.addWidget(self._sweep_values_input, 1, 3)
        gl.addWidget(QLabel("Manual candidate command"), 2, 0)
        gl.addWidget(self._candidate_input, 2, 1, 1, 2)
        gl.addWidget(self._send_candidate_btn, 2, 3)
        gl.addWidget(note, 3, 0, 1, 4)

        return group

    def _build_actions_group(self) -> QGroupBox:
        group = QGroupBox("Preset Runner / Quick Actions")
        outer = QVBoxLayout(group)
        outer.setSpacing(10)

        preset_row = QGridLayout()
        preset_row.setHorizontalSpacing(10)
        preset_row.setVerticalSpacing(8)

        self._preset_combo = QComboBox()
        for key, label in self._preset_definitions():
            self._preset_combo.addItem(label, key)

        self._load_preset_btn = QPushButton("Load Preset")
        self._run_preset_btn = QPushButton("Run Preset")
        self._run_preset_btn.setObjectName("primaryAction")

        preset_row.addWidget(QLabel("Preset"), 0, 0)
        preset_row.addWidget(self._preset_combo, 0, 1)
        preset_row.addWidget(self._load_preset_btn, 0, 2)
        preset_row.addWidget(self._run_preset_btn, 0, 3)

        self._preset_summary = QTextEdit()
        self._preset_summary.setObjectName("presetSummary")
        self._preset_summary.setReadOnly(True)
        self._preset_summary.setMinimumHeight(160)

        action_grid = QGridLayout()
        action_grid.setHorizontalSpacing(10)
        action_grid.setVerticalSpacing(9)

        self._fetch_once_btn = QPushButton("Fetch once")
        self._probe_queries_btn = QPushButton("Probe DC Bias Queries")
        self._bias_on_btn = QPushButton("Try Bias ON")
        self._bias_off_btn = QPushButton("Try Bias OFF")
        self._set_bias_voltage_btn = QPushButton("Try Set Bias Voltage")
        self._measure_with_bias_btn = QPushButton("Measure with Bias")
        self._run_sweep_btn = QPushButton("Run Bias Sweep")
        self._error_query_btn = QPushButton("Try Error Query")

        action_grid.addWidget(self._idn_btn, 0, 0)
        action_grid.addWidget(self._fetch_once_btn, 0, 1)
        action_grid.addWidget(self._probe_queries_btn, 0, 2)
        action_grid.addWidget(self._bias_on_btn, 1, 0)
        action_grid.addWidget(self._bias_off_btn, 1, 1)
        action_grid.addWidget(self._set_bias_voltage_btn, 1, 2)
        action_grid.addWidget(self._measure_with_bias_btn, 2, 0)
        action_grid.addWidget(self._run_sweep_btn, 2, 1)
        action_grid.addWidget(self._error_query_btn, 2, 2)

        note = QLabel(
            "Quick actions run preloaded experimental command families. Unsupported syntax should not crash the app; "
            "responses and errors are captured in the output panes below."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #6b7280; font-style: italic;")

        outer.addLayout(preset_row)
        outer.addWidget(self._preset_summary)
        outer.addLayout(action_grid)
        outer.addWidget(note)

        return group

    def _build_output_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self._build_results_group())
        splitter.addWidget(self._build_log_group())
        splitter.setSizes([420, 340])
        return splitter

    def _build_results_group(self) -> QGroupBox:
        group = QGroupBox("Experimental Results")
        layout = QVBoxLayout(group)

        self._results_output = QTextEdit()
        self._results_output.setObjectName("probeResults")
        self._results_output.setReadOnly(True)
        self._results_output.setPlaceholderText(
            "Preset activity, experimental notes, candidate command context, and measurement markers appear here."
        )

        self._clear_results_btn = QPushButton("Clear Results")

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._clear_results_btn)

        layout.addWidget(self._results_output)
        layout.addLayout(row)

        return group

    def _build_log_group(self) -> QGroupBox:
        group = QGroupBox("Session Log")
        layout = QVBoxLayout(group)

        self._log_output = QTextEdit()
        self._log_output.setObjectName("sessionLog")
        self._log_output.setReadOnly(True)
        self._log_output.setPlaceholderText("Timestamped transport log appears here.")

        self._save_log_btn = QPushButton("Save Log")
        self._clear_log_btn = QPushButton("Clear Log")

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._save_log_btn)
        row.addWidget(self._clear_log_btn)

        layout.addWidget(self._log_output)
        layout.addLayout(row)

        return group

    def _wire_events(self) -> None:
        self._refresh_btn.clicked.connect(self._controller.refresh_ports)
        self._connect_btn.clicked.connect(self._on_connect_clicked)
        self._disconnect_btn.clicked.connect(self._controller.disconnect_port)

        self._idn_btn.clicked.connect(self._send_idn)
        self._fetch_once_btn.clicked.connect(self._fetch_once)
        self._probe_queries_btn.clicked.connect(lambda: self._run_named_preset("B"))
        self._bias_on_btn.clicked.connect(lambda: self._run_named_preset("D"))
        self._bias_off_btn.clicked.connect(lambda: self._run_named_preset("E"))
        self._set_bias_voltage_btn.clicked.connect(lambda: self._run_named_preset("F"))
        self._measure_with_bias_btn.clicked.connect(lambda: self._run_named_preset("G"))
        self._run_sweep_btn.clicked.connect(self._run_bias_sweep)
        self._error_query_btn.clicked.connect(lambda: self._run_named_preset("C"))
        self._send_candidate_btn.clicked.connect(self._probe_candidate_once)
        self._candidate_input.returnPressed.connect(self._probe_candidate_once)

        self._load_preset_btn.clicked.connect(self._load_selected_preset)
        self._run_preset_btn.clicked.connect(self._run_selected_preset)
        self._clear_results_btn.clicked.connect(self._results_output.clear)
        self._clear_log_btn.clicked.connect(self._log_output.clear)
        self._save_log_btn.clicked.connect(self._save_log)

        self._controller.log_line.connect(self._append_log)
        self._controller.ports_updated.connect(self._on_ports_updated)
        self._controller.connection_changed.connect(self._set_connected_state)
        self._controller.identity_received.connect(self._on_identity_received)
        self._controller.response_received.connect(self._on_response_received)

    def _disconnect_controller_signals(self) -> None:
        for signal, slot in (
            (self._controller.log_line, self._append_log),
            (self._controller.ports_updated, self._on_ports_updated),
            (self._controller.connection_changed, self._set_connected_state),
            (self._controller.identity_received, self._on_identity_received),
            (self._controller.response_received, self._on_response_received),
        ):
            try:
                signal.disconnect(slot)
            except (RuntimeError, TypeError):
                pass

    def _preset_definitions(self) -> list[tuple[str, str]]:
        return [
            ("A", "Preset A: Base Measurement Test"),
            ("B", "Preset B: DC Bias Query Probe"),
            ("C", "Preset C: Error Query Probe"),
            ("D", "Preset D: Bias ON Candidates"),
            ("E", "Preset E: Bias OFF Candidates"),
            ("F", "Preset F: Set DC Bias Voltage Candidates"),
            ("G", "Preset G: Measure With Bias"),
            ("H", "Preset H: Bias Sweep"),
        ]

    def _preset_label(self, key: str) -> str:
        return dict(self._preset_definitions()).get(key, key)

    def _selected_terminator(self) -> str:
        data: Optional[str] = self._terminator_combo.currentData(Qt.ItemDataRole.UserRole)
        if isinstance(data, str):
            return data
        return normalize_terminator(self._terminator_combo.currentText())

    def _query_wait_seconds(self) -> float:
        return max(0.15, float(self._timeout_spin.value()))

    @staticmethod
    def _write_gap_seconds() -> float:
        return 0.06

    def _bias_query_commands(self) -> list[str]:
        return [
            ":BIAS?",
            "BIAS?",
            ":BIAS:STAT?",
            "BIAS:STAT?",
            ":BIAS:VOLT?",
            "BIAS:VOLT?",
            ":DCBIAS?",
            "DCBIAS?",
            ":DCBIAS:STAT?",
            "DCBIAS:STAT?",
            ":DCBIAS:VOLT?",
            "DCBIAS:VOLT?",
        ]

    def _error_query_commands(self) -> list[str]:
        return [
            "SYST:ERR?",
            ":SYST:ERR?",
            "SYSTEM:ERROR?",
            ":SYSTEM:ERROR?",
        ]

    def _bias_on_candidates(self) -> list[str]:
        return [
            ":BIAS:STAT ON",
            "BIAS:STAT ON",
            ":BIAS ON",
            "BIAS ON",
            ":DCBIAS:STAT ON",
            "DCBIAS:STAT ON",
            ":DCBIAS ON",
            "DCBIAS ON",
        ]

    def _bias_off_candidates(self) -> list[str]:
        return [
            ":BIAS:STAT OFF",
            "BIAS:STAT OFF",
            ":BIAS OFF",
            "BIAS OFF",
            ":DCBIAS:STAT OFF",
            "DCBIAS:STAT OFF",
            ":DCBIAS OFF",
            "DCBIAS OFF",
        ]

    def _set_bias_voltage_candidates(self, voltage: float) -> list[str]:
        value = f"{voltage:g}"
        return [
            f":BIAS:VOLT {value}",
            f"BIAS:VOLT {value}",
            f":BIAS:VOLTage {value}",
            f"BIAS:VOLTage {value}",
            f":DCBIAS:VOLT {value}",
            f"DCBIAS:VOLT {value}",
            f":DCBIAS:VOLTage {value}",
            f"DCBIAS:VOLTage {value}",
            f":BIAS {value}",
            f"BIAS {value}",
            f":DCBIAS {value}",
            f"DCBIAS {value}",
        ]

    def _command_step(
        self,
        command: str,
        *,
        expect_response: bool,
        response_optional: bool,
        label: str,
        response_context: str = "",
        pause_seconds: Optional[float] = None,
    ) -> dict[str, object]:
        return {
            "type": "command",
            "command": command,
            "expect_response": expect_response,
            "response_optional": response_optional,
            "label": label,
            "response_context": response_context,
            "pause_seconds": self._query_wait_seconds() if pause_seconds is None and expect_response else (
                self._write_gap_seconds() if pause_seconds is None else pause_seconds
            ),
        }

    @staticmethod
    def _delay_step(seconds: float, label: str) -> dict[str, object]:
        return {"type": "delay", "seconds": seconds, "label": label}

    @staticmethod
    def _note_step(label: str) -> dict[str, object]:
        return {"type": "note", "label": label}

    def _build_steps_for_preset(self, key: str, *, voltage_override: Optional[float] = None) -> list[dict[str, object]]:
        voltage = self._bias_voltage_spin.value() if voltage_override is None else voltage_override
        steps: list[dict[str, object]] = []

        if key == "A":
            steps.extend(
                [
                    self._command_step("*idn?", expect_response=True, response_optional=False, label="Request instrument identity", response_context="*IDN?"),
                    self._command_step("TRIG", expect_response=False, response_optional=True, label="Trigger measurement"),
                    self._delay_step(self._measure_delay_spin.value(), f"Wait {self._measure_delay_spin.value():.2f}s before fetch"),
                    self._command_step("FETC?", expect_response=True, response_optional=False, label="Fetch measurement", response_context="FETC?"),
                ]
            )
        elif key == "B":
            for command in self._bias_query_commands():
                steps.append(
                    self._command_step(
                        command,
                        expect_response=True,
                        response_optional=True,
                        label=f"Experimental query: {command}",
                        response_context=command,
                    )
                )
        elif key == "C":
            for command in self._error_query_commands():
                steps.append(
                    self._command_step(
                        command,
                        expect_response=True,
                        response_optional=True,
                        label=f"Experimental error query: {command}",
                        response_context=command,
                    )
                )
        elif key == "D":
            for command in self._bias_on_candidates():
                steps.append(
                    self._command_step(
                        command,
                        expect_response=False,
                        response_optional=True,
                        label=f"Experimental Bias ON candidate: {command}",
                    )
                )
        elif key == "E":
            for command in self._bias_off_candidates():
                steps.append(
                    self._command_step(
                        command,
                        expect_response=False,
                        response_optional=True,
                        label=f"Experimental Bias OFF candidate: {command}",
                    )
                )
        elif key == "F":
            steps.append(self._note_step(f"Using candidate DC bias voltage {voltage:g} V"))
            for command in self._set_bias_voltage_candidates(voltage):
                steps.append(
                    self._command_step(
                        command,
                        expect_response=False,
                        response_optional=True,
                        label=f"Experimental set-voltage candidate: {command}",
                    )
                )
        elif key == "G":
            steps.append(self._note_step(f"Measure-with-bias sequence using candidate voltage {voltage:g} V"))
            steps.extend(self._build_steps_for_preset("D"))
            steps.extend(self._build_steps_for_preset("F", voltage_override=voltage))
            steps.append(self._delay_step(self._bias_settle_spin.value(), f"Wait {self._bias_settle_spin.value():.2f}s for bias settle"))
            steps.append(self._command_step("TRIG", expect_response=False, response_optional=True, label="Trigger measurement with bias"))
            steps.append(self._delay_step(self._measure_delay_spin.value(), f"Wait {self._measure_delay_spin.value():.2f}s before FETC?"))
            steps.append(
                self._command_step(
                    "FETC?",
                    expect_response=True,
                    response_optional=False,
                    label=f"Fetch measurement after bias candidate {voltage:g} V",
                    response_context=f"Measurement with bias {voltage:g} V",
                )
            )

        return steps

    def _parse_sweep_values(self) -> list[float]:
        raw = self._sweep_values_input.text().strip()
        if not raw:
            raise ValueError("Sweep list is empty")

        values: list[float] = []
        for chunk in raw.split(","):
            item = chunk.strip()
            if not item:
                continue
            values.append(float(item))

        if not values:
            raise ValueError("Sweep list did not contain any valid numeric values")
        return values

    def _preset_summary_text(self, key: str) -> str:
        voltage = self._bias_voltage_spin.value()
        if key == "A":
            lines = ["*IDN?", "TRIG", f"wait {self._measure_delay_spin.value():.2f}s", "FETC?"]
        elif key == "B":
            lines = self._bias_query_commands()
        elif key == "C":
            lines = self._error_query_commands()
        elif key == "D":
            lines = self._bias_on_candidates()
        elif key == "E":
            lines = self._bias_off_candidates()
        elif key == "F":
            lines = self._set_bias_voltage_candidates(voltage)
        elif key == "G":
            lines = [
                "Run Bias ON candidates",
                f"Run Set DC Bias Voltage candidates using {voltage:g} V",
                f"wait {self._bias_settle_spin.value():.2f}s",
                "TRIG",
                f"wait {self._measure_delay_spin.value():.2f}s",
                "FETC?",
            ]
        else:
            try:
                sweep = ", ".join(f"{value:g}" for value in self._parse_sweep_values())
            except ValueError:
                sweep = self._sweep_values_input.text().strip() or "<invalid sweep list>"
            lines = [
                f"Sweep voltages: {sweep}",
                "For each voltage:",
                "  Run Bias ON candidates",
                "  Run Set DC Bias Voltage candidates",
                f"  wait {self._bias_settle_spin.value():.2f}s",
                "  TRIG",
                f"  wait {self._measure_delay_spin.value():.2f}s",
                "  FETC?",
                "Prompt for Bias OFF candidates at the end",
            ]

        return self._preset_label(key) + "\n\n" + "\n".join(lines)

    def _load_selected_preset(self, initial: bool = False) -> None:
        key = str(self._preset_combo.currentData(Qt.ItemDataRole.UserRole))
        self._preset_summary.setPlainText(self._preset_summary_text(key))
        if not initial:
            self._append_probe_result(f"Loaded {self._preset_label(key)}")

    def _run_selected_preset(self) -> None:
        key = str(self._preset_combo.currentData(Qt.ItemDataRole.UserRole))
        self._run_named_preset(key)

    def _run_named_preset(self, key: str) -> None:
        if key == "H":
            self._run_bias_sweep()
            return

        steps = self._build_steps_for_preset(key)
        if not steps:
            QMessageBox.information(self, "Preset Not Available", f"{self._preset_label(key)} has no runnable steps.")
            return

        self._queue_sequence(self._preset_label(key), steps)

    def _queue_sequence(
        self,
        name: str,
        steps: list[dict[str, object]],
        *,
        on_finished: Optional[Callable[[], None]] = None,
    ) -> None:
        if self._sequence_running:
            QMessageBox.information(self, "Sequence Running", "Wait for the current experimental sequence to finish before starting another.")
            return

        self._sequence_running = True
        self._sequence_name = name
        self._sequence_steps = list(steps)
        self._sequence_on_finished = on_finished
        self._pending_response_context = None
        self._set_connected_state(True, self._status_label.text().removeprefix("Status: Connected (").removesuffix(")"))
        self._append_probe_result(f"START {name}")
        self._run_next_sequence_step()

    def _run_next_sequence_step(self) -> None:
        if not self._sequence_steps:
            self._finish_sequence()
            return

        step = self._sequence_steps.pop(0)
        step_type = str(step["type"])

        if step_type == "note":
            self._append_probe_result(str(step["label"]))
            QTimer.singleShot(0, self._run_next_sequence_step)
            return

        if step_type == "delay":
            seconds = float(step["seconds"])
            self._append_probe_result(str(step["label"]))
            QTimer.singleShot(int(seconds * 1000), self._run_next_sequence_step)
            return

        self._send_sequence_command(step)
        pause_seconds = float(step["pause_seconds"])
        QTimer.singleShot(int(pause_seconds * 1000), self._run_next_sequence_step)

    def _send_sequence_command(self, step: dict[str, object]) -> None:
        command = str(step["command"])
        label = str(step["label"])
        expect_response = bool(step["expect_response"])
        response_optional = bool(step["response_optional"])
        response_context = str(step.get("response_context", ""))

        if response_context:
            self._pending_response_context = response_context

        self._append_probe_result(label)
        self._controller.send_command(
            CommandRequest(
                command=command,
                terminator=self._selected_terminator(),
                expect_response=expect_response,
                response_optional=response_optional,
            )
        )

    def _finish_sequence(self) -> None:
        name = self._sequence_name
        callback = self._sequence_on_finished
        self._sequence_running = False
        self._sequence_name = ""
        self._sequence_on_finished = None
        self._pending_response_context = None
        self._set_connected_state(self._disconnect_btn.isEnabled(), self._status_label.text().removeprefix("Status: Connected (").removesuffix(")") if self._disconnect_btn.isEnabled() else "")
        self._append_probe_result(f"COMPLETE {name}")
        if callback is not None:
            callback()

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
        self._append_probe_result("Direct action: *IDN?")
        self._controller.send_idn(self._selected_terminator())

    def _fetch_once(self) -> None:
        self._append_probe_result("Direct action: FETC?")
        self._pending_response_context = "FETC?"
        self._controller.send_command(
            CommandRequest(
                command="FETC?",
                terminator=self._selected_terminator(),
                expect_response=True,
                response_optional=False,
            )
        )

    def _probe_candidate_once(self) -> None:
        candidate = self._candidate_input.text().strip()
        if not candidate:
            QMessageBox.information(self, "Missing Candidate", "Enter a candidate command first.")
            return

        self._append_probe_result(f"Experimental manual candidate: {candidate}")
        self._pending_response_context = candidate
        self._controller.send_command(
            CommandRequest(
                command=candidate,
                terminator=self._selected_terminator(),
                expect_response=True,
                response_optional=True,
            )
        )

    def _run_bias_sweep(self) -> None:
        try:
            sweep_values = self._parse_sweep_values()
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid Sweep List", str(exc))
            return

        steps: list[dict[str, object]] = []
        for voltage in sweep_values:
            steps.append(self._note_step(f"Sweep voltage {voltage:g} V"))
            steps.extend(self._build_steps_for_preset("D"))
            steps.extend(self._build_steps_for_preset("F", voltage_override=voltage))
            steps.append(self._delay_step(self._bias_settle_spin.value(), f"Wait {self._bias_settle_spin.value():.2f}s for bias settle at {voltage:g} V"))
            steps.append(self._command_step("TRIG", expect_response=False, response_optional=True, label=f"Trigger measurement at {voltage:g} V"))
            steps.append(self._delay_step(self._measure_delay_spin.value(), f"Wait {self._measure_delay_spin.value():.2f}s before FETC? at {voltage:g} V"))
            steps.append(
                self._command_step(
                    "FETC?",
                    expect_response=True,
                    response_optional=False,
                    label=f"Fetch measurement for {voltage:g} V",
                    response_context=f"Sweep {voltage:g} V",
                )
            )

        self._queue_sequence("Preset H: Bias Sweep", steps, on_finished=self._offer_bias_off_candidates)

    def _offer_bias_off_candidates(self) -> None:
        answer = QMessageBox.question(
            self,
            "Run Bias OFF Candidates",
            "Bias sweep finished. Run Preset E (Bias OFF Candidates) now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._run_named_preset("E")

    def _save_log(self) -> None:
        default_path = str(Path.cwd() / "dc_bias_probe_log.txt")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Probe Log",
            default_path,
            "Text Files (*.txt);;All Files (*)",
        )
        if not file_path:
            return

        content = (
            "SynAptIp DC Bias Probe Log\n"
            "==========================\n\n"
            "Experimental Results\n"
            "--------------------\n"
            f"{self._results_output.toPlainText()}\n\n"
            "Session Log\n"
            "-----------\n"
            f"{self._log_output.toPlainText()}\n"
        )

        try:
            Path(file_path).write_text(content, encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, "Save Failed", f"Could not save the log file:\n{exc}")
            return

        self._append_probe_result(f"Saved combined probe log to {file_path}")

    def _append_log(self, line: str) -> None:
        self._log_output.append(line)

    def _append_probe_result(self, text: str) -> None:
        self._results_output.append(format_log_line(text))

    def _on_identity_received(self, identity: str) -> None:
        self._identity_value_lbl.setText(identity if identity else "<empty identity response>")

    def _on_response_received(self, response: str) -> None:
        if self._pending_response_context:
            self._append_probe_result(f"{self._pending_response_context} -> {response}")
            self._pending_response_context = None
        else:
            self._append_probe_result(f"Response -> {response}")

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

        self._refresh_btn.setEnabled(not connected)
        self._port_combo.setEnabled(not connected)
        self._baud_combo.setEnabled(not connected)
        self._timeout_spin.setEnabled(not connected)
        self._terminator_combo.setEnabled(not connected)

        self._preset_combo.setEnabled(not self._sequence_running)
        self._load_preset_btn.setEnabled(not self._sequence_running)

        run_enabled = connected and not self._sequence_running
        for button in (
            self._idn_btn,
            self._fetch_once_btn,
            self._probe_queries_btn,
            self._bias_on_btn,
            self._bias_off_btn,
            self._set_bias_voltage_btn,
            self._measure_with_bias_btn,
            self._run_sweep_btn,
            self._error_query_btn,
            self._send_candidate_btn,
            self._run_preset_btn,
        ):
            button.setEnabled(run_enabled)

        if connected:
            self._status_label.setText(f"Status: Connected ({port})")
            self._status_label.setStyleSheet("color: #166534; font-weight: 700;")
        else:
            self._status_label.setText("Status: Disconnected")
            self._status_label.setStyleSheet("color: #991b1b; font-weight: 700;")

    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            if hasattr(self, "_controller") and self._controller is not None:
                self._disconnect_controller_signals()
                self._controller.shutdown()
        finally:
            super().closeEvent(event)
