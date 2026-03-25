# Nyquist Transformation Method

## Pipeline Overview

The software implements the following computational workflow for Nyquist transformation.

Input columns expected from an illustrative dataset include:
- `freq_hz`
- `z_ohm` or `|Z|`
- `theta_deg`

If available, precomputed `z_real` and `z_imag` columns are also accepted.

Transformation workflow:
1. Load CSV rows and normalize column names.
2. Parse numeric values from accepted column patterns.
3. Convert phase from degrees to radians.
4. Compute Nyquist coordinates.
5. Compute `minus_z_imag` for plotting convention.
6. Export transformed rows.

Output columns:
- `z_real`
- `z_imag`
- `minus_z_imag`

## Equations

The following equations describe the transformation method:

- `theta_rad = theta_deg * pi / 180`
- `z_real = |Z| * cos(theta_rad)`
- `z_imag = |Z| * sin(theta_rad)`
- `minus_z_imag = -z_imag`

## Technical Explanation

### Degree-to-radian conversion

Trigonometric functions use radians, so phase in degrees is converted to radians before computing real and imaginary components.

### Nyquist convention

The plotting convention used is:
- X axis = `z_real`
- Y axis = `-z_imag`

This is implemented by explicitly storing `minus_z_imag`.

### Behavior when `z_real` and `z_imag` already exist

If both columns are present and parseable, the loader uses those values directly and avoids recomputing from magnitude-phase pairs.

### Assumptions

- Rows represent impedance points sampled across one frequency sequence.
- Phase is provided in degrees when `theta_deg` is used.
- Numeric fields are finite real values.

### Limitations

- Transformation quality depends on source CSV consistency.
- Non-numeric or malformed values are excluded.
- Datasets with no valid rows cannot produce transformed outputs.

### Missing values and malformed columns

The loader accepts multiple column patterns (`z_real`/`z_imag`, `z_ohm`/`theta_deg`, or `primary`/`secondary`).
Rows that cannot be parsed into finite values are skipped.
If all rows are invalid, the dataset is reported as having no valid Nyquist points.

## Scope Statement

This methodology describes software computation only. Repository documentation presents a general-purpose interoperability and data-analysis workflow and does not claim institutional validation.
