"""
main_window_v3.py — SynAptIp LCR Control V3 Main Window
SynAptIp Technologies

V3 extends V2.3 with a dedicated Nyquist Analysis tab that provides
post-processing, multi-file comparison, and CSV/JPG export.

All instrument control logic (connection, sweep, measure-once, live results,
diagnostics) is inherited unchanged from V2.3 via the same service layer.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
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
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.csv_exporter import (
    CsvExporter,
    ExportMetadata,
    LIVE_RESULTS_FIELDNAMES,
    build_nyquist_xy,
    detect_v2_file_type,
    load_nyquist_preview_points,
    nyquist_components,
)
from services.scan_runner import ConnectionSettings, ScanRunner, SweepSettings
from services.unit_conversion import frequency_to_hz
from ui.nyquist_analysis_panel import NyquistAnalysisPanel

try:
    from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
    QT_CHARTS_AVAILABLE = True
except Exception:
    QChart = object  # type: ignore[assignment]
    QChartView = object  # type: ignore[assignment]
    QLineSeries = object  # type: ignore[assignment]
    QValueAxis = object  # type: ignore[assignment]
    QT_CHARTS_AVAILABLE = False


class MainWindowV3(QMainWindow):
    """
    SynAptIp LCR Control V3 main window.

    Adds a Nyquist Analysis tab on top of the complete V2.3 control UI.
    V2.3 instrument control code is reproduced here without modification.
    """

    def __init__(self) -> None:
        super().__init__()
        self._runner = ScanRunner()
        self.current_run_rows: list[dict] = []
        self._manual_bias_enabled = False
        self._run_active = False
        self._nyquist_slot_inputs: list[QLineEdit] = []
        self._nyquist_status_output: QTextEdit
        self._nyquist_chart = None
        self._nyquist_chart_view = None

        self.setWindowTitle("SynAptIp LCR Control V3")
        self.setWindowIcon(QIcon(str(self._asset_path("assets/icons/SynAptIp_LCR_Control.ico"))))
        self.setMinimumSize(1260, 860)
        self.resize(1340, 940)

        self._build_ui()
        self._wire_events()
        self._refresh_ports()
        self._log_measurement_assumptions()

    @staticmethod
    def _asset_path(relative_path: str) -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / relative_path
        return Path(__file__).resolve().parents[2] / relative_path

    # ------------------------------------------------------------------ #
    #  UI top-level build                                                  #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(14)

        root.addWidget(self._build_header())

        tabs = QTabWidget()
        tabs.addTab(self._build_control_scan_tab(), "Control & Scan")
        tabs.addTab(self._build_live_results_tab(), "Live Results")
        tabs.addTab(self._build_sample_output_tab(), "Sample & Output")
        tabs.addTab(self._build_nyquist_compare_tab(), "Nyquist Compare")
        tabs.addTab(self._build_nyquist_analysis_tab(), "Nyquist Analysis (V3)")
        tabs.addTab(self._build_diagnostics_tab(), "Diagnostics & Commands")
        tabs.setDocumentMode(True)
        tabs.setCurrentIndex(0)

        root.addWidget(tabs, stretch=1)
        self.setCentralWidget(central)
        self.setStyleSheet(self._stylesheet())

    def _build_header(self) -> QWidget:
        header_card = QWidget()
        header_card.setObjectName("headerCard")

        header = QHBoxLayout(header_card)
        header.setContentsMargins(20, 18, 20, 18)
        header.setSpacing(18)

        # ---- Logo area ----
        logo_area = QWidget()
        logo_layout = QHBoxLayout(logo_area)
        logo_layout.setContentsMargins(16, 12, 16, 12)
        logo_layout.setSpacing(12)

        logo_label = QLabel()
        logo_path = self._asset_path("assets/icons/SynAptIp_LCR_Control.ico")
        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            logo_label.setPixmap(
                pixmap.scaled(78, 78, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
        logo_label.setFixedSize(80, 80)

        brand_pill = QLabel("SynAptIp")
        brand_pill.setObjectName("brandPill")
        brand_pill.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(brand_pill)
        logo_area.setStyleSheet(
            "background: rgba(255,255,255,0.08);"
            "border: 1px solid rgba(255,255,255,0.20);"
            "border-radius: 12px;"
        )

        # ---- Title block ----
        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        title = QLabel("SynAptIp LCR Control V3")
        title.setObjectName("headerTitle")
        title.setFont(QFont("Segoe UI", 19, QFont.Weight.DemiBold))

        company = QLabel("SynAptIp Technologies")
        company.setObjectName("headerCompany")

        subtitle = QLabel("Scientific Software, Instrument Control & Nyquist Analysis")
        subtitle.setObjectName("headerSubtitle")

        powered = QLabel("Powered by SynAptIp Technologies")
        powered.setObjectName("headerPowered")

        title_box.addWidget(title)
        title_box.addWidget(company)
        title_box.addWidget(subtitle)
        title_box.addWidget(powered)

        # ---- Version badge ----
        badge = QLabel("Version 3.0")
        badge.setObjectName("versionBadge")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(30)

        header.addWidget(logo_area, stretch=0)
        header.addLayout(title_box, stretch=1)
        header.addWidget(badge, stretch=0, alignment=Qt.AlignmentFlag.AlignTop)
        return header_card

    # ------------------------------------------------------------------ #
    #  Tabs                                                                #
    # ------------------------------------------------------------------ #

    def _build_control_scan_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(6, 8, 6, 6)
        layout.setSpacing(10)

        body = QHBoxLayout()
        body.setSpacing(12)
        body.addLayout(self._build_left_column(), stretch=10)
        body.addLayout(self._build_right_column(), stretch=12)

        layout.addLayout(body, stretch=7)
        layout.addWidget(self._build_log_panel(), stretch=3)
        return tab

    def _build_live_results_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 10, 8, 8)
        layout.setSpacing(10)

        status_group = QGroupBox("Live Result Status")
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(4)

        self._results_summary_lbl = QLabel("Rows: 0")
        self._results_summary_lbl.setStyleSheet("font-weight: 600; color: #1f2937;")
        self._results_last_status_lbl = QLabel("Last point: —")
        self._results_last_status_lbl.setStyleSheet("color: #4b5563;")
        self._export_live_results_btn = QPushButton("Export current live results now")

        status_layout.addWidget(self._results_summary_lbl)
        status_layout.addWidget(self._results_last_status_lbl)
        status_layout.addWidget(self._export_live_results_btn)
        layout.addWidget(status_group, stretch=0)
        layout.addWidget(self._build_live_results_group(), stretch=1)
        return tab

    def _build_sample_output_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 10, 8, 8)
        layout.setSpacing(10)

        layout.addWidget(self._build_sample_metadata_group(), stretch=0)
        layout.addWidget(self._build_output_config_group(), stretch=0)
        layout.addStretch(1)
        return tab

    def _build_nyquist_compare_tab(self) -> QWidget:
        """V2.3-compatible Nyquist Compare preview tab (unchanged from V2.3)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 10, 8, 8)
        layout.setSpacing(12)

        layout.addWidget(self._build_nyquist_file_slots_group())
        layout.addWidget(self._build_nyquist_visualization_group(), stretch=1)
        return tab

    def _build_nyquist_analysis_tab(self) -> QWidget:
        """V3 new tab: full Nyquist post-processing and export panel."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)

        self._nyquist_panel = NyquistAnalysisPanel()
        # Wire the output folder to stay in sync with the Sample & Output config
        self._nyquist_panel.set_output_dir(Path.cwd() / "exports_v3")
        layout.addWidget(self._nyquist_panel)
        return tab

    def _build_diagnostics_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 10, 8, 8)
        layout.setSpacing(10)
        layout.addWidget(self._build_diag_quick_commands_group(), stretch=0)
        layout.addWidget(self._build_diag_manual_group(), stretch=0)
        layout.addWidget(self._build_diag_output_group(), stretch=1)
        return tab

    # ------------------------------------------------------------------ #
    #  Column / group builders (identical to V2.3)                        #
    # ------------------------------------------------------------------ #

    def _build_left_column(self) -> QVBoxLayout:
        left = QVBoxLayout()
        left.setSpacing(10)
        left.addWidget(self._build_connection_group())
        left.addWidget(self._build_manual_control_group())
        left.addWidget(self._build_sweep_group())
        left.addStretch(1)
        return left

    def _build_right_column(self) -> QVBoxLayout:
        right = QVBoxLayout()
        right.setSpacing(10)
        right.addWidget(self._build_assumptions_group())
        right.addWidget(self._build_run_group())
        right.addStretch(1)
        return right

    def _build_connection_group(self) -> QGroupBox:
        group = QGroupBox("Connection")
        gl = QGridLayout(group)

        self._port_combo = QComboBox()
        self._port_combo.setEditable(True)
        self._port_combo.setPlaceholderText("Select COM port")
        self._refresh_ports_btn = QPushButton("Refresh Ports")

        self._baud_combo = QComboBox()
        self._baud_combo.setEditable(True)
        self._baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self._baud_combo.setCurrentText("115200")

        self._timeout_spin = QDoubleSpinBox()
        self._timeout_spin.setRange(0.1, 10.0)
        self._timeout_spin.setValue(1.0)
        self._timeout_spin.setSingleStep(0.1)
        self._timeout_spin.setSuffix(" s")

        self._terminator_combo = QComboBox()
        self._terminator_combo.addItems([r"\n", r"\r\n", r"\r"])

        self._connect_btn = QPushButton("Connect")
        self._disconnect_btn = QPushButton("Disconnect")
        self._conn_state_lbl = QLabel("Status: Disconnected")
        self._conn_state_lbl.setStyleSheet("color: #991b1b; font-weight: 600;")

        gl.addWidget(QLabel("COM Port"), 0, 0)
        gl.addWidget(self._port_combo, 0, 1)
        gl.addWidget(self._refresh_ports_btn, 0, 2)
        gl.addWidget(QLabel("Baud"), 1, 0)
        gl.addWidget(self._baud_combo, 1, 1)
        gl.addWidget(QLabel("Timeout"), 1, 2)
        gl.addWidget(self._timeout_spin, 1, 3)
        gl.addWidget(QLabel("Terminator"), 2, 0)
        gl.addWidget(self._terminator_combo, 2, 1)
        gl.addWidget(self._connect_btn, 2, 2)
        gl.addWidget(self._disconnect_btn, 2, 3)
        gl.addWidget(self._conn_state_lbl, 3, 0, 1, 4)
        return group

    def _build_manual_control_group(self) -> QGroupBox:
        group = QGroupBox("Manual Instrument Control")
        gl = QGridLayout(group)

        self._freq_value_spin = QDoubleSpinBox()
        self._freq_value_spin.setRange(0.001, 1_000_000.0)
        self._freq_value_spin.setValue(1.0)
        self._freq_value_spin.setDecimals(6)

        self._freq_unit_combo = QComboBox()
        self._freq_unit_combo.addItems(["Hz", "kHz", "MHz"])
        self._apply_freq_btn = QPushButton("Apply Frequency")

        self._ac_voltage_spin = QDoubleSpinBox()
        self._ac_voltage_spin.setRange(0.001, 5.0)
        self._ac_voltage_spin.setValue(0.5)
        self._ac_voltage_spin.setDecimals(3)
        self._apply_ac_btn = QPushButton("Apply AC VOLT")

        self._dc_bias_spin = QDoubleSpinBox()
        self._dc_bias_spin.setRange(0.0, 40.0)
        self._dc_bias_spin.setValue(0.0)
        self._dc_bias_spin.setDecimals(3)
        self._apply_bias_value_btn = QPushButton("Apply :BIAS:VOLTage")

        self._bias_on_btn = QPushButton("DC Bias ON")
        self._bias_off_btn = QPushButton("DC Bias OFF")
        self._query_bias_btn = QPushButton("Optional Bias Verify")

        gl.addWidget(QLabel("Frequency"), 0, 0)
        gl.addWidget(self._freq_value_spin, 0, 1)
        gl.addWidget(self._freq_unit_combo, 0, 2)
        gl.addWidget(self._apply_freq_btn, 0, 3)
        gl.addWidget(QLabel("AC Voltage (V)"), 1, 0)
        gl.addWidget(self._ac_voltage_spin, 1, 1)
        gl.addWidget(self._apply_ac_btn, 1, 3)
        gl.addWidget(QLabel("DC Bias Voltage (V)"), 2, 0)
        gl.addWidget(self._dc_bias_spin, 2, 1)
        gl.addWidget(self._apply_bias_value_btn, 2, 3)
        gl.addWidget(self._bias_on_btn, 3, 1)
        gl.addWidget(self._bias_off_btn, 3, 2)
        gl.addWidget(self._query_bias_btn, 3, 3)
        return group

    def _build_sweep_group(self) -> QGroupBox:
        group = QGroupBox("Sweep Controls")
        gl = QGridLayout(group)

        self._sweep_start_spin = QDoubleSpinBox()
        self._sweep_start_spin.setRange(0.001, 1_000_000.0)
        self._sweep_start_spin.setValue(1.0)
        self._sweep_start_spin.setDecimals(6)
        self._sweep_start_unit_combo = QComboBox()
        self._sweep_start_unit_combo.addItems(["Hz", "kHz", "MHz"])

        self._sweep_stop_spin = QDoubleSpinBox()
        self._sweep_stop_spin.setRange(0.001, 1_000_000.0)
        self._sweep_stop_spin.setValue(100.0)
        self._sweep_stop_spin.setDecimals(6)
        self._sweep_stop_unit_combo = QComboBox()
        self._sweep_stop_unit_combo.addItems(["Hz", "kHz", "MHz"])

        self._sweep_step_spin = QDoubleSpinBox()
        self._sweep_step_spin.setRange(0.001, 1_000_000.0)
        self._sweep_step_spin.setValue(1.0)
        self._sweep_step_spin.setDecimals(6)
        self._sweep_step_unit_combo = QComboBox()
        self._sweep_step_unit_combo.addItems(["Hz", "kHz", "MHz"])

        self._point_delay_spin = QDoubleSpinBox()
        self._point_delay_spin.setRange(0.0, 10.0)
        self._point_delay_spin.setValue(0.10)
        self._point_delay_spin.setDecimals(3)
        self._point_delay_spin.setSuffix(" s")

        self._measure_delay_spin = QDoubleSpinBox()
        self._measure_delay_spin.setRange(0.0, 10.0)
        self._measure_delay_spin.setValue(0.35)
        self._measure_delay_spin.setDecimals(3)
        self._measure_delay_spin.setSuffix(" s")

        self._bias_delay_spin = QDoubleSpinBox()
        self._bias_delay_spin.setRange(0.0, 10.0)
        self._bias_delay_spin.setValue(0.30)
        self._bias_delay_spin.setDecimals(3)
        self._bias_delay_spin.setSuffix(" s")

        gl.addWidget(QLabel("Start"), 0, 0)
        gl.addWidget(self._sweep_start_spin, 0, 1)
        gl.addWidget(self._sweep_start_unit_combo, 0, 2)
        gl.addWidget(QLabel("Stop"), 1, 0)
        gl.addWidget(self._sweep_stop_spin, 1, 1)
        gl.addWidget(self._sweep_stop_unit_combo, 1, 2)
        gl.addWidget(QLabel("Step"), 2, 0)
        gl.addWidget(self._sweep_step_spin, 2, 1)
        gl.addWidget(self._sweep_step_unit_combo, 2, 2)
        gl.addWidget(QLabel("Point settle"), 3, 0)
        gl.addWidget(self._point_delay_spin, 3, 1)
        gl.addWidget(QLabel("Measure delay"), 3, 2)
        gl.addWidget(self._measure_delay_spin, 3, 3)
        gl.addWidget(QLabel("Bias settle"), 4, 0)
        gl.addWidget(self._bias_delay_spin, 4, 1)
        return group

    def _build_sample_metadata_group(self) -> QGroupBox:
        group = QGroupBox("Sample Metadata")
        gl = QGridLayout(group)
        self._sample_name_input = QLineEdit("sample_001")
        self._operator_input = QLineEdit("operator")
        self._notes_input = QLineEdit()
        gl.addWidget(QLabel("Sample Name / ID"), 0, 0)
        gl.addWidget(self._sample_name_input, 0, 1, 1, 3)
        gl.addWidget(QLabel("Operator"), 1, 0)
        gl.addWidget(self._operator_input, 1, 1)
        gl.addWidget(QLabel("Notes"), 1, 2)
        gl.addWidget(self._notes_input, 1, 3)
        return group

    def _build_output_config_group(self) -> QGroupBox:
        group = QGroupBox("Output Configuration")
        gl = QGridLayout(group)
        self._output_folder_input = QLineEdit(str(Path.cwd() / "exports_v3"))
        self._browse_output_btn = QPushButton("Browse")
        gl.addWidget(QLabel("Output Folder"), 0, 0)
        gl.addWidget(self._output_folder_input, 0, 1, 1, 2)
        gl.addWidget(self._browse_output_btn, 0, 3)
        return group

    def _build_run_group(self) -> QGroupBox:
        group = QGroupBox("Run")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(8)

        self._run_mode_combo = QComboBox()
        self._run_mode_combo.addItems([
            "Frequency Sweep Only",
            "DC Bias List + Frequency Sweep",
        ])

        self._dc_bias_list_input = QLineEdit("-1,-0.5,0,0.5,1")
        self._dc_bias_list_input.setPlaceholderText("Comma-separated values, e.g. -1,-0.5,0,0.5,1")

        help_text = QLabel(
            "Run plan: one full frequency sweep is executed for each DC bias value in listed order."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #6b7280;")

        self._preview_run_plan_btn = QPushButton("Preview Run Plan")
        self._measure_once_btn = QPushButton("Measure Once")
        self._run_btn = QPushButton("Run")
        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setStyleSheet("background: #fee2e2;")

        layout.addWidget(QLabel("Run Mode"), 0, 0)
        layout.addWidget(self._run_mode_combo, 0, 1, 1, 3)
        layout.addWidget(QLabel("DC Bias List (V)"), 1, 0)
        layout.addWidget(self._dc_bias_list_input, 1, 1, 1, 3)
        layout.addWidget(help_text, 2, 0, 1, 4)
        layout.addWidget(self._preview_run_plan_btn, 3, 0)
        layout.addWidget(self._measure_once_btn, 3, 1)
        layout.addWidget(self._run_btn, 3, 2)
        layout.addWidget(self._stop_btn, 3, 3)
        return group

    def _build_assumptions_group(self) -> QGroupBox:
        group = QGroupBox("Instrument Setup Assumptions")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)
        for line in [
            "Main display: Z ohm",
            "Secondary display: theta / TD DEG",
            "Range mode: front-panel setting",
            "Speed mode: front-panel setting",
        ]:
            lbl = QLabel(line)
            lbl.setStyleSheet("color: #111827;")
            layout.addWidget(lbl)

        note = QLabel(
            "Current V3 acquisition assumes the instrument front panel is configured "
            "to Z / TD (or theta) mode before running measurements."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #6b7280;")
        self._assumptions_confirm_chk = QCheckBox(
            "I confirm the instrument is set to Z / TD on the front panel"
        )
        self._assumptions_confirm_chk.setChecked(False)
        layout.addWidget(note)
        layout.addWidget(self._assumptions_confirm_chk)
        return group

    def _build_live_results_group(self) -> QGroupBox:
        group = QGroupBox("Live Results Table")
        layout = QVBoxLayout(group)
        self._results_table = QTableWidget(0, 10)
        self._results_table.setHorizontalHeaderLabels([
            "timestamp", "sample_id", "freq_hz", "ac_voltage_v",
            "dc_bias_on", "dc_bias_v", "z_ohm", "theta_deg", "status", "raw_response",
        ])
        self._results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._results_table)
        return group

    def _build_log_panel(self) -> QGroupBox:
        group = QGroupBox("Live Log")
        vbox = QVBoxLayout(group)
        self._log_output = QTextEdit()
        self._log_output.setObjectName("sessionLog")
        self._log_output.setReadOnly(True)
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self._log_output.clear)
        vbox.addWidget(self._log_output)
        vbox.addWidget(clear_btn)
        return group

    def _build_nyquist_file_slots_group(self) -> QGroupBox:
        group = QGroupBox("Nyquist Compare Inputs")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self._nyquist_slot_inputs.clear()
        for index in range(3):
            label = QLabel(f"Slot {index + 1}")
            path_input = QLineEdit()
            path_input.setPlaceholderText("Select V2/V3 CSV file")
            browse_btn = QPushButton("Browse")
            clear_btn = QPushButton("Clear")

            browse_btn.clicked.connect(lambda _checked=False, i=index: self._browse_nyquist_slot_file(i))
            clear_btn.clicked.connect(lambda _checked=False, i=index: self._clear_nyquist_slot_file(i))

            self._nyquist_slot_inputs.append(path_input)

            row = index
            grid.addWidget(label, row, 0)
            grid.addWidget(path_input, row, 1)
            grid.addWidget(browse_btn, row, 2)
            grid.addWidget(clear_btn, row, 3)

        self._refresh_nyquist_btn = QPushButton("Refresh Nyquist")
        self._clear_nyquist_status_btn = QPushButton("Clear Status")
        grid.addWidget(self._refresh_nyquist_btn, 3, 2)
        grid.addWidget(self._clear_nyquist_status_btn, 3, 3)
        return group

    def _build_nyquist_visualization_group(self) -> QGroupBox:
        group = QGroupBox("Nyquist Visualization")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        if QT_CHARTS_AVAILABLE:
            self._nyquist_chart = QChart()
            self._nyquist_chart.setTitle("Nyquist Visualization Compare (Up to 3 Files)")
            self._nyquist_chart.legend().setVisible(True)
            self._nyquist_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
            self._nyquist_chart_view = QChartView(self._nyquist_chart)
            self._nyquist_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            layout.addWidget(self._nyquist_chart_view, stretch=1)
        else:
            fallback = QLabel("Nyquist visualization requires PySide6 QtCharts support.")
            fallback.setStyleSheet("color: #7f1d1d; font-weight: 600;")
            layout.addWidget(fallback)

        self._nyquist_status_output = QTextEdit()
        self._nyquist_status_output.setObjectName("nyquistStatus")
        self._nyquist_status_output.setReadOnly(True)
        self._nyquist_status_output.setPlaceholderText("Parsing details appear here.")
        layout.addWidget(self._nyquist_status_output, stretch=0)
        return group

    def _build_diag_quick_commands_group(self) -> QGroupBox:
        group = QGroupBox("Quick Commands")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        self._diag_idn_btn = QPushButton("*IDN?")
        self._diag_trig_btn = QPushButton("TRIG")
        self._diag_fetc_btn = QPushButton("FETC?")
        self._diag_read_btn = QPushButton("READ?")
        self._diag_bias_btn = QPushButton(":BIAS?")
        self._diag_bias_stat_btn = QPushButton(":BIAS:STAT?")
        self._diag_bias_volt_btn = QPushButton(":BIAS:VOLT?")

        grid.addWidget(self._diag_idn_btn, 0, 0)
        grid.addWidget(self._diag_trig_btn, 0, 1)
        grid.addWidget(self._diag_fetc_btn, 0, 2)
        grid.addWidget(self._diag_read_btn, 0, 3)
        grid.addWidget(self._diag_bias_btn, 1, 0)
        grid.addWidget(self._diag_bias_stat_btn, 1, 1)
        grid.addWidget(self._diag_bias_volt_btn, 1, 2)
        return group

    def _build_diag_manual_group(self) -> QGroupBox:
        group = QGroupBox("Manual Command")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        self._diag_manual_input = QLineEdit()
        self._diag_manual_input.setPlaceholderText("Type command, e.g. *IDN? or FREQ 1000")
        self._diag_send_btn = QPushButton("Send")
        self._diag_send_read_btn = QPushButton("Send and Read")
        self._diag_clear_input_btn = QPushButton("Clear")

        grid.addWidget(QLabel("Command"), 0, 0)
        grid.addWidget(self._diag_manual_input, 0, 1, 1, 3)
        grid.addWidget(self._diag_send_btn, 1, 1)
        grid.addWidget(self._diag_send_read_btn, 1, 2)
        grid.addWidget(self._diag_clear_input_btn, 1, 3)
        return group

    def _build_diag_output_group(self) -> QGroupBox:
        group = QGroupBox("Diagnostics Output")
        layout = QVBoxLayout(group)
        self._diag_output = QTextEdit()
        self._diag_output.setObjectName("diagOutput")
        self._diag_output.setReadOnly(True)
        self._diag_output.setPlaceholderText("Diagnostics command traffic and responses appear here.")
        clear_btn = QPushButton("Clear Diagnostics Output")
        clear_btn.clicked.connect(self._diag_output.clear)
        layout.addWidget(self._diag_output)
        layout.addWidget(clear_btn)
        return group

    # ------------------------------------------------------------------ #
    #  Stylesheet                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _stylesheet() -> str:
        return """
            QMainWindow { background-color: #f5f7fb; }
            QWidget#headerCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #0f172a,
                    stop: 0.55 #1e293b,
                    stop: 1 #27354d
                );
                border: 1px solid #334155;
                border-radius: 14px;
            }
            QLabel#headerTitle {
                color: #f8fafc;
                font-size: 22px;
                font-weight: 700;
            }
            QLabel#headerCompany {
                color: #38bdf8;
                font-size: 13px;
                font-weight: 700;
            }
            QLabel#headerSubtitle {
                color: #cbd5e1;
                font-size: 12px;
            }
            QLabel#headerPowered {
                color: #64748b;
                font-size: 10px;
            }
            QLabel#brandPill {
                background: rgba(255, 255, 255, 0.10);
                color: #e2e8f0;
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 11px;
                padding: 4px 10px;
                font-weight: 600;
            }
            QLabel#versionBadge {
                background: #dbeafe;
                color: #1e3a8a;
                border: 1px solid #93c5fd;
                border-radius: 12px;
                padding: 5px 14px;
                font-weight: 700;
            }
            QTabWidget::pane {
                border: 1px solid #dbe2ec;
                border-radius: 8px;
                top: -1px;
                background: #ffffff;
            }
            QTabBar::tab {
                padding: 9px 16px;
                margin-right: 4px;
            }
            QTabBar::tab:selected { font-weight: 600; }
            QGroupBox {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-top: 8px;
                font-weight: 600;
                background: #ffffff;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QPushButton { min-height: 30px; padding: 4px 10px; }
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox { min-height: 28px; }
            QTextEdit#sessionLog {
                background-color: #0b1220;
                color: #d7e3ff;
                border-radius: 6px;
                font-family: Consolas;
                font-size: 10.5pt;
            }
            QTextEdit#nyquistStatus {
                background-color: #f8fafc;
                color: #1f2937;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-family: Consolas;
                font-size: 10pt;
            }
            QTextEdit#diagOutput {
                background-color: #0b1220;
                color: #d7e3ff;
                border-radius: 6px;
                font-family: Consolas;
                font-size: 10pt;
            }
        """

    # ------------------------------------------------------------------ #
    #  Event wiring                                                        #
    # ------------------------------------------------------------------ #

    def _wire_events(self) -> None:
        self._refresh_ports_btn.clicked.connect(self._refresh_ports)
        self._connect_btn.clicked.connect(self._connect)
        self._disconnect_btn.clicked.connect(self._runner.disconnect)
        self._browse_output_btn.clicked.connect(self._browse_output_folder)

        self._apply_freq_btn.clicked.connect(self._apply_frequency)
        self._apply_ac_btn.clicked.connect(self._apply_ac_voltage)
        self._apply_bias_value_btn.clicked.connect(self._apply_bias_value)
        self._bias_on_btn.clicked.connect(lambda: self._set_bias_state(True))
        self._bias_off_btn.clicked.connect(lambda: self._set_bias_state(False))
        self._query_bias_btn.clicked.connect(self._query_optional_bias)

        self._preview_run_plan_btn.clicked.connect(self._preview_run_plan)
        self._measure_once_btn.clicked.connect(self._measure_once)
        self._run_btn.clicked.connect(self._run_selected_mode)
        self._stop_btn.clicked.connect(self._runner.stop)

        self._refresh_nyquist_btn.clicked.connect(self._refresh_nyquist_compare)
        self._clear_nyquist_status_btn.clicked.connect(self._nyquist_status_output.clear)
        self._assumptions_confirm_chk.toggled.connect(self._on_assumption_confirmation_changed)
        self._export_live_results_btn.clicked.connect(self._export_live_results_now)

        self._diag_idn_btn.clicked.connect(lambda: self._run_diag_command("*IDN?", expect_response=True))
        self._diag_trig_btn.clicked.connect(lambda: self._run_diag_command("TRIG", expect_response=False))
        self._diag_fetc_btn.clicked.connect(lambda: self._run_diag_command("FETC?", expect_response=True))
        self._diag_read_btn.clicked.connect(lambda: self._run_diag_command("READ?", expect_response=True))
        self._diag_bias_btn.clicked.connect(lambda: self._run_diag_command(":BIAS?", expect_response=True))
        self._diag_bias_stat_btn.clicked.connect(lambda: self._run_diag_command(":BIAS:STAT?", expect_response=True))
        self._diag_bias_volt_btn.clicked.connect(lambda: self._run_diag_command(":BIAS:VOLT?", expect_response=True))

        self._diag_send_btn.clicked.connect(lambda: self._run_diag_manual(expect_response=False))
        self._diag_send_read_btn.clicked.connect(lambda: self._run_diag_manual(expect_response=True))
        self._diag_clear_input_btn.clicked.connect(self._diag_manual_input.clear)

        self._runner.log.connect(self._append_log)
        self._runner.measurement.connect(self._on_measurement)
        self._runner.sweep_finished.connect(self._on_sweep_finished)
        self._runner.connected.connect(self._on_connection_changed)

        # Keep Nyquist panel output folder in sync
        self._output_folder_input.textChanged.connect(
            lambda t: self._nyquist_panel.set_output_dir(t) if t else None
        )

    # ------------------------------------------------------------------ #
    #  Action handlers (identical logic to V2.3)                          #
    # ------------------------------------------------------------------ #

    def _append_log(self, line: str) -> None:
        self._log_output.append(line)

    def _append_diag(self, line: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self._diag_output.append(f"[{stamp}] {line}")

    def _log_measurement_assumptions(self) -> None:
        self._append_log("[assumptions] Main display: Z ohm")
        self._append_log("[assumptions] Secondary display: theta / TD DEG")
        self._append_log("[assumptions] Range mode: front-panel setting")
        self._append_log("[assumptions] Speed mode: front-panel setting")
        self._append_log(
            "[assumptions] Front panel should be configured to Z / TD (or theta) before measurement runs."
        )

    def _on_assumption_confirmation_changed(self, checked: bool) -> None:
        if checked:
            self._append_log("[assumptions] Operator confirmed Z / TD front-panel setup.")
        else:
            self._append_log("[assumptions] Operator confirmation unchecked.")

    def _refresh_ports(self) -> None:
        self._port_combo.clear()
        self._port_combo.addItems(self._runner.list_ports())

    def _extract_port(self) -> str:
        text = self._port_combo.currentText().strip()
        if " - " in text:
            return text.split(" - ", 1)[0].strip()
        return text

    def _terminator_value(self) -> str:
        selected = self._terminator_combo.currentText()
        if selected == r"\r\n":
            return "\r\n"
        if selected == r"\r":
            return "\r"
        return "\n"

    def _connection_settings(self) -> ConnectionSettings:
        return ConnectionSettings(
            com_port=self._extract_port(),
            baudrate=int(self._baud_combo.currentText().strip()),
            timeout_s=float(self._timeout_spin.value()),
            terminator=self._terminator_value(),
        )

    def _connect(self) -> None:
        port = self._extract_port()
        if not port:
            QMessageBox.warning(self, "Missing COM Port", "Select or enter a COM port first.")
            return
        self._runner.connect(self._connection_settings())

    def _on_connection_changed(self, connected: bool, port: str) -> None:
        if connected:
            self._conn_state_lbl.setText(f"Status: Connected ({port})")
            self._conn_state_lbl.setStyleSheet("color: #065f46; font-weight: 600;")
        else:
            self._conn_state_lbl.setText("Status: Disconnected")
            self._conn_state_lbl.setStyleSheet("color: #991b1b; font-weight: 600;")

    def _apply_frequency(self) -> None:
        freq_hz = frequency_to_hz(self._freq_value_spin.value(), self._freq_unit_combo.currentText())
        self._runner.send_confirmed_controls(
            frequency_hz=freq_hz, ac_voltage_v=self._ac_voltage_spin.value(),
            dc_bias_v=self._dc_bias_spin.value(), bias_on=False,
            terminator=self._terminator_value(), run_optional_bias_queries=False,
        )

    def _apply_ac_voltage(self) -> None:
        freq_hz = frequency_to_hz(self._freq_value_spin.value(), self._freq_unit_combo.currentText())
        self._runner.send_confirmed_controls(
            frequency_hz=freq_hz, ac_voltage_v=self._ac_voltage_spin.value(),
            dc_bias_v=self._dc_bias_spin.value(), bias_on=False,
            terminator=self._terminator_value(), run_optional_bias_queries=False,
        )

    def _apply_bias_value(self) -> None:
        freq_hz = frequency_to_hz(self._freq_value_spin.value(), self._freq_unit_combo.currentText())
        self._manual_bias_enabled = True
        self._runner.send_confirmed_controls(
            frequency_hz=freq_hz, ac_voltage_v=self._ac_voltage_spin.value(),
            dc_bias_v=self._dc_bias_spin.value(), bias_on=True,
            terminator=self._terminator_value(), run_optional_bias_queries=False,
        )

    def _set_bias_state(self, enabled: bool) -> None:
        self._manual_bias_enabled = enabled
        freq_hz = frequency_to_hz(self._freq_value_spin.value(), self._freq_unit_combo.currentText())
        self._runner.send_confirmed_controls(
            frequency_hz=freq_hz, ac_voltage_v=self._ac_voltage_spin.value(),
            dc_bias_v=self._dc_bias_spin.value(), bias_on=enabled,
            terminator=self._terminator_value(), run_optional_bias_queries=False,
        )

    def _query_optional_bias(self) -> None:
        freq_hz = frequency_to_hz(self._freq_value_spin.value(), self._freq_unit_combo.currentText())
        self._runner.send_confirmed_controls(
            frequency_hz=freq_hz, ac_voltage_v=self._ac_voltage_spin.value(),
            dc_bias_v=self._dc_bias_spin.value(), bias_on=True,
            terminator=self._terminator_value(), run_optional_bias_queries=True,
        )

    def _reset_run_state_ui(self) -> None:
        self.current_run_rows = []
        self._results_table.setRowCount(0)
        self._results_summary_lbl.setText("Rows: 0")
        self._results_last_status_lbl.setText("Last point: —")

    @staticmethod
    def _build_frequency_list_hz(start_hz: float, stop_hz: float, step_hz: float) -> list[float]:
        if step_hz <= 0 or start_hz >= stop_hz:
            return []
        points: list[float] = []
        current_hz = float(start_hz)
        max_points = 500000
        while current_hz <= stop_hz + 1e-9:
            points.append(round(current_hz, 12))
            current_hz += step_hz
            if len(points) > max_points:
                break
        return points

    def _build_bias_plan_for_mode(self, mode: str) -> tuple[bool, list[float]]:
        if mode == "Frequency Sweep Only":
            if self._manual_bias_enabled:
                return True, [float(self._dc_bias_spin.value())]
            return False, [0.0]
        bias_values = self._parse_dc_bias_list(self._dc_bias_list_input.text())
        return True, bias_values

    def _measure_once(self) -> None:
        if self._runner.is_running():
            QMessageBox.warning(self, "Busy", "A run is already in progress.")
            return
        self._append_log("[measure-once] Starting single acquisition")
        unit = self._freq_unit_combo.currentText()
        target_hz = frequency_to_hz(self._freq_value_spin.value(), unit)
        use_dc_bias = self._manual_bias_enabled
        bias_value = float(self._dc_bias_spin.value()) if use_dc_bias else 0.0

        settings = SweepSettings(
            sample_id=self._sample_name_input.text().strip() or "sample",
            ac_voltage_v=float(self._ac_voltage_spin.value()),
            dc_bias_v=float(bias_value),
            frequency_start_hz=target_hz,
            frequency_stop_hz=target_hz,
            frequency_step_hz=1.0,
            point_settle_delay_s=float(self._point_delay_spin.value()),
            measure_delay_s=float(self._measure_delay_spin.value()),
            bias_settle_delay_s=float(self._bias_delay_spin.value()),
            use_dc_bias=use_dc_bias,
            dc_bias_list_v=[float(bias_value)],
            frequency_points_hz=[float(target_hz)],
        )
        self._run_active = False
        self._runner.measure_once(self._connection_settings(), settings)

    def _run_selected_mode(self) -> None:
        if self._runner.is_running():
            QMessageBox.warning(self, "Busy", "A run is already in progress.")
            return

        mode = self._run_mode_combo.currentText().strip()
        values = self._resolve_sweep_values_hz(show_warnings=True)
        if values is None:
            return
        start_hz, stop_hz, step_hz, _points = values

        frequency_points_hz = self._build_frequency_list_hz(start_hz, stop_hz, step_hz)
        if not frequency_points_hz:
            QMessageBox.warning(self, "Invalid Frequency Plan", "Sweep frequency list is empty.")
            return

        try:
            use_dc_bias, bias_plan = self._build_bias_plan_for_mode(mode)
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid DC Bias List", str(exc))
            return

        self._reset_run_state_ui()
        self._run_active = True
        self._append_log("[run] Run started")
        self._append_log(
            f"[run] start_hz={start_hz:g}, stop_hz={stop_hz:g}, step_hz={step_hz:g}, "
            f"points={len(frequency_points_hz)}"
        )
        self._append_log(f"[run] Bias plan: {bias_plan}")

        settings = SweepSettings(
            sample_id=self._sample_name_input.text().strip() or "sample",
            ac_voltage_v=float(self._ac_voltage_spin.value()),
            dc_bias_v=float(bias_plan[0]),
            frequency_start_hz=start_hz,
            frequency_stop_hz=stop_hz,
            frequency_step_hz=step_hz,
            point_settle_delay_s=float(self._point_delay_spin.value()),
            measure_delay_s=float(self._measure_delay_spin.value()),
            bias_settle_delay_s=float(self._bias_delay_spin.value()),
            use_dc_bias=use_dc_bias,
            dc_bias_list_v=bias_plan,
            frequency_points_hz=frequency_points_hz,
        )
        self._runner.run_sweep(self._connection_settings(), settings)

    def _preview_run_plan(self) -> None:
        mode = self._run_mode_combo.currentText().strip()
        values = self._resolve_sweep_values_hz(show_warnings=True)
        if values is None:
            return
        start_hz, stop_hz, step_hz, _points_per_sweep = values

        start_val = self._sweep_start_spin.value()
        stop_val = self._sweep_stop_spin.value()
        step_val = self._sweep_step_spin.value()
        start_unit = self._sweep_start_unit_combo.currentText()
        stop_unit = self._sweep_stop_unit_combo.currentText()
        step_unit = self._sweep_step_unit_combo.currentText()

        frequency_points_hz = self._build_frequency_list_hz(start_hz, stop_hz, step_hz)
        if not frequency_points_hz:
            QMessageBox.warning(self, "Invalid Frequency Plan", "Sweep frequency list is empty.")
            return
        try:
            _use_dc_bias, bias_values = self._build_bias_plan_for_mode(mode)
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid DC Bias List", str(exc))
            return

        total_points = len(frequency_points_hz) * len(bias_values)
        self._append_log("[run-plan] -----------------------------")
        self._append_log(f"[run-plan] Mode: {mode}")
        self._append_log(f"[run-plan] Start: {start_val:g} {start_unit} ({start_hz:g} Hz)")
        self._append_log(f"[run-plan] Stop: {stop_val:g} {stop_unit} ({stop_hz:g} Hz)")
        self._append_log(f"[run-plan] Step: {step_val:g} {step_unit} ({step_hz:g} Hz)")
        self._append_log(f"[run-plan] Points per sweep: {len(frequency_points_hz)}")
        self._append_log(f"[run-plan] Estimated total points: {total_points}")
        for index, bias in enumerate(bias_values, start=1):
            self._append_log(f"[run-plan] Bias {index}: {bias:g} V")

    def _resolve_sweep_values_hz(self, show_warnings: bool) -> tuple[float, float, float, int] | None:
        start_hz = frequency_to_hz(self._sweep_start_spin.value(), self._sweep_start_unit_combo.currentText())
        stop_hz = frequency_to_hz(self._sweep_stop_spin.value(), self._sweep_stop_unit_combo.currentText())
        step_hz = frequency_to_hz(self._sweep_step_spin.value(), self._sweep_step_unit_combo.currentText())

        if step_hz <= 0:
            if show_warnings:
                QMessageBox.warning(self, "Invalid Step", "Sweep step must be greater than zero.")
            return None
        if start_hz >= stop_hz:
            if show_warnings:
                QMessageBox.warning(self, "Invalid Range", "Sweep start must be less than sweep stop.")
            return None

        frequency_points_hz = self._build_frequency_list_hz(start_hz, stop_hz, step_hz)
        points = len(frequency_points_hz)
        if points == 0:
            if show_warnings:
                QMessageBox.warning(self, "Invalid Sweep", "Sweep frequency list is empty.")
            return None
        if points < 2:
            if show_warnings:
                QMessageBox.warning(self, "Sweep Resolution Warning", "Fewer than 2 points in sweep.")
            return None
        if show_warnings and points < 10:
            QMessageBox.warning(self, "Few Points Warning", f"This sweep has only {points} points.")
        if points > 20000:
            QMessageBox.warning(self, "Large Sweep Warning", f"This sweep has {points} points.")

        return start_hz, stop_hz, step_hz, points

    @staticmethod
    def _parse_dc_bias_list(text: str) -> list[float]:
        values: list[float] = []
        for token in text.split(","):
            raw = token.strip()
            if not raw:
                continue
            try:
                values.append(float(raw))
            except ValueError as exc:
                raise ValueError(f"Invalid DC bias value: '{raw}'") from exc
        if not values:
            raise ValueError("DC bias list is empty.")
        return values

    def _on_measurement(self, row: dict) -> None:
        run_row = {k: row.get(k, "") for k in LIVE_RESULTS_FIELDNAMES}
        run_row["measurement_ok"] = row.get("measurement_ok", True)
        self.current_run_rows.append(run_row)
        self._append_table_row(run_row)
        self._check_results_consistency()

    def _check_results_consistency(self) -> None:
        table_rows = self._results_table.rowCount()
        data_rows = len(self.current_run_rows)
        self._results_summary_lbl.setText(f"Rows: {data_rows}")
        if self.current_run_rows:
            last = self.current_run_rows[-1]
            self._results_last_status_lbl.setText(
                f"Last: f={last.get('freq_hz', '?')} Hz, "
                f"Z={last.get('z_ohm', '?')}, theta={last.get('theta_deg', '?')}"
            )

    def _append_table_row(self, row: dict) -> None:
        r_idx = self._results_table.rowCount()
        self._results_table.insertRow(r_idx)
        cols = [
            "timestamp", "sample_id", "freq_hz", "ac_voltage_v",
            "dc_bias_on", "dc_bias_v", "z_ohm", "theta_deg", "status", "raw_response",
        ]
        for c, key in enumerate(cols):
            self._results_table.setItem(r_idx, c, QTableWidgetItem(str(row.get(key, ""))))

    def _on_sweep_finished(self, summary: dict) -> None:
        mode = summary.get("mode", "")
        completed = summary.get("completed", False)
        rows = summary.get("rows_collected", 0)
        self._run_active = False

        if mode == "measure_once":
            status = "OK" if completed else "FAILED"
            self._append_log(f"[measure-once] {status}, rows={rows}")
        else:
            duration = summary.get("duration_s", 0.0)
            successful = summary.get("successful_points", 0)
            failed = summary.get("failed_points", 0)
            status = "COMPLETED" if completed else "INTERRUPTED"
            self._append_log(
                f"[sweep] {status} — rows={rows}, ok={successful}, failed={failed}, "
                f"duration={duration:.1f}s"
            )

        if self.current_run_rows and self._run_active is False and completed and rows > 0:
            self._auto_export_live_results()

    def _auto_export_live_results(self) -> None:
        folder = self._output_folder_input.text().strip() or str(Path.cwd() / "exports_v3")
        stem = self._sample_name_input.text().strip() or "sample"
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = Path(folder) / f"{stem}_live_{stamp}.csv"
        try:
            CsvExporter.export_live_results(out_path, self.current_run_rows)
            self._append_log(f"[auto-export] Saved: {out_path}")
        except Exception as exc:
            self._append_log(f"[auto-export] ERROR: {exc}")

    def _export_live_results_now(self) -> None:
        if not self.current_run_rows:
            QMessageBox.information(self, "No Data", "No live results to export yet.")
            return
        folder = self._output_folder_input.text().strip() or str(Path.cwd() / "exports_v3")
        stem = self._sample_name_input.text().strip() or "sample"
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = Path(folder) / f"{stem}_live_manual_{stamp}.csv"
        try:
            CsvExporter.export_live_results(out_path, self.current_run_rows)
            QMessageBox.information(self, "Export Complete", f"Saved to:\n{out_path}")
            self._append_log(f"[export] Saved: {out_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))

    def _browse_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self._output_folder_input.text()
        )
        if folder:
            self._output_folder_input.setText(folder)

    def _browse_nyquist_slot_file(self, index: int) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, f"Load Nyquist Slot {index + 1}",
            self._output_folder_input.text(),
            "CSV Files (*.csv);;All Files (*)",
        )
        if path:
            self._nyquist_slot_inputs[index].setText(path)

    def _clear_nyquist_slot_file(self, index: int) -> None:
        self._nyquist_slot_inputs[index].clear()

    def _refresh_nyquist_compare(self) -> None:
        """Refresh the V2.3-compatible Nyquist Compare tab."""
        if not QT_CHARTS_AVAILABLE or self._nyquist_chart is None:
            return

        self._nyquist_chart.removeAllSeries()
        for axis in self._nyquist_chart.axes():
            self._nyquist_chart.removeAxis(axis)

        series_colors = ["#1d4ed8", "#b45309", "#065f46"]
        loaded = 0

        for slot_index, path_input in enumerate(self._nyquist_slot_inputs):
            path = path_input.text().strip()
            if not path:
                continue
            try:
                points = load_nyquist_preview_points(path)
                if not points:
                    self._nyquist_status_output.append(
                        f"[slot {slot_index + 1}] No Nyquist points found in file"
                    )
                    continue

                from PySide6.QtGui import QColor
                from PySide6.QtCharts import QLineSeries
                series = QLineSeries()
                series.setName(Path(path).stem)
                color = QColor(series_colors[slot_index % len(series_colors)])
                pen = series.pen()
                pen.setColor(color)
                pen.setWidthF(2.0)
                series.setPen(pen)
                for pt in points:
                    series.append(pt.z_real, -pt.z_imag)

                self._nyquist_chart.addSeries(series)
                self._nyquist_chart.createDefaultAxes()
                loaded += 1
                self._nyquist_status_output.append(
                    f"[slot {slot_index + 1}] {Path(path).name} — {len(points)} points"
                )
            except Exception as exc:
                self._nyquist_status_output.append(
                    f"[slot {slot_index + 1}] ERROR: {exc}"
                )

        if loaded == 0:
            self._nyquist_chart.setTitle("Nyquist Compare — no data loaded")
        else:
            self._nyquist_chart.setTitle(f"Nyquist Compare — {loaded} file(s)")

    def _run_diag_manual(self, expect_response: bool) -> None:
        command = self._diag_manual_input.text().strip()
        if not command:
            self._append_diag("ERROR: Command input is empty")
            return
        self._run_diag_command(command, expect_response)

    def _run_diag_command(self, command: str, expect_response: bool) -> None:
        self._append_diag(f"TX: {command}")
        try:
            response = self._runner.execute_command(
                connection=self._connection_settings(),
                command=command,
                expect_response=expect_response,
            )
            if expect_response:
                if response is None:
                    self._append_diag("RX: <none>")
                elif response == "":
                    self._append_diag("RX: <empty>")
                else:
                    self._append_diag(f"RX: {response}")
            else:
                self._append_diag("INFO: Sent without read")
        except Exception as exc:
            self._append_diag(f"ERROR: {exc}")
