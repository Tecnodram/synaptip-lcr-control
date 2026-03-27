"""
plot_engine.py — Professional EIS Plot Generator
SynAptIp Nyquist Analyzer V3.5
SynAptIp Technologies

Generates all plots in the V3.5 analysis suite.
Uses matplotlib (Agg backend) for PNG export.

Plot IDs match the Analysis & Insights checkbox keys:
    nyquist_clean_comparative
    nyquist_raw_vs_clean
    nyquist_individual_per_bias
    nyquist_freq_colored_per_bias
    nyquist_freq_colored_comparative
    bode_mag_comparative
    bode_phase_comparative
    bode_mag_individual
    bode_phase_individual
    z_real_vs_freq
    minus_z_imag_vs_freq
    admittance_mag
    admittance_phase
    capacitance_series
    capacitance_parallel
"""
from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# Use non-interactive Agg backend — safe for PyInstaller packaging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.figure import Figure

from analysis_engine.eis_transformer import (
    COL_FREQ,
    COL_Z_REAL,
    COL_Z_IMAG,
    COL_MZ_IMG,
    COL_Z_MAG,
    COL_THETA,
    COL_OMEGA,
    COL_G,
    COL_B,
    COL_Y_MAG,
    COL_Y_PHS,
    COL_C_SER,
    COL_C_PAR,
    COL_DC,
)


# ---------------------------------------------------------------------------
# Palette / theme constants
# ---------------------------------------------------------------------------
_BIAS_COLORS = [
    "#1d4ed8",   # blue
    "#b45309",   # amber
    "#065f46",   # teal
    "#7c3aed",   # violet
    "#dc2626",   # red
    "#0891b2",   # cyan
    "#d97706",   # orange
    "#059669",   # green
]

