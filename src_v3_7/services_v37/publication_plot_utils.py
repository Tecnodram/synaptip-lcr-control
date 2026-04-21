"""
publication_plot_utils.py — Publication-Grade Plotting Utilities
SynAptIp Nyquist Analyzer V3.7
SynAptIp Technologies

Centralized plotting configuration and utilities for scientific publication-quality
figures. Implements consistent styling, proper scientific formatting, and professional
export capabilities.

This module provides:
- apply_publication_style(): Centralized style configuration
- Enhanced Nyquist plotting with frequency progression
- Professional Bode plot formatting
- High-DPI export (PNG ≥300dpi, PDF vector)
- Scientific color schemes and typography
- Proper axis scaling and labeling for impedance spectroscopy

All functions maintain backward compatibility with existing plot data.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import warnings

import numpy as np
import pandas as pd

# Use non-interactive Agg backend — safe for GUI applications
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar

# ------------------------------------------------------------------------------
# PUBLICATION STYLE CONSTANTS
# ------------------------------------------------------------------------------
# Figure dimensions (inches) - optimized for scientific publications
FIG_SIZE_NYQUIST = (6.0, 4.5)      # Standard single-column width
FIG_SIZE_BODE = (6.0, 4.0)         # Bode plots (magnitude + phase)
FIG_SIZE_COMPARISON = (8.0, 5.5)   # Multi-dataset comparisons

# High-resolution DPI for publication quality
DPI_EXPORT_PNG = 300
DPI_EXPORT_PDF = 300  # Vector format, DPI affects raster elements

# Typography - professional scientific fonts
FONT_FAMILY = 'DejaVu Sans'  # Fallback to sans-serif
FONT_SIZE_TITLE = 12
FONT_SIZE_LABEL = 11
FONT_SIZE_TICK = 10
FONT_SIZE_LEGEND = 9
FONT_SIZE_ANNOTATION = 8

# Scientific color palette - colorblind-safe, high contrast
SCIENTIFIC_COLORS = [
    '#1f77b4',  # blue
    '#d62728',  # red
    '#2ca02c',  # green
    '#ff7f0e',  # orange
    '#9467bd',  # purple
    '#8c564b',  # brown
    '#e377c2',  # pink
    '#7f7f7f',  # gray
    '#bcbd22',  # olive
    '#17becf',  # cyan
]

# Frequency progression colormap for Nyquist plots
FREQ_COLORMAP = 'viridis'  # Perceptually uniform, colorblind-friendly

# Grid and spine styling
GRID_ALPHA = 0.3
GRID_LINESTYLE = '--'
GRID_LINEWIDTH = 0.5
SPINE_LINEWIDTH = 0.8
SPINE_COLOR = '#333333'

# Marker styling for data points
MARKER_SIZE = 4
MARKER_EDGE_WIDTH = 0.5
MARKER_ALPHA = 0.8

# Line styling
LINE_WIDTH = 1.5
LINE_ALPHA = 0.9

# ------------------------------------------------------------------------------
# CENTRALIZED STYLE APPLICATION
# ------------------------------------------------------------------------------
def apply_publication_style(
    fig: Figure,
    ax: Axes,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    use_grid: bool = True,
    use_legend: bool = True,
    legend_loc: str = 'best'
) -> None:
    """
    Apply publication-grade styling to matplotlib figure and axes.

    This function enforces consistent scientific formatting across all plots:
    - Professional typography and sizing
    - Clean layout with proper margins
    - High readability
    - Scientific color schemes
    - Proper axis formatting

    Parameters:
        fig: Matplotlib Figure object
        ax: Matplotlib Axes object
        title: Plot title (optional)
        xlabel: X-axis label (optional)
        ylabel: Y-axis label (optional)
        use_grid: Whether to show grid lines
        use_legend: Whether to show legend if available
        legend_loc: Legend location ('best', 'upper right', etc.)
    """
    # Set font properties globally
    plt.rcParams.update({
        'font.family': FONT_FAMILY,
        'font.size': FONT_SIZE_TICK,
        'axes.labelsize': FONT_SIZE_LABEL,
        'axes.titlesize': FONT_SIZE_TITLE,
        'xtick.labelsize': FONT_SIZE_TICK,
        'ytick.labelsize': FONT_SIZE_TICK,
        'legend.fontsize': FONT_SIZE_LEGEND,
        'figure.titlesize': FONT_SIZE_TITLE,
    })

    # Apply title if provided
    if title:
        ax.set_title(title, fontweight='bold', pad=10)

    # Apply axis labels if provided
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    # Style spines (axis borders)
    for spine in ax.spines.values():
        spine.set_linewidth(SPINE_LINEWIDTH)
        spine.set_color(SPINE_COLOR)

    # Configure grid
    if use_grid:
        ax.grid(True, alpha=GRID_ALPHA, linestyle=GRID_LINESTYLE,
                linewidth=GRID_LINEWIDTH, which='both')

    # Configure legend
    if use_legend and ax.get_legend_handles_labels()[1]:
        legend = ax.legend(loc=legend_loc, framealpha=0.9, fancybox=False,
                          edgecolor=SPINE_COLOR, fontsize=FONT_SIZE_LEGEND)
        legend.get_frame().set_linewidth(SPINE_LINEWIDTH)

    # Ensure tight layout
    fig.tight_layout()

# ------------------------------------------------------------------------------
# SCIENTIFIC AXIS FORMATTING
# ------------------------------------------------------------------------------
def format_frequency_axis(ax: Axes, use_log_scale: bool = True) -> None:
    """
    Format frequency axis with proper scientific scaling and labeling.

    Ensures frequency plots use log scale and have readable tick labels
    distributed across orders of magnitude.

    Parameters:
        ax: Matplotlib Axes object
        use_log_scale: Whether to use logarithmic scaling (default True)
    """
    if use_log_scale:
        ax.set_xscale('log')

    # Set major ticks at decade boundaries
    ax.xaxis.set_major_locator(plt.LogLocator(base=10.0, numticks=12))
    ax.xaxis.set_minor_locator(plt.LogLocator(base=10.0, subs=np.arange(2, 10),
                                               numticks=12))

    # Format tick labels to show Hz, kHz, MHz appropriately
    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_frequency_ticks))

def format_frequency_ticks(x: float, pos: int) -> str:
    """
    Format frequency tick labels with appropriate units.

    Converts raw frequency values to Hz, kHz, MHz with proper scaling.

    Parameters:
        x: Frequency value in Hz
        pos: Tick position (unused)

    Returns:
        Formatted string with appropriate unit
    """
    if x >= 1e6:
        return f'{x/1e6:.0f}M'
    elif x >= 1e3:
        return f'{x/1e3:.0f}k'
    else:
        return f'{x:.0f}'

# ------------------------------------------------------------------------------
# ENHANCED NYQUIST PLOTTING
# ------------------------------------------------------------------------------
def plot_nyquist_publication(
    z_real: np.ndarray,
    z_imag_neg: np.ndarray,
    frequencies: Optional[np.ndarray] = None,
    ax: Optional[Axes] = None,
    fig: Optional[Figure] = None,
    label: str = "",
    color: Optional[str] = None,
    show_frequency_progression: bool = True,
    show_colorbar: bool = False,
    marker_every: int = 10,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create publication-grade Nyquist plot with frequency progression indication.

    Features:
    - Correct Z' vs -Z'' convention
    - Optional frequency progression coloring
    - Professional markers and line styling
    - Scientific formatting

    Parameters:
        z_real: Real part of impedance (Z')
        z_imag_neg: Negative imaginary part (-Z'')
        frequencies: Frequency array for color progression (optional)
        ax: Existing axes object (optional)
        fig: Existing figure object (optional)
        label: Plot label for legend
        color: Override default color
        show_frequency_progression: Whether to color by frequency
        show_colorbar: Whether to display frequency colorbar
        marker_every: Plot marker every N points (0 = no markers)
        **kwargs: Additional plotting arguments

    Returns:
        Tuple of (Figure, Axes) objects
    """
    # Create figure if not provided
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=FIG_SIZE_NYQUIST, dpi=DPI_EXPORT_PNG)

    # Determine color scheme
    if show_frequency_progression and frequencies is not None:
        # Color by frequency progression
        norm = mcolors.LogNorm(vmin=frequencies.min(), vmax=frequencies.max())
        colors = cm.get_cmap(FREQ_COLORMAP)(norm(frequencies))

        # Plot with color progression
        for i in range(len(z_real) - 1):
            ax.plot(z_real[i:i+2], z_imag_neg[i:i+2],
                   color=colors[i], linewidth=LINE_WIDTH, alpha=LINE_ALPHA)

        # Add colorbar for frequency scale if requested
        if show_colorbar:
            sm = plt.cm.ScalarMappable(cmap=FREQ_COLORMAP, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.8, aspect=20)
            cbar.set_label('Frequency (Hz)', fontsize=FONT_SIZE_LABEL)
            cbar.ax.tick_params(labelsize=FONT_SIZE_TICK)

    else:
        # Single color plot
        plot_color = color or SCIENTIFIC_COLORS[0]

        # Plot line
        ax.plot(z_real, z_imag_neg, color=plot_color,
               linewidth=LINE_WIDTH, alpha=LINE_ALPHA, label=label, **kwargs)

        # Add markers if requested
        if marker_every > 0:
            marker_indices = np.arange(0, len(z_real), marker_every)
            ax.plot(z_real[marker_indices], z_imag_neg[marker_indices],
                   marker='o', markersize=MARKER_SIZE, markeredgewidth=MARKER_EDGE_WIDTH,
                   markerfacecolor=plot_color, markeredgecolor='white',
                   linestyle='None', alpha=MARKER_ALPHA)

    # Ensure equal aspect ratio for all Nyquist plots, including frequency progression
    ax.set_aspect('equal', adjustable='box')

    # Apply publication styling
    apply_publication_style(
        fig, ax,
        xlabel="Z' (Ω)",
        ylabel="-Z'' (Ω)",
        use_grid=True,
        use_legend=bool(label)
    )

    return fig, ax

