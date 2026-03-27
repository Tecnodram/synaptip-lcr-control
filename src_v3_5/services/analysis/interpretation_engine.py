"""
interpretation_engine.py — Smart Analysis / Interpretation Engine
SynAptIp Nyquist Analyzer V3.5
SynAptIp Technologies

Generates a professional technical interpretation of EIS data using
cautious scientific language.  This module never overclaims.

Output is structured text that can be saved as report.txt / report.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

from services.analysis.eis_transformer import (
    COL_FREQ,
    COL_Z_REAL,
    COL_Z_IMAG,
    COL_MZ_IMG,
    COL_THETA,
    COL_Y_MAG,
    COL_C_SER,
    COL_DC,
)


@dataclass
class InterpretationResult:
    text: str                        # plain text version
    markdown: str                    # markdown version
    findings: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def interpret(
    clean_df: pd.DataFrame,
    global_summary: dict,
    *,
    has_dc_bias: bool = False,
    source_filename: str = "unknown",
    app_version: str = "3.5.0",
) -> InterpretationResult:
    """
    Produce a cautious technical interpretation of *clean_df*.
    """
    findings: list[str] = []
    warnings: list[str] = []

    try:
        _interpret_global(clean_df, global_summary, findings, warnings)
        _interpret_impedance_character(clean_df, findings)
        _interpret_nyquist_shape(clean_df, findings)
        _interpret_characteristic_frequency(clean_df, findings)
        if has_dc_bias and COL_DC in clean_df.columns:
            _interpret_dc_bias_effect(clean_df, findings)
    except Exception as exc:
        warnings.append(f"Interpretation engine encountered an error: {exc}")

    plain  = _render_text(findings, warnings, source_filename, app_version)
    md     = _render_markdown(findings, warnings, source_filename, app_version)

    return InterpretationResult(text=plain, markdown=md, findings=findings, warnings=warnings)


# ---------------------------------------------------------------------------
# Individual interpretation steps
# ---------------------------------------------------------------------------

def _interpret_global(
    df: pd.DataFrame,
    summary: dict,
    findings: list[str],
    warnings: list[str],
) -> None:
    n_clean   = summary.get("points_clean", len(df))
    n_removed = summary.get("points_removed", 0)
    pct_rem   = summary.get("percent_removed", 0.0)

    findings.append(
        f"The cleaned dataset contains {n_clean} valid measurement points "
        f"after the cleaning pipeline removed {n_removed} points ({pct_rem:.1f}%)."
    )

    if pct_rem > 20:
        warnings.append(
            f"A significant fraction of points ({pct_rem:.1f}%) was removed during "
            "cleaning. Results should be interpreted with caution. Consider reviewing "
            "the raw data and removed_points.csv."
        )
    elif pct_rem > 5:
        warnings.append(
            f"Some outlier points ({pct_rem:.1f}%) were removed. "
            "This is within a normal range but the removed_points.csv is available for review."
        )


def _interpret_impedance_character(df: pd.DataFrame, findings: list[str]) -> None:
    if COL_THETA not in df.columns:
        return
    theta = pd.to_numeric(df[COL_THETA], errors="coerce").dropna()
    if theta.empty:
        return

    median_theta = theta.median()
    std_theta    = theta.std()

    if median_theta > -10:
        char = "predominantly resistive"
        detail = (
            "The median phase angle is near 0°, which is consistent with "
            "resistive behavior dominating the response."
        )
    elif median_theta < -70:
        char = "predominantly capacitive"
        detail = (
            "The median phase angle approaches −90°, suggesting that "
            "capacitive impedance may be the dominant contribution."
        )
    else:
        char = "mixed resistive-capacitive"
        detail = (
            "The median phase angle is between 0° and −90°, suggesting a "
            "mixed resistive-capacitive character."
        )

    findings.append(
        f"The impedance response appears {char} (median θ ≈ {median_theta:.1f}°). "
        f"{detail}"
    )

    if std_theta > 20:
        findings.append(
            f"The phase angle shows substantial dispersion (σ ≈ {std_theta:.1f}°), "
            "which may indicate frequency-dependent behaviour, relaxation effects, "
            "or distributed-parameter contributions."
        )


def _interpret_nyquist_shape(df: pd.DataFrame, findings: list[str]) -> None:
    if COL_Z_REAL not in df.columns or COL_MZ_IMG not in df.columns:
        return
    zr   = pd.to_numeric(df[COL_Z_REAL], errors="coerce").dropna()
    mzim = pd.to_numeric(df[COL_MZ_IMG], errors="coerce").dropna()

    if zr.empty or mzim.empty:
        return

    # Estimate aspect ratio of the Nyquist arc
    z_range   = zr.max() - zr.min()
    mzi_range = mzim.max() - mzim.min()

    if mzi_range > 0 and z_range > 0:
        aspect = mzi_range / z_range
        if aspect > 0.6:
            findings.append(
                "The Nyquist plot appears to describe a significant arc in the "
                "−Z'' direction, which is consistent with a capacitive loop or "
                "charge-transfer process."
            )
        else:
            findings.append(
                "The Nyquist trajectory appears relatively flat, suggesting that "
                "the resistive contribution may be the primary spectral feature "
                "over the measured frequency range."
            )

    # Minimum offset (intercept suggests series resistance)
    zr_min = float(zr.min())
    if zr_min > 0:
        findings.append(
            f"The minimum Z' value is approximately {zr_min:.2f} Ω, which "
            "may be consistent with a finite series resistance contribution."
        )


def _interpret_characteristic_frequency(df: pd.DataFrame, findings: list[str]) -> None:
    """Estimate the characteristic frequency at the apex of the Nyquist arc."""
    if COL_FREQ not in df.columns or COL_MZ_IMG not in df.columns:
        return
    f    = pd.to_numeric(df[COL_FREQ],   errors="coerce")
    mzim = pd.to_numeric(df[COL_MZ_IMG], errors="coerce")

    valid = pd.DataFrame({"f": f, "mzim": mzim}).dropna()
    if valid.empty or len(valid) < 3:
        return

    idx_max = valid["mzim"].idxmax()
    f_char  = float(valid.loc[idx_max, "f"])
    mzim_max = float(valid.loc[idx_max, "mzim"])

    if mzim_max > 0:
        findings.append(
            f"The maximum −Z'' value of {mzim_max:.3g} Ω occurs near "
            f"{_fmt_freq(f_char)}, which may suggest a characteristic "
            "relaxation frequency associated with the dominant time constant."
        )


def _interpret_dc_bias_effect(df: pd.DataFrame, findings: list[str]) -> None:
    """Look for systematic variation with DC bias."""
    bias_levels = sorted(df[COL_DC].dropna().unique())
    if len(bias_levels) < 2:
        return

    findings.append(
        f"The dataset contains {len(bias_levels)} distinct DC bias conditions "
        f"({', '.join(_fmt_v(b) for b in bias_levels)}). "
        "Comparative Nyquist and Bode plots are available in the figures folder "
        "to assess how the impedance spectrum varies with bias."
    )

    # Try a simple check: does |Z_real| change with bias?
    try:
        z_by_bias = df.groupby(COL_DC)[COL_Z_REAL].median()
        z_range   = z_by_bias.max() - z_by_bias.min()
        z_mid     = z_by_bias.mean()
        if z_mid > 0 and z_range / z_mid > 0.15:
            findings.append(
                "The median Z' appears to change with DC bias level "
                f"(range ≈ {z_range:.3g} Ω), which may indicate "
                "a bias-dependent impedance response."
            )
        else:
            findings.append(
                "No strong variation in median Z' was detected across the DC bias "
                "conditions. The impedance response may be relatively stable with bias."
            )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _render_text(
    findings: list[str],
    warnings: list[str],
    source: str,
    version: str,
) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "=" * 72,
        "  SynAptIp Nyquist Analyzer V3.5 — Analysis Report",
        "  SynAptIp Technologies",
        "=" * 72,
        f"  Generated : {ts}",
        f"  Source    : {source}",
        f"  Version   : {version}",
        "=" * 72,
        "",
        "FINDINGS",
        "--------",
    ]
    for i, f in enumerate(findings, 1):
        lines.append(f"  [{i}] {f}")
    if warnings:
        lines += ["", "CAUTIONS", "--------"]
        for w in warnings:
            lines.append(f"  [!] {w}")
    lines += [
        "",
        "DISCLAIMER",
        "----------",
        "  This report is generated automatically from numerical analysis.",
        "  All statements use cautious, hedged language and should not be",
        "  treated as definitive engineering or scientific conclusions.",
        "  Human expert review is recommended for critical applications.",
        "",
        "=" * 72,
    ]
    return "\n".join(lines)


def _render_markdown(
    findings: list[str],
    warnings: list[str],
    source: str,
    version: str,
) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# SynAptIp Nyquist Analyzer V3.5 — Analysis Report",
        "",
        "**SynAptIp Technologies**",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Generated | {ts} |",
        f"| Source | `{source}` |",
        f"| Version | {version} |",
        "",
        "---",
        "",
        "## Findings",
        "",
    ]
    for i, f in enumerate(findings, 1):
        lines.append(f"{i}. {f}")
    if warnings:
        lines += ["", "## Cautions", ""]
        for w in warnings:
            lines.append(f"> **Note:** {w}")
    lines += [
        "",
        "---",
        "",
        "## Disclaimer",
        "",
        "This report is generated automatically from numerical analysis. "
        "All statements use cautious, hedged language and should not be treated "
        "as definitive engineering or scientific conclusions. "
        "Human expert review is recommended for critical applications.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _fmt_freq(f: float) -> str:
    if f >= 1e6:
        return f"{f / 1e6:.3g} MHz"
    if f >= 1e3:
        return f"{f / 1e3:.3g} kHz"
    return f"{f:.3g} Hz"


def _fmt_v(v: float) -> str:
    return f"{v:.3g} V"
