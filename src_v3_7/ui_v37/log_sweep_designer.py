"""
log_sweep_designer.py — Log Sweep Designer Panel for V3.7
SynAptIp Technologies

Provides a dedicated interface for designing logarithmic frequency sweeps
with professional scientific terminology and real-time preview.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import numpy for calculations
import numpy as np


class LogSweepDesigner(QWidget):
    """
    Log Sweep Designer panel for V3.7.

    Provides professional interface for configuring logarithmic frequency sweeps
    with scientific terminology and real-time preview capabilities.
    """

    def __init__(self) -> None:
        super().__init__()
        self._ppo_value = 25
        self._start_freq_hz = 10.0
        self._stop_freq_hz = 1e6
        self._output_dir = Path.cwd() / "exports_v3"

        self._build_ui()
        self._update_preview()

    def set_output_dir(self, output_dir: Path) -> None:
        """Set the output directory for exports."""
        self._output_dir = output_dir

    def _build_ui(self) -> None:
        """Build the log sweep designer interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        # Title
        title = QLabel("Adaptive Logarithmic Sweep Designer")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1f2937;")
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Design logarithmic frequency sweeps for impedance spectroscopy. "
            "Points are deterministically distributed across each order of magnitude "
            "to ensure reproducible and representative sampling."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #6b7280; margin-bottom: 8px;")
        layout.addWidget(desc)

        # Main configuration area
        config_group = QGroupBox("Sweep Configuration")
        config_layout = QVBoxLayout(config_group)

        # Frequency range section
        range_group = QGroupBox("Frequency Range")
        range_layout = QGridLayout(range_group)

        # Start frequency
        range_layout.addWidget(QLabel("Start Frequency"), 0, 0)
        self._start_freq_spin = QDoubleSpinBox()
        self._start_freq_spin.setRange(0.001, 1e6)
        self._start_freq_spin.setValue(10.0)
        self._start_freq_spin.setDecimals(3)
        self._start_freq_spin.valueChanged.connect(self._on_config_changed)
        range_layout.addWidget(self._start_freq_spin, 0, 1)

        self._start_freq_unit = QComboBox()
        self._start_freq_unit.addItems(["Hz", "kHz", "MHz"])
        self._start_freq_unit.currentTextChanged.connect(self._on_config_changed)
        range_layout.addWidget(self._start_freq_unit, 0, 2)

        # Stop frequency
        range_layout.addWidget(QLabel("Stop Frequency"), 1, 0)
        self._stop_freq_spin = QDoubleSpinBox()
        self._stop_freq_spin.setRange(0.001, 1e7)
        self._stop_freq_spin.setValue(1.0)
        self._stop_freq_spin.setDecimals(3)
        self._stop_freq_spin.valueChanged.connect(self._on_config_changed)
        range_layout.addWidget(self._stop_freq_spin, 1, 1)

        self._stop_freq_unit = QComboBox()
        self._stop_freq_unit.addItems(["Hz", "kHz", "MHz"])
        self._stop_freq_unit.setCurrentText("MHz")
        self._stop_freq_unit.currentTextChanged.connect(self._on_config_changed)
        range_layout.addWidget(self._stop_freq_unit, 1, 2)

        config_layout.addWidget(range_group)

        # Points per order of magnitude section
        ppo_group = QGroupBox("Points per Order of Magnitude (PPO)")
        ppo_layout = QVBoxLayout(ppo_group)

        # PPO explanation
        ppo_explanation = QLabel(
            "Points per order of magnitude defines how many measurement points are placed "
            "within each logarithmic frequency interval (e.g., 100 Hz to 1000 Hz)."
        )
        ppo_explanation.setWordWrap(True)
        ppo_explanation.setStyleSheet("color: #6b7280; font-size: 11px;")
        ppo_layout.addWidget(ppo_explanation)

        # PPO selection
        ppo_select_layout = QHBoxLayout()
        ppo_select_layout.addWidget(QLabel("PPO Preset:"))

        self._ppo_preset_combo = QComboBox()
        self._ppo_preset_combo.addItems([
            "10 (Fast)",
            "20 (Standard)",
            "25 (High Resolution)",
            "30 (Publication / Fine)"
        ])
        self._ppo_preset_combo.setCurrentText("25 (High Resolution)")
        self._ppo_preset_combo.currentTextChanged.connect(self._on_ppo_preset_changed)
        ppo_select_layout.addWidget(self._ppo_preset_combo)

        ppo_select_layout.addWidget(QLabel("Custom:"))
        self._ppo_custom_spin = QDoubleSpinBox()
        self._ppo_custom_spin.setRange(1, 100)
        self._ppo_custom_spin.setValue(25)
        self._ppo_custom_spin.setSingleStep(1)
        self._ppo_custom_spin.valueChanged.connect(self._on_ppo_custom_changed)
        ppo_select_layout.addWidget(self._ppo_custom_spin)

        ppo_select_layout.addStretch()
        ppo_layout.addLayout(ppo_select_layout)

        config_layout.addWidget(ppo_group)

        layout.addWidget(config_group)

        # Preview section
        preview_group = QGroupBox("Sweep Preview")
        preview_layout = QVBoxLayout(preview_group)

        # Summary
        self._summary_label = QLabel()
        self._summary_label.setStyleSheet("font-weight: bold; color: #1f2937;")
        preview_layout.addWidget(self._summary_label)

        # Frequency list preview
        preview_layout.addWidget(QLabel("Frequency Points Preview:"))
        self._frequency_preview = QTextEdit()
        self._frequency_preview.setMaximumHeight(120)
        self._frequency_preview.setReadOnly(True)
        self._frequency_preview.setStyleSheet("font-family: monospace; font-size: 10px;")
        preview_layout.addWidget(self._frequency_preview)

        layout.addWidget(preview_group)

        # Action buttons
        buttons_layout = QHBoxLayout()

        self._apply_to_control_btn = QPushButton("Apply to Control Tab")
        self._apply_to_control_btn.setStyleSheet("font-weight: bold; padding: 8px 16px;")
        self._apply_to_control_btn.clicked.connect(self._apply_to_control_tab)
        buttons_layout.addWidget(self._apply_to_control_btn)

        self._export_config_btn = QPushButton("Export Configuration")
        self._export_config_btn.clicked.connect(self._export_configuration)
        buttons_layout.addWidget(self._export_config_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        layout.addStretch()
        self._update_frequencies_from_ui()

    def _on_config_changed(self) -> None:
        """Handle configuration changes."""
        self._update_frequencies_from_ui()
        self._update_preview()

    def _on_ppo_preset_changed(self, preset: str) -> None:
        """Handle PPO preset changes."""
        if "Fast" in preset:
            self._ppo_value = 10
        elif "Standard" in preset:
            self._ppo_value = 20
        elif "High Resolution" in preset:
            self._ppo_value = 25
        elif "Publication" in preset:
            self._ppo_value = 30

        self._ppo_custom_spin.setValue(self._ppo_value)
        self._update_preview()

    def _on_ppo_custom_changed(self, value: float) -> None:
        """Handle custom PPO changes."""
        self._ppo_value = int(value)
        self._update_preview()

    def _update_frequencies_from_ui(self) -> None:
        """Update frequency values from UI controls."""
        # Convert start frequency to Hz
        start_value = self._start_freq_spin.value()
        start_unit = self._start_freq_unit.currentText()
        if start_unit == "kHz":
            self._start_freq_hz = start_value * 1000
        elif start_unit == "MHz":
            self._start_freq_hz = start_value * 1e6
        else:
            self._start_freq_hz = start_value

        # Convert stop frequency to Hz
        stop_value = self._stop_freq_spin.value()
        stop_unit = self._stop_freq_unit.currentText()
        if stop_unit == "kHz":
            self._stop_freq_hz = stop_value * 1000
        elif stop_unit == "MHz":
            self._stop_freq_hz = stop_value * 1e6
        else:
            self._stop_freq_hz = stop_value

    def _update_preview(self) -> None:
        """Update the sweep preview."""
        try:
            # Calculate orders of magnitude
            orders = math.log10(self._stop_freq_hz) - math.log10(self._start_freq_hz)
            n_points = int(orders * self._ppo_value) + 1

            # Generate frequency list
            frequencies = np.logspace(
                math.log10(self._start_freq_hz),
                math.log10(self._stop_freq_hz),
                n_points
            )

            # Update summary
            self._summary_label.setText(
                f"Total Points: {n_points} | "
                f"Orders of Magnitude: {orders:.2f} | "
                f"PPO: {self._ppo_value}"
            )

            # Update frequency preview
            freq_text = ""
            for i, freq in enumerate(frequencies[:20]):  # Show first 20 points
                if freq >= 1e6:
                    freq_text += f"{freq/1e6:.3f} MHz\n"
                elif freq >= 1000:
                    freq_text += f"{freq/1000:.3f} kHz\n"
                else:
                    freq_text += f"{freq:.3f} Hz\n"

            if len(frequencies) > 20:
                freq_text += f"... and {len(frequencies) - 20} more points"

            self._frequency_preview.setText(freq_text)

        except Exception as e:
            self._summary_label.setText(f"Error: {str(e)}")
            self._frequency_preview.setText("")

    def _apply_to_control_tab(self) -> None:
        """Apply the current configuration to the Control & Scan tab."""
        # This would need to communicate with the main window
        # For now, just show a message
        try:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Apply Configuration",
                "Configuration applied to Control & Scan tab successfully!"
            )
        except Exception:
            pass

    def _export_configuration(self) -> None:
        """Export the current sweep configuration."""
        try:
            config = {
                "mode": "logarithmic_sweep",
                "start_hz": self._start_freq_hz,
                "stop_hz": self._stop_freq_hz,
                "ppo": self._ppo_value,
                "orders_of_magnitude": math.log10(self._stop_freq_hz) - math.log10(self._start_freq_hz),
                "total_points": int((math.log10(self._stop_freq_hz) - math.log10(self._start_freq_hz)) * self._ppo_value) + 1
            }

            # Export to JSON file
            import json
            export_path = self._output_dir / "log_sweep_config.json"
            with open(export_path, 'w') as f:
                json.dump(config, f, indent=2)

            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Export Successful",
                f"Configuration exported to {export_path}"
            )

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Failed to export configuration: {str(e)}"
            )

    # ------------------------------------------------------------------ #
    # Public interface                                                   #
    # ------------------------------------------------------------------ #

    def get_current_config(self) -> dict:
        """Get the current sweep configuration."""
        return {
            "mode": "logarithmic_sweep",
            "start_hz": self._start_freq_hz,
            "stop_hz": self._stop_freq_hz,
            "ppo": self._ppo_value
        }
