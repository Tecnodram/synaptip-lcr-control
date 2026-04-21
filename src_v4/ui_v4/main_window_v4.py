"""
main_window_v4.py - SynAptIp Nyquist Analyzer V4 Main Window
SynAptIp Technologies

V4 takes the stable V3.6 base and integrates logarithmic sweep design
directly into the existing run workflow instead of separating it into
an independent tab.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

_HERE = Path(__file__).resolve().parent.parent
_ROOT = _HERE.parent
sys.path[0:0] = [
    str(_HERE),
    str(_ROOT / "src_v3_6"),
    str(_ROOT / "src_v3"),
    str(_ROOT / "src_v3_5"),
]

from ui_v36.main_window_v3_6 import MainWindowV3_6
from services.scan_runner import SweepSettings
from services.unit_conversion import frequency_to_hz


APP_VERSION_V4 = "4.0.0"


class MainWindowV4(MainWindowV3_6):
    """V4 main window built from the stable V3.6 workflow."""

    LOG_ONLY_MODE = "Log Sweep Designer"
    LOG_BIAS_MODE = "DC Bias List + Log Sweep Designer"

    def __init__(self) -> None:
        self._log_sweep_config_v4 = {
            "start_hz": 10.0,
            "stop_hz": 1_000_000.0,
            "ppo": 25,
        }
        super().__init__()
        self.setWindowTitle("SynAptIp Nyquist Analyzer V4")
        self._on_run_mode_changed_v4(self._run_mode_combo.currentText().strip())

    def _build_header_v36(self):
        header_card = super()._build_header_v36()
        try:
            from PySide6.QtWidgets import QLabel

            badge = header_card.findChild(QLabel, "versionBadge")
            if badge:
                badge.setText(f"Version {APP_VERSION_V4}")
            title_lbl = header_card.findChild(QLabel, "headerTitle")
            if title_lbl:
                title_lbl.setText("SynAptIp Nyquist Analyzer V4")
            subtitle_lbl = header_card.findChild(QLabel, "headerSubtitle")
            if subtitle_lbl:
                subtitle_lbl.setText(
                    "Stable V3.6 Base with Integrated Log Sweep Run Modes"
                )
        except Exception:
            pass
        return header_card

    def _build_sweep_group(self) -> QGroupBox:
        group = super()._build_sweep_group()
        layout = group.layout()
        if layout is None:
            return group

        row = layout.rowCount()
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

        self._log_preview_v4 = QTextEdit()
        self._log_preview_v4.setReadOnly(True)
        self._log_preview_v4.setMaximumHeight(130)
        self._log_preview_v4.setStyleSheet("font-family: Consolas; font-size: 9pt;")

        self._log_summary_label_v4 = QLabel()
        self._log_summary_label_v4.setStyleSheet("font-weight: 600; color: #1f2937;")

        layout.addWidget(QLabel("Log Start"), row, 0)
        layout.addWidget(self._log_start_spin_v4, row, 1)
        layout.addWidget(self._log_start_unit_combo_v4, row, 2)
        layout.addWidget(QLabel("Log Stop"), row + 1, 0)
        layout.addWidget(self._log_stop_spin_v4, row + 1, 1)
        layout.addWidget(self._log_stop_unit_combo_v4, row + 1, 2)
        layout.addWidget(QLabel("PPO Preset"), row + 2, 0)
        layout.addWidget(self._ppo_preset_combo_v4, row + 2, 1, 1, 2)
        layout.addWidget(QLabel("Custom PPO"), row + 3, 0)
        layout.addWidget(self._ppo_custom_spin_v4, row + 3, 1)
        layout.addWidget(self._log_summary_label_v4, row + 4, 0, 1, 4)
        layout.addWidget(QLabel("Sweep Preview"), row + 5, 0, 1, 4)
        layout.addWidget(self._log_preview_v4, row + 6, 0, 1, 4)

        self._update_log_sweep_controls_v4()
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
            self.LOG_ONLY_MODE,
            self.LOG_BIAS_MODE,
        ])

        self._dc_bias_list_input = QLineEdit("-1,-0.5,0,0.5,1")
        self._dc_bias_list_input.setPlaceholderText("Comma-separated values, e.g. -1,-0.5,0,0.5,1")

        help_text = QLabel(
            "Choose linear or integrated logarithmic sweep modes. "
            "Log sweep modes generate the full frequency list directly from PPO."
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

    def _wire_events(self) -> None:
        super()._wire_events()
        self._run_mode_combo.currentTextChanged.connect(self._on_run_mode_changed_v4)
        self._log_start_spin_v4.valueChanged.connect(self._on_log_sweep_changed_v4)
        self._log_start_unit_combo_v4.currentTextChanged.connect(self._on_log_sweep_changed_v4)
        self._log_stop_spin_v4.valueChanged.connect(self._on_log_sweep_changed_v4)
        self._log_stop_unit_combo_v4.currentTextChanged.connect(self._on_log_sweep_changed_v4)
        self._ppo_preset_combo_v4.currentTextChanged.connect(self._on_ppo_preset_changed_v4)
        self._ppo_custom_spin_v4.valueChanged.connect(self._on_ppo_custom_changed_v4)

    def _is_log_mode_v4(self, mode: str | None = None) -> bool:
        mode = mode or self._run_mode_combo.currentText().strip()
        return mode in {self.LOG_ONLY_MODE, self.LOG_BIAS_MODE}

    def _on_run_mode_changed_v4(self, mode_text: str) -> None:
        use_bias_list = mode_text in {"DC Bias List + Frequency Sweep", self.LOG_BIAS_MODE}
        is_log = self._is_log_mode_v4(mode_text)

        self._dc_bias_list_input.setEnabled(use_bias_list)

        for widget in [
            self._sweep_start_spin,
            self._sweep_start_unit_combo,
            self._sweep_stop_spin,
            self._sweep_stop_unit_combo,
            self._sweep_step_spin,
            self._sweep_step_unit_combo,
        ]:
            widget.setEnabled(not is_log)

        for widget in [
            self._log_start_spin_v4,
            self._log_start_unit_combo_v4,
            self._log_stop_spin_v4,
            self._log_stop_unit_combo_v4,
            self._ppo_preset_combo_v4,
            self._log_preview_v4,
        ]:
            widget.setEnabled(is_log)

        self._ppo_custom_spin_v4.setEnabled(
            is_log and self._ppo_preset_combo_v4.currentText().strip() == "Custom"
        )
        self._log_summary_label_v4.setEnabled(is_log)
        self._update_log_sweep_controls_v4()

    def _on_ppo_preset_changed_v4(self, preset: str) -> None:
        if "Fast" in preset:
            self._ppo_custom_spin_v4.setValue(10)
        elif "Standard" in preset:
            self._ppo_custom_spin_v4.setValue(20)
        elif "High Resolution" in preset:
            self._ppo_custom_spin_v4.setValue(25)
        elif "Publication" in preset:
            self._ppo_custom_spin_v4.setValue(30)
        self._ppo_custom_spin_v4.setEnabled(
            self._is_log_mode_v4() and preset.strip() == "Custom"
        )
        self._on_log_sweep_changed_v4()

    def _on_ppo_custom_changed_v4(self, _value: float) -> None:
        current_value = int(self._ppo_custom_spin_v4.value())
        preset_text = {
            10: "10 (Fast)",
            20: "20 (Standard)",
            25: "25 (High Resolution)",
            30: "30 (Publication / Fine)",
        }.get(current_value, "Custom")
        if self._ppo_preset_combo_v4.currentText().strip() != preset_text:
            self._ppo_preset_combo_v4.blockSignals(True)
            self._ppo_preset_combo_v4.setCurrentText(preset_text)
            self._ppo_preset_combo_v4.blockSignals(False)
        self._ppo_custom_spin_v4.setEnabled(
            self._is_log_mode_v4() and self._ppo_preset_combo_v4.currentText().strip() == "Custom"
        )
        self._on_log_sweep_changed_v4()

    def _on_log_sweep_changed_v4(self, *_args) -> None:
        self._log_sweep_config_v4 = {
            "start_hz": frequency_to_hz(self._log_start_spin_v4.value(), self._log_start_unit_combo_v4.currentText()),
            "stop_hz": frequency_to_hz(self._log_stop_spin_v4.value(), self._log_stop_unit_combo_v4.currentText()),
            "ppo": int(self._ppo_custom_spin_v4.value()),
        }
        self._update_log_sweep_controls_v4()

    def _update_log_sweep_controls_v4(self) -> None:
        try:
            start_hz = float(self._log_sweep_config_v4["start_hz"])
            stop_hz = float(self._log_sweep_config_v4["stop_hz"])
            ppo = int(self._log_sweep_config_v4["ppo"])
            if start_hz <= 0 or stop_hz <= start_hz or ppo <= 0:
                self._log_summary_label_v4.setText("Invalid logarithmic sweep configuration.")
                self._log_preview_v4.setPlainText("")
                return

            points = self._build_log_frequency_list_hz_v4(start_hz, stop_hz, ppo)
            orders = math.log10(stop_hz) - math.log10(start_hz)
            self._log_summary_label_v4.setText(
                f"Log Sweep Summary: {len(points)} points | Orders: {orders:.2f} | PPO: {ppo}"
            )

            preview_lines: list[str] = []
            for freq in points[:20]:
                if freq >= 1_000_000:
                    preview_lines.append(f"{freq / 1_000_000:.3f} MHz")
                elif freq >= 1_000:
                    preview_lines.append(f"{freq / 1_000:.3f} kHz")
                else:
                    preview_lines.append(f"{freq:.3f} Hz")
            if len(points) > 20:
                preview_lines.append(f"... and {len(points) - 20} more points")
            self._log_preview_v4.setPlainText("\n".join(preview_lines))
        except Exception as exc:
            self._log_summary_label_v4.setText(f"Invalid logarithmic sweep configuration: {exc}")
            self._log_preview_v4.setPlainText("")

    @staticmethod
    def _build_log_frequency_list_hz_v4(start_hz: float, stop_hz: float, ppo: int) -> list[float]:
        orders = math.log10(stop_hz) - math.log10(start_hz)
        n_points = int(orders * ppo) + 1
        if n_points < 2:
            return []
        step = orders / (n_points - 1)
        return [round(10 ** (math.log10(start_hz) + i * step), 12) for i in range(n_points)]

    def _resolve_sweep_values_hz(self, show_warnings: bool) -> tuple[float, float, float, int] | None:
        if not self._is_log_mode_v4():
            return super()._resolve_sweep_values_hz(show_warnings)

        start_hz = float(self._log_sweep_config_v4["start_hz"])
        stop_hz = float(self._log_sweep_config_v4["stop_hz"])
        ppo = int(self._log_sweep_config_v4["ppo"])
        frequency_points_hz = self._build_log_frequency_list_hz_v4(start_hz, stop_hz, ppo)

        if start_hz <= 0:
            if show_warnings:
                QMessageBox.warning(self, "Invalid Range", "Log sweep start must be greater than zero.")
            return None
        if stop_hz <= start_hz:
            if show_warnings:
                QMessageBox.warning(self, "Invalid Range", "Log sweep stop must be greater than start.")
            return None
        if ppo <= 0:
            if show_warnings:
                QMessageBox.warning(self, "Invalid PPO", "PPO must be greater than zero.")
            return None
        if len(frequency_points_hz) < 2:
            if show_warnings:
                QMessageBox.warning(self, "Invalid Sweep", "Logarithmic sweep frequency list is empty.")
            return None
        if show_warnings and len(frequency_points_hz) < 10:
            QMessageBox.warning(self, "Few Points Warning", f"This sweep has only {len(frequency_points_hz)} points.")
        if len(frequency_points_hz) > 20000:
            QMessageBox.warning(self, "Large Sweep Warning", f"This sweep has {len(frequency_points_hz)} points.")

        return start_hz, stop_hz, 0.0, len(frequency_points_hz)

    def _build_bias_plan_for_mode(self, mode: str) -> tuple[bool, list[float]]:
        if mode in {"Frequency Sweep Only", self.LOG_ONLY_MODE}:
            if self._manual_bias_enabled:
                return True, [float(self._dc_bias_spin.value())]
            return False, [0.0]
        return super()._build_bias_plan_for_mode("DC Bias List + Frequency Sweep")

    def _run_selected_mode(self) -> None:
        if self._runner.is_running():
            QMessageBox.warning(self, "Busy", "A run is already in progress.")
            return

        mode = self._run_mode_combo.currentText().strip()
        values = self._resolve_sweep_values_hz(show_warnings=True)
        if values is None:
            return
        start_hz, stop_hz, step_hz, _points = values

        if self._is_log_mode_v4(mode):
            ppo = int(self._log_sweep_config_v4["ppo"])
            frequency_points_hz = self._build_log_frequency_list_hz_v4(start_hz, stop_hz, ppo)
        else:
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
        self._append_log(f"[run] Mode: {mode}")
        self._append_log(
            f"[run] start_hz={start_hz:g}, stop_hz={stop_hz:g}, step_hz={step_hz:g}, points={len(frequency_points_hz)}"
        )
        if self._is_log_mode_v4(mode):
            self._append_log(f"[run] PPO={int(self._log_sweep_config_v4['ppo'])}")
        self._append_log(f"[run] Bias plan: {bias_plan}")

        settings = SweepSettings(
            sample_id=self._sample_name_input.text().strip() or "sample",
            ac_voltage_v=float(self._ac_voltage_spin.value()),
            dc_bias_v=float(bias_plan[0]),
            frequency_start_hz=frequency_points_hz[0],
            frequency_stop_hz=frequency_points_hz[-1],
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
        start_hz, stop_hz, step_hz, _points = values

        if self._is_log_mode_v4(mode):
            ppo = int(self._log_sweep_config_v4["ppo"])
            frequency_points_hz = self._build_log_frequency_list_hz_v4(start_hz, stop_hz, ppo)
        else:
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
        self._append_log(f"[run-plan] Start: {start_hz:g} Hz")
        self._append_log(f"[run-plan] Stop: {stop_hz:g} Hz")
        if self._is_log_mode_v4(mode):
            self._append_log(f"[run-plan] PPO: {int(self._log_sweep_config_v4['ppo'])}")
            self._append_log("[run-plan] Step: logarithmic distribution")
        else:
            self._append_log(f"[run-plan] Step: {step_hz:g} Hz")
        self._append_log(f"[run-plan] Points per sweep: {len(frequency_points_hz)}")
        self._append_log(f"[run-plan] Estimated total points: {total_points}")
        for index, bias in enumerate(bias_values, start=1):
            self._append_log(f"[run-plan] Bias {index}: {bias:g} V")
