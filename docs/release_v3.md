# Release Notes — SynAptIp LCR Control V3

**Version:** 3.0.0  
**Release Date:** March 2026  
**Status:** Production-Ready  
**Platform:** Windows 10 / 11 (64-bit)

---

## Overview

SynAptIp LCR Control V3 is a production release of the SynAptIp instrument control platform, building directly on the stable V2.3 codebase. V3 introduces a complete Nyquist post-processing and export pipeline while preserving all existing V2.3 functionality without modification.

All files in `src/` and `src_v2/` are unchanged and SHA-256 verified identical to their V2.3 originals.

---

## New Features in V3

### Nyquist Analysis Panel

- New **Nyquist Analysis (V3)** tab integrated into the main window
- Loads 1, 2, or 3 CSV files independently via **Load File 1 / 2 / 3** buttons
- Displays file name and valid data point count per slot
- Interactive Nyquist chart preview (Z' vs. −Z'') using PySide6 QtCharts
- **Autozoom** button recalculates axis limits at 10% margin and redraws

### Nyquist Transform Service

- Computes `z_real = z_ohm × cos(θ)` and `z_imag = z_ohm × sin(θ)` from raw Z-theta data
- Accepts three input column formats:
  - Pre-computed: `z_real`, `z_imag`
  - Z-theta: `z_ohm`, `theta_deg`
  - Primary/secondary raw index fallback
- Validates pre-computed columns before recomputing

### CSV Export (Nyquist)

- Exports per-file structured CSV: `<stem>_nyquist_data.csv`
- Columns: `freq_hz`, `z_real`, `z_imag`, `minus_z_imag`

### Individual JPG Plots (300 dpi)

- Per-file Nyquist plot with title, axis labels, grid, legend, and brand watermark
- Timestamped filename: `<stem>_nyquist_YYYYMMDD_HHMMSS.jpg`
- Resolution: 300 dpi, JPEG format, tight bounding box

### Comparison JPG Plot (300 dpi)

- Overlay of up to 3 datasets with distinct per-curve colors and shared axis limits
- Timestamped filename: `nyquist_compare_YYYYMMDD_HHMMSS.jpg`
- Requires at least 2 files loaded with valid data

### Export ALL

- One-click export of all Nyquist CSVs + all individual JPGs + comparison JPG

### pandas-based CSV Loader

- Replaced manual CSV parsing with `pandas.read_csv`
- Automatic encoding fallback: UTF-8 → Latin-1 → UTF-8 with error replacement
- Comment lines (`#`) stripped before parsing
- Robust to missing or reordered columns

### Offline License / Trial System

- 14-day trial period starts automatically on first launch
- Device-bound offline activation via HMAC-SHA256 signed keys
- Key format: `SYNAPT-V3-<base64_payload>.<sig24>`
- Trial state stored at: `%APPDATA%\SynAptIp\license.json`
- Fail-open: license errors never crash the application
- `SYNAPTIP_LICENSE_DISABLED=1` environment variable bypasses dialog for CI/dev use

### Windows EXE Distribution

- Single-file executable built with PyInstaller 6.x
- Embeds PySide6, pandas, numpy, matplotlib, pyserial
- VSVersionInfo metadata: company, file version, product name
- Output: `dist\SynAptIp_LCR_Control_V3.exe`

---

## Bug Fixes

### JPG Export — `quality` Keyword Argument Error (Critical)

**Symptom:** `FigureCanvasAgg.print_jpg() got an unexpected keyword argument 'quality'`  
**Root cause:** `matplotlib` Agg backend does not accept `quality` as a direct `savefig()` keyword argument on the installed version.  
**Fix:** Removed `quality=92` from both `savefig()` calls in `nyquist_plotter.py`. Replaced with `dpi=300, bbox_inches='tight'`, which produces consistent high-quality output without the unsupported kwarg.  
**Affected exports:** individual JPG export and comparison JPG export — both now functional.

### License Storage Path Mismatch

**Symptom:** License state was written to `%APPDATA%\SynAptIp_LCR_Control_V3\license_state.json` instead of the specified path.  
**Fix:** Updated `license_storage.py` constants:  
  - `_APP_DIR_NAME`: `"SynAptIp_LCR_Control_V3"` → `"SynAptIp"`  
  - `_STATE_FILE_NAME`: `"license_state.json"` → `"license.json"`  
**Final path:** `%APPDATA%\SynAptIp\license.json`

---

## Stability Improvements

- License system is fully fail-open: any exception during license evaluation or dialog display is silently caught, allowing the application to start normally.
- File loader encoding fallback prevents crashes on non-UTF-8 CSV files from legacy instruments.
- `matplotlib.use("Agg")` is set at module import in the plotter to ensure headless rendering on all configurations.
- PyInstaller hidden imports explicitly include `pandas`, `numpy`, `matplotlib`, `PySide6`, and `serial` submodules.

---

## Verified Build Outputs

| File | Status |
|---|---|
| `dist\SynAptIp_LCR_Control_V3.exe` | Confirmed produced, launches without crash |
| `src_v3\services\csv_exporter.py` | SHA-256 identical to V2.3 original |
| `src_v3\services\scan_runner.py` | SHA-256 identical to V2.3 original |
| `src_v3\services\unit_conversion.py` | SHA-256 identical to V2.3 original |

---

## V2.3 Integrity

All V2.3 service copies in `src_v3/services/` were verified SHA-256 identical to the originals in `src_v2/services/`. The V2.3 EXE was confirmed present after V3 build completion. No files in `src/` or `src_v2/` were modified.

---

## Dependencies

| Package | Purpose |
|---|---|
| PySide6 | GUI framework (QtWidgets, QtCharts, QtCore) |
| pandas | CSV loading with encoding fallback |
| numpy | Nyquist transform math |
| matplotlib | JPG export (Agg backend) |
| pyserial | Serial communication with LCR meter |
| PyInstaller | EXE packaging |

---

## Known Limitations

- DC bias magnitude command (`:BIAS:VOLT`) is experimental for the U2829C; behavior depends on instrument firmware. The front panel remains the authoritative bias control.
- Comparison JPG export requires at least 2 slots loaded with valid data.
- The application is Windows-only. Linux/macOS builds are not supported in this release.

---

*SynAptIp Technologies · 2026*
