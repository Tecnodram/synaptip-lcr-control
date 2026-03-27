"""
export_manager.py — Run Output Folder Manager
SynAptIp Nyquist Analyzer V3.5
SynAptIp Technologies

Creates a timestamped output structure for each analysis run:

    <base_dir>/run_YYYYMMDD_HHMMSS/
        raw/
            raw_input.csv
        cleaned/
            clean_data.csv
            removed_points.csv
            cleaning_summary.csv
        figures/           (populated by PlotEngine)
        tables/
            dc_bias_summary.csv   (if applicable)
        report/
            report.txt
            report.md
        metadata/
            run_config.json
            software_version.json
            detected_schema.json

All paths are safe for Windows and PyInstaller exe packaging.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd


@dataclass
class RunPaths:
    """All folder/file paths for a run."""
    run_dir: Path
    raw_dir: Path
    cleaned_dir: Path
    figures_dir: Path
    tables_dir: Path
    report_dir: Path
    metadata_dir: Path

    # Resolved file paths (populated after save)
    raw_input_csv: Optional[Path] = None
    clean_data_csv: Optional[Path] = None
    removed_points_csv: Optional[Path] = None
    cleaning_summary_csv: Optional[Path] = None
    report_txt: Optional[Path] = None
    report_md: Optional[Path] = None
    run_config_json: Optional[Path] = None
    software_version_json: Optional[Path] = None
    detected_schema_json: Optional[Path] = None
    dc_bias_summary_csv: Optional[Path] = None

    figures: dict[str, Path] = field(default_factory=dict)

    errors: list[str] = field(default_factory=list)


def create_run(base_dir: Path, *, timestamp: Optional[str] = None) -> RunPaths:
    """
    Create the run folder structure under *base_dir* and return populated RunPaths.
    """
    ts  = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    run = Path(base_dir) / f"run_{ts}"

    raw_dir      = run / "raw"
    cleaned_dir  = run / "cleaned"
    figures_dir  = run / "figures"
    tables_dir   = run / "tables"
    report_dir   = run / "report"
    metadata_dir = run / "metadata"

    for d in (raw_dir, cleaned_dir, figures_dir, tables_dir,
              report_dir, metadata_dir):
        d.mkdir(parents=True, exist_ok=True)

    return RunPaths(
        run_dir=run,
        raw_dir=raw_dir,
        cleaned_dir=cleaned_dir,
        figures_dir=figures_dir,
        tables_dir=tables_dir,
        report_dir=report_dir,
        metadata_dir=metadata_dir,
    )


# ---------------------------------------------------------------------------
# Individual save helpers  (all return the saved path for assignment)
# ---------------------------------------------------------------------------

def save_raw_input(paths: RunPaths, raw_df: pd.DataFrame) -> Optional[Path]:
    """Save the raw input DataFrame as CSV."""
    return _save_csv(paths, "raw_input_csv",
                     paths.raw_dir / "raw_input.csv", raw_df)


def save_clean_data(paths: RunPaths, clean_df: pd.DataFrame) -> Optional[Path]:
    return _save_csv(paths, "clean_data_csv",
                     paths.cleaned_dir / "clean_data.csv", clean_df)


def save_removed_points(paths: RunPaths, removed_df: pd.DataFrame) -> Optional[Path]:
    return _save_csv(paths, "removed_points_csv",
                     paths.cleaned_dir / "removed_points.csv", removed_df)


def save_cleaning_summary(paths: RunPaths, summary_df: pd.DataFrame) -> Optional[Path]:
    return _save_csv(paths, "cleaning_summary_csv",
                     paths.cleaned_dir / "cleaning_summary.csv", summary_df)


def save_dc_bias_summary(paths: RunPaths, df: pd.DataFrame) -> Optional[Path]:
    return _save_csv(paths, "dc_bias_summary_csv",
                     paths.tables_dir / "dc_bias_summary.csv", df)


def save_report(paths: RunPaths, text: str, markdown: str) -> None:
    """Save both plaintext and markdown versions of the interpretation report."""
    try:
        p_txt = paths.report_dir / "report.txt"
        p_txt.write_text(text, encoding="utf-8")
        paths.report_txt = p_txt
    except Exception as exc:
        paths.errors.append(f"report.txt: {exc}")

    try:
        p_md = paths.report_dir / "report.md"
        p_md.write_text(markdown, encoding="utf-8")
        paths.report_md = p_md
    except Exception as exc:
        paths.errors.append(f"report.md: {exc}")


def save_metadata(
    paths: RunPaths,
    *,
    run_config: Optional[dict] = None,
    app_version: str = "3.5.0",
    schema_info: Optional[dict] = None,
) -> None:
    """Save all metadata JSON files."""
    _save_json(paths, "run_config_json",
               paths.metadata_dir / "run_config.json",
               run_config or {})

    version_data: dict[str, Any] = {
        "app": "SynAptIp Nyquist Analyzer",
        "version": app_version,
        "company": "SynAptIp Technologies",
        "generated_at": datetime.now().isoformat(),
    }
    _save_json(paths, "software_version_json",
               paths.metadata_dir / "software_version.json",
               version_data)

    if schema_info:
        _save_json(paths, "detected_schema_json",
                   paths.metadata_dir / "detected_schema.json",
                   schema_info)


# ---------------------------------------------------------------------------
# DC bias summary table builder
# ---------------------------------------------------------------------------

def build_dc_bias_summary(clean_df: pd.DataFrame, dc_col: str) -> pd.DataFrame:
    """
    Compute per-bias-group statistics and return a summary DataFrame.
    """
    from services.analysis.eis_transformer import (
        COL_Z_REAL, COL_MZ_IMG, COL_Z_MAG, COL_THETA
    )

    rows: list[dict] = []
    for bv in sorted(clean_df[dc_col].dropna().unique()):
        g = clean_df[clean_df[dc_col] == bv]
        r: dict[str, Any] = {"dc_bias_v": bv, "n_points": len(g)}
        for col, label in [
            (COL_Z_REAL, "z_real_median_ohm"),
            (COL_MZ_IMG, "minus_z_imag_median_ohm"),
            (COL_Z_MAG,  "z_mag_median_ohm"),
            (COL_THETA,  "theta_median_deg"),
        ]:
            if col in g.columns:
                vals = pd.to_numeric(g[col], errors="coerce").dropna()
                r[label] = round(float(vals.median()), 6) if len(vals) else None
            else:
                r[label] = None
        rows.append(r)

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _save_csv(
    paths: RunPaths, attr: str, fpath: Path, df: pd.DataFrame
) -> Optional[Path]:
    try:
        df.to_csv(fpath, index=False)
        setattr(paths, attr, fpath)
        return fpath
    except Exception as exc:
        paths.errors.append(f"{fpath.name}: {exc}")
        return None


def _save_json(
    paths: RunPaths, attr: str, fpath: Path, data: dict
) -> Optional[Path]:
    try:
        fpath.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        setattr(paths, attr, fpath)
        return fpath
    except Exception as exc:
        paths.errors.append(f"{fpath.name}: {exc}")
        return None
