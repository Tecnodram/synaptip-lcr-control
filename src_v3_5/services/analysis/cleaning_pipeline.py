"""
cleaning_pipeline.py — EIS Data Cleaning Pipeline
SynAptIp Nyquist Analyzer V3.5
SynAptIp Technologies

Implements the four-step cleaning process:

  Step 1 — Remove rows with invalid status flag
  Step 2 — Remove rows with NaN / ±inf in required analysis columns
  Step 3 — Remove rows with non-positive frequency
  Step 4 — Robust percentile filter per analysis group

Each removed row is tagged with a removal reason.

The pipeline is fully auditable and traceable:
  - Returns clean_df, removed_df with reason column, and a summary dict.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from services.analysis.eis_transformer import (
    COL_FREQ,
    COL_Z_REAL,
    COL_Z_IMAG,
    COL_MZ_IMG,
    COL_Z_MAG,
    COL_DC,
    COL_STATUS,
)

# Columns required to be finite for the analysis to be meaningful
_REQUIRED_FINITE = [COL_Z_REAL, COL_Z_IMAG, COL_FREQ]

# Column used for percentile filtering
_PERCENTILE_COLS = [COL_Z_REAL, COL_MZ_IMG, COL_Z_MAG]

# Reason tag constants
REASON_INVALID_STATUS    = "invalid_status"
REASON_NON_FINITE        = "non_finite_value"
REASON_NON_POSITIVE_FREQ = "non_positive_frequency"
REASON_PERCENTILE        = "outside_percentile_filter"

REMOVAL_REASON_COL = "removal_reason"


@dataclass
class CleaningResult:
    clean_df: pd.DataFrame
    removed_df: pd.DataFrame
    summary: pd.DataFrame          # per-group summary rows
    global_summary: dict           # overall key metrics


def run(
    df: pd.DataFrame,
    *,
    percentile_low: float = 1.0,
    percentile_high: float = 99.0,
    valid_status_values: Optional[list[str]] = None,
    group_col: Optional[str] = None,
) -> CleaningResult:
    """
    Execute the full cleaning pipeline.

    Parameters
    ----------
    df : DataFrame
        Input frame from eis_transformer.transform().
    percentile_low, percentile_high : float
        Percentile bounds for the outlier filter (per group).
    valid_status_values : list[str] | None
        Acceptable status strings. Defaults to ["ok", "valid", "1", "true"].
    group_col : str | None
        If not None, apply percentile filter per group (typically COL_DC).
    """
    if valid_status_values is None:
        valid_status_values = ["ok", "valid", "1", "true", "yes"]

    n_raw = len(df)
    removed_frames: list[pd.DataFrame] = []
    work = df.copy()

    # ------------------------------------------------------------------ #
    # Step 1: invalid status                                               #
    # ------------------------------------------------------------------ #
    if COL_STATUS in work.columns:
        is_valid = work[COL_STATUS].str.lower().isin([v.lower() for v in valid_status_values])
        bad = work[~is_valid].copy()
        bad[REMOVAL_REASON_COL] = REASON_INVALID_STATUS
        removed_frames.append(bad)
        work = work[is_valid].copy()

    # ------------------------------------------------------------------ #
    # Step 2: NaN / inf in required columns                               #
    # ------------------------------------------------------------------ #
    exists = [c for c in _REQUIRED_FINITE if c in work.columns]
    if exists:
        bad_mask = ~work[exists].apply(
            lambda s: np.isfinite(s.values), axis=0
        ).all(axis=1)
        bad = work[bad_mask].copy()
        bad[REMOVAL_REASON_COL] = REASON_NON_FINITE
        removed_frames.append(bad)
        work = work[~bad_mask].copy()

    # ------------------------------------------------------------------ #
    # Step 3: non-positive frequency                                      #
    # ------------------------------------------------------------------ #
    if COL_FREQ in work.columns:
        bad_mask = work[COL_FREQ] <= 0
        bad = work[bad_mask].copy()
        bad[REMOVAL_REASON_COL] = REASON_NON_POSITIVE_FREQ
        removed_frames.append(bad)
        work = work[~bad_mask].copy()

    # ------------------------------------------------------------------ #
    # Step 4: percentile filter                                            #
    # ------------------------------------------------------------------ #
    if group_col and group_col in work.columns:
        groups = work[group_col].unique()
        keep_parts: list[pd.DataFrame] = []
        for g_val in groups:
            g_mask   = work[group_col] == g_val
            g_df     = work[g_mask].copy()
            kept, removed_rows = _percentile_filter(g_df, percentile_low, percentile_high)
            keep_parts.append(kept)
            removed_frames.append(removed_rows)
        work = pd.concat(keep_parts, ignore_index=True) if keep_parts else work.iloc[0:0]
    else:
        work, removed_rows = _percentile_filter(work, percentile_low, percentile_high)
        removed_frames.append(removed_rows)

    # ------------------------------------------------------------------ #
    # Combine removed rows                                                 #
    # ------------------------------------------------------------------ #
    removed_df: pd.DataFrame
    if removed_frames:
        all_removed = [r for r in removed_frames if len(r) > 0]
        if all_removed:
            removed_df = pd.concat(all_removed, ignore_index=True)
        else:
            removed_df = pd.DataFrame(columns=list(df.columns) + [REMOVAL_REASON_COL])
    else:
        removed_df = pd.DataFrame(columns=list(df.columns) + [REMOVAL_REASON_COL])

    n_clean   = len(work)
    n_removed = n_raw - n_clean

    # ------------------------------------------------------------------ #
    # Per-group summary                                                    #
    # ------------------------------------------------------------------ #
    summary_rows: list[dict] = []
    if group_col and group_col in work.columns and len(work) > 0:
        for g_val in sorted(work[group_col].dropna().unique()):
            g_df = work[work[group_col] == g_val]
            n_g_raw     = len(df[df[group_col] == g_val]) if group_col in df.columns else len(g_df)
            n_g_clean   = len(g_df)
            n_g_removed = n_g_raw - n_g_clean
            pct_removed = 100.0 * n_g_removed / n_g_raw if n_g_raw > 0 else 0.0
            summary_rows.append({
                "group": g_val,
                "points_raw": n_g_raw,
                "points_clean": n_g_clean,
                "points_removed": n_g_removed,
                "percent_removed": round(pct_removed, 2),
            })
    else:
        pct_removed = 100.0 * n_removed / n_raw if n_raw > 0 else 0.0
        summary_rows.append({
            "group": "all",
            "points_raw": n_raw,
            "points_clean": n_clean,
            "points_removed": n_removed,
            "percent_removed": round(pct_removed, 2),
        })

    summary_df = pd.DataFrame(summary_rows)

    global_summary = {
        "points_raw": n_raw,
        "points_clean": n_clean,
        "points_removed": n_removed,
        "percent_removed": round(100.0 * n_removed / n_raw, 2) if n_raw > 0 else 0.0,
    }

    return CleaningResult(
        clean_df=work.reset_index(drop=True),
        removed_df=removed_df.reset_index(drop=True),
        summary=summary_df,
        global_summary=global_summary,
    )


def _percentile_filter(
    df: pd.DataFrame,
    pct_low: float,
    pct_high: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Remove rows where any of the _PERCENTILE_COLS falls outside the
    [pct_low, pct_high] percentile range of that column.

    Returns (kept_df, removed_df).
    """
    if df.empty:
        empty_removed = pd.DataFrame(columns=list(df.columns) + [REMOVAL_REASON_COL])
        return df, empty_removed

    keep_mask = pd.Series(True, index=df.index)

    for col in _PERCENTILE_COLS:
        if col not in df.columns:
            continue
        vals = pd.to_numeric(df[col], errors="coerce")
        finite_vals = vals[np.isfinite(vals)]
        if len(finite_vals) < 4:
            continue
        lo = np.percentile(finite_vals, pct_low)
        hi = np.percentile(finite_vals, pct_high)
        in_range = (vals >= lo) & (vals <= hi)
        keep_mask = keep_mask & (in_range | ~np.isfinite(vals))

    kept    = df[keep_mask].copy()
    removed = df[~keep_mask].copy()
    removed[REMOVAL_REASON_COL] = REASON_PERCENTILE
    return kept, removed
