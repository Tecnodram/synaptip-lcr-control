# SynAptIp LCR Control V3

**SynAptIp Technologies**  
*AI, Scientific Software & Instrument Intelligence*

---

## What is V3?

SynAptIp LCR Control V3 is a safe evolution of the stable V2.3 release.

V3 adds a full **Nyquist post-processing and export pipeline** on top of the complete V2.3 instrument control suite.  All V2.3 functionality is preserved intact — nothing in `src/` or `src_v2/` was modified.

---

## How to Run

```bash
cd src_v3
python lcr_control_v3.py
```

Or from the project root:

```bash
python src_v3/lcr_control_v3.py
```

### Requirements

Same as V2.3 plus `matplotlib` for JPG export:

```bash
pip install -r requirements.txt
pip install matplotlib
```

---

## V3 New Tab: Nyquist Analysis

The new **Nyquist Analysis (V3)** tab is located to the right of the existing V2.3 tabs.

### Workflow

1. Click **Load File 1** (and optionally File 2 / File 3) to select CSV files.
2. The panel shows the file name and valid point count per slot.
3. Click **Refresh Nyquist** to render the in-app chart preview.
4. Use **Autozoom** to fit all curves into view.
5. Export:
   - **Export CSV** — saves `<stem>_nyquist_data.csv` for each loaded file
   - **Export JPG (individual)** — saves `<stem>_nyquist.jpg` per file
   - **Export JPG (compare)** — saves `nyquist_compare.jpg` (requires 2+ files)
   - **Export ALL** — all of the above in one click

### Accepted Input Columns

| Mode | Required Columns |
|------|-----------------|
| Pre-computed | `z_real`, `z_imag` |
| Standard V2 export | `z_ohm`, `theta_deg` |
| Raw instrument | `primary`, `secondary` (treated as z_ohm / theta_deg) |

Any V2.3 enriched or live-results CSV is accepted directly.

### Output Files

| File | Description |
|------|-------------|
| `<stem>_nyquist_data.csv` | Nyquist-transformed data: freq_hz, z_real, z_imag, −z_imag |
| `<stem>_nyquist.jpg` | Individual Nyquist plot |
| `nyquist_compare.jpg` | Overlay comparison of 2–3 files |

---

## V2.3 Features (Unchanged)

- COM port connection and instrument control
- Frequency sweep (Frequency Sweep Only / DC Bias List + Sweep)
- Measure Once
- Live Results table with auto-export
- Sample & Output metadata configuration
- Nyquist Compare tab (V2.3 preview)
- Diagnostics & Commands tab

---

## V3 Source Structure

```
src_v3/
  lcr_control_v3.py          ← entry point
  services/
    scan_runner.py            ← copied from V2.3 (unchanged)
    csv_exporter.py           ← copied from V2.3 (unchanged)
    unit_conversion.py        ← copied from V2.3 (unchanged)
    file_loader.py            ← NEW: CSV loader for Nyquist
    nyquist_transformer.py    ← NEW: z_real/z_imag computation + CSV export
    nyquist_plotter.py        ← NEW: matplotlib JPG generation
    nyquist_export_service.py ← NEW: export orchestrator
    plot_view_helpers.py      ← NEW: axis limits, colors
  ui/
    main_window_v3.py         ← NEW: V3 main window (V2.3 + Nyquist Analysis tab)
    nyquist_analysis_panel.py ← NEW: self-contained Nyquist panel widget
  docs/
    README_V3.md
    V3_CHANGELOG.md
    V2_3_STABLE_INTACT.md
```
