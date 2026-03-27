"""
analysis_insights_panel.py — Analysis & Insights Tab Panel
SynAptIp Nyquist Analyzer V3.5
SynAptIp Technologies

Self-contained QWidget for the "Analysis & Insights" tab.
Provides:
  - CSV file input with auto-detection of column schema and DC bias
  - Checklist of plots / outputs to generate
  - Output folder selection
  - Run Analysis button
  - Scrollable progress/log area
  - Graceful error handling — never crashes the main window
"""
from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


# ---------------------------------------------------------------------------
# Analysis checkbox definitions (id, display label)
# ---------------------------------------------------------------------------
ANALYSIS_ITEMS: list[tuple[str, str]] = [
    # Nyquist
    ("nyquist_clean_comparative",       "Nyquist — Clean comparative"),
    ("nyquist_raw_vs_clean",            "Nyquist — Raw vs clean"),
    ("nyquist_individual_per_bias",     "Nyquist — Individual per DC bias"),
    ("nyquist_freq_colored_per_bias",   "Nyquist — Frequency-colored per DC bias"),
    ("nyquist_freq_colored_comparative","Nyquist — Frequency-colored comparative"),
    # Bode
    ("bode_mag_comparative",            "Bode — |Z| magnitude comparative"),
    ("bode_phase_comparative",          "Bode — Phase comparative"),
    ("bode_mag_individual",             "Bode — |Z| magnitude individual"),
    ("bode_phase_individual",           "Bode — Phase individual"),
    # Domain
    ("z_real_vs_freq",                  "Z' vs frequency"),
    ("minus_z_imag_vs_freq",            "−Z'' vs frequency"),
    ("admittance_mag",                  "|Y| admittance magnitude"),
    ("admittance_phase",                "Phase(Y) admittance phase"),
    ("capacitance_series",              "C_series vs frequency"),
    ("capacitance_parallel",            "C_parallel vs frequency"),
    # Tables / Reports
    ("dc_bias_summary_tables",          "DC bias summary tables"),
    ("smart_interpretation_report",     "Smart interpretation report"),
]

_DEFAULT_SELECTED = {item[0] for item in ANALYSIS_ITEMS}


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

