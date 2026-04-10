# V3.6 Compare Tab — Update Summary
SynAptIp Technologies — Phase 6 Documentation
Date: 2026-04-09

---

## Overview

This document summarizes all changes made to extend the V3.6 Compare tab from its initial state (Nyquist overlay only) to the full 10-plot scientific comparison dashboard.

---

## Changes by File

### `src_v3_6/ui_v36/compare_panel.py` — REWRITTEN

Previous state: single Nyquist overlay, no plot selector, no export, label "Comparar".

New state:

| Feature | Detail |
|---|---|
| Plot types | 10 (was 1) |
| Plot selector | QComboBox dropdown, auto-replot on change |
| Visual strategy | 3-axis differentiation: color + line style + marker |
| New plot | Pattern Summary (3-panel: Nyquist + Bode + metrics table) |
| Export | PNG, 150 dpi, timestamped filename |
| Log | Color-coded log with [OK]/[SKIP]/[WARN]/[ERROR] tags |
| Missing column handling | Per-file graceful skip, no crash |
| Background threading | QThread worker, non-blocking UI |

**New functions added:**

| Function | Purpose |
|---|---|
| `_plot_nyquist()` | Nyquist overlay with equal aspect |
| `_plot_bode_mag()` | Bode \|Z\| log-log overlay |
| `_plot_bode_phase()` | Bode Phase semilog overlay |
| `_plot_freq_compare()` | Generic frequency-domain overlay (reused × 7) |
| `_compute_file_metrics()` | f_c, tau, R_dc, behavior per file |
| `_plot_pattern_summary()` | 3-panel Pattern Summary figure |
| `_fmt_si()` | SI prefix formatter for tau and R_dc |

**Constants added:**

```python
_FILE_STYLES = [...]   # 3 style triplets
PLOT_TYPES = [...]     # 10 (plot_id, label) pairs
_PLOT_DISPATCH = {...}  # plot_id → generator function
COL_Y_MAG, COL_Y_PHS, COL_C_SER, COL_C_PAR  # new column refs
```

### `src_v3_6/ui_v36/main_window_v3_6.py` — MINOR UPDATE

| Change | Detail |
|---|---|
| Tab label | "Comparar" → "Compare" |
| Stylesheet | Added QComboBox#comparePlotSelector CSS block |

No other changes. V3.5 and V3 code paths untouched.

### `docs/dev_notes/v3_6_compare_plot_audit.md` — CREATED

Phase 0 audit documenting all 15 V3.5 plots, integration decisions, and architecture choice (QComboBox dropdown).

---

## What Was NOT Changed

Per the additive architecture invariant:

| File/Module | Status |
|---|---|
| `src_v3_5/analysis_engine/plot_engine.py` | No changes |
| `src_v3_5/ui_v35/main_window_v3_5.py` | No changes |
| `src_v3/services/` | No changes |
| `src_v3/ui/` | No changes |
| `validate_v3_6.py` | No changes (existing tests still pass) |
| `lcr_control_v3_6.py` | No changes |
| `lcr_control_v3_6.spec` | No changes |
| `build_v3_6.bat` | No changes |

---

## Unicode Safety Note

Three Unicode characters were replaced to ensure safe output on Windows cp1252 console:

| Original | Replacement | Context |
|---|---|---|
| `★` (U+2605) | matplotlib path `(5, 1, 0)` | Star marker on Pattern Summary |
| `τ` (U+03C4) | `tau` | Log messages, table column header |
| `μ` (U+03BC) | `u` in `_fmt_si()` | SI prefix string (microseconds) |

These characters render correctly inside matplotlib PNG output (Agg backend) and Qt rich text widgets, but fail when printed to a Windows terminal. The replacements are invisible to the end user.

---

## Validation Summary

35/35 tests passed (see `v3_6_compare_validation_round2.md` for full report):

- All 10 plot types generate valid PNG (> 500 bytes)
- All 10 plot types work with 1, 2, and 3 files
- Missing column handling verified (Nyquist skip, frequency-domain skip)
- Pattern Summary metrics verified: f_c, tau, R_dc, behavior label
- V3.5 and V3 backward compatibility confirmed

---

## Release Recommendation

**Version designation: v3.6.1**

Rationale:
- This update is entirely within the Compare tab (one UI panel)
- No new modules, no new backend, no new license system changes
- 10× increase in plot coverage with zero regressions
- Appropriate for a patch release within the v3.6 series

A v3.7 designation would be appropriate if any of the following were added:
- New analysis engine modules (fitting, simulation)
- New tabs or major UI restructuring
- Changes to the license system or device fingerprint algorithm
- New file format support

