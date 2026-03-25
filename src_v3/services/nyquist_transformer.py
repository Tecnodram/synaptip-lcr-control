"""
nyquist_transformer.py — V3 Nyquist Transform Service
SynAptIp Technologies

Validates and enriches a NyquistDataset, computing Nyquist columns
from raw impedance data (z_ohm, theta_deg → z_real, z_imag, -z_imag).
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

from services.file_loader import NyquistDataset


NYQUIST_FIELDNAMES = [
    "freq_hz",
    "z_ohm",
    "theta_deg",
    "z_real",
    "z_imag",
    "minus_z_imag",
]


def transform_dataset(dataset: NyquistDataset) -> NyquistDataset:
    """
    Validate and enrich a NyquistDataset in-place.

    Each row already carries z_real and z_imag (computed by file_loader).
    This function adds the minus_z_imag convenience key.
    """
    for row in dataset.rows:
        row["minus_z_imag"] = -row["z_imag"]
    return dataset


def export_nyquist_csv(
    dataset: NyquistDataset,
    output_dir: str | Path,
    stem: str | None = None,
) -> Path:
    """
    Write a Nyquist-transformed CSV file for a single dataset.

    Output filename: <stem>_nyquist_data.csv
    (default stem is the original file's stem)
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    file_stem = stem or dataset.file_path.stem
    out_path = out_dir / f"{file_stem}_nyquist_data.csv"

    with out_path.open("w", newline="", encoding="utf-8") as fh:
        fh.write(f"# SynAptIp Technologies — Nyquist Transform Export\n")
        fh.write(f"# Source: {dataset.file_path.name}\n")
        fh.write(f"# Label: {dataset.label}\n")
        fh.write(f"# Valid points: {dataset.valid_count}\n\n")

        writer = csv.DictWriter(fh, fieldnames=NYQUIST_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in dataset.rows:
            writer.writerow(
                {
                    "freq_hz": _fmt(row.get("freq_hz", 0.0)),
                    "z_ohm": _fmt(row.get("z_ohm", "")),
                    "theta_deg": _fmt(row.get("theta_deg", "")),
                    "z_real": _fmt(row["z_real"]),
                    "z_imag": _fmt(row["z_imag"]),
                    "minus_z_imag": _fmt(row.get("minus_z_imag", -row["z_imag"])),
                }
            )

    return out_path


def _fmt(value: object) -> str:
    if isinstance(value, float):
        if math.isfinite(value):
            return f"{value:.6g}"
        return ""
    return str(value) if value != "" else ""
