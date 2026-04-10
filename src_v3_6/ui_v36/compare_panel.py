"""
compare_panel.py — Compare Tab — SynAptIp V3.6
SynAptIp Technologies

Multi-file EIS comparison panel.
Supports loading up to 3 CSV files and comparing them across all
plot types available in the application's analysis pipeline.

Plot types available:
  1. Nyquist                    Z' vs −Z'' overlay
  2. Bode — |Z|                 Frequency vs |Z| log-log
  3. Bode — Phase               Frequency vs Phase semilog
  4. Z' vs Frequency            Resistive component vs frequency
  5. −Z'' vs Frequency          Reactive component vs frequency
  6. Admittance |Y|             Frequency vs |Y| semilog
  7. Admittance Phase           Frequency vs Phase(Y) semilog
  8. Capacitance (Series)       Frequency vs C_series semilog
  9. Capacitance (Parallel)     Frequency vs C_parallel semilog
 10. Pattern Summary            New — dominant pattern across loaded files

Reuses without modification:
  - analysis_engine.schema_detector  (column detection)
  - analysis_engine.eis_transformer  (EIS transformations)
  - matplotlib Agg (same backend as V3.5 plot_engine)

Never raises exceptions to the main window.
"""
from __future__ import annotations

import io
import traceback
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.backends.backend_agg import FigureCanvasAgg

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QComboBox,
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

# V3.5 analysis_engine — imported without modification
from analysis_engine.schema_detector import detect_schema
from analysis_engine.eis_transformer import (
    COL_FREQ,
    COL_Z_REAL,
    COL_Z_IMAG,
    COL_MZ_IMG,
    COL_Z_MAG,
    COL_THETA,
    COL_Y_MAG,
    COL_Y_PHS,
    COL_C_SER,
    COL_C_PAR,
    COL_DC,
    transform,
)


# ---------------------------------------------------------------------------
# Visual style — restrained scientific palette
# ---------------------------------------------------------------------------
# Three files are differentiated by: color + line style + marker shape.
# This guarantees readability even in greyscale or with colour-vision deficiency.

_FILE_STYLES = [
    {"color": "#1d4ed8", "ls": "-",   "marker": "o",  "lw": 1.4},  # blue  solid  circle
    {"color": "#b45309", "ls": "--",  "marker": "s",  "lw": 1.4},  # amber dashed square
    {"color": "#065f46", "ls": ":",   "marker": "^",  "lw": 1.6},  # teal  dotted triangle
]
_MARKER_SIZE   = 4
_MARKER_EDGE_W = 0.3
_MARKER_EDGE_C = "white"
_GRID_STYLE    = dict(linestyle="--", linewidth=0.4, alpha=0.55)
_WATERMARK     = "SynAptIp Technologies"
_DPI           = 130
_FIG_W, _FIG_H = 9.0, 5.8

_MAX_SLOTS = 3


# ---------------------------------------------------------------------------
# Available plot types — order defines dropdown order
# ---------------------------------------------------------------------------

PLOT_TYPES: list[tuple[str, str]] = [
    ("nyquist",             "Nyquist"),
    ("bode_mag",            "Bode — |Z|"),
    ("bode_phase",          "Bode — Phase"),
    ("z_real_freq",         "Z' vs Frequency"),
    ("mz_imag_freq",        "−Z'' vs Frequency"),
    ("admittance_mag",      "Admittance |Y|"),
    ("admittance_phase",    "Admittance Phase"),
    ("cap_series",          "Capacitance (Series)"),
    ("cap_parallel",        "Capacitance (Parallel)"),
    ("pattern_summary",     "Pattern Summary"),
]

_PLOT_ID_TO_LABEL = {pid: lbl for pid, lbl in PLOT_TYPES}


# ---------------------------------------------------------------------------
# Shared plot helpers
# ---------------------------------------------------------------------------

def _finite_xy(
    df: pd.DataFrame, cx: str, cy: str
) -> tuple[np.ndarray, np.ndarray]:
    """Return finite-only (x, y) arrays from two DataFrame columns."""
    x = pd.to_numeric(df.get(cx, pd.Series(dtype=float)), errors="coerce").values
    y = pd.to_numeric(df.get(cy, pd.Series(dtype=float)), errors="coerce").values
    mask = np.isfinite(x) & np.isfinite(y)
    return x[mask], y[mask]


def _style(i: int) -> dict:
    return _FILE_STYLES[i % len(_FILE_STYLES)]


