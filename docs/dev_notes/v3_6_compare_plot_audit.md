# V3.6 Compare Tab — Plot Audit
SynAptIp Technologies — Phase 0
Date: 2026-04-09

---

## 1. ALL PLOTS AVAILABLE IN THE APPLICATION

Source: `src_v3_5/analysis_engine/plot_engine.py` — class `PlotEngine`

### NYQUIST GROUP (5 plots)

| # | plot_id | Method | Required Columns | Scientific Purpose | In Compare? | Risk |
|---|---|---|---|---|---|---|
| 1 | `nyquist_clean_comparative` | `_nyquist_clean_comparative` | Z_real_ohm, minus_Z_imag_ohm, (dc_bias_v opt.) | Nyquist: Z' vs −Z'', grouped by DC bias | **YES (only one)** | None |
| 2 | `nyquist_raw_vs_clean` | `_nyquist_raw_vs_clean` | Z_real_ohm, minus_Z_imag_ohm (raw + clean) | Overlay raw vs. cleaned data — single file quality check | NO | Not applicable for multi-file compare |
| 3 | `nyquist_individual_per_bias` | `_nyquist_individual` | Z_real_ohm, minus_Z_imag_ohm | Single-condition Nyquist trajectory | NO | Low — adapt as per-file Nyquist |
| 4 | `nyquist_freq_colored_per_bias` | `_nyquist_freq_colored` | Z_real_ohm, minus_Z_imag_ohm, freq_hz | Nyquist with plasma colormap by frequency | NO | Medium — colormap conflicts with 3 files |
| 5 | `nyquist_freq_colored_comparative` | `_nyquist_freq_colored_comparative` | Z_real_ohm, minus_Z_imag_ohm, freq_hz, dc_bias_v | Grid of freq-colored Nyquist per DC bias | NO | Medium — subplot grid |

### BODE GROUP (4 plots)

| # | plot_id | Method | Required Columns | Scientific Purpose | In Compare? | Risk |
|---|---|---|---|---|---|---|
| 6 | `bode_mag_comparative` | `_bode_mag_comparative` | freq_hz, z_ohm | log-log: Frequency vs \|Z\| (Ω) | NO | Low |
| 7 | `bode_phase_comparative` | `_bode_phase_comparative` | freq_hz, theta_deg | semilog: Frequency vs Phase (°) | NO | Low |
| 8 | `bode_mag_individual` | `_bode_mag_individual` | freq_hz, z_ohm | log-log single condition | NO | Low — merge with #6 |
| 9 | `bode_phase_individual` | `_bode_phase_individual` | freq_hz, theta_deg | semilog single condition | NO | Low — merge with #7 |

### DOMAIN / DERIVED GROUP (6 plots)

| # | plot_id | Method | Required Columns | Scientific Purpose | In Compare? | Risk |
|---|---|---|---|---|---|---|
| 10 | `z_real_vs_freq` | `_z_real_vs_freq` | freq_hz, Z_real_ohm | semilog: Frequency vs Z' (Ω) | NO | Low |
| 11 | `minus_z_imag_vs_freq` | `_minus_z_imag_vs_freq` | freq_hz, minus_Z_imag_ohm | semilog: Frequency vs −Z'' (Ω) | NO | Low |
| 12 | `admittance_mag` | `_admittance_mag` | freq_hz, Y_mag_siemens | semilog: Frequency vs \|Y\| (S) | NO | Low |
| 13 | `admittance_phase` | `_admittance_phase` | freq_hz, phase_y_deg | semilog: Frequency vs Phase(Y) (°) | NO | Low |
| 14 | `capacitance_series` | `_capacitance_series` | freq_hz, C_series_F | semilog: Frequency vs C_series (F) | NO | Low |
| 15 | `capacitance_parallel` | `_capacitance_parallel` | freq_hz, C_parallel_F | semilog: Frequency vs C_parallel (F) | NO | Low |

### NON-PLOT EXPORTS (from Analysis & Insights)

| Item | Type | Notes |
|---|---|---|
| dc_bias_summary_tables | CSV tables | Not a plot |
| smart_interpretation_report | Text/Markdown | Not a plot |

---

## 2. COMPARE TAB CURRENT STATE

**File:** `src_v3_6/ui_v36/compare_panel.py`

**Plots currently in Compare:** Only **Nyquist overlay** (1/15)

**Tab label:** "Comparar" (Spanish) — should be "Compare"

---

## 3. INTEGRATION PLAN

### Plots to integrate into Compare (9 of 15):

Selected based on: scientific relevance for multi-file comparison, practical column availability (no cleaning required), visual clarity.

| Plot | Compare Label | Notes |
|---|---|---|
| `nyquist_clean_comparative` | **Nyquist** | Already working — keep |
| `bode_mag_comparative` | **Bode — \|Z\|** | Direct port — freq + z_ohm |
| `bode_phase_comparative` | **Bode — Phase** | Direct port — freq + theta_deg |
| `z_real_vs_freq` | **Z' vs Frequency** | Direct port — freq + Z_real |
| `minus_z_imag_vs_freq` | **−Z'' vs Frequency** | Direct port — freq + -Z_imag |
| `admittance_mag` | **Admittance \|Y\|** | Direct port — freq + Y_mag |
| `admittance_phase` | **Admittance Phase** | Direct port — freq + phase_y |
| `capacitance_series` | **Capacitance (Series)** | Direct port — freq + C_series |
| `capacitance_parallel` | **Capacitance (Parallel)** | Direct port — freq + C_par |

### Plots NOT integrated (kept only in Analysis & Insights):

| Plot | Reason |
|---|---|
| `nyquist_raw_vs_clean` | Requires raw+clean split; not applicable multi-file |
| `nyquist_individual_per_bias` | Redundant with main Nyquist in compare context |
| `nyquist_freq_colored_per_bias` | Colormap conflicts with 3-file palette |
| `nyquist_freq_colored_comparative` | Grid layout not suitable for multi-file overlay |
| `bode_mag_individual` | Absorbed into Bode |Z| comparative |
| `bode_phase_individual` | Absorbed into Bode Phase comparative |

### NEW PLOT (1):

| Plot | Label | Method |
|---|---|---|
| Predominant Pattern Summary | **Pattern Summary** | New — derived from existing columns |

---

## 4. ARCHITECTURE DECISION: Plot selector

**Chosen approach:** `QComboBox` dropdown selector (safest, cleanest, no tab nesting complexity).

- Selector at top of Compare tab
- Re-renders current plot type on selection change (data already loaded)
- No re-parsing needed — DataFrames cached in `_CsvSlot`
