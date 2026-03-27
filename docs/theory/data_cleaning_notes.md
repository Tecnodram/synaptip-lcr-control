# Data Cleaning — Pipeline Notes

**SynAptIp Technologies — Internal Theory Documentation**

---

## Purpose

The data cleaning pipeline removes measurements that would corrupt the analysis.  
It is designed to be **auditable** — every removed point is retained in `removed_points.csv`
with a tagged removal reason.

---

## Cleaning Steps (in order)

### Step 1 — Invalid Status Filter

If the dataset contains a `status` column, rows with non-valid status are removed.

Accepted values (case-insensitive):
```
ok, valid, 1, true, yes
```

Any other value (e.g. `error`, `0`, `timeout`) causes removal.

**Tag:** `invalid_status`

---

### Step 2 — NaN / ±∞ Filter

Rows containing non-finite values in any required analysis column are removed.

Required finite columns:
- `freq_hz`
- `Z_real_ohm`
- `Z_imag_ohm`

NaN or infinity in these columns makes impedance computation meaningless.

**Tag:** `non_finite_value`

---

### Step 3 — Non-Positive Frequency Filter

Rows where `freq_hz ≤ 0` are removed.

Frequency must be strictly positive for logarithmic axes, angular frequency (ω = 2πf), and capacitance computations.

**Tag:** `non_positive_frequency`

---

### Step 4 — Percentile Outlier Filter

Rows where any of the following columns fall outside the [1%, 99%] percentile range are removed:
- `Z_real_ohm`
- `minus_Z_imag_ohm`
- `z_ohm`

This filter is applied **per DC bias group** when DC bias is present, to avoid cross-group contamination.

**Tag:** `outside_percentile_filter`

Default bounds: 1st to 99th percentile.  
This is robust and avoids excessive data loss for typical EIS measurements.

---

## Output Files

| File | Description |
|------|-------------|
| `raw_input.csv` | Original file as loaded, no modifications |
| `clean_data.csv` | All enriched columns after cleaning |
| `removed_points.csv` | Rows that were removed, with removal_reason column |
| `cleaning_summary.csv` | Row counts per group: raw, clean, removed, % removed |

---

## Design Principles

- **Non-destructive**: Raw file is always preserved in `raw/`
- **Transparent**: Every removed point carries a reason tag
- **Per-group filtering**: DC bias groups are filtered independently to preserve relative differences
- **Fail-safe**: If any step fails, the error is logged and the next step proceeds

---

*This documentation is for internal reference only and is not intended for end-user distribution without review.*
