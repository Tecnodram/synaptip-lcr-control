"""
file_loader.py — V3 Nyquist CSV Loader
SynAptIp Technologies

Loads 1–3 CSV files for Nyquist post-processing.
Supports V2 enriched exports and plain freq/z/theta CSVs.

Loading strategy:
  1. pandas read_csv with utf-8 encoding (primary)
  2. pandas read_csv with latin-1 fallback (if utf-8 fails)
  3. Metadata comment lines starting with '#' are stripped before parsing.

Accepted column sets (in priority order):
  A. z_real + z_imag         — used directly (no transform needed)
  B. z_ohm + theta_deg       — converted to z_real / z_imag
  C. primary + secondary     — treated as z_ohm / theta_deg
"""
from __future__ import annotations

import io
import math
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass
class NyquistDataset:
    """Holds parsed Nyquist data for one loaded file."""

    file_path: Path
    label: str
    rows: list[dict[str, float]] = field(default_factory=list)
    valid_count: int = 0
    total_count: int = 0
    error: str = ""

    @property
    def has_data(self) -> bool:
        return self.valid_count > 0

    @property
    def z_real(self) -> list[float]:
        return [r["z_real"] for r in self.rows]

    @property
    def z_imag(self) -> list[float]:
        return [r["z_imag"] for r in self.rows]

    @property
    def minus_z_imag(self) -> list[float]:
        return [-r["z_imag"] for r in self.rows]

    @property
    def freq_hz(self) -> list[float]:
        return [r.get("freq_hz", 0.0) for r in self.rows]


def load_nyquist_dataset(path: str | Path, label: str | None = None) -> NyquistDataset:
    """Load a single CSV file and return a NyquistDataset."""
    csv_path = Path(path)
    ds = NyquistDataset(
        file_path=csv_path,
        label=label or csv_path.stem,
    )

    if not csv_path.exists():
        ds.error = f"File not found: {csv_path}"
        return ds

    try:
        df = _load_dataframe(csv_path)
    except Exception as exc:
        ds.error = f"Read error: {exc}"
        return ds

    if df is None or df.empty:
        ds.error = "File is empty or contains no data rows"
        return ds

    ds.total_count = len(df)

    # Normalise column names: strip whitespace, lowercase
    df.columns = [str(c).strip().lower() for c in df.columns]

    for _, row in df.iterrows():
        try:
            parsed = _parse_pandas_row(row)
            if parsed is not None:
                ds.rows.append(parsed)
        except Exception:
            pass

    # Drop NaN / infinite values
    ds.rows = [
        r for r in ds.rows
        if all(math.isfinite(v) for v in r.values())
    ]
    ds.valid_count = len(ds.rows)

    if ds.valid_count == 0:
        ds.error = (
            "No valid Nyquist points could be extracted. "
            "Expected columns: z_ohm + theta_deg  OR  z_real + z_imag  "
            "(or primary + secondary for raw instrument exports)."
        )

    return ds


# ------------------------------------------------------------------ #
#  Internal helpers                                                    #
# ------------------------------------------------------------------ #

def _load_dataframe(path: Path) -> pd.DataFrame:
    """
    Read a CSV, skipping '#' comment lines, with encoding fallback.

    Tries utf-8 first; falls back to latin-1 if decoding fails.
    """
    raw = path.read_bytes()
    for encoding in ("utf-8", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        # Last resort: replace undecodable bytes
        text = raw.decode("utf-8", errors="replace")

    # Strip metadata comment lines
    clean_lines = [
        ln for ln in text.splitlines(keepends=True)
        if not ln.lstrip().startswith("#") and ln.strip()
    ]
    if not clean_lines:
        return pd.DataFrame()

    clean_text = "".join(clean_lines)
    return pd.read_csv(io.StringIO(clean_text))


def _parse_pandas_row(row: pd.Series) -> dict[str, float] | None:  # type: ignore[type-arg]
    def _get(key: str) -> float | None:
        val = row.get(key)
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    freq_hz = _get("freq_hz") or 0.0

    # Priority 1: pre-computed z_real / z_imag
    z_real = _get("z_real")
    z_imag = _get("z_imag")
    if z_real is not None and z_imag is not None:
        return {"freq_hz": freq_hz, "z_real": z_real, "z_imag": z_imag}

    # Priority 2: z_ohm + theta_deg
    z_ohm = _get("z_ohm") if _get("z_ohm") is not None else _get("primary")
    theta_deg = _get("theta_deg") if _get("theta_deg") is not None else _get("secondary")
    if z_ohm is None or theta_deg is None:
        return None

    theta_rad = math.radians(theta_deg)
    return {
        "freq_hz": freq_hz,
        "z_real": z_ohm * math.cos(theta_rad),
        "z_imag": z_ohm * math.sin(theta_rad),
        "z_ohm": z_ohm,
        "theta_deg": theta_deg,
    }