_WATERMARK = "SynAptIp Technologies"
_DPI_EXPORT = 150
_FIG_SIZE_SINGLE   = (8, 5.5)
_FIG_SIZE_COMPARE  = (10, 6.5)
_FIG_SIZE_DOUBLE   = (12, 5)          # side-by-side


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class PlotEngine:
    """
    Generates EIS plots and saves them as PNG files to *output_dir*.

    Usage::

        engine = PlotEngine(output_dir=Path("run_20250101/figures"))
        generated = engine.run(clean_df, raw_df=raw_df, selected={"nyquist_clean_comparative"})
        # generated is a dict of {plot_id: Path}
    """

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._generated: dict[str, Path] = {}

    # ------------------------------------------------------------------ #
    # Master dispatcher                                                    #
    # ------------------------------------------------------------------ #

    def run(
        self,
        clean_df: pd.DataFrame,
        *,
        raw_df: Optional[pd.DataFrame] = None,
        selected: Optional[set[str]] = None,
    ) -> dict[str, Path]:
        """
        Generate all selected plots.

        Parameters
        ----------
        clean_df : cleaned DataFrame from cleaning_pipeline
        raw_df   : original DataFrame (needed for raw vs clean plots)
        selected : set of plot IDs to generate; None = generate all

        Returns
        -------
        dict mapping plot_id -> saved Path
        """
        self._generated = {}

        if clean_df.empty:
            return self._generated

        # Detect DC bias groups
        has_dc = (COL_DC in clean_df.columns) and clean_df[COL_DC].notna().any()
        if has_dc:
            bias_groups = sorted(clean_df[COL_DC].dropna().unique())
        else:
            bias_groups = []

        def want(pid: str) -> bool:
            return selected is None or pid in selected

        # --- NYQUIST ---
        if want("nyquist_clean_comparative"):
            self._safe(self._nyquist_clean_comparative, clean_df, bias_groups)

        if want("nyquist_raw_vs_clean") and raw_df is not None:
            self._safe(self._nyquist_raw_vs_clean, raw_df, clean_df)

        if want("nyquist_individual_per_bias") and has_dc:
            for bv in bias_groups:
                g = clean_df[clean_df[COL_DC] == bv]
                self._safe(self._nyquist_individual, g, label=_bias_label(bv))
        elif want("nyquist_individual_per_bias"):
            self._safe(self._nyquist_individual, clean_df, label="all")

        if want("nyquist_freq_colored_per_bias") and has_dc:
            for bv in bias_groups:
                g = clean_df[clean_df[COL_DC] == bv]
                self._safe(self._nyquist_freq_colored, g,
                           label=_bias_label(bv), plot_id_suffix=f"_{_bias_label(bv)}")
        elif want("nyquist_freq_colored_per_bias"):
            self._safe(self._nyquist_freq_colored, clean_df, label="all")

        if want("nyquist_freq_colored_comparative") and has_dc:
            self._safe(self._nyquist_freq_colored_comparative, clean_df, bias_groups)
        elif want("nyquist_freq_colored_comparative"):
            self._safe(self._nyquist_freq_colored, clean_df, label="all",
                       plot_id_suffix="_comparative")

        # --- BODE ---
        if want("bode_mag_comparative"):
            self._safe(self._bode_mag_comparative, clean_df, bias_groups)
        if want("bode_phase_comparative"):
            self._safe(self._bode_phase_comparative, clean_df, bias_groups)

        if want("bode_mag_individual") and has_dc:
            for bv in bias_groups:
                g = clean_df[clean_df[COL_DC] == bv]
                self._safe(self._bode_mag_individual, g, label=_bias_label(bv))
        elif want("bode_mag_individual"):
            self._safe(self._bode_mag_individual, clean_df, label="all")

        if want("bode_phase_individual") and has_dc:
            for bv in bias_groups:
                g = clean_df[clean_df[COL_DC] == bv]
                self._safe(self._bode_phase_individual, g, label=_bias_label(bv))
        elif want("bode_phase_individual"):
            self._safe(self._bode_phase_individual, clean_df, label="all")

        # --- DOMAIN ---
        if want("z_real_vs_freq"):
            self._safe(self._z_real_vs_freq, clean_df, bias_groups)
        if want("minus_z_imag_vs_freq"):
            self._safe(self._minus_z_imag_vs_freq, clean_df, bias_groups)
        if want("admittance_mag"):
            self._safe(self._admittance_mag, clean_df, bias_groups)
        if want("admittance_phase"):
            self._safe(self._admittance_phase, clean_df, bias_groups)
        if want("capacitance_series"):
            self._safe(self._capacitance_series, clean_df, bias_groups)
        if want("capacitance_parallel"):
            self._safe(self._capacitance_parallel, clean_df, bias_groups)

        return self._generated

    # ------------------------------------------------------------------ #
    # Safety wrapper                                                       #
    # ------------------------------------------------------------------ #

    def _safe(self, fn, *args, **kwargs) -> None:
        """Call a plot function; silently skip on any error."""
        try:
            fn(*args, **kwargs)
        except Exception:
            pass  # fail gracefully — never crash the app

    # ------------------------------------------------------------------ #
    # Nyquist plots                                                        #
    # ------------------------------------------------------------------ #

    def _nyquist_clean_comparative(
        self, df: pd.DataFrame, bias_groups: list
    ) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_COMPARE)

        if bias_groups:
            for i, bv in enumerate(bias_groups):
                g = df[df[COL_DC] == bv]
                zr, mzi = _finite_pair(g, COL_Z_REAL, COL_MZ_IMG)
                ax.plot(zr, mzi, "o", ms=4,
                        color=_color(i), label=_bias_label(bv),
                        markeredgewidth=0.3, markeredgecolor="white",
                        linewidth=0.8)
        else:
            zr, mzi = _finite_pair(df, COL_Z_REAL, COL_MZ_IMG)
            ax.plot(zr, mzi, "o", ms=4, color=_color(0))

        _finish_nyquist(ax, fig, "Nyquist — Clean Data", bool(bias_groups))
        self._save(fig, "nyquist_clean_comparative")

    def _nyquist_raw_vs_clean(
        self, raw_df: pd.DataFrame, clean_df: pd.DataFrame
    ) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_COMPARE)

        zr_raw,  mzi_raw  = _finite_pair(raw_df,   COL_Z_REAL, COL_MZ_IMG)
        zr_cln,  mzi_cln  = _finite_pair(clean_df, COL_Z_REAL, COL_MZ_IMG)

        ax.plot(zr_raw,  mzi_raw,  "o", ms=4,  color="#94a3b8",
                label="Raw", alpha=0.55,
                markeredgewidth=0.2, markeredgecolor="white")
        ax.plot(zr_cln,  mzi_cln,  "o", ms=4,  color="#1d4ed8",
                label="Clean",
                markeredgewidth=0.3, markeredgecolor="white")

        _finish_nyquist(ax, fig, "Nyquist — Raw vs Clean", legend=True)
        self._save(fig, "nyquist_raw_vs_clean")

    def _nyquist_individual(
        self, df: pd.DataFrame, *, label: str
    ) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        zr, mzi = _finite_pair(df, COL_Z_REAL, COL_MZ_IMG)
        ax.plot(zr, mzi, "-", ms=4, marker="o", color=_color(0),
            linewidth=0.8, markeredgewidth=0.3, markeredgecolor="white")
        _finish_nyquist(ax, fig, f"Nyquist — {label}", legend=False)
        self._save(fig, f"nyquist_individual_{label}")

    def _nyquist_freq_colored(
        self,
        df: pd.DataFrame,
        *,
        label: str,
        plot_id_suffix: str = "",
    ) -> None:
        """Single-condition frequency-colored Nyquist with f_high / f_low annotations."""
        zr_s  = pd.to_numeric(df[COL_Z_REAL], errors="coerce")
        mzi_s = pd.to_numeric(df[COL_MZ_IMG], errors="coerce")
        f_s   = pd.to_numeric(df[COL_FREQ],   errors="coerce")

        valid = pd.DataFrame({"zr": zr_s, "mzi": mzi_s, "f": f_s}).dropna()
        if len(valid) < 2:
            return
        valid = valid.sort_values("f").reset_index(drop=True)

        zr  = valid["zr"].values
        mzi = valid["mzi"].values
        f   = valid["f"].values

        log_f = np.log10(f)
        norm  = mcolors.LogNorm(vmin=max(f.min(), 1e-3), vmax=f.max())
        cmap  = cm.get_cmap("plasma")

        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)

        # Connected trajectory as background line
        ax.plot(zr, mzi, "-", color="#d1d5db", linewidth=0.8, zorder=1)

        # Frequency-colored scatter
        sc = ax.scatter(zr, mzi, c=f, cmap=cmap, norm=norm,
                        s=30, zorder=2, edgecolors="white", linewidths=0.3)

        cbar = fig.colorbar(sc, ax=ax, pad=0.02)
        cbar.set_label("Frequency (Hz)", fontsize=9)

        # Annotations for lowest and highest frequency
        _annotate_freq_endpoint(ax, zr[0],  mzi[0],  f[0],  "f low")
        _annotate_freq_endpoint(ax, zr[-1], mzi[-1], f[-1], "f high")

        _finish_nyquist(ax, fig, f"Nyquist — Frequency Colored — {label}", legend=False)
        self._save(fig, f"nyquist_freq_colored{plot_id_suffix}_{label}")

    def _nyquist_freq_colored_comparative(
        self, df: pd.DataFrame, bias_groups: list
    ) -> None:
        """Overlay of frequency-colored Nyquist for each DC bias."""
        n = len(bias_groups)
        cols = min(n, 3)
        rows = math.ceil(n / cols)
        fig, axes = plt.subplots(rows, cols,
                                  figsize=(_FIG_SIZE_SINGLE[0] * cols,
                                           _FIG_SIZE_SINGLE[1] * rows),
                                  squeeze=False)

        for idx, bv in enumerate(bias_groups):
            ax = axes[idx // cols][idx % cols]
            g = df[df[COL_DC] == bv]

            zr_s  = pd.to_numeric(g[COL_Z_REAL], errors="coerce")
            mzi_s = pd.to_numeric(g[COL_MZ_IMG], errors="coerce")
            f_s   = pd.to_numeric(g[COL_FREQ],   errors="coerce")
            valid = pd.DataFrame({"zr": zr_s, "mzi": mzi_s, "f": f_s}).dropna()

            if len(valid) >= 2:
                valid = valid.sort_values("f").reset_index(drop=True)
                zr  = valid["zr"].values
                mzi = valid["mzi"].values
                f   = valid["f"].values
                norm = mcolors.LogNorm(vmin=max(f.min(), 1e-3), vmax=f.max())
                cmap = cm.get_cmap("plasma")
                ax.plot(zr, mzi, "-", color="#d1d5db", linewidth=0.8, zorder=1)
                ax.scatter(zr, mzi, c=f, cmap=cmap, norm=norm,
                           s=25, zorder=2, edgecolors="white", linewidths=0.3)
                _annotate_freq_endpoint(ax, zr[0],  mzi[0],  f[0],  "f low")
                _annotate_freq_endpoint(ax, zr[-1], mzi[-1], f[-1], "f high")

            _finish_nyquist(ax, fig, _bias_label(bv), legend=False, tight=False)

        # Hide extra axes
        for extra in range(n, rows * cols):
            axes[extra // cols][extra % cols].set_visible(False)

        fig.suptitle("Nyquist — Frequency Colored Comparative", fontsize=13, fontweight="bold", y=1.01)
        _watermark(fig)
        fig.tight_layout()
        self._save(fig, "nyquist_freq_colored_comparative")

    # ------------------------------------------------------------------ #
    # Bode plots                                                           #
    # ------------------------------------------------------------------ #

    def _bode_mag_comparative(
        self, df: pd.DataFrame, bias_groups: list
    ) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        _plot_bode_grouped(ax, df, bias_groups, COL_Z_MAG, "|Z| / Ω")
        ax.set_xscale("log"); ax.set_yscale("log")
        _finish_bode(ax, fig, "Bode — |Z| Comparative", bool(bias_groups))
        self._save(fig, "bode_mag_comparative")

    def _bode_phase_comparative(
        self, df: pd.DataFrame, bias_groups: list
    ) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        _plot_bode_grouped(ax, df, bias_groups, COL_THETA, "Phase / °")
        ax.set_xscale("log")
        _finish_bode(ax, fig, "Bode — Phase Comparative", bool(bias_groups))
        self._save(fig, "bode_phase_comparative")

    def _bode_mag_individual(
        self, df: pd.DataFrame, *, label: str
    ) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        f, y = _finite_pair(df, COL_FREQ, COL_Z_MAG)
        _sort_plot(ax, f, y, color=_color(0), marker="o")
        ax.set_xscale("log"); ax.set_yscale("log")
        _finish_bode(ax, fig, f"Bode — |Z| — {label}", legend=False, ylabel="|Z| / Ω")
        self._save(fig, f"bode_mag_individual_{label}")

    def _bode_phase_individual(
        self, df: pd.DataFrame, *, label: str
    ) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        f, y = _finite_pair(df, COL_FREQ, COL_THETA)
        _sort_plot(ax, f, y, color=_color(0), marker="o")
        ax.set_xscale("log")
        _finish_bode(ax, fig, f"Bode — Phase — {label}", legend=False, ylabel="Phase / °")
        self._save(fig, f"bode_phase_individual_{label}")

    # ------------------------------------------------------------------ #
    # Domain / derived plots                                               #
    # ------------------------------------------------------------------ #

    def _z_real_vs_freq(self, df: pd.DataFrame, bias_groups: list) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        _plot_bode_grouped(ax, df, bias_groups, COL_Z_REAL, "Z' / Ω")
        ax.set_xscale("log")
        _finish_bode(ax, fig, "Z' vs Frequency", bool(bias_groups), ylabel="Z' / Ω")
        self._save(fig, "z_real_vs_freq")

    def _minus_z_imag_vs_freq(self, df: pd.DataFrame, bias_groups: list) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        _plot_bode_grouped(ax, df, bias_groups, COL_MZ_IMG, "−Z'' / Ω")
        ax.set_xscale("log")
        _finish_bode(ax, fig, "−Z'' vs Frequency", bool(bias_groups), ylabel="−Z'' / Ω")
        self._save(fig, "minus_z_imag_vs_freq")

    def _admittance_mag(self, df: pd.DataFrame, bias_groups: list) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        _plot_bode_grouped(ax, df, bias_groups, COL_Y_MAG, "|Y| / S")
        ax.set_xscale("log")
        _finish_bode(ax, fig, "|Y| vs Frequency", bool(bias_groups), ylabel="|Y| / S")
        self._save(fig, "admittance_mag")

    def _admittance_phase(self, df: pd.DataFrame, bias_groups: list) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        _plot_bode_grouped(ax, df, bias_groups, COL_Y_PHS, "Phase(Y) / °")
        ax.set_xscale("log")
        _finish_bode(ax, fig, "Phase(Y) vs Frequency", bool(bias_groups), ylabel="Phase(Y) / °")
        self._save(fig, "admittance_phase")

    def _capacitance_series(self, df: pd.DataFrame, bias_groups: list) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        _plot_bode_grouped(ax, df, bias_groups, COL_C_SER, "C_series / F")
        ax.set_xscale("log")
        _finish_bode(ax, fig, "C_series vs Frequency", bool(bias_groups), ylabel="C_series / F")
        self._save(fig, "capacitance_series")

    def _capacitance_parallel(self, df: pd.DataFrame, bias_groups: list) -> None:
        fig, ax = plt.subplots(figsize=_FIG_SIZE_SINGLE)
        _plot_bode_grouped(ax, df, bias_groups, COL_C_PAR, "C_parallel / F")
        ax.set_xscale("log")
        _finish_bode(ax, fig, "C_parallel vs Frequency", bool(bias_groups), ylabel="C_parallel / F")
        self._save(fig, "capacitance_parallel")

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _save(self, fig: Figure, plot_id: str) -> None:
        fname = f"{plot_id}.png"
        fpath = self.output_dir / fname
        fig.savefig(fpath, dpi=_DPI_EXPORT, bbox_inches="tight")
        plt.close(fig)
        self._generated[plot_id] = fpath


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _color(index: int) -> str:
    return _BIAS_COLORS[index % len(_BIAS_COLORS)]


def _bias_label(bv: float) -> str:
    try:
        return f"{float(bv):.3g}V"
    except Exception:
        return str(bv)


def _finite_pair(
    df: pd.DataFrame, col_x: str, col_y: str
) -> tuple[np.ndarray, np.ndarray]:
    x = pd.to_numeric(df[col_x], errors="coerce").values
    y = pd.to_numeric(df[col_y], errors="coerce").values
    mask = np.isfinite(x) & np.isfinite(y)
    return x[mask], y[mask]


def _sort_plot(ax, x, y, **kw) -> None:
    idx = np.argsort(x)
    ax.plot(x[idx], y[idx], "-", ms=4, linewidth=0.8,
            marker="o", markeredgewidth=0.3, markeredgecolor="white", **kw)


def _annotate_freq_endpoint(ax, x, y, f, text: str) -> None:
    ax.annotate(
        f"{text}\n{_fmt_freq_short(f)}",
        xy=(x, y),
        xytext=(8, 6),
        textcoords="offset points",
        fontsize=7,
        color="#374151",
        arrowprops=dict(arrowstyle="->", lw=0.6, color="#6b7280"),
    )


def _fmt_freq_short(f: float) -> str:
    if f >= 1e6:
        return f"{f / 1e6:.2g} MHz"
    if f >= 1e3:
        return f"{f / 1e3:.2g} kHz"
    return f"{f:.2g} Hz"


def _plot_bode_grouped(ax, df, bias_groups, y_col, ylabel: str) -> None:
    if bias_groups:
        for i, bv in enumerate(bias_groups):
            g = df[df[COL_DC] == bv].copy()
            f, y = _finite_pair(g, COL_FREQ, y_col)
            if len(f) == 0:
                continue
            idx = np.argsort(f)
            ax.plot(f[idx], y[idx], "-", ms=4, marker="o",
                    color=_color(i), label=_bias_label(bv),
                    linewidth=0.8, markeredgewidth=0.3, markeredgecolor="white")
    else:
        f, y = _finite_pair(df, COL_FREQ, y_col)
        if len(f) > 0:
            idx = np.argsort(f)
            ax.plot(f[idx], y[idx], "-", ms=4, marker="o", color=_color(0),
                    linewidth=0.8, markeredgewidth=0.3, markeredgecolor="white")


def _watermark(fig: Figure, text: str = _WATERMARK) -> None:
    fig.text(
        0.99, 0.01, text,
        ha="right", va="bottom",
        fontsize=7.5, color="#cbd5e1",
        transform=fig.transFigure,
        style="italic",
    )


def _finish_nyquist(
    ax, fig: Figure, title: str, legend: bool = True, tight: bool = True
) -> None:
    ax.set_xlabel("Z' / Ω", fontsize=10)
    ax.set_ylabel("−Z'' / Ω", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    if legend:
        ax.legend(fontsize=8, framealpha=0.9)
    _style_spines(ax)
    _watermark(fig)
    if tight:
        fig.tight_layout()


def _finish_bode(
    ax, fig: Figure, title: str,
    legend: bool = True,
    ylabel: str = "",
    tight: bool = True,
) -> None:
    ax.set_xlabel("Frequency / Hz", fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    ax.grid(True, which="both", linestyle="--", linewidth=0.4, alpha=0.6)
    if legend:
        ax.legend(fontsize=8, framealpha=0.9)
    _style_spines(ax)
    _watermark(fig)
    if tight:
        fig.tight_layout()


def _style_spines(ax) -> None:
    for spine in ax.spines.values():
        spine.set_edgecolor("#d1d5db")
    ax.tick_params(labelsize=9, colors="#374151")
