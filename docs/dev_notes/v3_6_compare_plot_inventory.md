# V3.6 Compare Tab — Plot Inventory
SynAptIp Technologies — Phase 6 Documentation
Date: 2026-04-09

---

## 1. Complete Plot Inventory (V3.5 Analysis Engine)

All plots available in `src_v3_5/analysis_engine/plot_engine.py`:

| # | plot_id | Method | Required Columns |
|---|---|---|---|
| 1 | `nyquist_clean_comparative` | `_nyquist_clean_comparative` | Z_real_ohm, minus_Z_imag_ohm, dc_bias_v (opt.) |
| 2 | `nyquist_raw_vs_clean` | `_nyquist_raw_vs_clean` | Z_real_ohm, minus_Z_imag_ohm (raw + clean) |
| 3 | `nyquist_individual_per_bias` | `_nyquist_individual` | Z_real_ohm, minus_Z_imag_ohm |
| 4 | `nyquist_freq_colored_per_bias` | `_nyquist_freq_colored` | Z_real_ohm, minus_Z_imag_ohm, freq_hz |
| 5 | `nyquist_freq_colored_comparative` | `_nyquist_freq_colored_comparative` | Z_real_ohm, minus_Z_imag_ohm, freq_hz, dc_bias_v |
| 6 | `bode_mag_comparative` | `_bode_mag_comparative` | freq_hz, z_ohm |
| 7 | `bode_phase_comparative` | `_bode_phase_comparative` | freq_hz, theta_deg |
| 8 | `bode_mag_individual` | `_bode_mag_individual` | freq_hz, z_ohm |
| 9 | `bode_phase_individual` | `_bode_phase_individual` | freq_hz, theta_deg |
| 10 | `z_real_vs_freq` | `_z_real_vs_freq` | freq_hz, Z_real_ohm |
| 11 | `minus_z_imag_vs_freq` | `_minus_z_imag_vs_freq` | freq_hz, minus_Z_imag_ohm |
| 12 | `admittance_mag` | `_admittance_mag` | freq_hz, Y_mag_siemens |
| 13 | `admittance_phase` | `_admittance_phase` | freq_hz, phase_y_deg |
| 14 | `capacitance_series` | `_capacitance_series` | freq_hz, C_series_F |
| 15 | `capacitance_parallel` | `_capacitance_parallel` | freq_hz, C_parallel_F |

---

## 2. Integration Decision Per Plot

### Integrated into Compare (9 existing + 1 new = 10 total)

| # | plot_id | Compare Label | Reason for inclusion |
|---|---|---|---|
| 1 | `nyquist_clean_comparative` | **Nyquist** | Primary EIS diagnostic; already working |
| 6 | `bode_mag_comparative` | **Bode — \|Z\|** | Fundamental impedance magnitude view |
| 7 | `bode_phase_comparative` | **Bode — Phase** | Fundamental phase response view |
| 10 | `z_real_vs_freq` | **Z' vs Frequency** | Real part frequency dispersion |
| 11 | `minus_z_imag_vs_freq` | **−Z'' vs Frequency** | Imaginary part frequency dispersion |
| 12 | `admittance_mag` | **Admittance \|Y\|** | Conductance perspective |
| 13 | `admittance_phase` | **Admittance Phase** | Admittance phase view |
| 14 | `capacitance_series` | **Capacitance (Series)** | Series equivalent capacitance |
| 15 | `capacitance_parallel` | **Capacitance (Parallel)** | Parallel equivalent capacitance |
| NEW | `pattern_summary` | **Pattern Summary** | Multi-metric derived dashboard |

### Excluded from Compare

| # | plot_id | Reason |
|---|---|---|
| 2 | `nyquist_raw_vs_clean` | Requires raw + clean split — single-file only |
| 3 | `nyquist_individual_per_bias` | Redundant with Nyquist in multi-file context |
| 4 | `nyquist_freq_colored_per_bias` | Colormap conflicts with 3-file palette |
| 5 | `nyquist_freq_colored_comparative` | Subplot grid not suitable for file comparison |
| 8 | `bode_mag_individual` | Absorbed by Bode \|Z\| comparative |
| 9 | `bode_phase_individual` | Absorbed by Bode Phase comparative |

---

## 3. Column Mapping

Columns computed by `analysis_engine/eis_transformer.py` and consumed by Compare:

| Column constant | Physical quantity | Used by |
|---|---|---|
| `COL_FREQ` = `freq_hz` | Frequency (Hz) | All frequency-domain plots |
| `COL_Z_REAL` = `Z_real_ohm` | Z' — Real impedance (Ω) | Nyquist, Z' vs Freq |
| `COL_MZ_IMG` = `minus_Z_imag_ohm` | −Z'' — Neg. imaginary (Ω) | Nyquist, −Z'' vs Freq, Pattern Summary |
| `COL_Z_MAG` = `z_ohm` | \|Z\| — Impedance magnitude (Ω) | Bode \|Z\|, Pattern Summary |
| `COL_THETA` = `theta_deg` | Phase angle θ (°) | Bode Phase |
| `COL_Y_MAG` = `Y_mag_siemens` | \|Y\| — Admittance magnitude (S) | Admittance \|Y\| |
| `COL_Y_PHS` = `phase_y_deg` | Phase(Y) (°) | Admittance Phase |
| `COL_C_SER` = `C_series_F` | C_series (F) | Capacitance (Series) |
| `COL_C_PAR` = `C_parallel_F` | C_parallel (F) | Capacitance (Parallel) |

All columns are guaranteed by `eis_transformer.transform()` if the source file contains at least `freq_hz`, `z_real`, and `z_imag` (or equivalent detected by `schema_detector`).

---

## 4. Implementation File

**File:** `src_v3_6/ui_v36/compare_panel.py`

**Key structures:**
- `PLOT_TYPES: list[tuple[str, str]]` — ordered registry of (plot_id, display_label)
- `_PLOT_DISPATCH: dict[str, Callable]` — maps plot_id → generator function
- `_CsvSlot` — per-file state (path, label, DataFrame)
- `ComparePanel(QWidget)` — main UI with QComboBox selector
- `_PlotWorker(QThread)` — background plot generation

