# Methods

## Input Data Model

The computational workflow accepts impedance datasets with one of the following column patterns:

- `z_real` and `z_imag` (precomputed complex components), or
- `z_ohm` (or `|Z|`) and `theta_deg` (magnitude-phase representation), or
- `primary` and `secondary` as a raw fallback mapping.

Frequency metadata is carried through `freq_hz` when available.

## Mathematical Transformation

When magnitude-phase inputs are provided, phase is converted from degrees to radians, and complex components are computed as:

- `theta_rad = theta_deg * pi / 180`
- `z_real = |Z| * cos(theta_rad)`
- `z_imag = |Z| * sin(theta_rad)`
- `minus_z_imag = -z_imag`

The Nyquist plotting convention is defined as:

- X-axis: `z_real`
- Y-axis: `minus_z_imag`

## Computational Pipeline

1. Load CSV content and normalize column names.
2. Parse accepted input schema per row.
3. Compute or reuse Nyquist components.
4. Filter malformed or non-finite values.
5. Export transformed CSV outputs.
6. Optionally export comparison visualization.

## Assumptions

- Input rows represent impedance points from a frequency-domain sequence.
- Phase values are expressed in degrees when `theta_deg` is used.
- Numeric fields required for transformation are finite.

## Notes on Robustness

Rows with missing or malformed required values are skipped. If no valid rows remain, the dataset is reported as non-processable for Nyquist export. This method description is scoped to software computation and reproducible data handling.
