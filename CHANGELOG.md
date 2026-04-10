# Changelog

## v3.6.1 — 2026-04-11

### Compare Tab — 10-Plot Scientific Dashboard

The Compare tab has been extended from a single Nyquist overlay to a full
10-plot scientific comparison dashboard. No existing features were modified.

**Plot types now available (select via dropdown):**

| # | Plot | Description |
|---|---|---|
| 1 | Nyquist Comparison | Z' vs −Z'' overlay, equal-aspect |
| 2 | Bode Magnitude | |Z| vs Frequency, log-log |
| 3 | Bode Phase | Phase vs Frequency, semilog |
| 4 | Z' (Real) vs Frequency | Real impedance vs Frequency |
| 5 | −Z'' (Imaginary) vs Frequency | Imaginary impedance vs Frequency |
| 6 | Admittance Magnitude | |Y| vs Frequency |
| 7 | Admittance Phase | Admittance phase vs Frequency |
| 8 | Series Capacitance | C_series vs Frequency |
| 9 | Parallel Capacitance | C_parallel vs Frequency |
| 10 | Pattern Summary | 3-panel: Nyquist + Bode + per-file metrics table |

**Visual differentiation strategy (3-axis):**
- Color: blue / amber / green per dataset
- Line style: solid / dashed / dotted per dataset
- Marker: circle / square / triangle per dataset

**Pattern Summary metrics (per loaded file):**
- Corner frequency f_c
- Time constant tau
- R_dc (low-frequency real impedance)
- Dominant behavior classification: resistive / capacitive / inductive

**UX improvements:**
- QComboBox dropdown selector with auto-replot on selection change
- Color-coded log: `[OK]` / `[SKIP]` / `[WARN]` / `[ERROR]`
- Per-file graceful column skip — no crash on missing data
- Background QThread rendering — non-blocking UI
- Tab label updated: "Comparar" → "Compare"

**Validation:** 35/35 tests passed across all 10 plot types with 1, 2, and 3 files.
No regressions in V3 or V3.5 behavior.

---

## v3.6.0 — 2026-04-09

- Professional offline license system (.lic file, HMAC-SHA256, device-bound)
- License dialog with 5 validation states (valid / expired / wrong_device / corrupt / not_loaded)
- Compare tab (Nyquist overlay, initial single-plot version)
- Additive architecture: V3 and V3.5 code paths completely unchanged

---

## v3.5.0 — 2026-03-xx

- Finalized stable V3.5.0 release baseline
- Preserved V3 compatibility while shipping V3.5 analysis workflow
- Validated release datasets and reproducibility outputs
- Hardened packaged startup behavior for console and double-click launch modes
- Standardized release metadata for GitHub Release and Zenodo archival
