"""
plot_view_helpers.py — V3 Axis / View Helpers
SynAptIp Technologies

Utility functions for computing axis limits and plot metadata.
"""
from __future__ import annotations

import math


SERIES_COLORS = [
    "#1d4ed8",  # blue
    "#b45309",  # amber
    "#065f46",  # green
]


def compute_axis_limits(
    datasets: list,
    margin_fraction: float = 0.10,
) -> tuple[float, float, float, float]:
    """
    Return (x_min, x_max, y_min, y_max) that fit all curves.

    Computes global min/max across ALL loaded datasets then adds
    `margin_fraction` (default 10%) of the data span on each side.
    Safe when all values are identical (span → 1.0 fallback).

    `datasets` should be a list of NyquistDataset objects with valid data.
    """
    all_x: list[float] = []
    all_y: list[float] = []

    for ds in datasets:
        if ds.has_data:
            all_x.extend(ds.z_real)
            all_y.extend(ds.minus_z_imag)

    if not all_x:
        return 0.0, 1.0, 0.0, 1.0

    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)

    x_span = x_max - x_min or 1.0
    y_span = y_max - y_min or 1.0

    pad_x = x_span * margin_fraction
    pad_y = y_span * margin_fraction

    return x_min - pad_x, x_max + pad_x, y_min - pad_y, y_max + pad_y


def series_color(index: int) -> str:
    """Return a plot color for series at the given index."""
    return SERIES_COLORS[index % len(SERIES_COLORS)]


def nice_axis_label(unit: str = "Ω") -> tuple[str, str]:
    """Return (xlabel, ylabel) for a Nyquist plot."""
    return f"Z' / {unit}", f"−Z'' / {unit}"
