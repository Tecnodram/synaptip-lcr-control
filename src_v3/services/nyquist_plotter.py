"""
nyquist_plotter.py — V3 Nyquist Plot Generator
SynAptIp Technologies

Generates individual and comparison Nyquist plots as JPG files
using matplotlib.  All rendering is isolated here so the UI
only calls high-level functions.

Filenames include a timestamp so repeated exports never overwrite:
  <stem>_nyquist_YYYYMMDD_HHMMSS.jpg
  nyquist_compare_YYYYMMDD_HHMMSS.jpg

Autozoom uses global min/max across all series with a 10% margin.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from services.file_loader import NyquistDataset
from services.plot_view_helpers import compute_axis_limits, series_color, nice_axis_label

try:
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend — safe for GUI thread
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


_BRAND = "SynAptIp Technologies"
_DPI = 150


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def plot_individual(
    dataset: NyquistDataset,
    output_dir: str | Path,
    stem: str | None = None,
) -> Path:
    """
    Render a single Nyquist plot and save it as a JPG.

    Output: <stem>_nyquist_YYYYMMDD_HHMMSS.jpg
    """
    if not MATPLOTLIB_AVAILABLE:
        raise RuntimeError("matplotlib is not installed. Run: pip install matplotlib")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    file_stem = stem or dataset.file_path.stem
    out_path = out_dir / f"{file_stem}_nyquist_{_timestamp()}.jpg"

    xlabel, ylabel = nice_axis_label()
    x_min, x_max, y_min, y_max = compute_axis_limits([dataset])

    fig, ax = plt.subplots(figsize=(8, 6), dpi=_DPI)
    ax.plot(
        dataset.z_real,
        dataset.minus_z_imag,
        marker="o",
        markersize=4,
        linewidth=1.4,
        color=series_color(0),
        label=dataset.label,
    )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(
        f"Nyquist Plot — {dataset.label}",
        fontsize=13,
        fontweight="bold",
    )
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.text(
        0.99, 0.01, _BRAND,
        ha="right", va="bottom", fontsize=7, color="#9ca3af",
    )

    fig.tight_layout()
    fig.savefig(str(out_path), format="jpeg", dpi=300, bbox_inches="tight")
    plt.close(fig)

    return out_path


def plot_comparison(
    datasets: list[NyquistDataset],
    output_dir: str | Path,
    filename: str | None = None,
) -> Path:
    """
    Render an overlay comparison of 2–3 datasets and save as JPG.

    Output: nyquist_compare_YYYYMMDD_HHMMSS.jpg
    """
    if not MATPLOTLIB_AVAILABLE:
        raise RuntimeError("matplotlib is not installed. Run: pip install matplotlib")

    active = [ds for ds in datasets if ds.has_data]
    if not active:
        raise ValueError("No datasets with valid data to plot")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = filename or f"nyquist_compare_{_timestamp()}.jpg"
    out_path = out_dir / fname

    xlabel, ylabel = nice_axis_label()
    x_min, x_max, y_min, y_max = compute_axis_limits(active)

    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=_DPI)

    for idx, ds in enumerate(active):
        ax.plot(
            ds.z_real,
            ds.minus_z_imag,
            marker="o",
            markersize=3.5,
            linewidth=1.4,
            color=series_color(idx),
            label=ds.label,
        )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title("Nyquist Comparison", fontsize=13, fontweight="bold")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.text(
        0.99, 0.01, _BRAND,
        ha="right", va="bottom", fontsize=7, color="#9ca3af",
    )

    fig.tight_layout()
    fig.savefig(str(out_path), format="jpeg", dpi=300, bbox_inches="tight")
    plt.close(fig)

    return out_path
