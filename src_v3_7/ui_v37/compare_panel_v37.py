"""
compare_panel_v37.py — Enhanced Compare Tab — SynAptIp V3.7
SynAptIp Technologies

Enhanced version of the V3.6 compare panel with publication-grade visualization.

Upgrades:
- Publication-grade Nyquist plots with frequency progression
- Professional Bode plots with proper scaling
- High-DPI export (PNG 300dpi, PDF vector)
- Scientific color schemes and typography
- Enhanced export system with multiple formats

Maintains full backward compatibility with V3.6 data structures.
"""
from __future__ import annotations

import io
import traceback
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Import V3.7 publication-grade plotting utilities
from services_v37.publication_plot_utils import (
    plot_nyquist_publication,
    plot_bode_magnitude_publication,
    plot_bode_phase_publication,
    export_figure_publication,
    export_figure_bytes,
    get_scientific_color,
    FIG_SIZE_COMPARISON,
    DPI_EXPORT_PNG,
)

# Import V3.6 compare panel for base functionality
from ui_v36.compare_panel import ComparePanel

# Import analysis engine constants
from analysis_engine.eis_transformer import (
    COL_FREQ,
    COL_Z_REAL,
    COL_Z_IMAG,
    COL_MZ_IMG,
    COL_Z_MAG,
    COL_THETA,
)


