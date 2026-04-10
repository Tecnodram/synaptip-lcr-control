"""
main_window_v3_6.py — SynAptIp Nyquist Analyzer V3.6 Main Window
SynAptIp Technologies

Extends MainWindowV3_5 by adding the "Comparar" tab.

Strategy (identical to V3.5 approach):
  - Subclass MainWindowV3_5 via Python MRO
  - Override _build_ui() to inject the new tab
  - All existing tabs remain completely untouched
  - New components live in ui_v36/ — no namespace collision
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

# V3.5 base window (resolved via sys.path)
from ui_v35.main_window_v3_5 import MainWindowV3_5

# V3.6 panels (from src_v3_6/ui_v36/)
from ui_v36.compare_panel import ComparePanel


APP_VERSION_V36 = "3.6.0"


def _app_base_dir() -> Path:
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


class MainWindowV3_6(MainWindowV3_5):
    """
    V3.6 main window.

    Identical to V3.5 except:
      1. Window title / header badge show V3.6
      2. A "Comparar" tab is appended after all V3.5 tabs
      3. The compare output dir is kept in sync with Sample & Output folder
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SynAptIp Nyquist Analyzer V3.6")
        self._sync_compare_output_dir()

    # ------------------------------------------------------------------ #
    # Override _build_ui to inject the Comparar tab                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        """Replicate V3.5 layout and append the new Comparar tab."""
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(14)

        root.addWidget(self._build_header_v36())

        self._tabs = QTabWidget()

        # --- All V3 tabs (from MainWindowV3, unchanged) ---
        self._tabs.addTab(self._build_control_scan_tab(),     "Control & Scan")
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

        # --- V3.6 new tab ---
        self._compare_panel = ComparePanel()
        self._tabs.addTab(self._compare_panel, "Compare")

        self._tabs.setDocumentMode(True)
        self._tabs.setCurrentIndex(0)

        root.addWidget(self._tabs, stretch=1)
        self.setCentralWidget(central)
        self.setStyleSheet(self._stylesheet_v36())

    # ------------------------------------------------------------------ #
    # V3.6 header                                                          #
    # ------------------------------------------------------------------ #

    def _build_header_v36(self) -> QWidget:
        """Patch header to show V3.6 info."""
        header_card = super()._build_header()
        try:
            from PySide6.QtWidgets import QLabel
            badge = header_card.findChild(QLabel, "versionBadge")
            if badge:
                badge.setText(f"Version {APP_VERSION_V36}")
            title_lbl = header_card.findChild(QLabel, "headerTitle")
            if title_lbl:
                title_lbl.setText("SynAptIp Nyquist Analyzer V3.6")
            subtitle_lbl = header_card.findChild(QLabel, "headerSubtitle")
            if subtitle_lbl:
                subtitle_lbl.setText(
                    "Scientific Software, Instrument Control, Advanced EIS & Multi-File Comparison"
                )
        except Exception:
            pass
        return header_card

    # ------------------------------------------------------------------ #
    # V3.6 stylesheet                                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _stylesheet_v36() -> str:
        from ui_v35.main_window_v3_5 import MainWindowV3_5
        base = MainWindowV3_5._stylesheet_v35()
        additions = """
            QLabel#comparePanelTitle {
                font-size: 12pt;
                font-weight: 700;
                color: #0f172a;
                padding-bottom: 4px;
            }
            QLabel#compareSelectorLabel {
                font-size: 9pt;
                font-weight: 600;
                color: #374151;
            }
            QComboBox#comparePlotSelector {
                font-size: 9pt;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                padding: 4px 8px;
                background: #ffffff;
                color: #0f172a;
            }
            QComboBox#comparePlotSelector:hover {
                border-color: #1d4ed8;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 9pt;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                color: #374151;
            }
            QLabel#slotPathLabel {
                font-size: 8.5pt;
                color: #374151;
            }
            QPushButton#slotBrowseBtn {
                background: #1d4ed8;
                color: #fff;
                border: none;
                border-radius: 5px;
                padding: 4px 8px;
                font-weight: 600;
            }
            QPushButton#slotBrowseBtn:hover { background: #1e40af; }
            QPushButton#slotClearBtn {
                background: transparent;
                color: #64748b;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                padding: 4px 8px;
            }
            QPushButton#slotClearBtn:hover { background: #f1f5f9; }
            QPushButton#comparePlotBtn {
                background: #059669;
                color: #fff;
                border: none;
                border-radius: 6px;
                padding: 6px 20px;
                font-weight: 700;
            }
            QPushButton#comparePlotBtn:hover { background: #047857; }
            QPushButton#compareClearBtn {
                background: transparent;
                color: #64748b;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 6px 16px;
            }
            QPushButton#compareClearBtn:hover { background: #f1f5f9; }
            QPushButton#compareExportBtn {
                background: #7c3aed;
                color: #fff;
                border: none;
                border-radius: 6px;
                padding: 6px 18px;
                font-weight: 700;
            }
            QPushButton#compareExportBtn:hover { background: #6d28d9; }
            QPushButton#compareExportBtn:disabled { background: #94a3b8; }
            QLabel#comparePlotArea {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                color: #94a3b8;
                font-size: 9pt;
            }
            QTextEdit#compareLog {
                background: #0b1220;
                color: #d7e3ff;
                border-radius: 6px;
                font-family: Consolas;
                font-size: 8.5pt;
            }
        """
        return base + additions

    # ------------------------------------------------------------------ #
    # Output folder sync                                                    #
    # ------------------------------------------------------------------ #

    def _sync_compare_output_dir(self) -> None:
        try:
            folder = self._output_folder_input.text().strip()
            base   = Path(folder) if folder else _app_base_dir()
            self._compare_panel.set_output_dir(base / "compare")
        except Exception:
            pass

    def _browse_output_folder(self) -> None:
        super()._browse_output_folder()
        self._sync_compare_output_dir()
