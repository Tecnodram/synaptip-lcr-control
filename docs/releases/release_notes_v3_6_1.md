# Release Notes — SynAptIp LCR Link Tester V3.6.1

**Release date:** 2026-04-11
**Version:** 3.6.1
**Executable:** `SynAptIp_Nyquist_Analyzer_V3_6.exe`
**Platform:** Windows 10/11 (64-bit)

---

## Summary

V3.6.1 is a patch release within the V3.6 series. It extends the Compare tab
from a single Nyquist overlay to a full 10-plot scientific comparison dashboard.

All changes are isolated to `src_v3_6/ui_v36/compare_panel.py` and a minor
stylesheet update in `main_window_v3_6.py`. No existing modules were modified.

---

## What Changed

### `src_v3_6/ui_v36/compare_panel.py` — rewritten

| Metric | Before | After |
|---|---|---|
| Plot types | 1 | 10 |
| Plot selector | none | QComboBox dropdown |
| Export | none | PNG, 150 dpi, timestamped |
| Log | basic | color-coded [OK]/[SKIP]/[WARN]/[ERROR] |
| Missing column handling | crash risk | per-file graceful skip |
| Thread model | main thread | QThread worker (non-blocking) |

**New plot types:**

1. Nyquist Comparison
2. Bode Magnitude (|Z| vs Frequency, log-log)
3. Bode Phase (Phase vs Frequency, semilog)
4. Z' (Real) vs Frequency
5. −Z'' (Imaginary) vs Frequency
6. Admittance Magnitude (|Y| vs Frequency)
7. Admittance Phase vs Frequency
8. Series Capacitance vs Frequency
9. Parallel Capacitance vs Frequency
10. Pattern Summary — 3-panel figure with per-file metrics table

**Pattern Summary metrics:**
- f_c — corner frequency (Hz)
- tau — time constant (SI-prefixed)
- R_dc — low-frequency real impedance
- Behavior label: resistive / capacitive / inductive

**Visual differentiation (3-axis):**
- Color: blue (`#1d4ed8`) / amber (`#b45309`) / green (`#059669`)
- Line style: solid / dashed / dotted
- Marker: circle `o` / square `s` / triangle `^`

### `src_v3_6/ui_v36/main_window_v3_6.py` — minor

- Tab label changed: "Comparar" → "Compare"
- QComboBox `#comparePlotSelector` stylesheet block added

---

## What Was NOT Changed

| Module | Status |
|---|---|
| `src_v3_5/analysis_engine/` | Unchanged |
| `src_v3_5/ui_v35/` | Unchanged |
| `src_v3/services/` | Unchanged |
| `src_v3/ui/` | Unchanged |
| `src_v3_6/lcr_control_v3_6.py` | Unchanged |
| `src_v3_6/licensing/` | Unchanged |
| `lcr_control_v3_6.spec` | Unchanged |
| `build_v3_6.bat` | Unchanged |

---

## Validation Results

35/35 tests passed:

- All 10 plot types generate valid PNG output (> 500 bytes)
- All 10 plot types work with 1, 2, and 3 simultaneously loaded files
- Missing column handling verified: graceful skip, no crash
- Pattern Summary metrics verified: f_c, tau, R_dc, behavior label
- V3.5 Analysis & Insights tab: no regression
- V3 measurement and scan tabs: no regression

---

## Upgrade Notes

V3.6.1 is backward-compatible with all V3.6.0 license files. No license
regeneration is required.

---

## License Access in V3.6.1

A valid license file (`.lic`) is required to launch the application. The license
is device-bound and loaded through the built-in license dialog at startup.

V3.6.1 does not include an automatic free trial period. Evaluation licenses are
available on request:

1. Launch the application and copy the Device Fingerprint from the license dialog.
2. Email the fingerprint to **synaptip.tech@gmail.com**.
3. A time-limited evaluation `.lic` file will be provided by return email.
4. Load the file in the license dialog to unlock the application.

An automatic self-service trial is planned for a future version and is not part
of this release.

---

## Known Limitations

- Maximum 3 files per Compare session (by design)
- Series/Parallel Capacitance plots skip files without the relevant column
- Pattern Summary behavior classification is heuristic; review manually for
  publication-grade conclusions
