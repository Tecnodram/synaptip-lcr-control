"""
main_window_v3_5.py — SynAptIp Nyquist Analyzer V3.5 Main Window
SynAptIp Technologies

Extends MainWindowV3 (src_v3) by adding the "Analysis & Insights" tab.

Strategy:
  - Subclass MainWindowV3 from src_v3 (available via sys.path)
  - Override _build_ui() so the overridden version runs on super().__init__()
  - All existing V3 tabs and logic remain completely untouched
  - New UI components live in ui_v35/ — no namespace collision with V3's ui/
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

# V3 base window (from src_v3, resolved via sys.path in entry point)
from ui.main_window_v3 import MainWindowV3

# V3.5-specific panel (from src_v3_5/ui_v35/)
from ui_v35.analysis_insights_panel import AnalysisInsightsPanel


APP_VERSION_V35 = "3.5.0"


def _app_base_dir() -> Path:
    import sys

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


class MainWindowV3_5(MainWindowV3):
    """
    V3.5 main window.

    Identical to V3 except:
      1. Window title / header badge show V3.5
      2. An "Analysis & Insights" tab is appended after the V3 tabs
      3. The new tab output dir is kept in sync with the Sample & Output folder
    """

    def __init__(self) -> None:
        # super().__init__() calls self._build_ui() which resolves to the
        # overridden version in this subclass via Python MRO.
        super().__init__()
        self.setWindowTitle("SynAptIp Nyquist Analyzer V3.5")
        self._output_folder_input.setText(str(_app_base_dir() / "exports_v3"))
        self._sync_analysis_output_dir()

    # ------------------------------------------------------------------ #
    # Override _build_ui to inject the Analysis & Insights tab            #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        """Replicate V3 layout and append the new Analysis & Insights tab."""
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(14)

        root.addWidget(self._build_header_v35())

        self._tabs = QTabWidget()
        # All existing V3 tab builders (inherited unchanged)
        self._tabs.addTab(self._build_control_scan_tab(),     "Control & Scan")
        self._tabs.addTab(self._build_live_results_tab(),     "Live Results")
        self._tabs.addTab(self._build_sample_output_tab(),    "Sample & Output")
        self._tabs.addTab(self._build_nyquist_compare_tab(),  "Nyquist Compare")
        self._tabs.addTab(self._build_nyquist_analysis_tab(), "Nyquist Analysis (V3)")
        self._tabs.addTab(self._build_diagnostics_tab(),      "Diagnostics & Commands")

        # --- V3.5 new tab ---
        self._analysis_panel = AnalysisInsightsPanel()
        self._tabs.addTab(self._analysis_panel, "Analysis & Insights")

        self._tabs.setDocumentMode(True)
        self._tabs.setCurrentIndex(0)

        root.addWidget(self._tabs, stretch=1)
        self.setCentralWidget(central)
        self.setStyleSheet(self._stylesheet_v35())

    # ------------------------------------------------------------------ #
    # V3.5 header                                                          #
    # ------------------------------------------------------------------ #

    def _build_header_v35(self) -> QWidget:
        """Patch the V3 header to show V3.5 version info."""
        header_card = super()._build_header()
        try:
            from PySide6.QtWidgets import QLabel
            badge = header_card.findChild(QLabel, "versionBadge")
            if badge:
                badge.setText(f"Version {APP_VERSION_V35}")
            title_lbl = header_card.findChild(QLabel, "headerTitle")
            if title_lbl:
                title_lbl.setText("SynAptIp Nyquist Analyzer V3.5")
            subtitle_lbl = header_card.findChild(QLabel, "headerSubtitle")
            if subtitle_lbl:
                subtitle_lbl.setText(
                    "Scientific Software, Instrument Control & Advanced EIS Analysis"
                )
        except Exception:
            pass  # cosmetic only — fail gracefully
        return header_card

    # ------------------------------------------------------------------ #
    # V3.5 stylesheet (V3 base + new widget styles)                       #
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
            QPushButton#runBtn:hover  { background: #1e40af; }
            QPushButton#runBtn:disabled { background: #94a3b8; }
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
        try:
            folder = self._output_folder_input.text().strip()
            base = Path(folder) if folder else _app_base_dir()
            self._analysis_panel.set_output_dir(base / "analysis")
        except Exception:
            pass

    def _browse_output_folder(self) -> None:
        super()._browse_output_folder()
        self._sync_analysis_output_dir()
