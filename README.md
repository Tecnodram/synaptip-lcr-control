# SynAptIp LCR Control V3

### Scientific Instrument Control & Nyquist Analysis Platform

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)
![License](https://img.shields.io/badge/License-Proprietary-orange)

**SynAptIp Technologies** · AI · Scientific Software · Instrument Intelligence

---

## Overview

SynAptIp LCR Control V3 is a professional desktop application for scientists and engineers who require precise impedance measurement, frequency sweep automation, and Nyquist plot generation from LCR instruments.

It communicates with LCR meters over serial (SCPI protocol), automates frequency sweeps with configurable DC bias conditions, and provides a full post-processing pipeline that produces publication-quality Nyquist plots and structured CSV exports — all offline, with no cloud dependency.

V3 is an additive evolution of the stable V2.3 instrument control release. All existing V2.3 functionality is preserved intact. V3 adds an entirely new Nyquist analysis and export layer.

**Target users:** researchers, laboratory engineers, materials scientists, electrochemists, and semiconductor characterization teams.

---

## Key Features

| Feature | Details |
|---|---|
| LCR instrument communication | SCPI serial protocol over RS-232 / USB-Serial |
| Frequency sweep automation | Configurable start / stop / step with selectable units (Hz, kHz, MHz) |
| DC Bias control | Per-sweep bias list, ON/OFF with settle delays |
| Single measurement | One-shot FETC? acquisition for quick checks |
| Live results display | Real-time table with Z, theta, and status columns |
| CSV export | Structured per-run export with sample metadata |
| Nyquist transform | z_real / z_imag computation from Z-theta raw data |
| Nyquist plot (individual) | 300 dpi JPG per file, timestamped filename |
| Nyquist plot (comparison) | Overlay of up to 3 datasets in a single 300 dpi JPG |
| Export ALL | One-click: all CSVs + all individual JPGs + comparison JPG |
| Offline-first | No internet required; all processing is local |
| Trial / license system | 14-day trial; device-bound offline activation |
| Windows EXE distribution | Single-file `.exe` via PyInstaller |

---

## Use Cases

- **Electrochemical impedance spectroscopy (EIS):** generate Nyquist plots from multi-frequency impedance measurements to characterize electrodes, electrolytes, and interfaces.
- **Materials characterization:** automated frequency sweeps across dielectrics, ferroelectrics, and thin films.
- **Semiconductor analysis:** impedance profiling of MOS capacitors, p-n junctions, and passivation layers.
- **Research instrumentation automation:** scripted multi-bias sweeps for parameter extraction in device modeling.
- **Quality assurance:** repeatable measurement protocols with logged metadata and structured CSV archives.

---

## Installation (Development)

Requires Python 3.11+ and Git.

```bash
git clone https://github.com/your-org/SynAptIp-LCR-Link-Tester.git
cd SynAptIp-LCR-Link-Tester

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
pip install matplotlib
```

Run directly from source:

```bash
python src_v3/lcr_control_v3.py
```

To bypass the trial dialog during development:

```bash
$env:SYNAPTIP_LICENSE_DISABLED="1"
python src_v3/lcr_control_v3.py
```

---

## Build Executable

A fully self-contained Windows `.exe` is produced by PyInstaller.

```bat
.\build_v3.bat
```

Output:

```
dist\SynAptIp_LCR_Control_V3.exe
```

The build script:
- removes previous V3 build artifacts only (V2.x releases are untouched)
- verifies matplotlib and PyInstaller are present
- confirms the V2.3 `.exe` is still intact after the build completes

---

## Running the Software

1. Double-click `SynAptIp_LCR_Control_V3.exe`
2. On first launch, the trial system activates a **14-day trial period**
3. To permanently activate, enter a valid activation key in the license dialog
4. Click **Continue Trial** to proceed during the trial window

Trial state and activation keys are stored in:

```
%APPDATA%\SynAptIp\license.json
```

---

## Scientific Output

### Nyquist Plots (JPG, 300 dpi)

Individual plots per input file:
```
exports_v3/<sample>_nyquist_YYYYMMDD_HHMMSS.jpg
```

Comparison overlay plot (requires 2–3 files loaded):
```
exports_v3/nyquist_compare_YYYYMMDD_HHMMSS.jpg
```

All plots include axis labels (Z' [Ω] and −Z'' [Ω]), a title, a legend, and a SynAptIp Technologies watermark.

### Structured CSV Export

Per-run measurement CSV files contain: `freq_hz`, `z_ohm`, `theta_deg`, `z_real`, `z_imag`, sample metadata, and run timestamp.

Nyquist transform CSVs (from the Nyquist Analysis tab) contain: `freq_hz`, `z_real`, `z_imag`, `minus_z_imag`.

---

## Citation

If you use this software in academic or scientific work, please cite:

> SynAptIp Technologies. (2026). *SynAptIp LCR Control V3: Scientific Instrument Control & Nyquist Analysis Platform*. DOI: (pending Zenodo)

---

## Project Structure

```
src_v3/               # V3 application source
  lcr_control_v3.py   # Entry point
  services/           # Instrument, CSV, Nyquist, licensing services
  ui/                 # PySide6 main window and panels
  docs/               # V3-specific internal docs
src_v2/               # V2.x stable release (DO NOT MODIFY)
src/                  # V1 legacy source (DO NOT MODIFY)
packaging/windows/    # VSVersionInfo files for EXE metadata
docs/                 # Project-level documentation
assets/icons/         # Application icons
build_v3.bat          # V3 build script
requirements.txt      # Python dependencies
```

---

## License

Proprietary software. Academic and research use is permitted upon request. Commercial use requires written authorization from SynAptIp Technologies.

---

## Author

**Dan Ramirez**  
SynAptIp Technologies  
AI · Scientific Software · Instrument Intelligence

---

> *Legacy note: The original README content for V1/V2 tooling is preserved below for reference.*

---

# SynAptIp U2829C Desktop Tools (Legacy V1/V2 Reference)

This repository also provides two related Windows desktop applications for the EUCOL U2829C:

- SynAptIp LCR Control: clean day-to-day control and measurement UI for confirmed commands.
- SynAptIp DC Bias Probe: experimental utility for safe, manual probing of unresolved DC bias value command syntax.

Both tools share the same controller and serial communication layers.

## Tool Split

### 1) SynAptIp LCR Control

Canonical packaging entry point: src/nyquist_analyzer.py

Compatibility wrapper: src/main.py

Purpose:
- Stable serial connection and identity query
- Confirmed frequency/level/DC-bias-state controls
- Single-shot measurement fetch via FETC?
- Compact instrument-style workflow with diagnostics log

### 2) SynAptIp DC Bias Probe

Canonical packaging entry point: src/dc_bias_probe.py

Compatibility wrapper: src/main_dc_bias_probe.py

Purpose:
- Keep experimental command probing out of the main control app
- Send one candidate command at a time by explicit user action
- Optionally run a constrained short sequence with delay and follow-up read
- Record probe attempts and responses while treating front panel as source of truth

## Confirmed Protocol Status

Confirmed write commands:
- FREQ <value>
- VOLT <value>
- BIAS ON / BIAS OFF

Confirmed read/measurement commands:
- *idn?
- FETC?

Confirmed measurement field mapping in Z-theta mode:
- Field 0 -> primary value (Z in ohms)
- Field 1 -> secondary value (theta in degrees)
- Field 2 -> status flag (0 means normal)

Unresolved command:
- DC bias magnitude/value command remains unknown for U2829C.
- The main app intentionally does not send guessed DC bias value commands.

## Tech Stack

- Python 3.11+
- PySide6 (GUI)
- pyserial (serial communications)
- PyInstaller (Windows executable packaging)

## Project Structure

SynAptIp-LCR-Link-Tester/
|
+-- src/
|   +-- main.py
|   +-- main_dc_bias_probe.py
|   +-- nyquist_analyzer.py
|   +-- dc_bias_probe.py
|   +-- ui/
|   |   +-- main_window.py
|   |   +-- dc_bias_probe_window.py
|   +-- core/
|   |   +-- controller.py
|   +-- instrument/
|   |   +-- serial_client.py
|   +-- utils/
|       +-- helpers.py
|
+-- build_exe.bat
+-- build_all.bat
+-- nyquist_analyzer.spec
+-- dc_bias_probe.spec
+-- packaging/
|   +-- windows/
|       +-- nyquist_analyzer_version.txt
|       +-- dc_bias_probe_version.txt
+-- requirements.txt
+-- README.md

## Setup (Windows PowerShell)

1. Open this folder in VS Code.
2. Create and activate a virtual environment.
3. Install dependencies.

```powershell
cd c:\Projects\SynAptIp-LCR-Link-Tester
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Run in Development

Run LCR Control:

```powershell
python src\nyquist_analyzer.py
```

Run DC Bias Probe:

```powershell
python src\dc_bias_probe.py
```

## Build Windows Executables

### Prerequisites

- Python 3.11 virtual environment created and activated.
- Dependencies installed from `requirements.txt`.
- Run all commands from the repository root (`C:\Projects\SynAptIp-LCR-Link-Tester`).

### Optional: Add Application Icons

No `.ico` files are currently included. To add branded icons, place them here before building:

- `assets/icons/SynAptIp_LCR_Control.ico` — used by SynAptIp LCR Control
- `assets/icons/SynAptIp_DC_Bias_Probe.ico` — used by SynAptIp DC Bias Probe

If the files are absent the build succeeds without an icon.

### Run the Build

```powershell
.\build_all.bat
```

This builds both executables in sequence using the dedicated spec files:
- `nyquist_analyzer.spec` → SynAptIp LCR Control
- `dc_bias_probe.spec` → SynAptIp DC Bias Probe

### Output Locations

- `dist\SynAptIp_LCR_Control.exe` — main instrument control app
- `dist\SynAptIp_DC_Bias_Probe.exe` — experimental DC bias probe utility
- `build\` — intermediate PyInstaller work files (safe to delete after a successful build)

### Direct Commands (alternative to build_all.bat)

```powershell
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --distpath dist --workpath build\nyquist_analyzer nyquist_analyzer.spec
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --distpath dist --workpath build\dc_bias_probe dc_bias_probe.spec
```

## Safety Notes for Probe Workflow

- Do not infer write success from serial response alone.
- Run probe commands only by explicit operator action.
- Keep command sequences short and rate-limited.
- Use the instrument front panel as the confirmation authority.

## Architecture Notes

The code remains layered (UI -> controller/worker -> serial client -> helpers), allowing the two tools to share stable communication behavior while separating production controls from protocol experimentation.
