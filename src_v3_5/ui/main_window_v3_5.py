"""
main_window_v3_5.py — SynAptIp Nyquist Analyzer V3.5 Main Window
SynAptIp Technologies

Extends MainWindowV3 (src_v3) by adding the "Analysis & Insights" tab.

Strategy:
  - Subclass MainWindowV3 from src_v3
  - Override _build_ui() to inject the new tab (MRO ensures this override
    is called during super().__init__())
  - All existing V3 tabs and logic remain completely untouched
  - The Analysis & Insights panel is isolated in its own widget
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

# Import the V3 base window (src_v3 must be on sys.path before this import)
from ui.main_window_v3 import MainWindowV3

# Import the new panel
from ui.analysis_insights_panel import AnalysisInsightsPanel


APP_VERSION_V35 = "3.5.0"


class MainWindowV3_5(MainWindowV3):
    """
    V3.5 main window.

    Identical to V3 except:
      1. Window title / header badge show "V3.5"
      2. An "Analysis & Insights" tab is appended to the existing tab bar
      3. The new tab output dir is kept in sync with the Sample & Output folder
    """

    def __init__(self) -> None:
        # super().__init__() calls self._build_ui() which resolves to the
        # overridden version in this subclass (Python MRO).
        super().__init__()
        self.setWindowTitle("SynAptIp Nyquist Analyzer V3.5")
        # Sync output folder once the UI is fully built
        self._sync_analysis_output_dir()

    # ------------------------------------------------------------------ #
    # Override _build_ui to inject the Analysis & Insights tab            #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        """Override: replicate V3 layout and add the Analysis & Insights tab."""
        from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow
        from PySide6.QtCore import Qt

        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(14)

        root.addWidget(self._build_header_v35())

        self._tabs = QTabWidget()
        # All existing V3 tabs — methods are inherited unchanged
        self._tabs.addTab(self._build_control_scan_tab(),      "Control & Scan")
        self._tabs.addTab(self._build_live_results_tab(),      "Live Results")
        self._tabs.addTab(self._build_sample_output_tab(),     "Sample & Output")
        self._tabs.addTab(self._build_nyquist_compare_tab(),   "Nyquist Compare")
        self._tabs.addTab(self._build_nyquist_analysis_tab(),  "Nyquist Analysis (V3)")
        self._tabs.addTab(self._build_diagnostics_tab(),       "Diagnostics & Commands")

        # ---- NEW tab ----
        self._analysis_panel = AnalysisInsightsPanel()
        self._tabs.addTab(self._analysis_panel, "Analysis & Insights")

        self._tabs.setDocumentMode(True)
        self._tabs.setCurrentIndex(0)

        root.addWidget(self._tabs, stretch=1)
        self.setCentralWidget(central)
        self.setStyleSheet(self._stylesheet_v35())

    # ------------------------------------------------------------------ #
    # V3.5 header (updated version badge / title)                         #
    # ------------------------------------------------------------------ #

    def _build_header_v35(self) -> QWidget:
        """Header variant that shows the V3.5 version badge."""
        header_card = super()._build_header()

        # Patch the version badge text to show V3.5
        try:
            from PySide6.QtWidgets import QLabel
            badge = header_card.findChild(QLabel, "versionBadge")
            if badge:
                badge.setText("Version 3.5")

            title_lbl = header_card.findChild(QLabel, "headerTitle")
            if title_lbl:
                title_lbl.setText("SynAptIp Nyquist Analyzer V3.5")

            subtitle_lbl = header_card.findChild(QLabel, "headerSubtitle")
            if subtitle_lbl:
                subtitle_lbl.setText(
                    "Scientific Software, Instrument Control & Advanced EIS Analysis"
                )
        except Exception:
            pass  # fail-safe — cosmetic only

        return header_card

    # ------------------------------------------------------------------ #
    # V3.5 stylesheet (extends V3 with new widget styles)                 #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _stylesheet_v35() -> str:
        base = MainWindowV3._stylesheet()
        additions = """
            QPushButton#runBtn {
                background: #1d4ed8;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 20px;
                font-weight: 700;
            }
            QPushButton#runBtn:hover {
                background: #1e40af;
            }
            QPushButton#runBtn:disabled {
                background: #94a3b8;
            }
            QTextEdit#analysisLog {
                background-color: #0b1220;
                color: #d7e3ff;
                border-radius: 6px;
                font-family: Consolas;
                font-size: 9.5pt;
            }
            QLabel#schemaInfo {
                color: #374151;
                font-size: 9pt;
                padding: 2px 4px;
            }
        """
        return base + additions

    # ------------------------------------------------------------------ #
    # Output folder sync                                                   #
    # ------------------------------------------------------------------ #

    def _sync_analysis_output_dir(self) -> None:
        """Keep the analysis panel in sync with the Sample & Output folder."""
        try:
            folder = self._output_folder_input.text().strip()
            if folder:
                self._analysis_panel.set_output_dir(Path(folder) / "analysis")
            else:
                self._analysis_panel.set_output_dir(Path.cwd() / "analysis_outputs")
        except Exception:
            pass  # non-critical

    def _browse_output_folder(self) -> None:
        """Override to also update analysis panel when output folder changes."""
        super()._browse_output_folder()
        self._sync_analysis_output_dir()
