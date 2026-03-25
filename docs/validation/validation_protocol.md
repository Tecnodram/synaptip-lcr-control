# Workflow Validation Protocol (Example-Based)

## Purpose

This document describes a workflow validation procedure focused on computational consistency checks and example-based demonstration of the Nyquist processing pipeline.

It is not a formal experimental validation study.

## Example Datasets

The following illustrative datasets are included in the repository under `example_data/`:

- `resistance_example.csv`
- `capacitor_example.csv`
- `rc_example.csv`
- `rc_dcbias_example.csv`

## What Each Dataset Illustrates

- `resistance_example.csv`: example impedance behavior dominated by resistive contribution.
- `capacitor_example.csv`: example impedance behavior with capacitive phase characteristics.
- `rc_example.csv`: example mixed response from combined resistance-capacitance behavior.
- `rc_dcbias_example.csv`: example mixed response including a DC-bias-oriented workflow variant.

## Expected Processing Flow

1. Load one or more datasets from `example_data/`.
2. Parse accepted input columns (`z_real`/`z_imag`, `z_ohm`/`theta_deg`, or `primary`/`secondary`).
3. Compute or validate Nyquist coordinates.
4. Export transformed CSV files.
5. Generate comparison JPG for illustrative visualization.

## Expected Outputs

Outputs are expected in `example_outputs/`:

- `resistance_example_nyquist_data.csv`
- `capacitor_example_nyquist_data.csv`
- `rc_example_nyquist_data.csv`
- `rc_dcbias_example_nyquist_data.csv`
- `nyquist_compare_examples.jpg`

## Limitations

- This protocol checks software workflow consistency, not instrument performance.
- Results depend on the formatting and numeric integrity of input files.
- Documentation and examples are illustrative and intended for reproducible software-use demonstration.
