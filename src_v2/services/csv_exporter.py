from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


RAW_FIELDNAMES = [
    "timestamp",
    "sample_id",
    "freq_hz",
    "dc_bias_v",
    "raw_response",
    "primary",
    "secondary",
    "status",
]

ENRICHED_FIELDNAMES = [
    "timestamp",
    "sample_id",
    "freq_hz",
    "ac_voltage_v",
    "dc_bias_on",
    "dc_bias_v",
    "z_ohm",
    "theta_deg",
    "status",
    "raw_response",
    "z_real",
    "z_imag",
    "notes",
]

LIVE_RESULTS_FIELDNAMES = [
    "timestamp",
    "sample_id",
    "freq_hz",
    "ac_voltage_v",
    "dc_bias_on",
    "dc_bias_v",
    "z_ohm",
    "theta_deg",
    "status",
    "raw_response",
]


@dataclass(slots=True)
class NyquistPoint:
    freq_hz: float
    z_real: float
    z_imag: float
    sample_id: str
    status: str


@dataclass(slots=True)
class ExportMetadata:
    project_name: str
    app_name: str
    app_version: str
    instrument_model: str
    instrument_idn: str
    com_port: str
    baudrate: int
    terminator: str
    created_at: str
    operator: str
    sample_id: str
    notes: str
    frequency_start_hz: float
    frequency_stop_hz: float
    frequency_step_hz: float
    bias_list: str
    point_settle_delay_s: float
    measure_delay_s: float
    bias_settle_delay_s: float
    main_display_assumption: str
    secondary_display_assumption: str
    range_mode: str
    speed_mode: str


class CsvExporter:
    """Writes V2 exports with metadata headers and schema-stable columns."""

    @staticmethod
    def export_live_results(path: str | Path, rows: list[dict]) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        frame = pd.DataFrame(rows)
        frame = frame.reindex(columns=LIVE_RESULTS_FIELDNAMES)
        frame["dc_bias_v"] = pd.to_numeric(frame["dc_bias_v"], errors="coerce")
        frame["freq_hz"] = pd.to_numeric(frame["freq_hz"], errors="coerce")
        frame = frame.sort_values(by=["dc_bias_v", "freq_hz"], kind="mergesort", na_position="last")
        frame.to_csv(output_path, index=False)
        return output_path

    @staticmethod
    def export_raw(path: str | Path, rows: list[dict], metadata: ExportMetadata) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="", encoding="utf-8") as handle:
            CsvExporter._write_metadata_block(handle, metadata)
            writer = csv.DictWriter(handle, fieldnames=RAW_FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in RAW_FIELDNAMES})

        return output_path

    @staticmethod
    def export_enriched(path: str | Path, rows: list[dict], metadata: ExportMetadata) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="", encoding="utf-8") as handle:
            CsvExporter._write_metadata_block(handle, metadata)
            writer = csv.DictWriter(handle, fieldnames=ENRICHED_FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in ENRICHED_FIELDNAMES})

        return output_path

    @staticmethod
    def _write_metadata_block(handle, metadata: ExportMetadata) -> None:
        # Metadata is written as comment-prefixed key/value lines so CSV readers can skip safely.
        for key, value in metadata.__dict__.items():
            handle.write(f"# {key}: {value}\n")
        handle.write("\n")


def parse_measurement_triple(raw_response: str) -> tuple[float | None, float | None, str]:
    parts = [part.strip() for part in raw_response.split(",")]
    z_ohm = None
    theta_deg = None
    status = ""

    if len(parts) >= 1:
        try:
            z_ohm = float(parts[0])
        except ValueError:
            z_ohm = None
    if len(parts) >= 2:
        try:
            theta_deg = float(parts[1])
        except ValueError:
            theta_deg = None
    if len(parts) >= 3:
        status = parts[2]

    return z_ohm, theta_deg, status


def nyquist_components(z_ohm: float, theta_deg: float) -> tuple[float, float]:
    theta_rad = math.radians(theta_deg)
    z_real = z_ohm * math.cos(theta_rad)
    z_imag = z_ohm * math.sin(theta_rad)
    return z_real, z_imag


def load_nyquist_preview_points(path: str | Path) -> list[NyquistPoint]:
    """
    Lightweight Nyquist preview loader for V2.

    Supports both expected file types:
    - Type A raw instrument-compatible rows (primary/secondary)
    - Type B enriched rows (z_ohm/theta_deg or z_real/z_imag)
    """
    csv_path = Path(path)
    rows = _read_csv_rows_skip_metadata(csv_path)
    if not rows:
        return []

    points: list[NyquistPoint] = []
    for row in rows:
        sample_id = (row.get("sample_id") or "").strip()
        status = (row.get("status") or "").strip()
        freq_hz = _safe_float(row.get("freq_hz"), default=0.0)

        z_real_val = row.get("z_real")
        z_imag_val = row.get("z_imag")
        if z_real_val not in (None, "") and z_imag_val not in (None, ""):
            z_real = _safe_float(z_real_val, 0.0)
            z_imag = _safe_float(z_imag_val, 0.0)
            points.append(NyquistPoint(freq_hz=freq_hz, z_real=z_real, z_imag=z_imag, sample_id=sample_id, status=status))
            continue

        z_ohm = _safe_float(row.get("z_ohm"), default=None)
        theta_deg = _safe_float(row.get("theta_deg"), default=None)
        if z_ohm is None:
            z_ohm = _safe_float(row.get("primary"), default=None)
        if theta_deg is None:
            theta_deg = _safe_float(row.get("secondary"), default=None)

        if z_ohm is None or theta_deg is None:
            raw_response = row.get("raw_response") or ""
            parsed_z, parsed_theta, parsed_status = parse_measurement_triple(raw_response)
            z_ohm = parsed_z if z_ohm is None else z_ohm
            theta_deg = parsed_theta if theta_deg is None else theta_deg
            if not status:
                status = parsed_status

        if z_ohm is None or theta_deg is None:
            continue

        z_real, z_imag = nyquist_components(z_ohm, theta_deg)
        points.append(NyquistPoint(freq_hz=freq_hz, z_real=z_real, z_imag=z_imag, sample_id=sample_id, status=status))

    return points


def detect_v2_file_type(path: str | Path) -> str:
    """
    Detect the expected V2 export type for Nyquist preview.

    Returns one of:
    - "type_a_raw"
    - "type_b_enriched"
    - "empty"
    - "unsupported"
    """
    rows = _read_csv_rows_skip_metadata(Path(path))
    if not rows:
        return "empty"

    keys = set(rows[0].keys())
    if {"primary", "secondary", "raw_response"}.issubset(keys):
        return "type_a_raw"
    if ({"z_ohm", "theta_deg"}.issubset(keys) or {"z_real", "z_imag"}.issubset(keys)) and "raw_response" in keys:
        return "type_b_enriched"
    return "unsupported"


def _read_csv_rows_skip_metadata(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        content = [line for line in handle.readlines() if not line.startswith("#") and line.strip()]
    if not content:
        return []

    reader = csv.DictReader(content)
    return [dict(row) for row in reader]


def _safe_float(value: str | None, default: float | None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_nyquist_xy(points: Iterable[NyquistPoint]) -> tuple[list[float], list[float]]:
    """Return plotting arrays using Nyquist convention X=z_real, Y=-z_imag."""
    x_vals: list[float] = []
    y_vals: list[float] = []
    for point in points:
        x_vals.append(point.z_real)
        y_vals.append(-point.z_imag)
    return x_vals, y_vals