# ------------------------------------------------------------------------------
# ENHANCED BODE PLOTTING
# ------------------------------------------------------------------------------
def plot_bode_magnitude_publication(
    frequencies: np.ndarray,
    magnitude: np.ndarray,
    ax: Optional[Axes] = None,
    fig: Optional[Figure] = None,
    label: str = "",
    color: Optional[str] = None,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create publication-grade Bode magnitude plot.

    Features:
    - Logarithmic frequency axis
    - Proper |Z| vs frequency formatting
    - Scientific units and scaling

    Parameters:
        frequencies: Frequency array in Hz
        magnitude: |Z| magnitude array in Ω
        ax: Existing axes object (optional)
        fig: Existing figure object (optional)
        label: Plot label for legend
        color: Override default color
        **kwargs: Additional plotting arguments

    Returns:
        Tuple of (Figure, Axes) objects
    """
    # Create figure if not provided
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=FIG_SIZE_BODE, dpi=DPI_EXPORT_PNG)

    plot_color = color or SCIENTIFIC_COLORS[0]

    # Plot magnitude vs frequency
    ax.plot(frequencies, magnitude, color=plot_color,
           linewidth=LINE_WIDTH, alpha=LINE_ALPHA, label=label, **kwargs)

    # Format frequency axis
    format_frequency_axis(ax, use_log_scale=True)

    # Format magnitude axis
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_impedance_ticks))

    # Apply publication styling
    apply_publication_style(
        fig, ax,
        xlabel="Frequency (Hz)",
        ylabel="|Z| (Ω)",
        use_grid=True,
        use_legend=bool(label)
    )

    return fig, ax

def plot_bode_phase_publication(
    frequencies: np.ndarray,
    phase: np.ndarray,
    ax: Optional[Axes] = None,
    fig: Optional[Figure] = None,
    label: str = "",
    color: Optional[str] = None,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create publication-grade Bode phase plot.

    Features:
    - Logarithmic frequency axis
    - Proper phase vs frequency formatting
    - Degree units with appropriate scaling

    Parameters:
        frequencies: Frequency array in Hz
        phase: Phase angle array in degrees
        ax: Existing axes object (optional)
        fig: Existing figure object (optional)
        label: Plot label for legend
        color: Override default color
        **kwargs: Additional plotting arguments

    Returns:
        Tuple of (Figure, Axes) objects
    """
    # Create figure if not provided
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=FIG_SIZE_BODE, dpi=DPI_EXPORT_PNG)

    plot_color = color or SCIENTIFIC_COLORS[0]

    # Plot phase vs frequency
    ax.plot(frequencies, phase, color=plot_color,
           linewidth=LINE_WIDTH, alpha=LINE_ALPHA, label=label, **kwargs)

    # Format frequency axis
    format_frequency_axis(ax, use_log_scale=True)

    # Format phase axis
    ax.set_ylabel("Phase (°)")

    # Apply publication styling
    apply_publication_style(
        fig, ax,
        xlabel="Frequency (Hz)",
        ylabel="Phase (°)",
        use_grid=True,
        use_legend=bool(label)
    )

    return fig, ax

