"""
demo_v3_7_plotting.py — Demonstration of V3.7 Publication-Grade Plotting
SynAptIp Nyquist Analyzer V3.7
SynAptIp Technologies

This script demonstrates the publication-grade visualization improvements in V3.7.
It generates example plots showing the enhanced quality suitable for scientific
publications, posters, and technical reports.

Run this script to see the quality improvements:
    python demo_v3_7_plotting.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add V3.7 services to path
v37_services = Path(__file__).parent / "src_v3_7" / "services"
if v37_services.exists():
    sys.path.insert(0, str(v37_services))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from publication_plot_utils import (
    plot_nyquist_publication,
    plot_bode_magnitude_publication,
    plot_bode_phase_publication,
    export_figure_publication,
)

def generate_demo_data():
    """Generate realistic EIS data for demonstration."""
    # Frequency range: 100 Hz to 1 MHz
    frequencies = np.logspace(2, 6, 101)

    # Two different samples: high resistance vs low resistance
    samples = []

    for sample_name, r_ct in [("High Z", 5000), ("Low Z", 500)]:
        omega = 2 * np.pi * frequencies
        R_s = 100.0  # Series resistance
        C_dl = 10e-6  # Double layer capacitance

        # Calculate impedance
        denominator = 1 + 1j * omega * r_ct * C_dl
        Z = R_s + r_ct / denominator

        # Add realistic noise
        noise_level = 0.02
        Z_real = Z.real + np.random.normal(0, noise_level * abs(Z.real).mean(), len(Z))
        Z_imag = Z.imag + np.random.normal(0, noise_level * abs(Z.imag).mean(), len(Z))

        Z_mag = np.sqrt(Z_real**2 + Z_imag**2)
        Z_phase = np.arctan2(Z_imag, Z_real) * 180 / np.pi

        df = pd.DataFrame({
            'Frequency (Hz)': frequencies,
            'Z_real': Z_real,
            'Z_imag': Z_imag,
            'Z_mag': Z_mag,
            'Z_phase': Z_phase,
            'Minus_Z_imag': -Z_imag,
        })

        samples.append((sample_name, df))

    return samples

def demo_nyquist_plot():
    """Demonstrate publication-grade Nyquist plot."""
    print("Generating Nyquist plot with frequency progression...")

    samples = generate_demo_data()

    # Create comparison plot
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    colors = ['#1f77b4', '#d62728']  # Scientific colors

    for i, (label, df) in enumerate(samples):
        z_real = df['Z_real'].values
        z_imag_neg = df['Minus_Z_imag'].values
        frequencies = df['Frequency (Hz)'].values

        fig, ax = plot_nyquist_publication(
            z_real, z_imag_neg, frequencies,
            fig=fig, ax=ax,
            label=label,
            color=colors[i],
            show_frequency_progression=True,
            marker_every=20
        )

    ax.set_title("Nyquist Plot Comparison — Publication Quality", fontweight="bold", fontsize=14)

    # Export
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)

    export_figure_publication(fig, output_dir / "nyquist_demo.png", format="png")
    export_figure_publication(fig, output_dir / "nyquist_demo.pdf", format="pdf")

    plt.close(fig)
    print(f"✓ Nyquist plot saved to {output_dir}/nyquist_demo.png & .pdf")

def demo_bode_plots():
    """Demonstrate publication-grade Bode plots."""
    print("Generating Bode plots...")

    samples = generate_demo_data()

    # Create side-by-side Bode plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    colors = ['#1f77b4', '#d62728']

    for i, (label, df) in enumerate(samples):
        freq = df['Frequency (Hz)'].values
        mag = df['Z_mag'].values
        phase = df['Z_phase'].values

        # Magnitude plot
        fig, ax1 = plot_bode_magnitude_publication(
            freq, mag,
            fig=fig, ax=ax1,
            label=label,
            color=colors[i]
        )

        # Phase plot
        fig, ax2 = plot_bode_phase_publication(
            freq, phase,
            fig=fig, ax=ax2,
            label=label,
            color=colors[i]
        )

    ax1.set_title("Bode Plot — |Z| Magnitude", fontweight="bold")
    ax2.set_title("Bode Plot — Phase", fontweight="bold")

    fig.suptitle("Bode Plot Comparison — Publication Quality", fontsize=14, fontweight="bold")

    # Export
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)

    export_figure_publication(fig, output_dir / "bode_demo.png", format="png")
    export_figure_publication(fig, output_dir / "bode_demo.pdf", format="pdf")

    plt.close(fig)
    print(f"✓ Bode plots saved to {output_dir}/bode_demo.png & .pdf")

def demo_export_quality():
    """Demonstrate high-quality export capabilities."""
    print("Demonstrating export quality...")

    # Create a simple high-quality plot
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)

    # Generate smooth theoretical data for quality demonstration
    frequencies = np.logspace(2, 6, 1000)
    omega = 2 * np.pi * frequencies

    # Perfect semicircle (no noise)
    R_ct = 1000.0
    R_s = 100.0
    C_dl = 10e-6

    denominator = 1 + 1j * omega * R_ct * C_dl
    Z = R_s + R_ct / denominator

    fig, ax = plot_nyquist_publication(
        Z.real, -Z.imag, frequencies,
        fig=fig, ax=ax,
        show_frequency_progression=True,
        marker_every=0  # No markers for clean look
    )

    ax.set_title("High-Quality Nyquist Plot — Publication Ready", fontweight="bold")

    # Export in multiple formats
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)

    # PNG at maximum quality
    export_figure_publication(fig, output_dir / "quality_demo_300dpi.png", format="png", dpi=300)

    # PDF vector format
    export_figure_publication(fig, output_dir / "quality_demo_vector.pdf", format="pdf")

    plt.close(fig)
    print(f"✓ High-quality exports saved to {output_dir}/")

def main():
    """Run the publication-grade plotting demonstration."""
    print("=" * 70)
    print("SynAptIp V3.7 — Publication-Grade Plotting Demonstration")
    print("=" * 70)
    print()
    print("This demo generates publication-quality plots showcasing:")
    print("• Nyquist plots with frequency progression coloring")
    print("• Professional Bode plots with proper scaling")
    print("• High-DPI PNG export (300 dpi)")
    print("• Vector PDF export for publications")
    print("• Scientific typography and color schemes")
    print()

    try:
        demo_nyquist_plot()
        demo_bode_plots()
        demo_export_quality()

        print()
        print("=" * 70)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 70)
        print()
        print("Generated files in 'demo_output/' directory:")
        print("• nyquist_demo.png & .pdf — Nyquist comparison")
        print("• bode_demo.png & .pdf — Bode magnitude & phase")
        print("• quality_demo_300dpi.png — High-res PNG")
        print("• quality_demo_vector.pdf — Vector PDF")
        print()
        print("These plots are suitable for:")
        print("• Peer-reviewed journal articles")
        print("• Scientific posters and presentations")
        print("• Technical reports and theses")
        print("• Patent applications")
        print()
        print("All plots use 300 DPI resolution and professional formatting.")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)