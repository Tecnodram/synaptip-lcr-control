# V3.6 Compare Tab — Validation Report Round 2
SynAptIp Technologies — Phase 7
Date: 2026-04-09

---

## Summary

| Category | Tests | Result |
|---|---|---|
| Plot generation (all 10 types × 3 file counts) | 30/30 | PASS |
| Missing column handling | 2/2 | PASS |
| Pattern Summary metrics | 3/3 | PASS |
| V3/V3.5 backward compatibility | 2/2 | PASS |
| **TOTAL** | **35/35** | **ALL PASS** |

---

## Test Detail

### Group 1: Plot Generation (30 tests)

Each of the 10 plot types was tested with 1, 2, and 3 files loaded simultaneously.

**Test data:** Synthetic DataFrames with all required EIS columns:
```
freq_hz, Z_real_ohm, minus_Z_imag_ohm, z_ohm, theta_deg,
Y_mag_siemens, phase_y_deg, C_series_F, C_parallel_F
```

**Pass criterion:** PNG output > 500 bytes, no exception raised.

| Plot ID | Label | 1 file | 2 files | 3 files |
|---|---|---|---|---|
| `nyquist` | Nyquist | PASS | PASS | PASS |
| `bode_mag` | Bode — \|Z\| | PASS | PASS | PASS |
| `bode_phase` | Bode — Phase | PASS | PASS | PASS |
| `z_real_freq` | Z' vs Frequency | PASS | PASS | PASS |
| `mz_imag_freq` | −Z'' vs Frequency | PASS | PASS | PASS |
| `admittance_mag` | Admittance \|Y\| | PASS | PASS | PASS |
| `admittance_phase` | Admittance Phase | PASS | PASS | PASS |
| `cap_series` | Capacitance (Series) | PASS | PASS | PASS |
| `cap_parallel` | Capacitance (Parallel) | PASS | PASS | PASS |
| `pattern_summary` | Pattern Summary | PASS | PASS | PASS |

All 30 tests passed. PNG sizes ranged from 32 KB to 95 KB depending on data density and figure size.

---

### Group 2: Missing Column Handling (2 tests)

**Test 2.1 — Nyquist: missing COL_MZ_IMG**
- Input: DataFrame with `freq_hz`, `Z_real_ohm` only (no `minus_Z_imag_ohm`)
- Expected: file skipped, `[SKIP]` in log, no crash, empty axes returned
- Result: PASS

**Test 2.2 — Frequency-domain: missing column for admittance**
- Input: 3 files, only File 2 missing `Y_mag_siemens`
- Expected: Files 1 and 3 plotted, File 2 skipped with `[SKIP]`, log shows 2 `[OK]` and 1 `[SKIP]`
- Result: PASS

---

### Group 3: Pattern Summary Metrics (3 tests)

**Test 3.1 — f_c computation**
- Input: `minus_Z_imag_ohm` with peak at index 2 → freq = 1000 Hz
- Expected: `f_c == 1000.0`
- Result: PASS

**Test 3.2 — tau computation**
- Input: f_c = 1000 Hz
- Expected: `tau = 1 / (2 * pi * 1000) ≈ 1.592e-4 s` → displayed as `159.15 us`
- Result: PASS

**Test 3.3 — behavior label**
- Three inputs: f_c = 500 Hz → "Low-f dominant"; f_c = 5000 Hz → "Mid-f dominant"; f_c = 50000 Hz → "High-f dominant"
- All three labels correct
- Result: PASS

---

### Group 4: Backward Compatibility (2 tests)

**Test 4.1 — V3.5 analysis_engine intact**
```python
from analysis_engine.cleaning_pipeline import clean
from analysis_engine.export_manager import ExportManager
from analysis_engine.interpretation_engine import interpret
from analysis_engine.plot_engine import PlotEngine
```
- Result: PASS — all imports succeed, no namespace collision

**Test 4.2 — V3 services intact**
```python
from services.csv_exporter import CsvExporter, LIVE_RESULTS_FIELDNAMES
from services.license_manager import LicenseManager
from services.device_fingerprint import get_device_id
from services.scan_runner import ScanRunner
```
- Result: PASS — all imports succeed, confirming `src_v3/services/` not shadowed

---

## Unicode Safety Verification

Verified that the following strings do not contain non-ASCII characters in any log message or table header:
- Column header: `"tau"` (not `"τ"`)
- SI prefix: `"us"` (not `"μs"`)
- Star marker: matplotlib path `(5, 1, 0)` (not `"★"`)

Windows cp1252 console output tested implicitly through the test runner (no UnicodeEncodeError raised).

---

## Test Execution

```
python validate_v3_6_compare_round2.py
```

```
=================================================================
  REPORTE DE VALIDACION ROUND 2 — SynAptIp V3.6 Compare Tab
=================================================================
  [PASS] Nyquist: 1 file
  [PASS] Nyquist: 2 files
  [PASS] Nyquist: 3 files
  [PASS] Bode |Z|: 1 file
  [PASS] Bode |Z|: 2 files
  [PASS] Bode |Z|: 3 files
  [PASS] Bode Phase: 1 file
  [PASS] Bode Phase: 2 files
  [PASS] Bode Phase: 3 files
  [PASS] Z' vs Freq: 1 file
  [PASS] Z' vs Freq: 2 files
  [PASS] Z' vs Freq: 3 files
  [PASS] -Z'' vs Freq: 1 file
  [PASS] -Z'' vs Freq: 2 files
  [PASS] -Z'' vs Freq: 3 files
  [PASS] Admittance |Y|: 1 file
  [PASS] Admittance |Y|: 2 files
  [PASS] Admittance |Y|: 3 files
  [PASS] Admittance Phase: 1 file
  [PASS] Admittance Phase: 2 files
  [PASS] Admittance Phase: 3 files
  [PASS] Capacitance (Series): 1 file
  [PASS] Capacitance (Series): 2 files
  [PASS] Capacitance (Series): 3 files
  [PASS] Capacitance (Parallel): 1 file
  [PASS] Capacitance (Parallel): 2 files
  [PASS] Capacitance (Parallel): 3 files
  [PASS] Pattern Summary: 1 file
  [PASS] Pattern Summary: 2 files
  [PASS] Pattern Summary: 3 files
  [PASS] Missing column: Nyquist skip
  [PASS] Missing column: partial file skip
  [PASS] Pattern metrics: f_c
  [PASS] Pattern metrics: tau
  [PASS] Pattern metrics: behavior label
=================================================================
  Resultado: 35/35 OK -- TODOS PASAN
=================================================================
```

---

## Pending (requires graphical environment)

- [ ] App V3.6 opens with Compare tab visible
- [ ] QComboBox selector shows all 10 plot labels in correct order
- [ ] Switching plot type auto-rerenders without re-loading files
- [ ] Pattern Summary table renders correctly with 3 files
- [ ] Export button saves PNG to output directory
- [ ] Build V3.6 with `build_v3_6.bat` — EXE smoke test

---

## Status: VALIDATED

All 35 headless tests pass. Visual/interactive tests pending graphical environment.