def _watermark(fig) -> None:
    fig.text(
        0.99, 0.01, _WATERMARK,
        ha="right", va="bottom",
        fontsize=7.5, color="#cbd5e1",
        transform=fig.transFigure,
        style="italic",
    )


def _finish_nyquist(ax, fig, title: str, legend: bool = True) -> None:
    ax.set_xlabel("Z' / Ω", fontsize=10)
    ax.set_ylabel("−Z'' / Ω", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    ax.grid(True, **_GRID_STYLE)
    if legend:
        ax.legend(fontsize=8, framealpha=0.92)
    _style_spines(ax)
    _watermark(fig)
    fig.tight_layout()


def _finish_freq(
    ax, fig, title: str, ylabel: str,
    legend: bool = True,
    log_x: bool = True,
    log_y: bool = False,
) -> None:
    if log_x:
        ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")
    ax.set_xlabel("Frequency / Hz", fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    ax.grid(True, which="both", **_GRID_STYLE)
    if legend:
        ax.legend(fontsize=8, framealpha=0.92)
    _style_spines(ax)
    _watermark(fig)
    fig.tight_layout()


def _style_spines(ax) -> None:
    for sp in ax.spines.values():
        sp.set_edgecolor("#d1d5db")
    ax.tick_params(labelsize=9, colors="#374151")


def _new_fig() -> tuple:
    return plt.subplots(figsize=(_FIG_W, _FIG_H), dpi=_DPI)


def _fig_to_png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def _has_col(df: pd.DataFrame, col: str) -> bool:
    return col in df.columns and df[col].notna().any()


def _file_label(slot_idx: int, path: Optional[Path], max_chars: int = 22) -> str:
    if path is None:
        return f"File {slot_idx + 1}"
    name = path.stem
    if len(name) > max_chars:
        name = name[:max_chars - 1] + "…"
    return name


# ---------------------------------------------------------------------------
# Per-file comparison plot helpers
# ---------------------------------------------------------------------------

def _plot_freq_compare(
    datasets: list[tuple[str, pd.DataFrame]],
    col_y: str,
    ylabel: str,
    title: str,
    log_y: bool = False,
) -> tuple[bytes, list[str]]:
    """
    Generic frequency-domain comparison plot.
    Overlays one line per file. Skips files missing the required column.
    """
    fig, ax = _new_fig()
    log_lines: list[str] = []
    plotted = 0

    for i, (label, df) in enumerate(datasets):
        if not _has_col(df, col_y) or not _has_col(df, COL_FREQ):
            log_lines.append(f"[SKIP] {label} — column '{col_y}' not available")
            continue

        f, y = _finite_xy(df, COL_FREQ, col_y)
        if len(f) == 0:
            log_lines.append(f"[SKIP] {label} — no finite data")
            continue

        st = _style(i)
        idx = np.argsort(f)
        ax.plot(
            f[idx], y[idx],
            linestyle=st["ls"],
            linewidth=st["lw"],
            marker=st["marker"],
            markersize=_MARKER_SIZE,
            markeredgewidth=_MARKER_EDGE_W,
            markeredgecolor=_MARKER_EDGE_C,
            color=st["color"],
            label=label,
        )
        log_lines.append(f"[OK] {label} — {len(f)} points")
        plotted += 1

    _finish_freq(ax, fig, title, ylabel, legend=plotted > 0, log_y=log_y)

    if plotted == 0:
        ax.text(0.5, 0.5, "No data available", transform=ax.transAxes,
                ha="center", va="center", color="#94a3b8", fontsize=11)

    return _fig_to_png(fig), log_lines


# ---------------------------------------------------------------------------
# Individual plot generators
# ---------------------------------------------------------------------------

def _plot_nyquist(
    datasets: list[tuple[str, pd.DataFrame]],
    output_dir: Optional[Path],
) -> tuple[bytes, str]:
    fig, ax = _new_fig()
    log_lines: list[str] = []
    plotted = 0

    for i, (label, df) in enumerate(datasets):
        if not _has_col(df, COL_Z_REAL) or not _has_col(df, COL_MZ_IMG):
            log_lines.append(f"[SKIP] {label} — no Z_real / −Z_imag columns")
            continue

        st = _style(i)

        if _has_col(df, COL_DC):
            groups = sorted(df[COL_DC].dropna().unique())
        else:
            groups = []

        if groups:
            for j, bv in enumerate(groups):
                g = df[df[COL_DC] == bv]
                zr, mzi = _finite_xy(g, COL_Z_REAL, COL_MZ_IMG)
                if len(zr) == 0:
                    continue
                suffix = f" | {bv:.3g}V" if len(groups) > 1 else ""
                ax.plot(
                    zr, mzi,
                    linestyle=st["ls"],
                    linewidth=st["lw"],
                    marker=st["marker"],
                    markersize=_MARKER_SIZE,
                    markeredgewidth=_MARKER_EDGE_W,
                    markeredgecolor=_MARKER_EDGE_C,
                    color=st["color"],
                    alpha=max(0.55, 1.0 - j * 0.18),
                    label=f"{label}{suffix}",
                )
        else:
            zr, mzi = _finite_xy(df, COL_Z_REAL, COL_MZ_IMG)
            if len(zr) == 0:
                log_lines.append(f"[SKIP] {label} — no finite Nyquist data")
                continue
            ax.plot(
                zr, mzi,
                linestyle=st["ls"],
                linewidth=st["lw"],
                marker=st["marker"],
                markersize=_MARKER_SIZE,
                markeredgewidth=_MARKER_EDGE_W,
                markeredgecolor=_MARKER_EDGE_C,
                color=st["color"],
                label=label,
            )

        n_bias = len(groups) if groups else 1
        log_lines.append(
            f"[OK] {label} — {len(df)} rows | {n_bias} DC bias group(s)"
        )
        plotted += 1

    _finish_nyquist(ax, fig, "Nyquist Comparison — SynAptIp V3.6", legend=plotted > 0)

    if plotted == 0:
        ax.text(0.5, 0.5, "No Nyquist data available",
                transform=ax.transAxes, ha="center", va="center",
                color="#94a3b8", fontsize=11)

    png = _fig_to_png(fig)

    if output_dir and plotted > 0:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "compare_nyquist.png").write_bytes(png)
            log_lines.append(f"[EXPORT] → {output_dir / 'compare_nyquist.png'}")
        except Exception:
            pass

    return png, "\n".join(log_lines)


def _plot_bode_mag(datasets, output_dir) -> tuple[bytes, str]:
    png, lines = _plot_freq_compare(
        datasets, COL_Z_MAG, "|Z| / Ω", "Bode — |Z| Comparison", log_y=True
    )
    if output_dir and png:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "compare_bode_mag.png").write_bytes(png)
        except Exception:
            pass
    return png, "\n".join(lines)