class _AnalysisWorker(QThread):
    """
    Runs the full analysis pipeline in a background thread so the UI
    remains responsive.
    """

    log_line   = Signal(str)
    finished   = Signal(bool, str)   # success, run_dir_str

    def __init__(
        self,
        input_path: Path,
        output_dir: Path,
        selected: set[str],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._input_path = input_path
        self._output_dir = output_dir
        self._selected   = selected

    def run(self) -> None:
        try:
            self._execute()
        except Exception as exc:
            tb = traceback.format_exc()
            self.log_line.emit(f"[FATAL] Unexpected error: {exc}\n{tb}")
            self.finished.emit(False, "")

    def _execute(self) -> None:
        from services.analysis.schema_detector import detect_schema
        from services.analysis.eis_transformer import transform, COL_DC
        from services.analysis.cleaning_pipeline import run as clean
        from services.analysis.plot_engine import PlotEngine
        from services.analysis.interpretation_engine import interpret
        from services.analysis import export_manager as em

        log = self.log_line.emit

        # ------------------------------------------------------------------
        # 1. Load file
        # ------------------------------------------------------------------
        log(f"Loading: {self._input_path.name}")
        try:
            raw_df = _load_csv(self._input_path)
        except Exception as exc:
            log(f"[ERROR] Cannot read file: {exc}")
            self.finished.emit(False, "")
            return

        if raw_df is None or raw_df.empty:
            log("[ERROR] File is empty or unreadable.")
            self.finished.emit(False, "")
            return

        log(f"  {len(raw_df)} rows loaded.")

        # ------------------------------------------------------------------
        # 2. Detect schema
        # ------------------------------------------------------------------
        log("Detecting column schema…")
        schema = detect_schema(raw_df)
        for w in schema.warnings:
            log(f"  [WARN] {w}")

        if schema.impedance_mode == "incomplete":
            log("[ERROR] Insufficient impedance data columns. Cannot proceed.")
            self.finished.emit(False, "")
            return

        log(f"  Impedance mode : {schema.impedance_mode}")
        log(f"  Has DC bias    : {schema.has_dc_bias}")
        log(f"  Has status     : {schema.has_status}")
        log(f"  Has frequency  : {schema.has_freq}")

        # ------------------------------------------------------------------
        # 3. Transform
        # ------------------------------------------------------------------
        log("Applying EIS transformations…")
        enriched_df = transform(raw_df, schema)
        log(f"  {len(ANALYSIS_ITEMS)} derived quantities computed.")

        # ------------------------------------------------------------------
        # 4. Clean
        # ------------------------------------------------------------------
        log("Running cleaning pipeline…")
        group_col = COL_DC if (schema.has_dc_bias and COL_DC in enriched_df.columns
                               and enriched_df[COL_DC].notna().any()) else None
        result = clean(enriched_df, group_col=group_col)
        gs = result.global_summary
        log(f"  Raw: {gs['points_raw']}  Clean: {gs['points_clean']}"
            f"  Removed: {gs['points_removed']} ({gs['percent_removed']:.1f}%)")

        if result.clean_df.empty:
            log("[ERROR] All points were removed by the cleaning pipeline.")
            self.finished.emit(False, "")
            return

        # ------------------------------------------------------------------
        # 5. Create run folder
        # ------------------------------------------------------------------
        log("Creating output folder structure…")
        ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
        paths = em.create_run(self._output_dir, timestamp=ts)
        log(f"  {paths.run_dir}")

        # ------------------------------------------------------------------
        # 6. Save cleaning outputs
        # ------------------------------------------------------------------
        log("Saving data files…")
        em.save_raw_input(paths, raw_df)
        em.save_clean_data(paths, result.clean_df)
        em.save_removed_points(paths, result.removed_df)
        em.save_cleaning_summary(paths, result.summary)

        # DC bias summary
        if ("dc_bias_summary_tables" in self._selected
                and group_col and group_col in result.clean_df.columns):
            summary_tbl = em.build_dc_bias_summary(result.clean_df, group_col)
            em.save_dc_bias_summary(paths, summary_tbl)
            log("  DC bias summary table saved.")

        # ------------------------------------------------------------------
        # 7. Generate plots
        # ------------------------------------------------------------------
        log("Generating figures…")
        engine = PlotEngine(paths.figures_dir)
        plot_selection = self._selected - {"dc_bias_summary_tables",
                                           "smart_interpretation_report"}
        gen = engine.run(
            result.clean_df,
            raw_df=enriched_df,
            selected=plot_selection if plot_selection != set(ANALYSIS_ITEMS) else None,
        )
        paths.figures.update(gen)
        log(f"  {len(gen)} figure(s) generated.")

        # ------------------------------------------------------------------
        # 8. Interpretation report
        # ------------------------------------------------------------------
        if "smart_interpretation_report" in self._selected:
            log("Generating interpretation report…")
            interp = interpret(
                result.clean_df,
                gs,
                has_dc_bias=schema.has_dc_bias,
                source_filename=self._input_path.name,
                app_version="3.5.0",
            )
            em.save_report(paths, interp.text, interp.markdown)
            log(f"  {len(interp.findings)} finding(s) written to report.")

        # ------------------------------------------------------------------
        # 9. Metadata
        # ------------------------------------------------------------------
        em.save_metadata(
            paths,
            run_config={
                "input_file": str(self._input_path),
                "output_dir": str(self._output_dir),
                "selected_outputs": sorted(self._selected),
                "group_col": group_col,
                "timestamp": ts,
            },
            schema_info={
                "impedance_mode": schema.impedance_mode,
                "column_map": schema.column_map,
                "has_dc_bias": schema.has_dc_bias,
                "has_status": schema.has_status,
                "has_freq": schema.has_freq,
                "warnings": schema.warnings,
            },
        )

        # Report any export errors
        for err in paths.errors:
            log(f"  [WARN] Export error: {err}")

        log("Analysis complete.")
        self.finished.emit(True, str(paths.run_dir))


# ---------------------------------------------------------------------------
# Main panel widget
# ---------------------------------------------------------------------------

class AnalysisInsightsPanel(QWidget):
    """
    Full "Analysis & Insights" tab panel for V3.5.
    Drop this widget into any QTabWidget tab.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._input_path: Optional[Path] = None
        self._output_dir: Path = Path.cwd() / "analysis_outputs"
        self._worker: Optional[_AnalysisWorker] = None
        self._checkboxes: dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        layout.addWidget(self._build_input_group())
        layout.addWidget(self._build_options_group(), stretch=1)
        layout.addWidget(self._build_output_group())
        layout.addWidget(self._build_run_group())
        layout.addWidget(self._build_log_group())

    # ------------------------------------------------------------------
    # Public API (called by main window to sync output folder)
    # ------------------------------------------------------------------

    def set_output_dir(self, path: Path) -> None:
        self._output_dir = Path(path)
        self._output_folder_edit.setText(str(self._output_dir))

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_input_group(self) -> QGroupBox:
        group = QGroupBox("Input Data File")
        row   = QHBoxLayout(group)
        row.setSpacing(8)

        self._input_edit = QLineEdit()
        self._input_edit.setPlaceholderText("Select a CSV file to analyse…")
        self._input_edit.setReadOnly(True)

        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_input)

        self._schema_label = QLabel("No file loaded")
        self._schema_label.setObjectName("schemaInfo")
        self._schema_label.setWordWrap(True)

        col = QVBoxLayout()
        col.addLayout(self._hrow(self._input_edit, browse_btn))
        col.addWidget(self._schema_label)

        row.addLayout(col)
        group.setLayout(row)
        return group

    def _build_options_group(self) -> QGroupBox:
        group = QGroupBox("Analysis Options")
        outer = QVBoxLayout(group)

        # Select All / Deselect All buttons
        btn_row = QHBoxLayout()
        sel_all_btn   = QPushButton("Select All")
        desel_all_btn = QPushButton("Deselect All")
        sel_all_btn.setFixedWidth(100)
        desel_all_btn.setFixedWidth(110)
        sel_all_btn.clicked.connect(self._select_all)
        desel_all_btn.clicked.connect(self._deselect_all)
        btn_row.addWidget(sel_all_btn)
        btn_row.addWidget(desel_all_btn)
        btn_row.addStretch()
        outer.addLayout(btn_row)

        # Scrollable checkbox area
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(4)
        scroll_layout.setContentsMargins(4, 4, 4, 4)

        # Group checkboxes by category
        categories = [
            ("Nyquist Plots", [k for k, _ in ANALYSIS_ITEMS if k.startswith("nyquist")]),
            ("Bode Plots",    [k for k, _ in ANALYSIS_ITEMS if k.startswith("bode")]),
            ("Derived / Domain Plots", [
                k for k, _ in ANALYSIS_ITEMS
                if k in ("z_real_vs_freq", "minus_z_imag_vs_freq",
                         "admittance_mag", "admittance_phase",
                         "capacitance_series", "capacitance_parallel")
            ]),
            ("Tables & Reports", [
                k for k, _ in ANALYSIS_ITEMS
                if k in ("dc_bias_summary_tables", "smart_interpretation_report")
            ]),
        ]

        label_map = {k: lbl for k, lbl in ANALYSIS_ITEMS}

        for cat_title, keys in categories:
            cat_label = QLabel(cat_title)
            cat_label.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
            cat_label.setStyleSheet("color: #374151; margin-top: 6px;")
            scroll_layout.addWidget(cat_label)

            for key in keys:
                cb = QCheckBox(label_map[key])
                cb.setChecked(key in _DEFAULT_SELECTED)
                self._checkboxes[key] = cb
                scroll_layout.addWidget(cb)

        scroll_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setMinimumHeight(180)
        outer.addWidget(scroll_area, stretch=1)
        return group

    def _build_output_group(self) -> QGroupBox:
        group = QGroupBox("Output Folder")
        row   = QHBoxLayout(group)

        self._output_folder_edit = QLineEdit(str(self._output_dir))
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_output)

        row.addWidget(self._output_folder_edit)
        row.addWidget(browse_btn)
        return group

    def _build_run_group(self) -> QWidget:
        widget = QWidget()
        row    = QHBoxLayout(widget)
        row.setContentsMargins(0, 0, 0, 0)

        self._run_btn  = QPushButton("Run Analysis")
        self._run_btn.setObjectName("runBtn")
        self._run_btn.setMinimumHeight(36)
        self._run_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self._run_btn.clicked.connect(self._run_analysis)

        self._open_btn = QPushButton("Open Output Folder")
        self._open_btn.setEnabled(False)
        self._open_btn.setFixedWidth(160)
        self._open_btn.clicked.connect(self._open_output_folder)

        self._status_label = QLabel("Ready")
        self._status_label.setStyleSheet("color: #6b7280; font-size: 10px;")

        row.addWidget(self._run_btn)
        row.addWidget(self._open_btn)
        row.addStretch()
        row.addWidget(self._status_label)
        return widget

    def _build_log_group(self) -> QGroupBox:
        group  = QGroupBox("Log")
        layout = QVBoxLayout(group)

        self._log = QTextEdit()
        self._log.setObjectName("analysisLog")
        self._log.setReadOnly(True)
        self._log.setFixedHeight(160)
        self._log.setFont(QFont("Consolas", 9))

        clear_btn = QPushButton("Clear Log")
        clear_btn.setFixedWidth(90)
        clear_btn.clicked.connect(self._log.clear)

        layout.addWidget(self._log)
        layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        return group

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _browse_input(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Input CSV", str(self._output_dir),
            "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return
        self._input_path = Path(path)
        self._input_edit.setText(path)
        self._probe_schema(self._input_path)

    def _browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Base Folder",
            self._output_folder_edit.text()
        )
        if folder:
            self._output_folder_edit.setText(folder)
            self._output_dir = Path(folder)

    def _select_all(self) -> None:
        for cb in self._checkboxes.values():
            cb.setChecked(True)

    def _deselect_all(self) -> None:
        for cb in self._checkboxes.values():
            cb.setChecked(False)

    def _run_analysis(self) -> None:
        if self._worker and self._worker.isRunning():
            self._log_msg("[WARN] Analysis already running. Please wait.")
            return

        if self._input_path is None or not self._input_path.exists():
            QMessageBox.warning(self, "No Input",
                                "Please select a valid CSV file first.")
            return

        selected = {k for k, cb in self._checkboxes.items() if cb.isChecked()}
        if not selected:
            QMessageBox.warning(self, "Nothing Selected",
                                "Please select at least one output to generate.")
            return

        out_dir = Path(self._output_folder_edit.text().strip() or str(self._output_dir))
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            QMessageBox.critical(self, "Output Folder Error",
                                 f"Cannot create output folder:\n{exc}")
            return

        self._run_btn.setEnabled(False)
        self._open_btn.setEnabled(False)
        self._status_label.setText("Running…")
        self._log_msg(f"[{datetime.now().strftime('%H:%M:%S')}] Starting analysis…")
        self._log_msg(f"  Input  : {self._input_path}")
        self._log_msg(f"  Output : {out_dir}")
        self._log_msg(f"  Selected: {len(selected)} output(s)")

        self._worker = _AnalysisWorker(self._input_path, out_dir, selected, parent=self)
        self._worker.log_line.connect(self._log_msg)
        self._worker.finished.connect(self._on_analysis_finished)
        self._worker.start()

    def _on_analysis_finished(self, success: bool, run_dir: str) -> None:
        self._run_btn.setEnabled(True)
        if success:
            self._last_run_dir = Path(run_dir)
            self._open_btn.setEnabled(True)
            self._status_label.setText(f"Done: {Path(run_dir).name}")
            self._log_msg(f"[OK] Output saved to: {run_dir}")
        else:
            self._status_label.setText("Failed — see log")
            self._log_msg("[FAIL] Analysis did not complete. See errors above.")

    def _open_output_folder(self) -> None:
        try:
            import subprocess
            subprocess.Popen(["explorer", str(self._last_run_dir)])
        except Exception:
            pass

    def _probe_schema(self, path: Path) -> None:
        """Quick schema probe to show detected columns to the user."""
        try:
            df = _load_csv(path)
            if df is None or df.empty:
                self._schema_label.setText("Could not read file.")
                return
            from services.analysis.schema_detector import detect_schema
            schema = detect_schema(df)
            parts = [
                f"Mode: {schema.impedance_mode}",
                f"DC bias: {'yes' if schema.has_dc_bias else 'no'}",
                f"Status: {'yes' if schema.has_status else 'no'}",
                f"Rows: {len(df)}",
            ]
            if schema.warnings:
                parts.append(f"Warnings: {'; '.join(schema.warnings)}")
            self._schema_label.setText("  |  ".join(parts))
        except Exception as exc:
            self._schema_label.setText(f"Schema detection error: {exc}")

    def _log_msg(self, msg: str) -> None:
        self._log.append(msg)
        sb = self._log.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hrow(*widgets) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(6)
        for w in widgets:
            row.addWidget(w)
        return row


# ---------------------------------------------------------------------------
# CSV loader (utf-8 → latin-1 fallback, skips # comment lines)
# ---------------------------------------------------------------------------

def _load_csv(path: Path) -> Optional[pd.DataFrame]:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            lines = path.read_text(encoding=enc).splitlines()
            data_lines = [ln for ln in lines if not ln.strip().startswith("#")]
            if not data_lines:
                return None
            from io import StringIO
            return pd.read_csv(StringIO("\n".join(data_lines)))
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    return None
