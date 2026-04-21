"""
main_window_v4_1.py - SynAptIp Nyquist Analyzer V4.1 Main Window
SynAptIp Technologies

V4.1 keeps the V4 measurement logic intact and improves the Control & Scan
layout by adding scrolling and organizing sweep controls into tabs.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

_HERE = Path(__file__).resolve().parent.parent
_ROOT = _HERE.parent
sys.path[0:0] = [
    str(_HERE),
    str(_ROOT / "src_v4"),
    str(_ROOT / "src_v3_6"),
    str(_ROOT / "src_v3"),
    str(_ROOT / "src_v3_5"),
]

from ui_v4.main_window_v4 import MainWindowV4


APP_VERSION_V41 = "4.1.0"


class MainWindowV4_1(MainWindowV4):
    """V4.1 reorganizes the V4 control layout without changing run logic."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SynAptIp Nyquist Analyzer V4.1")

    def _build_header_v36(self):
        header_card = super()._build_header_v36()
        try:
            from PySide6.QtWidgets import QLabel

            brand_pill = header_card.findChild(QLabel, "brandPill")
            if brand_pill:
                brand_pill.setText("SynAptIp\nPrecision LCR & EIS Software")
                brand_pill.setWordWrap(True)
                brand_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
                brand_pill.setMinimumWidth(150)
                brand_pill.setStyleSheet(
                    "background: rgba(255, 255, 255, 0.10);"
                    "color: #e2e8f0;"
                    "border: 1px solid rgba(255, 255, 255, 0.22);"
                    "border-radius: 11px;"
                    "padding: 8px 10px;"
                    "font-weight: 600;"
                )
            badge = header_card.findChild(QLabel, "versionBadge")
            if badge:
                badge.setText(f"Version {APP_VERSION_V41}")
            title_lbl = header_card.findChild(QLabel, "headerTitle")
            if title_lbl:
                title_lbl.setText("SynAptIp Nyquist Analyzer V4.1")
            subtitle_lbl = header_card.findChild(QLabel, "headerSubtitle")
            if subtitle_lbl:
                subtitle_lbl.setText(
                    "Professional LCR Control, Nyquist Analysis, and Electrochemical Impedance Spectroscopy"
                )
            powered_lbl = header_card.findChild(QLabel, "headerPowered")
            if powered_lbl:
                powered_lbl.setText(
                    "Support, improvements and licensing: synaptip.tech@gmail.com"
                )
        except Exception:
            pass
        return header_card

    def _build_control_scan_tab(self) -> QWidget:
        tab = QWidget()
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(6, 8, 6, 6)
        layout.setSpacing(10)

        top = QWidget()
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        columns = self._build_control_scan_columns_v41()
        top_layout.addLayout(columns)
        layout.addWidget(top, stretch=0)
        layout.addWidget(self._build_log_panel(), stretch=0)
        layout.addStretch(1)

        scroll.setWidget(content)
        outer.addWidget(scroll)
        return tab

    def _build_control_scan_columns_v41(self) -> QVBoxLayout:
        wrapper = QVBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.setSpacing(12)

        columns = QWidget()
        grid = QGridLayout(columns)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        left_layout.addWidget(self._build_connection_group())
        left_layout.addWidget(self._build_manual_control_group())
        left_layout.addWidget(self._build_sweep_group())
        left_layout.addStretch(1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_layout.addWidget(self._build_assumptions_group())
        right_layout.addWidget(self._build_run_group())
        right_layout.addStretch(1)

        grid.addWidget(left, 0, 0)
        grid.addWidget(right, 0, 1)
        grid.setColumnStretch(0, 10)
        grid.setColumnStretch(1, 12)

        wrapper.addWidget(columns)
        return wrapper

    def _build_sweep_group(self) -> QGroupBox:
        group = QGroupBox("Sweep Controls")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        help_text = QLabel(
            "Use the Run Mode to choose linear or logarithmic operation. "
            "These tabs only organize the input controls and do not change the run logic."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #6b7280;")
        layout.addWidget(help_text)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        self._sweep_tabs_v41 = tabs

        linear_tab = QWidget()
        linear_form = QFormLayout(linear_tab)
        linear_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

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

        linear_form.addRow("Start", self._row_widget_v41(self._sweep_start_spin, self._sweep_start_unit_combo))
        linear_form.addRow("Stop", self._row_widget_v41(self._sweep_stop_spin, self._sweep_stop_unit_combo))
        linear_form.addRow("Step", self._row_widget_v41(self._sweep_step_spin, self._sweep_step_unit_combo))

        log_tab = QWidget()
        log_form = QFormLayout(log_tab)
        log_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._log_start_spin_v4 = QDoubleSpinBox()
        self._log_start_spin_v4.setRange(0.001, 1_000_000.0)
        self._log_start_spin_v4.setValue(10.0)
        self._log_start_spin_v4.setDecimals(6)
        self._log_start_unit_combo_v4 = QComboBox()
        self._log_start_unit_combo_v4.addItems(["Hz", "kHz", "MHz"])

        self._log_stop_spin_v4 = QDoubleSpinBox()
        self._log_stop_spin_v4.setRange(0.001, 1_000_000.0)
        self._log_stop_spin_v4.setValue(1.0)
        self._log_stop_spin_v4.setDecimals(6)
        self._log_stop_unit_combo_v4 = QComboBox()
        self._log_stop_unit_combo_v4.addItems(["Hz", "kHz", "MHz"])
        self._log_stop_unit_combo_v4.setCurrentText("MHz")

        self._ppo_preset_combo_v4 = QComboBox()
        self._ppo_preset_combo_v4.addItems([
            "10 (Fast)",
            "20 (Standard)",
            "25 (High Resolution)",
            "30 (Publication / Fine)",
            "Custom",
        ])
        self._ppo_preset_combo_v4.setCurrentText("25 (High Resolution)")

        self._ppo_custom_spin_v4 = QDoubleSpinBox()
        self._ppo_custom_spin_v4.setRange(1, 100)
        self._ppo_custom_spin_v4.setSingleStep(1)
        self._ppo_custom_spin_v4.setDecimals(0)
        self._ppo_custom_spin_v4.setValue(25)

        self._log_summary_label_v4 = QLabel()
        self._log_summary_label_v4.setStyleSheet("font-weight: 600; color: #1f2937;")

        self._log_preview_v4 = QTextEdit()
        self._log_preview_v4.setReadOnly(True)
        self._log_preview_v4.setMinimumHeight(160)
        self._log_preview_v4.setStyleSheet("font-family: Consolas; font-size: 9pt;")

        log_form.addRow("Log Start", self._row_widget_v41(self._log_start_spin_v4, self._log_start_unit_combo_v4))
        log_form.addRow("Log Stop", self._row_widget_v41(self._log_stop_spin_v4, self._log_stop_unit_combo_v4))
        log_form.addRow("PPO Preset", self._ppo_preset_combo_v4)
        log_form.addRow("Custom PPO", self._ppo_custom_spin_v4)
        log_form.addRow("Summary", self._log_summary_label_v4)
        log_form.addRow("Sweep Preview", self._log_preview_v4)

        timing_tab = QWidget()
        timing_form = QFormLayout(timing_tab)
        timing_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

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

        timing_note = QLabel(
            "These delays are shared by both linear and logarithmic runs."
        )
        timing_note.setWordWrap(True)
        timing_note.setStyleSheet("color: #6b7280;")

        timing_form.addRow("Point settle", self._point_delay_spin)
        timing_form.addRow("Measure delay", self._measure_delay_spin)
        timing_form.addRow("Bias settle", self._bias_delay_spin)
        timing_form.addRow("", timing_note)

        tabs.addTab(linear_tab, "Linear Sweep")
        tabs.addTab(log_tab, "Log Sweep")
        tabs.addTab(timing_tab, "Timing")
        layout.addWidget(tabs)

        self._update_log_sweep_controls_v4()
        return group

    @staticmethod
    def _row_widget_v41(*widgets) -> QWidget:
        row = QWidget()
        layout = QGridLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(6)
        for index, widget in enumerate(widgets):
            layout.addWidget(widget, 0, index)
        if widgets:
            layout.setColumnStretch(len(widgets), 1)
        return row

    def _on_run_mode_changed_v4(self, mode_text: str) -> None:
        super()._on_run_mode_changed_v4(mode_text)
        if hasattr(self, "_sweep_tabs_v41"):
            if self._is_log_mode_v4(mode_text):
                self._sweep_tabs_v41.setCurrentIndex(1)
            else:
                self._sweep_tabs_v41.setCurrentIndex(0)