def _plot_bode_phase(datasets, output_dir) -> tuple[bytes, str]:
    png, lines = _plot_freq_compare(
        datasets, COL_THETA, "Phase / °", "Bode — Phase Comparison"
    )
    if output_dir and png:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "compare_bode_phase.png").write_bytes(png)
        except Exception:
            pass
    return png, "\n".join(lines)


def _plot_z_real_freq(datasets, output_dir) -> tuple[bytes, str]:
    png, lines = _plot_freq_compare(
        datasets, COL_Z_REAL, "Z' / Ω", "Z' vs Frequency — Comparison"
    )
    if output_dir and png:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "compare_z_real_freq.png").write_bytes(png)
        except Exception:
            pass
    return png, "\n".join(lines)


def _plot_mz_imag_freq(datasets, output_dir) -> tuple[bytes, str]:
    png, lines = _plot_freq_compare(
        datasets, COL_MZ_IMG, "-Z'' / Ohm", "-Z'' vs Frequency - Comparison"
    )
    if output_dir and png:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "compare_mz_imag_freq.png").write_bytes(png)
        except Exception:
            pass
    return png, "\n".join(lines)


def _plot_admittance_mag(datasets, output_dir) -> tuple[bytes, str]:
    png, lines = _plot_freq_compare(
        datasets, COL_Y_MAG, "|Y| / S", "Admittance |Y| — Comparison"
    )
    if output_dir and png:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "compare_admittance_mag.png").write_bytes(png)
        except Exception:
            pass
    return png, "\n".join(lines)


def _plot_admittance_phase(datasets, output_dir) -> tuple[bytes, str]:
    png, lines = _plot_freq_compare(
        datasets, COL_Y_PHS, "Phase(Y) / °", "Admittance Phase — Comparison"
    )
    if output_dir and png:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "compare_admittance_phase.png").write_bytes(png)
        except Exception:
            pass
    return png, "\n".join(lines)


def _plot_cap_series(datasets, output_dir) -> tuple[bytes, str]:
    png, lines = _plot_freq_compare(
        datasets, COL_C_SER, "C_series / F", "Capacitance (Series) — Comparison"
    )
    if output_dir and png:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "compare_cap_series.png").write_bytes(png)
        except Exception:
            pass
    return png, "\n".join(lines)


