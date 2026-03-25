"""
nyquist_analysis_panel.py — V3 Nyquist Analysis Panel
SynAptIp Technologies

Self-contained QWidget panel that provides:
  - Load File 1/2/3 with file name + valid point count display
  - In-app Nyquist chart preview (PySide6 QtCharts if available)
  - Autozoom / Fit to View
  - Export CSV, Export JPG (individual), Export JPG (compare), Export ALL
  - Robust error handling — never crashes on bad data
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.file_loader import NyquistDataset, load_nyquist_dataset
from services.nyquist_transformer import transform_dataset
from services.nyquist_export_service import NyquistExportService
from services.plot_view_helpers import compute_axis_limits, series_color

try:
    from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
    QT_CHARTS_AVAILABLE = True
except Exception:
    QChart = object  # type: ignore[assignment]
    QChartView = object  # type: ignore[assignment]
    QLineSeries = object  # type: ignore[assignment]
    QValueAxis = object  # type: ignore[assignment]
    QT_CHARTS_AVAILABLE = False

_MAX_SLOTS = 3
_SLOT_COLORS = ["#1d4ed8", "#b45309", "#065f46"]


class NyquistAnalysisPanel(QWidget):
    """
    Full Nyquist post-processing panel for V3.
    Drop this widget into any QTabWidget tab.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._datasets: list[NyquistDataset | None] = [None, None, None]
        self._exporter = NyquistExportService()
        self._output_dir: Path = Path.cwd() / "exports_v3"

        self._chart = None
        self._chart_view = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        layout.addWidget(self._build_file_slots_group())
        layout.addWidget(self._build_actions_group())
        layout.addWidget(self._build_chart_group(), stretch=1)
        layout.addWidget(self._build_status_group())

    # ------------------------------------------------------------------ #
    #  UI construction                                                     #
    # ------------------------------------------------------------------ #

    def _build_file_slots_group(self) -> QGroupBox:
        group = QGroupBox("Input Files (1–3)")
        grid_layout = QVBoxLayout(group)
        grid_layout.setSpacing(6)

        self._slot_labels: list[QLabel] = []
        self._slot_info: list[QLabel] = []

        for i in range(_MAX_SLOTS):
            row = QHBoxLayout()
            row.setSpacing(8)

            load_btn = QPushButton(f"Load File {i + 1}")
            load_btn.setFixedWidth(110)
            load_btn.clicked.connect(lambda _=False, idx=i: self._load_file(idx))

            clear_btn = QPushButton("Clear")
            clear_btn.setFixedWidth(60)
            clear_btn.clicked.connect(lambda _=False, idx=i: self._clear_slot(idx))

            name_lbl = QLabel("(no file)")
            name_lbl.setStyleSheet("color: #6b7280; font-style: italic;")
            name_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

            info_lbl = QLabel("")
            info_lbl.setFixedWidth(160)
            info_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            self._slot_labels.append(name_lbl)
            self._slot_info.append(info_lbl)

            row.addWidget(load_btn)
            row.addWidget(clear_btn)
            row.addWidget(name_lbl, stretch=1)
            row.addWidget(info_lbl)

            grid_layout.addLayout(row)

        return group

    def _build_actions_group(self) -> QGroupBox:
        group = QGroupBox("Actions")
        row = QHBoxLayout(group)
        row.setSpacing(8)

        self._refresh_btn = QPushButton("Refresh Nyquist")
        self._autozoom_btn = QPushButton("Autozoom")
        self._export_csv_btn = QPushButton("Export CSV")
        self._export_jpg_btn = QPushButton("Export JPG (individual)")
        self._export_cmp_btn = QPushButton("Export JPG (compare)")
        self._export_all_btn = QPushButton("Export ALL")
        self._export_all_btn.setStyleSheet("font-weight: 700; background: #dbeafe; color: #1e3a8a;")

        for btn in (
            self._refresh_btn,
            self._autozoom_btn,
            self._export_csv_btn,
            self._export_jpg_btn,
            self._export_cmp_btn,
            self._export_all_btn,
        ):
            row.addWidget(btn)

        self._refresh_btn.clicked.connect(self._refresh_chart)
        self._autozoom_btn.clicked.connect(self._autozoom)
        self._export_csv_btn.clicked.connect(self._run_export_csv)
        self._export_jpg_btn.clicked.connect(self._run_export_jpg_individual)
        self._export_cmp_btn.clicked.connect(self._run_export_jpg_compare)
        self._export_all_btn.clicked.connect(self._run_export_all)

        return group

    def _build_chart_group(self) -> QGroupBox:
        group = QGroupBox("Nyquist Chart Preview")
        layout = QVBoxLayout(group)

        if QT_CHARTS_AVAILABLE:
            self._chart = QChart()
            self._chart.setTitle("Nyquist — Z' vs −Z''")
            self._chart.legend().setVisible(True)
            self._chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
            self._chart_view = QChartView(self._chart)
            self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            layout.addWidget(self._chart_view)
        else:
            fallback = QLabel(
                "QtCharts not available — chart preview disabled.\n"
                "Export functions still work without the preview."
            )
            fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback.setStyleSheet("color: #7f1d1d; padding: 20px;")
            layout.addWidget(fallback)

        return group

    def _build_status_group(self) -> QGroupBox:
        group = QGroupBox("Status / Log")
        layout = QVBoxLayout(group)
        self._status_output = QTextEdit()
        self._status_output.setObjectName("nyquistStatus")
        self._status_output.setReadOnly(True)
        self._status_output.setFixedHeight(120)
        self._status_output.setPlaceholderText("Load files and click Refresh Nyquist to begin.")
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(self._status_output.clear)
        layout.addWidget(self._status_output)
        layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        return group

    # ------------------------------------------------------------------ #
    #  Slot management                                                     #
    # ------------------------------------------------------------------ #

    def _load_file(self, idx: int) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            f"Load File {idx + 1}",
            str(self._output_dir),
            "CSV Files (*.csv);;All Files (*)",
        )
        if not path:
            return

        self._log(f"[file {idx + 1}] Loading: {Path(path).name}")
        try:
            ds = load_nyquist_dataset(path, label=Path(path).stem)
            transform_dataset(ds)
        except Exception as exc:
            self._log(f"[file {idx + 1}] ERROR during load: {exc}")
            return

        self._datasets[idx] = ds
        self._update_slot_ui(idx)

        if ds.has_data:
            self._log(
                f"[file {idx + 1}] OK — {ds.valid_count}/{ds.total_count} valid points"
            )
        else:
            self._log(f"[file {idx + 1}] WARNING — {ds.error}")

        self._refresh_chart()

    def _clear_slot(self, idx: int) -> None:
        self._datasets[idx] = None
        self._slot_labels[idx].setText("(no file)")
        self._slot_labels[idx].setStyleSheet("color: #6b7280; font-style: italic;")
        self._slot_info[idx].setText("")
        self._log(f"[file {idx + 1}] Cleared")
        self._refresh_chart()

    def _update_slot_ui(self, idx: int) -> None:
        ds = self._datasets[idx]
        if ds is None:
            self._slot_labels[idx].setText("(no file)")
            self._slot_labels[idx].setStyleSheet("color: #6b7280; font-style: italic;")
            self._slot_info[idx].setText("")
            return

        self._slot_labels[idx].setText(ds.file_path.name)
        if ds.has_data:
            color = _SLOT_COLORS[idx]
            self._slot_labels[idx].setStyleSheet(f"color: {color}; font-weight: 600;")
            self._slot_info[idx].setText(
                f"{ds.valid_count} pts"
            )
            self._slot_info[idx].setStyleSheet("color: #065f46; font-weight: 600;")
        else:
            self._slot_labels[idx].setStyleSheet("color: #991b1b;")
            self._slot_info[idx].setText("No valid data")
            self._slot_info[idx].setStyleSheet("color: #991b1b;")

    # ------------------------------------------------------------------ #
    #  Chart rendering                                                     #
    # ------------------------------------------------------------------ #

    def _refresh_chart(self) -> None:
        if not QT_CHARTS_AVAILABLE or self._chart is None:
            return

        self._chart.removeAllSeries()
        for axis in self._chart.axes():
            self._chart.removeAxis(axis)

        active = [ds for ds in self._datasets if ds is not None and ds.has_data]
        if not active:
            self._chart.setTitle("Nyquist — no data loaded")
            return

        x_min, x_max, y_min, y_max = compute_axis_limits(active)

        x_axis = QValueAxis()
        x_axis.setTitleText("Z' (Ω)")
        x_axis.setRange(x_min, x_max)

        y_axis = QValueAxis()
        y_axis.setTitleText("−Z'' (Ω)")
        y_axis.setRange(y_min, y_max)

        self._chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        self._chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)

        series_index = 0
        for ds in self._datasets:
            if ds is None or not ds.has_data:
                continue

            from PySide6.QtGui import QColor
            series = QLineSeries()
            series.setName(ds.label)
            color = QColor(_SLOT_COLORS[series_index % len(_SLOT_COLORS)])
            pen = series.pen()
            pen.setColor(color)
            pen.setWidthF(2.0)
            series.setPen(pen)

            for x, y in zip(ds.z_real, ds.minus_z_imag):
                series.append(x, y)

            self._chart.addSeries(series)
            series.attachAxis(x_axis)
            series.attachAxis(y_axis)
            series_index += 1

        count = sum(1 for ds in active)
        self._chart.setTitle(
            f"Nyquist — {count} file{'s' if count > 1 else ''} loaded"
        )

    def _autozoom(self) -> None:
        if not QT_CHARTS_AVAILABLE or self._chart is None:
            return

        active = [ds for ds in self._datasets if ds is not None and ds.has_data]
        if not active:
            self._log("[autozoom] No data to fit")
            return

        x_min, x_max, y_min, y_max = compute_axis_limits(active)

        x_axes = self._chart.axes(Qt.Orientation.Horizontal)
        y_axes = self._chart.axes(Qt.Orientation.Vertical)

        if x_axes:
            x_axes[0].setRange(x_min, x_max)
        if y_axes:
            y_axes[0].setRange(y_min, y_max)

        self._log("[autozoom] Axis limits recalculated and applied")

    # ------------------------------------------------------------------ #
    #  Export actions                                                      #
    # ------------------------------------------------------------------ #

    def _active_datasets(self) -> list[NyquistDataset]:
        return [ds for ds in self._datasets if ds is not None]

    def _run_export_csv(self) -> None:
        datasets = self._active_datasets()
        if not datasets:
            QMessageBox.information(self, "No Data", "Load at least one file first.")
            return
        out_dir = self._pick_output_dir()
        if out_dir is None:
            return
        result = self._exporter.export_csv(datasets, out_dir)
        self._report_export(result)

    def _run_export_jpg_individual(self) -> None:
        datasets = self._active_datasets()
        if not datasets:
            QMessageBox.information(self, "No Data", "Load at least one file first.")
            return
        out_dir = self._pick_output_dir()
        if out_dir is None:
            return
        result = self._exporter.export_jpg_individual(datasets, out_dir)
        self._report_export(result)

    def _run_export_jpg_compare(self) -> None:
        datasets = self._active_datasets()
        if not datasets:
            QMessageBox.information(self, "No Data", "Load at least one file first.")
            return
        out_dir = self._pick_output_dir()
        if out_dir is None:
            return
        result = self._exporter.export_jpg_compare(datasets, out_dir)
        self._report_export(result)

    def _run_export_all(self) -> None:
        datasets = self._active_datasets()
        if not datasets:
            QMessageBox.information(self, "No Data", "Load at least one file first.")
            return
        out_dir = self._pick_output_dir()
        if out_dir is None:
            return
        result = self._exporter.export_all(datasets, out_dir)
        self._report_export(result)

    def _pick_output_dir(self) -> Path | None:
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            str(self._output_dir),
        )
        if not folder:
            return None
        self._output_dir = Path(folder)
        return self._output_dir

    def _report_export(self, result) -> None:
        for p in result.all_paths:
            self._log(f"[export] Saved: {p.name}  →  {p.parent}")
        for err in result.errors:
            self._log(f"[export] ERROR: {err}")
        if result.all_paths and not result.errors:
            QMessageBox.information(
                self,
                "Export Complete",
                f"Exported {len(result.all_paths)} file(s) to:\n{self._output_dir}",
            )
        elif result.errors:
            QMessageBox.warning(
                self,
                "Export Completed with Warnings",
                "\n".join(result.errors),
            )

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _log(self, text: str) -> None:
        self._status_output.append(text)

    def set_output_dir(self, path: str | Path) -> None:
        """Allow parent window to set the default output directory."""
        self._output_dir = Path(path)
