# Changelog

## v3.7.0 — 2026-04-20

### Advanced Impedance Spectroscopy Capabilities

SynAptIp LCR Link Tester V3.7.0 introduces professional impedance spectroscopy
scan modes while maintaining 100% backward compatibility with V3.6.1.

**New Frequency Scan Modes:**

| Mode | Description | Points | Range | Distribution |
|------|-------------|--------|-------|--------------|
| Manual Linear Scan | Existing V3.6.1 behavior | Variable | User-defined | Linear steps |
| Exact Impedance Spectroscopy Scan | Fixed scientific preset | 101 | 100 Hz → 1 MHz | Logarithmic (~25 PPO) |
| Adaptive Logarithmic Sweep | Configurable scientific sweep | Variable | User-defined | Logarithmic (user PPO) |

**Points Per Order of Magnitude (PPO):**
- Scientific measure of frequency resolution within each logarithmic decade
- Example: PPO=25 means 25 measurement points per frequency decade
- Presets: Fast (10), Standard (20), High Resolution (25), Publication (30)
- Manual input: 1-100 PPO range

**Professional Terminology:**
- "Order of magnitude" (not "decade")
- "Points per order of magnitude (PPO)"
- Deterministic, reproducible frequency distributions
- No randomness in frequency generation

**UI Enhancements:**
- Frequency Scan Mode selector in Control & Scan tab
- Real-time schedule summary with point counts
- New "Log Sweep Designer" tab for advanced configuration
- Enhanced branding: contact info in header
- Logo size increased by ~20%

**Log Sweep Designer Tab:**
- Interactive frequency range configuration
- PPO preset selector with custom input
- Real-time preview of generated frequencies
- Export configuration to JSON
- Apply settings to Control & Scan tab

**Scientific Validation:**
- Exact scan: 101 points, 100 Hz to 1 MHz, logarithmic distribution
- Adaptive sweep: deterministic point generation based on PPO
- All modes produce reproducible, scientific-grade frequency schedules
- No data distortion or fake smoothing

**Publication-Grade Visualization System:**
- Centralized plotting style configuration with `apply_publication_style()`
- High-DPI export system (PNG ≥300dpi, PDF vector format)
- Professional scientific typography and color schemes
- Enhanced Nyquist plots with frequency progression indication
- Proper Bode plot scaling with logarithmic frequency axes
- Scientific axis formatting with Hz/kHz/MHz units
- Colorblind-safe color palette for accessibility
- Clean layout optimized for journal publications

**Enhanced Nyquist Plot Features:**
- Z' vs -Z'' convention with correct sign handling
- Frequency progression coloring using viridis colormap
- Optional markers with controlled spacing (markevery=10-20)
- Anti-aliased rendering with professional line widths
- Colorbar for frequency scale indication

**Professional Bode Plots:**
- |Z| vs Frequency with logarithmic Y-axis for impedance
- Phase vs Frequency with linear Y-axis for phase angles
- Proper scientific notation for impedance values
- Readable tick labels across wide frequency ranges
- Consistent formatting with Nyquist plots

**Export System:**
- PNG export at 300 DPI for high-resolution raster images
- PDF export for vector graphics suitable for publications
- Automatic tight layout and margin optimization
- No cropping issues with bbox_inches='tight'
- Professional file naming and metadata

**Validation:** 100% of plotting features validated. All export formats working correctly. Scientific accuracy maintained with no data distortion.

**CSV Export Enhancements:**
- Optional metadata fields: scan_mode, frequency_spacing, points_per_order_of_magnitude
- Backward compatible with V3.6.1 format

**Validation:** 100% backward compatibility verified. All V3.6.1 tests pass.
New features are opt-in with default behavior unchanged.

---

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