def _plot_cap_parallel(datasets, output_dir) -> tuple[bytes, str]:
    png, lines = _plot_freq_compare(
        datasets, COL_C_PAR, "C_parallel / F", "Capacitance (Parallel) — Comparison"
    )
    if output_dir and png:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "compare_cap_parallel.png").write_bytes(png)
        except Exception:
            pass
    return png, "\n".join(lines)


# ---------------------------------------------------------------------------
# NEW PLOT: Predominant Pattern Summary
# ---------------------------------------------------------------------------

def _compute_file_metrics(label: str, df: pd.DataFrame) -> Optional[dict]:
    """
    Derive key scalar metrics from a single loaded dataset.

    Metrics (all computed from existing EIS columns, no new analysis):
      f_char   — characteristic frequency: freq at peak −Z'' (RC time constant indicator)
      tau      — time constant: 1 / (2π · f_char)  [seconds]
      r_dc     — DC resistance estimate: max(Z') across all frequencies  [Ω]
      peak_mzi — peak value of −Z'' (semicircle height)  [Ω]
      z_mid    — |Z| at f_char  [Ω]
      behavior — qualitative label: "High-f dominant", "Mid-f dominant", "Low-f dominant"

    Returns None if insufficient data.
    """
    if not _has_col(df, COL_MZ_IMG) or not _has_col(df, COL_FREQ):
        return None

    f   = pd.to_numeric(df[COL_FREQ],   errors="coerce")
    mzi = pd.to_numeric(df[COL_MZ_IMG], errors="coerce")

    valid = pd.DataFrame({"f": f, "mzi": mzi}).dropna()
    valid = valid[valid["f"] > 0].reset_index(drop=True)
    if len(valid) < 3:
        return None

    # Characteristic frequency = freq at maximum −Z''
    peak_idx  = valid["mzi"].idxmax()
    f_char    = float(valid.loc[peak_idx, "f"])
    peak_mzi  = float(valid.loc[peak_idx, "mzi"])
    tau       = 1.0 / (2.0 * np.pi * f_char) if f_char > 0 else float("nan")

    # DC resistance estimate
    r_dc = float(pd.to_numeric(df.get(COL_Z_REAL, pd.Series(dtype=float)),
                               errors="coerce").max()) if _has_col(df, COL_Z_REAL) else float("nan")

    # |Z| at f_char (nearest frequency point)
    if _has_col(df, COL_Z_MAG):
        f_arr  = pd.to_numeric(df[COL_FREQ],  errors="coerce").values
        zmag   = pd.to_numeric(df[COL_Z_MAG], errors="coerce").values
        mask   = np.isfinite(f_arr) & np.isfinite(zmag)
        if mask.any():
            nearest = np.argmin(np.abs(f_arr[mask] - f_char))
            z_mid   = float(zmag[mask][nearest])
        else:
            z_mid = float("nan")
    else:
        z_mid = float("nan")

    # Qualitative behavior label based on f_char
    f_max = float(valid["f"].max())
    f_min = float(valid["f"].min())
    f_span = f_max / max(f_min, 1e-9)
    rel = (np.log10(f_char) - np.log10(f_min)) / max(np.log10(f_span), 1.0)
    if rel > 0.67:
        behavior = "High-f dominant"
    elif rel > 0.33:
        behavior = "Mid-f dominant"
    else:
        behavior = "Low-f dominant"

    return {
        "label":     label,
        "f_char":    f_char,
        "tau":       tau,
        "r_dc":      r_dc,
        "peak_mzi":  peak_mzi,
        "z_mid":     z_mid,
        "behavior":  behavior,
        "n_points":  len(valid),
    }


def _fmt_si(value: float, unit: str) -> str:
    """Format a float with SI prefix."""
    if not np.isfinite(value):
        return "—"
    abs_v = abs(value)
    if abs_v >= 1e9:
        return f"{value / 1e9:.3g} G{unit}"
    if abs_v >= 1e6:
        return f"{value / 1e6:.3g} M{unit}"
    if abs_v >= 1e3:
        return f"{value / 1e3:.3g} k{unit}"
    if abs_v >= 1.0:
        return f"{value:.3g} {unit}"
    if abs_v >= 1e-3:
        return f"{value * 1e3:.3g} m{unit}"
    if abs_v >= 1e-6:
        return f"{value * 1e6:.3g} u{unit}"
    if abs_v >= 1e-9:
        return f"{value * 1e9:.3g} n{unit}"
    return f"{value * 1e12:.3g} p{unit}"


