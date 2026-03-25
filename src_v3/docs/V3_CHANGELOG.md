# V3 Changelog

**SynAptIp Technologies**  
*AI, Scientific Software & Instrument Intelligence*

---

## Version 3.0.0 — Initial V3 Release

### New Features

#### Nyquist Analysis Tab (V3)
- New dedicated **Nyquist Analysis (V3)** tab in the main window
- Load 1, 2, or 3 CSV files independently via **Load File 1/2/3** buttons
- File name and valid point count displayed per slot
- In-app Nyquist chart preview using PySide6 QtCharts (if available)
- **Autozoom / Fit to View** button — recalculates axis limits and redraws

#### Nyquist Transform & CSV Export
- Computes `z_real = z_ohm × cos(θ)`, `z_imag = z_ohm × sin(θ)`, `−z_imag`
- If `z_real`/`z_imag` already exist in the file, they are validated and reused
- Exports per-file `<stem>_nyquist_data.csv` with all Nyquist columns

#### Individual JPG Plots
- Per-file Nyquist plot: X = `z_real`, Y = `−z_imag`
- Axis labels, title, legend, and SynAptIp Technologies brand watermark
- Output: `<stem>_nyquist.jpg`

#### Comparison JPG Plot
- Overlay plot of 2–3 loaded files with per-curve legend and distinct colors
- Output: `nyquist_compare.jpg`

#### Export ALL
- One-click export of all CSVs + individual JPGs + comparison JPG

#### Branding Updates
- Header shows: **SynAptIp LCR Control V3**
- Company label: **SynAptIp Technologies**
- Subtitle: *Scientific Software, Instrument Control & Nyquist Analysis*
- Footer: *Powered by SynAptIp Technologies*
- Version badge: **Version 3.0**

### Bug Fixes / Safety
- All Nyquist operations handle missing columns, empty files, and NaN values without crashing
- Export errors are reported per-file; other files still export successfully

### Preserved from V2.3
- All instrument communication logic (unchanged copy of scan_runner.py)
- All CSV export logic (unchanged copy of csv_exporter.py)
- All unit conversion utilities (unchanged copy of unit_conversion.py)
- Control & Scan tab — identical to V2.3
- Live Results tab — identical to V2.3
- Sample & Output tab — identical to V2.3
- Nyquist Compare tab — identical to V2.3
- Diagnostics & Commands tab — identical to V2.3