def format_impedance_ticks(x: float, pos: int) -> str:
    """
    Format impedance tick labels with appropriate scientific notation.

    Parameters:
        x: Impedance value in Ω
        pos: Tick position (unused)

    Returns:
        Formatted string
    """
    if x >= 1e6:
        return f'{x/1e6:.0f}M'
    elif x >= 1e3:
        return f'{x/1e3:.0f}k'
    elif x >= 1:
        return f'{x:.1f}'
    elif x >= 1e-3:
        return f'{x*1e3:.1f}m'
    elif x > 0:
        return f'{x:.0e}'
    else:
        return '0'

# ------------------------------------------------------------------------------
# PROFESSIONAL EXPORT SYSTEM
# ------------------------------------------------------------------------------
def export_figure_publication(
    fig: Figure,
    output_path: Path,
    format: str = 'png',
    dpi: Optional[int] = None
) -> Path:
    """
    Export figure in publication-ready format.

    Supports high-resolution PNG and vector PDF formats optimized for
    scientific publications.

    Parameters:
        fig: Matplotlib Figure object
        output_path: Output file path (extension will be added if needed)
        format: Export format ('png' or 'pdf')
        dpi: DPI for raster formats (default: 300 for PNG, ignored for PDF)

    Returns:
        Path to exported file
    """
    # Determine format and DPI
    if format.lower() == 'pdf':
        actual_dpi = DPI_EXPORT_PDF
        ext = '.pdf'
    else:  # PNG or default
        actual_dpi = dpi or DPI_EXPORT_PNG
        ext = '.png'

    # Ensure correct extension
    if not str(output_path).lower().endswith(ext):
        output_path = output_path.with_suffix(ext)

    # Export with tight layout and high quality
    fig.savefig(
        output_path,
        format=format.lower(),
        dpi=actual_dpi,
        bbox_inches='tight',
        pad_inches=0.1,
        facecolor='white',
        edgecolor='none'
    )

    return output_path

