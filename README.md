# SynAptIp LCR Link Tester — V3.6.1

### Scientific Instrument Control & Nyquist Analysis Platform

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)
![License](https://img.shields.io/badge/License-Proprietary-orange)
[![DOI](https://zenodo.org/badge/1191187505.svg)](https://doi.org/10.5281/zenodo.19212713)

![SynAptIp LCR Control V3 Interface](assets/screenshots/main_ui.png)

**SynAptIp Technologies** · AI · Scientific Software · Instrument Intelligence

---

## Overview

SynAptIp LCR Link Tester is a scientific desktop application for impedance
workflows and Nyquist analysis. It is compatible with LCR instruments supporting
SCPI communication and designed for repeatable frequency-domain characterization.

V3.6.1 is the current production release. It extends the V3.5 analysis platform
with a professional license system and a 10-plot scientific Compare tab.
V3, V3.5, and V3.6 share a strict additive architecture — no existing behavior
was modified between versions.

---

## Key Features

| Feature | Details |
|---|---|
| Instrument communication | SCPI serial over standard COM interfaces |
| Frequency sweep automation | Configurable start / stop / step (Hz, kHz, MHz) |
| DC bias control | Per-sweep bias list workflow with settle delays |
| Single measurement | One-shot FETC? acquisition for quick checks |
| Live results display | Real-time table with Z, theta, and status columns |
| CSV export | Structured per-run export with sample metadata |
| Nyquist transform | Z_real / Z_imag computation from Z-theta raw data |
| Analysis & Insights | EIS post-processing: cleaning, plots, interpretation report |
| **Compare tab** | **10-plot scientific multi-file comparison dashboard** |
| Pattern Summary | Per-file f_c, tau, R_dc, behavior classification |
| Offline-first | Local processing, no cloud dependency |
| License system | Offline device-bound .lic activation |
| Windows EXE | Single-file .exe via PyInstaller |

### Compare Tab — 10 Plot Types

| # | Plot |
|---|---|
| 1 | Nyquist Comparison |
| 2 | Bode Magnitude |
| 3 | Bode Phase |
| 4 | Z' (Real) vs Frequency |
| 5 | −Z'' (Imaginary) vs Frequency |
| 6 | Admittance Magnitude |
| 7 | Admittance Phase |
| 8 | Series Capacitance |
| 9 | Parallel Capacitance |
| 10 | Pattern Summary (3-panel + metrics table) |

Supports up to 3 simultaneous CSV files. Datasets are visually differentiated
by color, line style, and marker shape.

---

## Scientific Positioning

SynAptIp LCR Link Tester is a general-purpose platform for:

- Impedance analysis and Nyquist interpretation
- Repeatable frequency-domain characterization workflows
- Structured data generation for reports and publication pipelines
- Research and engineering environments requiring offline instrumentation software

---

## Use Cases

- Electrical characterization workflows
- Materials science impedance studies
- Electrochemistry data processing
- Semiconductor analysis support
- Instrumentation automation for repeatable measurement sequences

---

## License & Evaluation

V3.6.1 requires a valid license file (`.lic`) to run. The license is
device-bound and loaded through the application's built-in license dialog at
startup.

**V3.6.1 does not include an automatic free trial.** Evaluation access is
available on request at no cost.

### Requesting an Evaluation License

1. Launch `SynAptIp_Nyquist_Analyzer_V3_6.exe`.
2. When the license dialog appears, locate and copy the **Device Fingerprint**
   displayed in the dialog.
3. Email the fingerprint to **synaptip.tech@gmail.com** with a brief description
   of your use case (research, academic, commercial evaluation, etc.).
4. You will receive a `.lic` file by return email.
5. In the license dialog, click **Load License File**, select the `.lic` file,
   and the application will unlock.

Evaluation licenses are time-limited. The expiry date is shown in the license
dialog once a license is loaded. A streamlined self-service evaluation flow is
planned for a future version.

---

## Installation (Development)

Requires Python 3.11+ and Git.

```bash
git clone https://github.com/your-org/SynAptIp-LCR-Link-Tester.git
cd SynAptIp-LCR-Link-Tester

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

Run from source (V3.6):

```bash
python src_v3_6/lcr_control_v3_6.py
```

---

## Build Executable

Build the V3.6 Windows executable:

```bat
.\build_v3_6.bat
```

Output:

```text
dist\SynAptIp_Nyquist_Analyzer_V3_6.exe
```

---

## Running the Software

1. Double-click `SynAptIp_Nyquist_Analyzer_V3_6.exe`
2. The license dialog appears — copy the Device Fingerprint shown
3. Request a `.lic` file as described in [License & Evaluation](#license--evaluation)
4. Load the `.lic` file in the dialog — the application unlocks fully

---

## Scientific Output

### Nyquist & Analysis Plots (PNG, 150–300 dpi)

Individual analysis output per run:

```text
<output_folder>/run_YYYYMMDD_HHMMSS/
  cleaned/          cleaned dataset CSV
  figures/          individual analysis plots
  report/           interpretation report
  metadata/         metadata.json
```

Compare tab output:

```text
<output_folder>/compare/
  compare_nyquist.png
  compare_bode_mag.png
  compare_<plot_id>_YYYYMMDD_HHMMSS.png
```

### Structured CSV Export

Per-run output fields:

- `freq_hz`, `z_ohm`, `theta_deg`
- `z_real`, `z_imag`, `minus_z_imag`
- Sample metadata and run timestamps

---

## Scientific Methodology

- [docs/methodology/nyquist_method.md](docs/methodology/nyquist_method.md)
- [docs/theory/](docs/theory/)
- [docs/paper_support/](docs/paper_support/)

Nyquist analysis plots Z_real on the horizontal axis and −Z_imag on the vertical:

```
Z' = |Z| cos(θ)
Z'' = |Z| sin(θ)
```

---

## Example Datasets and Validation

- [example_data/](example_data/) — illustrative input datasets
- [example_outputs/](example_outputs/) — reference output plots and CSVs
- [docs/validation/validation_protocol.md](docs/validation/validation_protocol.md)

Scripted validation (V3.5 engine):

```bat
.venv\Scripts\python.exe validation\validate_v3_5.py
```

---

## Project Structure

```text
src_v3_6/              V3.6 entry point and UI (Compare tab, license dialog)
  lcr_control_v3_6.py  Entry point
  ui_v36/              Main window, Compare tab, license dialog
src_v3_5/              V3.5 analysis engine (unchanged)
  analysis_engine/     EIS pipeline: schema detection, transform, cleaning, plots
  ui_v35/              Analysis & Insights panel
src_v3/                V3 base (unchanged)
  services/            Instrument, CSV, Nyquist services
  ui/                  Base main window
docs/                  Methodology, theory, validation, release notes
assets/icons/          Application icons
example_data/          Example CSV input files
example_outputs/       Reference output plots and CSVs
validation/            Validation scripts and datasets
build_v3_6.bat         V3.6 build script
lcr_control_v3_6.spec  PyInstaller spec
requirements.txt       Python dependencies
```

---

## Reproducibility

1. Load a CSV in the Analysis & Insights tab
2. Select an output folder
3. Click Run Analysis
4. Review the generated `run_YYYYMMDD_HHMMSS/` folder

Compare tab:

1. Load 1–3 CSV files in the Compare tab
2. Select a plot type from the dropdown
3. Click Compare
4. Export PNG via the Export button

---

## Citation

If you use this software in academic or scientific work, please cite:

Ramírez Martínez, D. (2026). *SynAptIp LCR Link Tester: Scientific Instrument
Control & Nyquist Analysis Platform* (Version 3.6.1) [Software]. Zenodo.
https://doi.org/10.5281/zenodo.19212714

---

## DISCLAIMER

This software is an independent development by SynAptIp Technologies.

It is not affiliated with, endorsed by, or officially connected to any instrument
manufacturer, laboratory, or institution.

All product names, trademarks, and registered trademarks are property of their
respective owners.

---

## License

This software is proprietary and owned by SynAptIp Technologies.

Permission is granted for academic and non-commercial research use only, subject
to explicit request and approval by the author.

Commercial use, redistribution, sublicensing, or integration into commercial
systems is strictly prohibited without prior written authorization.

No warranty is provided. This software is supplied "as is."

---

## Author

Developed independently by Daniel Ramírez Martínez, SynAptIp Technologies