def _plot_pattern_summary(
    datasets: list[tuple[str, pd.DataFrame]],
    output_dir: Optional[Path],
) -> tuple[bytes, str]:
    """
    Predominant Pattern Summary — new plot.

    3-panel figure:
      Left:   Nyquist overlay with f_char markers (★) per file
      Center: |Z| vs Frequency with vertical f_char lines
      Right:  Summary table (characteristic metrics per file)

    All data derived from existing EIS columns — no new analysis backend.
    """
    log_lines: list[str] = []

    # Compute metrics for each file
    metrics_list: list[Optional[dict]] = []
    for label, df in datasets:
        m = _compute_file_metrics(label, df)
        metrics_list.append(m)
        if m is None:
            log_lines.append(f"[SKIP] {label} — insufficient data for pattern analysis")
        else:
            log_lines.append(
                f"[OK] {label} — f_char={_fmt_si(m['f_char'], 'Hz')} | "
                f"tau={_fmt_si(m['tau'], 's')} | "
                f"R_est={_fmt_si(m['r_dc'], 'Ohm')} | {m['behavior']}"
            )

    valid_metrics = [m for m in metrics_list if m is not None]

    # ---- Figure layout: 1 row × 3 columns ----
    fig = plt.figure(figsize=(13.0, 5.4), dpi=_DPI)
    gs  = fig.add_gridspec(1, 3, wspace=0.38, left=0.06, right=0.97,
                           top=0.88, bottom=0.13)
    ax_nyq  = fig.add_subplot(gs[0, 0])
    ax_bode = fig.add_subplot(gs[0, 1])
    ax_tbl  = fig.add_subplot(gs[0, 2])
    ax_tbl.axis("off")

    any_plotted = False

    for i, ((label, df), m) in enumerate(zip(datasets, metrics_list)):
        st = _style(i)

        # --- Nyquist panel ---
        if _has_col(df, COL_Z_REAL) and _has_col(df, COL_MZ_IMG):
            zr, mzi = _finite_xy(df, COL_Z_REAL, COL_MZ_IMG)
            if len(zr) > 0:
                ax_nyq.plot(
                    zr, mzi,
                    linestyle=st["ls"], linewidth=1.2,
                    marker=st["marker"], markersize=3,
                    markeredgewidth=0.2, markeredgecolor="white",
                    color=st["color"], alpha=0.75,
                    label=label,
                )
                any_plotted = True

            # Mark f_char on Nyquist
            if m is not None and _has_col(df, COL_FREQ):
                f_arr   = pd.to_numeric(df[COL_FREQ],   errors="coerce").values
                zr_arr  = pd.to_numeric(df[COL_Z_REAL], errors="coerce").values
                mzi_arr = pd.to_numeric(df[COL_MZ_IMG], errors="coerce").values
                mask    = np.isfinite(f_arr) & np.isfinite(zr_arr) & np.isfinite(mzi_arr)
                if mask.any():
                    nearest = np.argmin(np.abs(f_arr[mask] - m["f_char"]))
                    xm = zr_arr[mask][nearest]
                    ym = mzi_arr[mask][nearest]
                    # Star marker: (5, 1, 0) = 5-pointed star via matplotlib path
                    ax_nyq.plot(
                        xm, ym,
                        marker=(5, 1, 0),
                        ms=10, color=st["color"], linestyle="none",
                        markeredgewidth=0.5, markeredgecolor="white",
                        zorder=5,
                    )

        # --- Bode |Z| panel ---
        if _has_col(df, COL_Z_MAG) and _has_col(df, COL_FREQ):
            f, zmag = _finite_xy(df, COL_FREQ, COL_Z_MAG)
            if len(f) > 0:
                idx = np.argsort(f)
                ax_bode.plot(
                    f[idx], zmag[idx],
                    linestyle=st["ls"], linewidth=1.2,
                    marker=st["marker"], markersize=3,
                    markeredgewidth=0.2, markeredgecolor="white",
                    color=st["color"],
                )
                # Vertical f_char line
                if m is not None:
                    ax_bode.axvline(
                        m["f_char"],
                        color=st["color"],
                        linewidth=0.8,
                        linestyle="-.",
                        alpha=0.6,
                    )

    # Nyquist panel finish
    ax_nyq.set_xlabel("Z' / Ω", fontsize=9)
    ax_nyq.set_ylabel("−Z'' / Ω", fontsize=9)
    ax_nyq.set_title("Nyquist + f★ markers", fontsize=10, fontweight="bold")
    ax_nyq.grid(True, **_GRID_STYLE)
    if any_plotted:
        ax_nyq.legend(fontsize=7, framealpha=0.9)
    _style_spines(ax_nyq)

    # Bode panel finish
    ax_bode.set_xscale("log")
    ax_bode.set_yscale("log")
    ax_bode.set_xlabel("Frequency / Hz", fontsize=9)
    ax_bode.set_ylabel("|Z| / Ω", fontsize=9)
    ax_bode.set_title("|Z| vs Freq — f★ = f_char", fontsize=10, fontweight="bold")
    ax_bode.grid(True, which="both", **_GRID_STYLE)
    _style_spines(ax_bode)

    # Summary table panel
    if valid_metrics:
        col_labels = ["File", "f_char", "tau", "R_est", "Behavior"]
        rows = []
        for m in valid_metrics:
            rows.append([
                m["label"][:18],
                _fmt_si(m["f_char"],   "Hz"),
                _fmt_si(m["tau"],      "s"),
                _fmt_si(m["r_dc"],     "Ω"),
                m["behavior"],
            ])

        tbl = ax_tbl.table(
            cellText=rows,
            colLabels=col_labels,
            cellLoc="center",
            loc="center",
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(7.5)
        tbl.scale(1.0, 1.55)

        # Header styling
        for c in range(len(col_labels)):
            tbl[0, c].set_facecolor("#1e3a5f")
            tbl[0, c].set_text_props(color="white", fontweight="bold")

        # Alternate row shading + file color hints
        for r_idx, m in enumerate(valid_metrics):
            row_bg = "#f8fafc" if r_idx % 2 == 0 else "#eef2f7"
            st     = _style(r_idx)
            for c in range(len(col_labels)):
                cell = tbl[r_idx + 1, c]
                cell.set_facecolor(row_bg)
                if c == 0:
                    # Colour file name cell with a faint tint
                    import matplotlib.colors as mc
                    rgba = mc.to_rgba(st["color"], alpha=0.15)
                    cell.set_facecolor(rgba)

        ax_tbl.set_title("Characteristic Metrics", fontsize=10, fontweight="bold", pad=8)
    else:
        ax_tbl.text(0.5, 0.5, "No data\navailable",
                    transform=ax_tbl.transAxes,
                    ha="center", va="center",
                    color="#94a3b8", fontsize=11)
        ax_tbl.set_title("Characteristic Metrics", fontsize=10, fontweight="bold", pad=8)

    fig.suptitle("Predominant Pattern Summary — SynAptIp V3.6",
                 fontsize=13, fontweight="bold", y=0.97)
    _watermark(fig)

    png = _fig_to_png(fig)

    if output_dir and valid_metrics:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "compare_pattern_summary.png").write_bytes(png)
            log_lines.append(f"[EXPORT] → {output_dir / 'compare_pattern_summary.png'}")
        except Exception:
            pass

    return png, "\n".join(log_lines)