def export_figure_bytes(
    fig: Figure,
    format: str = 'png',
    dpi: Optional[int] = None
) -> bytes:
    """
    Export figure to bytes for in-memory use (e.g., GUI display).

    Parameters:
        fig: Matplotlib Figure object
        format: Export format ('png' or 'pdf')
        dpi: DPI for raster formats

    Returns:
        Figure data as bytes
    """
    buf = io.BytesIO()

    if format.lower() == 'pdf':
        actual_dpi = dpi or DPI_EXPORT_PDF
    else:
        actual_dpi = dpi or DPI_EXPORT_PNG

    fig.savefig(
        buf,
        format=format.lower(),
        dpi=actual_dpi,
        bbox_inches='tight',
        pad_inches=0.1,
        facecolor='white',
        edgecolor='none'
    )

    return buf.getvalue()

# ------------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ------------------------------------------------------------------------------
def get_scientific_color(index: int) -> str:
    """
    Get color from scientific color palette.

    Parameters:
        index: Color index (cycles through palette)

    Returns:
        Hex color string
    """
    return SCIENTIFIC_COLORS[index % len(SCIENTIFIC_COLORS)]

def create_figure_with_style(
    figsize: Tuple[float, float] = FIG_SIZE_NYQUIST,
    dpi: int = DPI_EXPORT_PNG
) -> Tuple[Figure, Axes]:
    """
    Create a new figure with publication styling pre-configured.

    Parameters:
        figsize: Figure size in inches
        dpi: Resolution for the figure

    Returns:
        Tuple of (Figure, Axes) objects
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Apply base styling
    apply_publication_style(fig, ax, use_grid=True, use_legend=False)

    return fig, ax

# ------------------------------------------------------------------------------
# BACKWARD COMPATIBILITY HELPERS
# ------------------------------------------------------------------------------
def enhance_existing_plot(
    fig: Figure,
    ax: Axes,
    plot_type: str = 'nyquist',
    title: str = "",
    xlabel: str = "",
    ylabel: str = ""
) -> None:
    """
    Enhance an existing plot with publication styling.

    Useful for upgrading existing plotting code without major refactoring.

    Parameters:
        fig: Existing Figure object
        ax: Existing Axes object
        plot_type: Type of plot ('nyquist', 'bode_mag', 'bode_phase')
        title: Plot title
        xlabel: X-axis label (auto-detected if empty)
        ylabel: Y-axis label (auto-detected if empty)
    """
    # Auto-detect labels based on plot type
    if not xlabel or not ylabel:
        if plot_type == 'nyquist':
            xlabel = xlabel or "Z' (Ω)"
            ylabel = ylabel or "-Z'' (Ω)"
        elif plot_type == 'bode_mag':
            xlabel = xlabel or "Frequency (Hz)"
            ylabel = ylabel or "|Z| (Ω)"
        elif plot_type == 'bode_phase':
            xlabel = xlabel or "Frequency (Hz)"
            ylabel = ylabel or "Phase (°)"

    # Apply publication styling
    apply_publication_style(fig, ax, title=title, xlabel=xlabel, ylabel=ylabel)

    # Apply plot-type specific formatting
    if plot_type in ['bode_mag', 'bode_phase']:
        format_frequency_axis(ax, use_log_scale=True)

        if plot_type == 'bode_mag':
            ax.set_yscale('log')
            ax.yaxis.set_major_formatter(plt.FuncFormatter(format_impedance_ticks))