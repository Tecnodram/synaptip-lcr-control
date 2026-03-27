"""
eis_transformer.py — EIS Core Transformations
SynAptIp Nyquist Analyzer V3.5
SynAptIp Technologies

Computes the full set of EIS-derived quantities from a normalised DataFrame.

Input: raw DataFrame + DetectedSchema
Output: DataFrame with appended canonical columns

Safe numerical handling:
  - Uses np.where / np.divide to avoid ZeroDivisionError
  - Stores NaN where a quantity is undefined or non-physical
  - Never raises on bad input rows
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from services.analysis.schema_detector import DetectedSchema


# Canonical output column names
COL_FREQ   = "freq_hz"
COL_Z_REAL = "Z_real_ohm"
COL_Z_IMAG = "Z_imag_ohm"
COL_MZ_IMG = "minus_Z_imag_ohm"
COL_Z_MAG  = "z_ohm"
COL_THETA  = "theta_deg"
COL_OMEGA  = "omega_rad_s"
COL_G      = "G_siemens"
COL_B      = "B_siemens"
COL_Y_MAG  = "Y_mag_siemens"
COL_Y_PHS  = "phase_y_deg"
COL_C_SER  = "C_series_F"
COL_C_PAR  = "C_parallel_F"
COL_DC     = "dc_bias_v"
COL_STATUS = "status"

# All canonical analysis columns in preferred display order
ANALYSIS_COLUMNS = [
    COL_FREQ, COL_Z_REAL, COL_Z_IMAG, COL_MZ_IMG,
    COL_Z_MAG, COL_THETA, COL_OMEGA,
    COL_G, COL_B, COL_Y_MAG, COL_Y_PHS,
    COL_C_SER, COL_C_PAR,
]


def transform(df: pd.DataFrame, schema: DetectedSchema) -> pd.DataFrame:
    """
    Apply all EIS transformations and return an enriched copy of *df*.

    The returned DataFrame contains all original columns plus the computed
    canonical columns. Existing columns are not overwritten.
    """
    out = df.copy()

    try:
        _resolve_impedance(out, schema)
        _compute_derived(out)
        _normalise_dc_bias(out, schema)
        _normalise_status(out, schema)
    except Exception as exc:  # pragma: no cover
        # Fail-safe: return whatever was computed so far
        out.attrs["transform_error"] = str(exc)

    return out


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_impedance(df: pd.DataFrame, schema: DetectedSchema) -> None:
    """Populate Z_real_ohm and Z_imag_ohm from whichever source columns exist."""
    mode = schema.impedance_mode

    if mode == "real_imag":
        z_real_src = schema.canonical("z_real")
        z_imag_src = schema.canonical("z_imag")
        df[COL_Z_REAL] = pd.to_numeric(df[z_real_src], errors="coerce")
        df[COL_Z_IMAG] = pd.to_numeric(df[z_imag_src], errors="coerce")

    elif mode == "minus_imag":
        z_real_src  = schema.canonical("z_real")
        mz_imag_src = schema.canonical("minus_z_imag")
        df[COL_Z_REAL] = pd.to_numeric(df[z_real_src], errors="coerce")
        df[COL_Z_IMAG] = -pd.to_numeric(df[mz_imag_src], errors="coerce")

    elif mode == "z_theta":
        z_src     = schema.canonical("z_ohm")
        theta_src = schema.canonical("theta_deg")
        z_mag   = pd.to_numeric(df[z_src],     errors="coerce")
        theta   = pd.to_numeric(df[theta_src], errors="coerce")
        theta_r = np.deg2rad(theta.values)
        df[COL_Z_REAL] = z_mag * np.cos(theta_r)
        df[COL_Z_IMAG] = z_mag * np.sin(theta_r)
    else:
        df[COL_Z_REAL] = np.nan
        df[COL_Z_IMAG] = np.nan

    df[COL_MZ_IMG] = -df[COL_Z_IMAG]

    # |Z| and theta if not already resolved
    if COL_Z_MAG not in df.columns:
        zr = df[COL_Z_REAL].values
        zi = df[COL_Z_IMAG].values
        df[COL_Z_MAG] = np.sqrt(zr**2 + zi**2)

    if COL_THETA not in df.columns:
        zr = df[COL_Z_REAL].values
        zi = df[COL_Z_IMAG].values
        df[COL_THETA] = np.rad2deg(np.arctan2(zi, zr))

    # Frequency column
    freq_src = schema.canonical("freq_hz")
    if freq_src:
        df[COL_FREQ] = pd.to_numeric(df[freq_src], errors="coerce")


def _compute_derived(df: pd.DataFrame) -> None:
    """Compute admittance, capacitance, and angular frequency columns."""
    zr = df[COL_Z_REAL].values.astype(float)
    zi = df[COL_Z_IMAG].values.astype(float)
    f  = df[COL_FREQ].values.astype(float)

    # Angular frequency — NaN if freq <= 0
    omega = np.where(f > 0, 2.0 * np.pi * f, np.nan)
    df[COL_OMEGA] = omega

    # Admittance: Y = 1/Z = (Z* / |Z|^2)
    z_sq = zr**2 + zi**2
    safe_z_sq = np.where(z_sq > 0, z_sq, np.nan)

    df[COL_G]     = zr / safe_z_sq          # G = Z' / |Z|^2
    df[COL_B]     = -zi / safe_z_sq         # B = −Z'' / |Z|^2

    g = df[COL_G].values
    b = df[COL_B].values
    df[COL_Y_MAG] = np.sqrt(g**2 + b**2)
    df[COL_Y_PHS] = np.rad2deg(np.arctan2(b, g))

    # Capacitance
    # C_series  = −1 / (ω · Z'')   → represents the series RC model
    # C_parallel = B / ω            → represents the parallel RC model
    safe_omega = np.where(np.isfinite(omega) & (omega != 0), omega, np.nan)
    safe_zi    = np.where(zi != 0, zi, np.nan)

    df[COL_C_SER] = -1.0 / (safe_omega * safe_zi)
    df[COL_C_PAR] =  b   /  safe_omega


def _normalise_dc_bias(df: pd.DataFrame, schema: DetectedSchema) -> None:
    """Copy dc_bias to canonical column if present."""
    if schema.has_dc_bias:
        raw = schema.canonical("dc_bias")
        df[COL_DC] = pd.to_numeric(df[raw], errors="coerce")
    else:
        df[COL_DC] = np.nan


def _normalise_status(df: pd.DataFrame, schema: DetectedSchema) -> None:
    """Copy status to canonical column if present."""
    if schema.has_status:
        raw = schema.canonical("status")
        df[COL_STATUS] = df[raw].astype(str).str.strip()
    else:
        df[COL_STATUS] = "ok"
