"""
main_window_v3_7.py — SynAptIp Nyquist Analyzer V3.7 Main Window
SynAptIp Technologies

Extends MainWindowV3_6 by adding:
  - Advanced impedance spectroscopy scan capabilities
  - Exact Impedance Spectroscopy Scan (fixed preset)
  - Adaptive Logarithmic Sweep (configurable)
  - Publication-grade scientific visualization
  - Professional terminology and UI
  - Branding improvements

Strategy (identical to V3.6 approach):
  - Subclass MainWindowV3_6 via Python MRO
  - Override _build_ui() to inject new features
  - All existing tabs remain completely untouched
  - New components live in ui_v37/ — no namespace collision
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

# Ensure this module can locate V3.7, V3.6, V3.5 and V3 packages when imported or run directly.
_MODULE_ROOT = Path(__file__).resolve().parent.parent
_PARENT = _MODULE_ROOT.parent
sys.path[0:0] = [
    str(_MODULE_ROOT),
    str(_PARENT / "src_v3_6"),
    str(_PARENT / "src_v3"),
    str(_PARENT / "src_v3_5"),
]
for _path in tuple(sys.path[:4]):
    if not Path(_path).exists():
        sys.path.remove(_path)

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

# V3.6 base window (resolved via sys.path)
from ui_v36.main_window_v3_6 import MainWindowV3_6

# V3.7 panels (from src_v3_7/ui_v37/)
from ui_v37.log_sweep_designer import LogSweepDesigner
from ui_v37.compare_panel_v37 import ComparePanelV37


APP_VERSION_V37 = "3.7.0"


def _app_base_dir() -> Path:
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


class MainWindowV3_7(MainWindowV3_6):
    """
    V3.7 main window.

    Identical to V3.6 except:
      1. Window title / header badge show V3.7
      2. Enhanced Control & Scan tab with frequency scan modes
      3. A "Log Sweep Designer" tab is appended after all V3.6 tabs
      4. Branding improvements with contact info
      5. Publication-grade visualization enhancements
    """

    def __init__(self) -> None:
        self._active_log_sweep_config = {
            "mode": "logarithmic_sweep",
            "start_hz": 10.0,
            "stop_hz": 1000000.0,
            "ppo": 25,
        }
        super().__init__()
        self.setWindowTitle("SynAptIp Nyquist Analyzer V3.7")
        self._sync_log_sweep_output_dir()

    # ------------------------------------------------------------------ #
    # Override _build_ui to inject the Log Sweep Designer tab            #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        """Replicate V3.6 layout and append the new Log Sweep Designer tab."""
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(14)

        root.addWidget(self._build_header_v37())

        self._tabs = QTabWidget()

        # --- All V3.6 tabs (from MainWindowV3_6, with enhanced Control & Scan) ---
        self._tabs.addTab(self._build_control_scan_tab_v37(), "Control & Scan")
        self._tabs.addTab(self._build_live_results_tab(),     "Live Results")
        self._tabs.addTab(self._build_sample_output_tab(),    "Sample & Output")
        self._tabs.addTab(self._build_nyquist_compare_tab(),  "Nyquist Compare")
        self._tabs.addTab(self._build_nyquist_analysis_tab(), "Nyquist Analysis (V3)")
        self._tabs.addTab(self._build_diagnostics_tab(),      "Diagnostics & Commands")

        # --- V3.5 tab ---
        self._analysis_panel = __import__(
            "ui_v35.analysis_insights_panel", fromlist=["AnalysisInsightsPanel"]
        ).AnalysisInsightsPanel()
        self._tabs.addTab(self._analysis_panel, "Analysis & Insights")

        # --- V3.6 tab (enhanced with V3.7 publication-grade plotting) ---
        self._compare_panel = ComparePanelV37()
        self._tabs.addTab(self._compare_panel, "Compare")

        # --- V3.7 new tab ---
        self._log_sweep_panel = LogSweepDesigner()
        try:
            self._log_sweep_panel._start_freq_spin.valueChanged.connect(
                lambda *_: self._on_scan_mode_changed_v37(self._frequency_scan_mode)
            )
            self._log_sweep_panel._start_freq_unit.currentTextChanged.connect(
                lambda *_: self._on_scan_mode_changed_v37(self._frequency_scan_mode)
            )
            self._log_sweep_panel._stop_freq_spin.valueChanged.connect(
                lambda *_: self._on_scan_mode_changed_v37(self._frequency_scan_mode)
            )
            self._log_sweep_panel._stop_freq_unit.currentTextChanged.connect(
                lambda *_: self._on_scan_mode_changed_v37(self._frequency_scan_mode)
            )
            self._log_sweep_panel._ppo_preset_combo.currentTextChanged.connect(
                lambda *_: self._on_scan_mode_changed_v37(self._frequency_scan_mode)
            )
            self._log_sweep_panel._ppo_custom_spin.valueChanged.connect(
                lambda *_: self._on_scan_mode_changed_v37(self._frequency_scan_mode)
            )
            self._log_sweep_panel._apply_to_control_btn.clicked.connect(
                self._apply_log_sweep_to_control_v37
            )
        except Exception:
            pass
        self._tabs.addTab(self._log_sweep_panel, "Log Sweep Designer")
        try:
            self._output_folder_input.textChanged.connect(lambda *_: self._sync_log_sweep_output_dir())
        except Exception:
            pass

        self._tabs.setDocumentMode(True)
        self._tabs.setCurrentIndex(0)

        root.addWidget(self._tabs, stretch=1)
        self.setCentralWidget(central)
        self.setStyleSheet(self._stylesheet_v37())

    # ------------------------------------------------------------------ #
    # V3.7 header                                                          #
    # ------------------------------------------------------------------ #

    def _build_header_v37(self) -> QWidget:
        """Patch header to show V3.7 info with enhanced branding."""
        header_card = super()._build_header_v36()
        try:
            from PySide6.QtWidgets import QLabel
            # Find the version badge and update it
            for child in header_card.findChildren(QLabel):
                if hasattr(child, 'objectName') and child.objectName() == "versionBadge":
                    child.setText("Version 3.7.0")
                    break

            # Find the header title and update it
            for child in header_card.findChildren(QLabel):
                if hasattr(child, 'objectName') and child.objectName() == "headerTitle":
                    child.setText("SynAptIp Nyquist Analyzer V3.7")
                    break

            # Find the subtitle and update it
            for child in header_card.findChildren(QLabel):
                if hasattr(child, 'objectName') and child.objectName() == "headerSubtitle":
                    child.setText("Advanced EIS, Scientific Visualization & Impedance Spectroscopy")
                    break

            # Add contact info - we need to find the layout containing the subtitle
            # This is a bit hacky but works
            layout = header_card.layout()
            if layout:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item and item.layout():
                        sublayout = item.layout()
                        for j in range(sublayout.count()):
                            subitem = sublayout.itemAt(j)
                            if subitem and subitem.widget() and hasattr(subitem.widget(), 'objectName'):
                                if subitem.widget().objectName() == "headerSubtitle":
                                    # Found the subtitle, add contact after it
                                    contact = QLabel("Contact: synaptip.tech@gmail.com")
                                    contact.setObjectName("headerContact")
                                    contact.setStyleSheet("color: #6b7280; font-size: 11px; margin-top: 2px;")
                                    sublayout.insertWidget(j + 1, contact)
                                    break

        except Exception:
            pass
        return header_card

    # ------------------------------------------------------------------ #
    # Enhanced Control & Scan tab                                        #
    # ------------------------------------------------------------------ #

    def _build_control_scan_tab_v37(self) -> QWidget:
        """Enhanced Control & Scan tab with frequency scan modes."""
        # Get the base V3.6 control scan tab
        tab = super()._build_control_scan_tab()

        # Find the sweep group and enhance it with frequency scan mode selection
        try:
            from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox

            # Find the sweep group
            for child in tab.findChildren(QGroupBox):
                if child.title() == "Sweep Controls":
                    sweep_group = child
                    break
            else:
                return tab  # If not found, return original

            # Get the existing layout
            layout = sweep_group.layout()
            if not layout:
                return tab

            # Insert frequency scan mode selection at the top
            mode_layout = QHBoxLayout()
            mode_layout.addWidget(QLabel("Scan Mode:"))
            self._scan_mode_combo = QComboBox()
            self._scan_mode_combo.addItems([
                "Manual Linear Scan",
                "Exact Impedance Spectroscopy Scan",
                "Adaptive Logarithmic Sweep"
            ])

            # Set tooltips for each scan mode
            self._scan_mode_combo.setItemData(
                0,
                "Traditional linear frequency sweep with fixed steps (Hz). Default behavior identical to V3.6.1",
                role=1  # ToolTip role
            )
            self._scan_mode_combo.setItemData(
                1,
                "Fixed scientific preset: 101 points from 100 Hz to 1 MHz with logarithmic distribution (~25 PPO). Deterministic and reproducible for publication figures.",
                role=1
            )
            self._scan_mode_combo.setItemData(
                2,
                "Configurable logarithmic sweep. Points per order of magnitude (PPO) controls sampling density within each logarithmic decade. Higher PPO = better frequency resolution but longer acquisition time.",
                role=1
            )

            self._scan_mode_combo.currentTextChanged.connect(self._on_scan_mode_changed_v37)
            mode_layout.addWidget(self._scan_mode_combo)
            mode_layout.addStretch()

            # Insert at the beginning of the sweep group layout
            layout.insertLayout(0, mode_layout)

            # Add schedule summary label
            self._schedule_summary_label = QLabel(
                "Schedule: Manual linear scan from 1.0 Hz to 100.0 Hz (step: 1.0 Hz)"
            )
            self._schedule_summary_label.setStyleSheet(
                "font-weight: 600; color: #1f2937; padding: 8px; background: #f9fafb; border-radius: 4px;"
            )
            layout.addWidget(self._schedule_summary_label)

            # Initialize scan mode
            self._frequency_scan_mode = "Manual Linear Scan"
            self._ppo_value = 25

        except Exception:
            pass  # If enhancement fails, return original tab

        return tab

    def _resolve_sweep_values_hz(self, show_warnings: bool) -> tuple[float, float, float, int] | None:
        """Override to support new frequency scan modes."""
        from PySide6.QtWidgets import QMessageBox

        scan_mode = (
            self._scan_mode_combo.currentText().strip()
            if hasattr(self, "_scan_mode_combo")
            else getattr(self, "_frequency_scan_mode", "Manual Linear Scan")
        )
        self._frequency_scan_mode = scan_mode

        if scan_mode == "Exact Impedance Spectroscopy Scan":
            return 100.0, 1000000.0, 0.0, 101

        if scan_mode == "Adaptive Logarithmic Sweep":
            config = self._get_active_log_sweep_config_v37()
            start_hz = float(config.get("start_hz", 10.0))
            stop_hz = float(config.get("stop_hz", 1000000.0))
            ppo = float(config.get("ppo", getattr(self, "_ppo_value", 25)))

            if start_hz <= 0:
                if show_warnings:
                    QMessageBox.warning(self, "Invalid Range", "Sweep start must be greater than zero.")
                return None
            if stop_hz <= start_hz:
                if show_warnings:
                    QMessageBox.warning(self, "Invalid Range", "Sweep start must be less than sweep stop.")
                return None
            if ppo <= 0:
                if show_warnings:
                    QMessageBox.warning(self, "Invalid PPO", "Points per order must be greater than zero.")
                return None

            orders = math.log10(stop_hz) - math.log10(start_hz)
            points = int(orders * ppo) + 1
            if points < 2:
                if show_warnings:
                    QMessageBox.warning(self, "Sweep Resolution Warning", "Fewer than 2 points in sweep.")
                return None
            if show_warnings and points < 10:
                QMessageBox.warning(self, "Few Points Warning", f"This sweep has only {points} points.")
            if points > 20000:
                QMessageBox.warning(self, "Large Sweep Warning", f"This sweep has {points} points.")

            return start_hz, stop_hz, 0.0, points

        return super()._resolve_sweep_values_hz(show_warnings)

    @staticmethod
    def _build_frequency_list_hz(start_hz: float, stop_hz: float, step_hz: float) -> list[float]:
        """Override to support new frequency generation modes."""
        # This is a static method, so we need to check the instance somehow
        # For now, return the parent implementation
        # In a real implementation, we'd need to pass the scan mode
        return MainWindowV3_6._build_frequency_list_hz(start_hz, stop_hz, step_hz)

    def _on_scan_mode_changed_v37(self, mode_text: str) -> None:
        """Handle scan mode combo change. Store mode and update preview label."""
        self._frequency_scan_mode = mode_text.strip()
        try:
            if self._frequency_scan_mode == "Exact Impedance Spectroscopy Scan":
                self._schedule_summary_label.setText(
                    "Schedule: Exact Impedance Spectroscopy Scan - 101 logarithmic points from 100 Hz to 1 MHz (~25 PPO)"
                )
                return
            if self._frequency_scan_mode == "Adaptive Logarithmic Sweep":
                config = self._get_active_log_sweep_config_v37()
                start = float(config.get("start_hz", 10.0))
                stop = float(config.get("stop_hz", 1e6))
                ppo = float(config.get("ppo", 25))
                orders = math.log10(stop) - math.log10(start)
                n_points = int(orders * ppo) + 1
                self._schedule_summary_label.setText(
                    f"Schedule: Adaptive Log Sweep - {n_points} points from {start:.0f} Hz to {stop:.0f} Hz (PPO={ppo:g})"
                )
                return
        except Exception:
            pass
        
        # Update schedule summary label
        try:
            if self._frequency_scan_mode == "Exact Impedance Spectroscopy Scan":
                self._schedule_summary_label.setText(
                    "Schedule: Exact Impedance Spectroscopy Scan — 101 logarithmic points from 100 Hz to 1 MHz (~25 PPO)"
                )
            elif self._frequency_scan_mode == "Adaptive Logarithmic Sweep":
                # Show current LogSweepDesigner settings
                if hasattr(self, '_log_sweep_panel'):
                    config = self._log_sweep_panel.get_current_config()
                    start = config.get('start_hz', 10.0)
                    stop = config.get('stop_hz', 1e6)
                    ppo = config.get('ppo', 25)
                    orders = math.log10(stop) - math.log10(start)
                    n_points = int(orders * ppo) + 1
                    self._schedule_summary_label.setText(
                        f"Schedule: Adaptive Log Sweep — {n_points} points from {start:.0f} Hz to {stop:.0f} Hz (PPO={ppo})"
                    )
                else:
                    self._schedule_summary_label.setText(
                        "Schedule: Adaptive Logarithmic Sweep — see Log Sweep Designer tab for settings"
                    )
            else:  # Manual Linear Scan
                start = self._sweep_start_spin.value() if hasattr(self, '_sweep_start_spin') else 1.0
                stop = self._sweep_stop_spin.value() if hasattr(self, '_sweep_stop_spin') else 100.0
                step = self._sweep_step_spin.value() if hasattr(self, '_sweep_step_spin') else 1.0
                n_points = max(1, int((stop - start) / step) + 1) if step > 0 else 0
                self._schedule_summary_label.setText(
                    f"Schedule: Manual linear scan from {start:.1f} Hz to {stop:.1f} Hz (step: {step:.1f} Hz) — {n_points} points"
                )
        except Exception:
            pass

    def _apply_log_sweep_to_control_v37(self) -> None:
        """Apply the adaptive log sweep designer configuration to Control & Scan."""
        try:
            config = self._get_active_log_sweep_config_v37()
            self._set_sweep_controls_from_log_config_v37(config)
            if hasattr(self, "_scan_mode_combo"):
                self._scan_mode_combo.setCurrentText("Adaptive Logarithmic Sweep")
            else:
                self._frequency_scan_mode = "Adaptive Logarithmic Sweep"
                self._on_scan_mode_changed_v37(self._frequency_scan_mode)

            self._append_log(
                "[log-sweep] Applied configuration: "
                f"start_hz={config['start_hz']:g}, stop_hz={config['stop_hz']:g}, ppo={config['ppo']:g}"
            )
            if hasattr(self, "_tabs"):
                self._tabs.setCurrentIndex(0)
        except Exception:
            pass

    def _build_frequency_list_hz_v37(self, start_hz: float, stop_hz: float, step_hz: float) -> list[float]:
        """Enhanced frequency list builder supporting new modes."""
        import numpy as np

        scan_mode = (
            self._scan_mode_combo.currentText().strip()
            if hasattr(self, "_scan_mode_combo")
            else getattr(self, "_frequency_scan_mode", "Manual Linear Scan")
        )
        self._frequency_scan_mode = scan_mode

        if scan_mode == "Exact Impedance Spectroscopy Scan":
            return np.logspace(2, 6, 101).tolist()

        if scan_mode == "Adaptive Logarithmic Sweep":
            config = self._get_active_log_sweep_config_v37()
            start_hz = float(config.get("start_hz", start_hz))
            stop_hz = float(config.get("stop_hz", stop_hz))
            ppo = float(config.get("ppo", getattr(self, "_ppo_value", 25)))
            orders = math.log10(stop_hz) - math.log10(start_hz)
            n_points = int(orders * ppo) + 1
            return np.logspace(math.log10(start_hz), math.log10(stop_hz), n_points).tolist()

        return MainWindowV3_6._build_frequency_list_hz(start_hz, stop_hz, step_hz)

    def _run_selected_mode(self) -> None:
        """Override to support new frequency scan modes."""
        if self._runner.is_running():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Busy", "A run is already in progress.")
            return

        scan_mode = (
            self._scan_mode_combo.currentText().strip()
            if hasattr(self, "_scan_mode_combo")
            else getattr(self, "_frequency_scan_mode", "Manual Linear Scan")
        )
        self._frequency_scan_mode = scan_mode
        bias_mode = self._run_mode_combo.currentText().strip()
        values = self._resolve_sweep_values_hz(show_warnings=True)
        if values is None:
            return
        start_hz, stop_hz, step_hz, _points = values

        frequency_points_hz = self._build_frequency_list_hz_v37(start_hz, stop_hz, step_hz)
        if not frequency_points_hz:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Frequency Plan", "Sweep frequency list is empty.")
            return

        try:
            use_dc_bias, bias_plan = self._build_bias_plan_for_mode(bias_mode)
        except ValueError as exc:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid DC Bias List", str(exc))
            return

        self._reset_run_state_ui()
        self._run_active = True
        self._append_log("[run] Run started")
        self._append_log(
            f"[run] start_hz={start_hz:g}, stop_hz={stop_hz:g}, step_hz={step_hz:g}, "
            f"points={len(frequency_points_hz)}"
        )
        self._append_log(f"[run] Using scan mode: {scan_mode}")
        self._append_log(f"[run] Bias plan: {bias_plan}")

        settings = self._create_sweep_settings(frequency_points_hz, bias_plan, use_dc_bias)
        self._runner.run_sweep(self._connection_settings(), settings)

    def _preview_run_plan(self) -> None:
        """Preview run plan using the V3.7 scan mode selector and frequency builder."""
        scan_mode = (
            self._scan_mode_combo.currentText().strip()
            if hasattr(self, "_scan_mode_combo")
            else getattr(self, "_frequency_scan_mode", "Manual Linear Scan")
        )
        self._frequency_scan_mode = scan_mode
        values = self._resolve_sweep_values_hz(show_warnings=True)
        if values is None:
            return
        start_hz, stop_hz, step_hz, _points_per_sweep = values

        bias_mode = self._run_mode_combo.currentText().strip()
        frequency_points_hz = self._build_frequency_list_hz_v37(start_hz, stop_hz, step_hz)
        if not frequency_points_hz:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Frequency Plan", "Sweep frequency list is empty.")
            return

        try:
            _use_dc_bias, bias_values = self._build_bias_plan_for_mode(bias_mode)
        except ValueError as exc:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid DC Bias List", str(exc))
            return

        total_points = len(frequency_points_hz) * len(bias_values)
        self._append_log("[run-plan] -----------------------------")
        self._append_log(f"[run-plan] Bias Mode: {bias_mode}")
        self._append_log(f"[run-plan] Scan Mode: {scan_mode}")
        self._append_log(f"[run-plan] Start: {start_hz:g} Hz")
        self._append_log(f"[run-plan] Stop: {stop_hz:g} Hz")
        if scan_mode == "Manual Linear Scan":
            self._append_log(f"[run-plan] Step: {step_hz:g} Hz")
        else:
            self._append_log("[run-plan] Step: logarithmic distribution")
        self._append_log(f"[run-plan] Points per sweep: {len(frequency_points_hz)}")
        self._append_log(f"[run-plan] Estimated total points: {total_points}")
        for index, bias in enumerate(bias_values, start=1):
            self._append_log(f"[run-plan] Bias {index}: {bias:g} V")

    def _create_sweep_settings(self, frequency_points_hz, bias_plan, use_dc_bias):
        """Create sweep settings with V3.7 enhancements."""
        from services.scan_runner import SweepSettings

        settings = SweepSettings(
            sample_id=self._sample_name_input.text().strip() or "sample",
            ac_voltage_v=float(self._ac_voltage_spin.value()),
            dc_bias_v=float(bias_plan[0]),
            frequency_start_hz=frequency_points_hz[0],
            frequency_stop_hz=frequency_points_hz[-1],
            frequency_step_hz=0.0,  # Not applicable for log scans
            point_settle_delay_s=float(self._point_delay_spin.value()),
            measure_delay_s=float(self._measure_delay_s.value()),
            bias_settle_delay_s=float(self._bias_delay_spin.value()),
            use_dc_bias=use_dc_bias,
            dc_bias_list_v=bias_plan,
            frequency_points_hz=frequency_points_hz,
        )

        return settings

    # ------------------------------------------------------------------ #
    # V3.7 stylesheet                                                     #
    # ------------------------------------------------------------------ #

    def _stylesheet_v37(self) -> str:
        """V3.7 stylesheet with enhanced branding."""
        base_style = super()._stylesheet_v36()
        return base_style + """

        QLabel#headerContact {
            color: #6b7280;
            font-size: 11px;
            margin-top: 2px;
        }

        /* Enhanced logo scaling for V3.7 */
        QLabel#logoLabel {
            padding: 8px;
        }

        /* Professional scientific styling */
        QGroupBox {
            font-weight: 600;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            margin-top: 1ex;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
        }
        """

    def _get_active_log_sweep_config_v37(self) -> dict:
        """Return the active logarithmic sweep configuration used by preview and run."""
        config = dict(getattr(self, "_active_log_sweep_config", {}))
        if hasattr(self, "_log_sweep_panel"):
            try:
                config = dict(self._log_sweep_panel.get_current_config())
            except Exception:
                pass
        if not config:
            config = {
                "mode": "logarithmic_sweep",
                "start_hz": 10.0,
                "stop_hz": 1000000.0,
                "ppo": getattr(self, "_ppo_value", 25),
            }
        self._active_log_sweep_config = config
        self._ppo_value = int(float(config.get("ppo", getattr(self, "_ppo_value", 25))))
        return config

    def _set_sweep_controls_from_log_config_v37(self, config: dict) -> None:
        """Reflect logarithmic sweep bounds in Control & Scan so the active plan is visible."""
        def to_display(value_hz: float) -> tuple[float, str]:
            if value_hz >= 1_000_000:
                return value_hz / 1_000_000.0, "MHz"
            if value_hz >= 1_000:
                return value_hz / 1_000.0, "kHz"
            return value_hz, "Hz"

        try:
            start_value, start_unit = to_display(float(config.get("start_hz", 10.0)))
            stop_value, stop_unit = to_display(float(config.get("stop_hz", 1000000.0)))
            if hasattr(self, "_sweep_start_spin"):
                self._sweep_start_spin.setValue(start_value)
            if hasattr(self, "_sweep_start_unit_combo"):
                self._sweep_start_unit_combo.setCurrentText(start_unit)
            if hasattr(self, "_sweep_stop_spin"):
                self._sweep_stop_spin.setValue(stop_value)
            if hasattr(self, "_sweep_stop_unit_combo"):
                self._sweep_stop_unit_combo.setCurrentText(stop_unit)
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # Sync methods                                                       #
    # ------------------------------------------------------------------ #

    def _sync_log_sweep_output_dir(self) -> None:
        """Keep log sweep designer output dir in sync with Sample & Output folder."""
        try:
            if hasattr(self, '_log_sweep_panel'):
                folder = (
                    Path(self._output_folder_input.text().strip())
                    if hasattr(self, "_output_folder_input") and self._output_folder_input.text().strip()
                    else Path.cwd() / "exports_v3"
                )
                self._log_sweep_panel.set_output_dir(folder)
        except Exception:
            pass