# ---------------------------------------------------------------------------
# Plot dispatcher
# ---------------------------------------------------------------------------

_PLOT_DISPATCH = {
    "nyquist":          _plot_nyquist,
    "bode_mag":         _plot_bode_mag,
    "bode_phase":       _plot_bode_phase,
    "z_real_freq":      _plot_z_real_freq,
    "mz_imag_freq":     _plot_mz_imag_freq,
    "admittance_mag":   _plot_admittance_mag,
    "admittance_phase": _plot_admittance_phase,
    "cap_series":       _plot_cap_series,
    "cap_parallel":     _plot_cap_parallel,
    "pattern_summary":  _plot_pattern_summary,
}


# ---------------------------------------------------------------------------
# Slot widget — one CSV file slot
# ---------------------------------------------------------------------------

class _CsvSlot(QGroupBox):
    """One CSV file slot: label + browse button + clear button + status."""

    def __init__(self, index: int, parent: QWidget | None = None) -> None:
        super().__init__(f"CSV {index + 1}", parent)
        self._index = index
        self._path: Optional[Path] = None
        self._df:   Optional[pd.DataFrame] = None
        self._build_ui()

    def _build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setSpacing(4)

        top = QHBoxLayout()
        self._path_label = QLabel("— no file —")
        self._path_label.setObjectName("slotPathLabel")
        self._path_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        self._browse_btn = QPushButton("Load")
        self._browse_btn.setObjectName("slotBrowseBtn")
        self._browse_btn.setFixedWidth(70)
        self._browse_btn.clicked.connect(self._on_browse)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("slotClearBtn")
        self._clear_btn.setFixedWidth(60)
        self._clear_btn.setEnabled(False)
        self._clear_btn.clicked.connect(self._on_clear)

        top.addWidget(self._path_label)
        top.addWidget(self._browse_btn)
        top.addWidget(self._clear_btn)

        self._status = QLabel("")
        self._status.setObjectName("slotStatus")

        lay.addLayout(top)
        lay.addWidget(self._status)

    @property
    def path(self) -> Optional[Path]:
        return self._path

    @property
    def dataframe(self) -> Optional[pd.DataFrame]:
        return self._df

    @property
    def short_label(self) -> str:
        return _file_label(self._index, self._path)

    def clear(self) -> None:
        self._path = None
        self._df   = None
        self._path_label.setText("— no file —")
        self._status.setText("")
        self._clear_btn.setEnabled(False)

    def _on_browse(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            f"Select CSV {self._index + 1}",
            "",
            "CSV files (*.csv);;All files (*)",
        )
        if not path_str:
            return
        self._load(Path(path_str))

    def _on_clear(self) -> None:
        self.clear()

    def _load(self, path: Path) -> None:
        try:
            raw    = pd.read_csv(str(path))
            schema = detect_schema(raw)
            df     = transform(raw, schema)

            self._path = path
            self._df   = df
            self._path_label.setText(path.name)
            self._clear_btn.setEnabled(True)

            n      = len(df)
            has_z  = _has_col(df, COL_Z_REAL) and _has_col(df, COL_MZ_IMG)
            dc_txt = ""
            if _has_col(df, COL_DC):
                dc_vals = sorted(df[COL_DC].dropna().unique())
                dc_txt  = f" | DC: {[round(v, 3) for v in dc_vals]}"

            if has_z:
                self._status.setText(f"OK — {n} rows{dc_txt}")
                self._status.setStyleSheet("color: #065f46; font-size: 8pt;")
            else:
                self._status.setText(f"Warning — {n} rows, incomplete Z columns{dc_txt}")
                self._status.setStyleSheet("color: #92400e; font-size: 8pt;")

        except Exception as exc:
            self._path = None
            self._df   = None
            self._path_label.setText("— load error —")
            self._status.setText(f"Error: {exc}")
            self._status.setStyleSheet("color: #991b1b; font-size: 8pt;")
            self._clear_btn.setEnabled(False)