class ComparePanelV37(ComparePanel):
    """
    Enhanced compare panel with publication-grade visualization.

    Extends V3.6 ComparePanel with:
    - Publication-grade plotting using scientific formatting
    - Frequency progression indication in Nyquist plots
    - Professional export system (PNG 300dpi, PDF)
    - Enhanced color schemes and typography
    - High-DPI rendering for scientific publications
    """

    def __init__(self) -> None:
        super().__init__()
        self._export_format = "png"  # Default export format

    def _build_export_controls(self) -> QWidget:
        """Enhanced export controls with format selection and publication options."""
        controls = QWidget()
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(0, 0, 0, 0)

        # Export format selector
        layout.addWidget(QLabel("Format:"))
        self._export_format_combo = QComboBox()
        self._export_format_combo.addItems(["PNG (300 DPI)", "PDF (Vector)"])
        self._export_format_combo.currentTextChanged.connect(self._on_export_format_changed)
        layout.addWidget(self._export_format_combo)

        # Export button
        self._export_btn = QPushButton("Export All Plots")
        self._export_btn.clicked.connect(self._export_all_plots_publication)
        layout.addWidget(self._export_btn)

        layout.addStretch()
        return controls

    def _on_export_format_changed(self, format_text: str) -> None:
        """Update export format based on combo box selection."""
        if "PDF" in format_text:
            self._export_format = "pdf"
        else:
            self._export_format = "png"

    def _export_all_plots_publication(self) -> None:
        """Export all plots in publication-ready format."""
        if not hasattr(self, '_datasets') or not self._datasets:
            self._show_status("No data to export")
            return

        # Select output directory
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Export Directory"
        )
        if not output_dir:
            return

        output_path = Path(output_dir)
        exported_files = []

        try:
            # Export Nyquist plot
            png_data, _ = self._plot_nyquist_publication()
            if png_data:
                filename = f"nyquist_comparison_publication.{self._export_format}"
                filepath = output_path / filename
                with open(filepath, 'wb') as f:
                    f.write(png_data)
                exported_files.append(filename)

            # Export Bode magnitude
            png_data, _ = self._plot_bode_mag_publication()
            if png_data:
                filename = f"bode_magnitude_publication.{self._export_format}"
                filepath = output_path / filename
                with open(filepath, 'wb') as f:
                    f.write(png_data)
                exported_files.append(filename)

            # Export Bode phase
            png_data, _ = self._plot_bode_phase_publication()
            if png_data:
                filename = f"bode_phase_publication.{self._export_format}"
                filepath = output_path / filename
                with open(filepath, 'wb') as f:
                    f.write(png_data)
                exported_files.append(filename)

            if exported_files:
                self._show_status(f"Exported {len(exported_files)} plots: {', '.join(exported_files)}")
            else:
                self._show_status("No plots were generated")

        except Exception as e:
            self._show_status(f"Export failed: {str(e)}")

    # ------------------------------------------------------------------------------
    # PUBLICATION-GRADE PLOTTING METHODS
    # ------------------------------------------------------------------------------
    def _plot_nyquist_publication(self) -> tuple[bytes, str]:
        """Generate publication-grade Nyquist plot with frequency progression."""
        datasets = self._get_datasets_for_plotting()
        if not datasets:
            return b"", "No data available"

        fig, ax = plt.subplots(figsize=FIG_SIZE_COMPARISON, dpi=DPI_EXPORT_PNG)
        log_lines = []

        for i, (label, df) in enumerate(datasets):
            if not self._has_col(df, COL_Z_REAL) or not self._has_col(df, COL_MZ_IMG):
                log_lines.append(f"[SKIP] {label} — no Z_real / −Z_imag columns")
                continue

            # Extract data
            z_real = df[COL_Z_REAL].values
            z_imag_neg = df[COL_MZ_IMG].values
            frequencies = df[COL_FREQ].values if self._has_col(df, COL_FREQ) else None

            # Use scientific color
            color = get_scientific_color(i)

            # Plot with publication styling
            fig, ax = plot_nyquist_publication(
                z_real, z_imag_neg, frequencies,
                fig=fig, ax=ax,
                label=label,
                color=color,
                show_frequency_progression=True,
                marker_every=15  # Show markers every 15 points
            )

            log_lines.append(f"[OK] {label} — {len(z_real)} points")

        if not any("[OK]" in line for line in log_lines):
            ax.text(0.5, 0.5, "No data available", transform=ax.transAxes,
                    ha="center", va="center", fontsize=12)
        else:
            ax.set_title("Nyquist Plot Comparison", fontweight="bold")

        # Export to bytes
        plot_bytes = export_figure_bytes(fig, format=self._export_format)
        plt.close(fig)

        return plot_bytes, "\n".join(log_lines)

    def _plot_bode_mag_publication(self) -> tuple[bytes, str]:
        """Generate publication-grade Bode magnitude plot."""
        datasets = self._get_datasets_for_plotting()
        if not datasets:
            return b"", "No data available"

        fig, ax = plt.subplots(figsize=FIG_SIZE_COMPARISON, dpi=DPI_EXPORT_PNG)
        log_lines = []

        for i, (label, df) in enumerate(datasets):
            if not self._has_col(df, COL_Z_MAG) or not self._has_col(df, COL_FREQ):
                log_lines.append(f"[SKIP] {label} — no |Z| / frequency columns")
                continue

            # Extract and sort data by frequency
            freq = df[COL_FREQ].values
            mag = df[COL_Z_MAG].values
            sort_idx = np.argsort(freq)

            color = get_scientific_color(i)

            fig, ax = plot_bode_magnitude_publication(
                freq[sort_idx], mag[sort_idx],
                fig=fig, ax=ax,
                label=label,
                color=color
            )

            log_lines.append(f"[OK] {label} — {len(freq)} points")

        if not any("[OK]" in line for line in log_lines):
            ax.text(0.5, 0.5, "No data available", transform=ax.transAxes,
                    ha="center", va="center", fontsize=12)
        else:
            ax.set_title("Bode Plot — |Z| Magnitude", fontweight="bold")

        plot_bytes = export_figure_bytes(fig, format=self._export_format)
        plt.close(fig)

        return plot_bytes, "\n".join(log_lines)

    def _plot_bode_phase_publication(self) -> tuple[bytes, str]:
        """Generate publication-grade Bode phase plot."""
        datasets = self._get_datasets_for_plotting()
        if not datasets:
            return b"", "No data available"

        fig, ax = plt.subplots(figsize=FIG_SIZE_COMPARISON, dpi=DPI_EXPORT_PNG)
        log_lines = []

        for i, (label, df) in enumerate(datasets):
            if not self._has_col(df, COL_THETA) or not self._has_col(df, COL_FREQ):
                log_lines.append(f"[SKIP] {label} — no phase / frequency columns")
                continue

            # Extract and sort data by frequency
            freq = df[COL_FREQ].values
            phase = df[COL_THETA].values
            sort_idx = np.argsort(freq)

            color = get_scientific_color(i)

            fig, ax = plot_bode_phase_publication(
                freq[sort_idx], phase[sort_idx],
                fig=fig, ax=ax,
                label=label,
                color=color
            )

            log_lines.append(f"[OK] {label} — {len(freq)} points")

        if not any("[OK]" in line for line in log_lines):
            ax.text(0.5, 0.5, "No data available", transform=ax.transAxes,
                    ha="center", va="center", fontsize=12)
        else:
            ax.set_title("Bode Plot — Phase", fontweight="bold")

        plot_bytes = export_figure_bytes(fig, format=self._export_format)
        plt.close(fig)

        return plot_bytes, "\n".join(log_lines)

    # ------------------------------------------------------------------------------
    # OVERRIDE BASE METHODS TO USE PUBLICATION PLOTTING
    # ------------------------------------------------------------------------------
    def _plot_nyquist(self, datasets, output_dir) -> tuple[bytes, str]:
        """Override to use publication-grade Nyquist plotting."""
        png, lines = self._plot_nyquist_publication()
        if output_dir and png:
            try:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = f"nyquist_compare_publication.{self._export_format}"
                (output_dir / filename).write_bytes(png)
            except Exception:
                pass
        return png, "\n".join(lines)

    def _plot_bode_mag(self, datasets, output_dir) -> tuple[bytes, str]:
        """Override to use publication-grade Bode magnitude plotting."""
        png, lines = self._plot_bode_mag_publication()
        if output_dir and png:
            try:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = f"bode_mag_compare_publication.{self._export_format}"
                (output_dir / filename).write_bytes(png)
            except Exception:
                pass
        return png, "\n".join(lines)

    def _plot_bode_phase(self, datasets, output_dir) -> tuple[bytes, str]:
        """Override to use publication-grade Bode phase plotting."""
        png, lines = self._plot_bode_phase_publication()
        if output_dir and png:
            try:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = f"bode_phase_compare_publication.{self._export_format}"
                (output_dir / filename).write_bytes(png)
            except Exception:
                pass
        return png, "\n".join(lines)

    # ------------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------------
    def _get_datasets_for_plotting(self) -> list[tuple[str, pd.DataFrame]]:
        """Get datasets ready for plotting."""
        if not hasattr(self, '_datasets'):
            return []

        datasets = []
        for slot_idx, dataset in enumerate(self._datasets):
            if dataset and self._has_data(dataset.df):
                label = self._file_label(slot_idx, dataset.path)
                datasets.append((label, dataset.df))

        return datasets

    def _has_data(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame has valid data."""
        return df is not None and not df.empty

    def _show_status(self, message: str) -> None:
        """Show status message to user."""
        # This would connect to the UI status display
        print(f"Status: {message}")

    # Inherit other methods from base ComparePanel class