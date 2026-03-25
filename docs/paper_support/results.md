# Results

## Illustrative Dataset Set

The repository includes four illustrative datasets in `example_data/`:

- `resistance_example.csv`
- `capacitor_example.csv`
- `rc_example.csv`
- `rc_dcbias_example.csv`

## Interpretable Behavior Representations

Within the software workflow, these datasets represent the following qualitative response families:

- `resistance_example.csv`: predominantly resistive-like behavior representation.
- `capacitor_example.csv`: capacitive-phase-oriented behavior representation.
- `rc_example.csv`: mixed resistance-capacitance response representation.
- `rc_dcbias_example.csv`: mixed response representation including a DC-bias-oriented sequence context.

## Generated Artifacts

Using the existing export-capable services, the following artifacts are generated in `example_outputs/`:

- `resistance_example_nyquist_data.csv`
- `capacitor_example_nyquist_data.csv`
- `rc_example_nyquist_data.csv`
- `rc_dcbias_example_nyquist_data.csv`
- `nyquist_compare_examples.jpg`

## What the Plots Show

The comparison Nyquist figure provides a side-by-side visualization of distinct trajectory shapes across the four illustrative datasets, while each transformed CSV provides tabulated Nyquist coordinates suitable for reproducible downstream analysis. The result is a traceable computational workflow from input CSV to exportable analysis artifacts.
