"""
nyquist_export_service.py — V3 Nyquist Export Orchestrator
SynAptIp Technologies

High-level service that coordinates CSV and JPG exports for
1–3 loaded Nyquist datasets.  Returns an ExportResult with
paths of all files written and any per-file errors.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from services.file_loader import NyquistDataset
from services.nyquist_transformer import transform_dataset, export_nyquist_csv
from services.nyquist_plotter import plot_individual, plot_comparison


@dataclass
class ExportResult:
    csv_paths: list[Path] = field(default_factory=list)
    jpg_individual: list[Path] = field(default_factory=list)
    jpg_compare: Path | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def all_paths(self) -> list[Path]:
        paths = list(self.csv_paths) + list(self.jpg_individual)
        if self.jpg_compare:
            paths.append(self.jpg_compare)
        return paths


class NyquistExportService:
    """Orchestrates all V3 Nyquist export operations."""

    def export_csv(
        self,
        datasets: list[NyquistDataset],
        output_dir: str | Path,
    ) -> ExportResult:
        """Export one Nyquist CSV per dataset."""
        result = ExportResult()
        for ds in datasets:
            if not ds.has_data:
                result.errors.append(f"Skipped CSV for '{ds.label}': no valid data")
                continue
            try:
                transform_dataset(ds)
                out = export_nyquist_csv(ds, output_dir)
                result.csv_paths.append(out)
            except Exception as exc:
                result.errors.append(f"CSV export failed for '{ds.label}': {exc}")
        return result

    def export_jpg_individual(
        self,
        datasets: list[NyquistDataset],
        output_dir: str | Path,
    ) -> ExportResult:
        """Export one JPG Nyquist plot per dataset."""
        result = ExportResult()
        for ds in datasets:
            if not ds.has_data:
                result.errors.append(f"Skipped JPG for '{ds.label}': no valid data")
                continue
            try:
                out = plot_individual(ds, output_dir)
                result.jpg_individual.append(out)
            except Exception as exc:
                result.errors.append(f"JPG export failed for '{ds.label}': {exc}")
        return result

    def export_jpg_compare(
        self,
        datasets: list[NyquistDataset],
        output_dir: str | Path,
    ) -> ExportResult:
        """Export a single comparison JPG for 2–3 datasets."""
        result = ExportResult()
        active = [ds for ds in datasets if ds.has_data]
        if len(active) < 2:
            result.errors.append(
                "Comparison plot requires at least 2 files with valid data"
            )
            return result
        try:
            out = plot_comparison(active, output_dir)
            result.jpg_compare = out
        except Exception as exc:
            result.errors.append(f"Comparison JPG export failed: {exc}")
        return result

    def export_all(
        self,
        datasets: list[NyquistDataset],
        output_dir: str | Path,
    ) -> ExportResult:
        """Export CSVs + individual JPGs + comparison JPG."""
        result = ExportResult()

        csv_result = self.export_csv(datasets, output_dir)
        result.csv_paths.extend(csv_result.csv_paths)
        result.errors.extend(csv_result.errors)

        jpg_result = self.export_jpg_individual(datasets, output_dir)
        result.jpg_individual.extend(jpg_result.jpg_individual)
        result.errors.extend(jpg_result.errors)

        active = [ds for ds in datasets if ds.has_data]
        if len(active) >= 2:
            cmp_result = self.export_jpg_compare(active, output_dir)
            result.jpg_compare = cmp_result.jpg_compare
            result.errors.extend(cmp_result.errors)

        return result