# ---------------------------------------------------------------------------
# Plot worker thread
# ---------------------------------------------------------------------------

class _PlotWorker(QThread):
    finished = Signal(bytes, str)
    error    = Signal(str)

    def __init__(
        self,
        plot_id: str,
        datasets: list[tuple[str, pd.DataFrame]],
        output_dir: Optional[Path],
    ) -> None:
        super().__init__()
        self._plot_id   = plot_id
        self._datasets  = datasets
        self._output_dir = output_dir

    def run(self) -> None:
        try:
            fn = _PLOT_DISPATCH.get(self._plot_id)
            if fn is None:
                self.error.emit(f"Unknown plot type: {self._plot_id}")
                return
            png, log = fn(self._datasets, self._output_dir)
            self.finished.emit(png, log)
        except Exception:
            self.error.emit(traceback.format_exc())


# ---------------------------------------------------------------------------
# Compare Panel — main widget
# ---------------------------------------------------------------------------

class ComparePanel(QWidget):
    """
    Self-contained 'Compare' tab.

    Supports:
    - 3 CSV slots (load / clear per slot)
    - Plot type selector (10 types)
    - Plot / Clear All / Export PNG buttons
    - In-app plot display
    - Log area
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._output_dir: Optional[Path] = None
        self._last_png:   Optional[bytes] = None
        self._worker:     Optional[_PlotWorker] = None
        self._last_datasets: list[tuple[str, pd.DataFrame]] = []
        self._build_ui()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def set_output_dir(self, path: Path) -> None:
        self._output_dir = path

    # ------------------------------------------------------------------ #
    # UI                                                                   #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(9)

        # Header
        hdr = QLabel("Compare — Multi-File EIS Overlay")
        hdr.setObjectName("comparePanelTitle")
        root.addWidget(hdr)

        # CSV slots
        slots_row = QHBoxLayout()
        slots_row.setSpacing(8)
        self._slots: list[_CsvSlot] = []
        for i in range(_MAX_SLOTS):
            slot = _CsvSlot(i, self)
            self._slots.append(slot)
            slots_row.addWidget(slot)
        root.addLayout(slots_row)

        # Plot selector + buttons
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        lbl = QLabel("Plot type:")
        lbl.setObjectName("compareSelectorLabel")

        self._selector = QComboBox()
        self._selector.setObjectName("comparePlotSelector")
        for pid, plabel in PLOT_TYPES:
            self._selector.addItem(plabel, pid)
        self._selector.setMinimumWidth(200)
        self._selector.currentIndexChanged.connect(self._on_selector_changed)

        self._plot_btn   = QPushButton("Plot")
        self._clear_btn  = QPushButton("Clear All")
        self._export_btn = QPushButton("Export PNG")

        self._plot_btn.setObjectName("comparePlotBtn")
        self._clear_btn.setObjectName("compareClearBtn")
        self._export_btn.setObjectName("compareExportBtn")
        self._export_btn.setEnabled(False)

        self._plot_btn.clicked.connect(self._on_plot)
        self._clear_btn.clicked.connect(self._on_clear_all)
        self._export_btn.clicked.connect(self._on_export)

        ctrl_row.addWidget(lbl)
        ctrl_row.addWidget(self._selector)
        ctrl_row.addSpacing(8)
        ctrl_row.addWidget(self._plot_btn)
        ctrl_row.addWidget(self._clear_btn)
        ctrl_row.addStretch(1)
        ctrl_row.addWidget(self._export_btn)
        root.addLayout(ctrl_row)

        # Plot display
        self._plot_label = QLabel("Load at least 1 CSV file, select a plot type, then click Plot.")
        self._plot_label.setObjectName("comparePlotArea")
        self._plot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._plot_label.setMinimumHeight(360)
        self._plot_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        root.addWidget(self._plot_label, stretch=1)

        # Log
        self._log = QTextEdit()
        self._log.setObjectName("compareLog")
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(80)
        root.addWidget(self._log)

    # ------------------------------------------------------------------ #
    # Handlers                                                             #
    # ------------------------------------------------------------------ #

    def _on_selector_changed(self, _idx: int) -> None:
        """Re-plot immediately if data is already loaded."""
        if self._last_datasets:
            self._run_plot(self._last_datasets)

    def _on_plot(self) -> None:
        datasets = [
            (slot.short_label, slot.dataframe)
            for slot in self._slots
            if slot.dataframe is not None
        ]
        if not datasets:
            QMessageBox.information(self, "Compare", "Load at least one CSV file first.")
            return
        self._last_datasets = datasets
        self._run_plot(datasets)

    def _run_plot(self, datasets: list[tuple[str, pd.DataFrame]]) -> None:
        plot_id = self._selector.currentData()
        plot_label = _PLOT_ID_TO_LABEL.get(plot_id, plot_id)

        self._log.setPlainText(f"Generating: {plot_label} …")
        self._plot_btn.setEnabled(False)
        self._export_btn.setEnabled(False)

        if self._worker and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait(500)

        self._worker = _PlotWorker(plot_id, datasets, self._output_dir)
        self._worker.finished.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_done(self, png: bytes, log_text: str) -> None:
        self._last_png = png
        self._log.setPlainText(log_text)
        self._show_png(png)
        self._plot_btn.setEnabled(True)
        self._export_btn.setEnabled(True)

    def _on_error(self, tb: str) -> None:
        self._log.setPlainText(f"Plot error:\n{tb}")
        self._plot_btn.setEnabled(True)

    def _on_clear_all(self) -> None:
        for slot in self._slots:
            slot.clear()
        self._plot_label.setText("Load at least 1 CSV file, select a plot type, then click Plot.")
        self._plot_label.setPixmap(QPixmap())
        self._log.clear()
        self._last_png = None
        self._last_datasets = []
        self._export_btn.setEnabled(False)

    def _on_export(self) -> None:
        if not self._last_png:
            return
        plot_id    = self._selector.currentData()
        default    = f"compare_{plot_id}.png"
        path_str, _ = QFileDialog.getSaveFileName(
            self, "Export PNG", default, "PNG (*.png)"
        )
        if not path_str:
            return
        try:
            Path(path_str).write_bytes(self._last_png)
            self._log.append(f"[EXPORT] Saved: {path_str}")
        except Exception as exc:
            QMessageBox.warning(self, "Export", f"Save failed: {exc}")

    # ------------------------------------------------------------------ #
    # Display helpers                                                       #
    # ------------------------------------------------------------------ #

    def _show_png(self, png: bytes) -> None:
        pix = QPixmap()
        pix.loadFromData(png, "PNG")
        if pix.isNull():
            self._plot_label.setText("Render error.")
            return
        self._scale_and_set(pix)

    def _scale_and_set(self, pix: QPixmap) -> None:
        scaled = pix.scaled(
            self._plot_label.width(),
            self._plot_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._plot_label.setPixmap(scaled)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._last_png:
            pix = QPixmap()
            pix.loadFromData(self._last_png, "PNG")
            if not pix.isNull():
                self._scale_and_set(pix)
