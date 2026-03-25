# SynAptIp LCR Control V3 — User Manual

**SynAptIp Technologies**  
Version 3.0.0 · March 2026

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Connecting the LCR Instrument](#connecting-the-lcr-instrument)
3. [Control & Scan Tab](#control--scan-tab)
4. [Running a Frequency Sweep](#running-a-frequency-sweep)
5. [Single Measurement](#single-measurement)
6. [DC Bias Control](#dc-bias-control)
7. [Live Results Tab](#live-results-tab)
8. [Sample & Output Tab](#sample--output-tab)
9. [Nyquist Analysis Tab](#nyquist-analysis-tab)
10. [Exporting Data](#exporting-data)
11. [Comparison Plots](#comparison-plots)
12. [Diagnostics & Commands Tab](#diagnostics--commands-tab)
13. [Trial & License System](#trial--license-system)
14. [Instrument Setup Assumptions](#instrument-setup-assumptions)
15. [Troubleshooting](#troubleshooting)

---

## System Requirements

- Windows 10 or Windows 11 (64-bit)
- LCR meter with RS-232 or USB-Serial interface (SCPI protocol)
- Appropriate USB-Serial driver installed
- At least 200 MB free disk space

---

## Connecting the LCR Instrument

1. Connect the LCR meter to your PC via the serial (RS-232 or USB-Serial) cable.
2. Open SynAptIp LCR Control V3.
3. Navigate to the **Control & Scan** tab.
4. In the **Connection** section:
   - Click **Refresh Ports** to populate the port list with currently available COM ports.
   - Select the correct COM port from the dropdown.
   - Set the baud rate (default: 9600).
5. Click **Connect**.
   - On success, the status bar confirms the connection and the instrument identity (`*IDN?` response) is logged.
6. To disconnect, click **Disconnect**.

> **Tip:** If the port does not appear, check Device Manager to confirm the USB-Serial driver is installed and the port is recognized.

---

## Control & Scan Tab

This tab contains all instrument control and sweep configuration panels.

### Connection Panel

| Control | Purpose |
|---|---|
| Port selector | Choose the COM port connected to the LCR meter |
| Baud rate | Serial communication speed (default 9600) |
| **Refresh Ports** | Re-scan available COM ports |
| **Connect** | Open the serial connection |
| **Disconnect** | Close the serial connection |

### Sweep Controls

| Control | Purpose |
|---|---|
| Start | Sweep start frequency (value + unit) |
| Stop | Sweep stop frequency (value + unit) |
| Step | Frequency increment per step |
| Point settle | Delay between setting frequency and measuring (default 0.10 s) |
| Measure settle | Additional delay before the FETC? read (default 0.35 s) |
| Bias settle | Delay after applying each DC bias value (default 0.30 s) |

Units for Start / Stop / Step can be selected as Hz, kHz, or MHz from the adjacent dropdown.

### Instrument Direct Controls

These buttons send individual SCPI commands immediately:

| Button | Command Sent |
|---|---|
| **Apply Frequency** | `FREQ <value>` |
| **Apply AC VOLT** | `VOLT <value>` |
| **Apply :BIAS:VOLTage** | `:BIAS:VOLT <value>` (experimental) |
| **DC Bias ON** | `BIAS ON` |
| **DC Bias OFF** | `BIAS OFF` |
| **Optional Bias Verify** | Sends a query to read back the bias state |

### Run Panel

| Control | Purpose |
|---|---|
| Run Mode | **Frequency Sweep Only** or **DC Bias List + Frequency Sweep** |
| DC Bias List (V) | Comma-separated bias voltages, e.g. `-1,-0.5,0,0.5,1` |
| **Preview Run Plan** | Shows the total step count and estimated duration |
| **Measure Once** | Fires a single `FETC?` measurement at the current instrument state |
| **Run** | Starts the selected sweep mode |
| **Stop** | Aborts the running sweep immediately |

---

## Running a Frequency Sweep

1. Connect to the instrument (see above).
2. Confirm the instrument front panel is configured with **Z / TD (theta)** as primary and secondary display modes.
3. Check the **"I confirm the instrument is set to Z / TD on the front panel"** checkbox.
4. Set **Start**, **Stop**, and **Step** frequencies.
5. Select **Run Mode**: choose *Frequency Sweep Only* for a single sweep.
6. Click **Run**.

The sweep will step through each frequency, apply settle delays, issue `FETC?`, and record the result. Progress is shown in the live results table.

---

## Single Measurement

Click **Measure Once** at any time to read one measurement at the current instrument frequency and bias state. The result appears in the Live Results tab.

Use this to verify the instrument is responding correctly before committing to a full sweep.

---

## DC Bias Control

DC Bias enables impedance sweeps across different static bias voltages — useful for characterizing nonlinear devices, capacitors, and electrochemical cells.

1. Set **Run Mode** to *DC Bias List + Frequency Sweep*.
2. Enter bias values in the **DC Bias List** field, separated by commas (e.g. `-1,-0.5,0,0.5,1`).
3. Click **Preview Run Plan** to verify the total number of steps.
4. Click **Run**.

The runner will:
- Apply each bias value from the list in order
- Wait for the **Bias settle** delay
- Execute one full frequency sweep per bias value
- Log all results tagged with the bias level used

> **Note:** The DC bias magnitude command (`:BIAS:VOLT`) is marked experimental for the U2829C. Results depend on instrument firmware. The front panel remains the authoritative source for the active bias value.

---

## Live Results Tab

Displays all measurements collected during the current session in a scrollable table.

Columns: `freq_hz`, `z_ohm`, `theta_deg`, `dc_bias_v`, `status`.

- **Export current live results now** — saves the current table to a CSV immediately, without waiting for the sweep to complete.

---

## Sample & Output Tab

Configure sample identity and output location before running a sweep.

| Field | Purpose |
|---|---|
| Sample Name / ID | Identifier embedded in the exported CSV filename |
| Operator | Operator name logged in the CSV metadata |
| Notes | Free-text note appended to the CSV header |
| Output Folder | Directory where all exports are written |
| **Browse** | Open a folder picker dialog |

> **Tip:** Set the output folder before running the sweep. The Nyquist Analysis tab will inherit this folder automatically.

---

## Nyquist Analysis Tab

The **Nyquist Analysis (V3)** tab is a standalone post-processing panel. It operates independently of the live sweep — you can load any CSV file from a previous run or from another instrument.

### Loading Files

- Up to **3 CSV files** can be loaded simultaneously in slots 1, 2, and 3.
- Click **Load File 1** (or 2 / 3) to open a file picker.
- After loading, the panel shows the filename and the number of valid data points detected.
- Click **Clear** on any slot to unload that file.

### Accepted CSV Formats

The loader accepts three column naming conventions:

| Mode | Required Columns |
|---|---|
| Pre-computed | `z_real`, `z_imag` |
| Z-theta | `z_ohm`, `theta_deg` |
| Primary/Secondary raw | `primary`, `secondary` (integer column index fallback) |

Comment lines starting with `#` are ignored. UTF-8 and Latin-1 encodings are both supported.

### Chart Preview

Click **Refresh Nyquist** to render the Nyquist diagram (Z' on the X-axis, −Z'' on the Y-axis) for all loaded datasets in the built-in chart panel.

Click **Autozoom** to recalculate the axis limits with a 10% margin around all data and redraw.

---

## Exporting Data

All exports are written to the folder configured in the Sample & Output tab (default: `exports_v3/`).

| Button | Output |
|---|---|
| **Export CSV** | `<sample>_nyquist_data.csv` — one file per loaded slot |
| **Export JPG (individual)** | `<sample>_nyquist_YYYYMMDD_HHMMSS.jpg` — 300 dpi Nyquist plot per file |
| **Export JPG (compare)** | `nyquist_compare_YYYYMMDD_HHMMSS.jpg` — overlay of all loaded datasets |
| **Export ALL** | All of the above in one click |

### CSV Structure

Exported Nyquist CSV columns:

```
freq_hz, z_real, z_imag, minus_z_imag
```

### JPG Plot Specifications

- Resolution: 300 dpi
- Format: JPEG (tight bounding box)
- Axes: Z' [Ω] (X-axis), −Z'' [Ω] (Y-axis)
- Includes: title, axis labels, grid, legend, SynAptIp Technologies watermark

---

## Comparison Plots

To generate a Nyquist comparison overlay:

1. Load 2 or 3 CSV files in the Nyquist Analysis tab.
2. Click **Export JPG (compare)** or **Export ALL**.

Each dataset is plotted with a distinct color. The legend uses the filename stem as the label. Axis limits are computed globally across all datasets so all curves are visible.

> **Requirement:** At least 2 slots must contain valid data for the comparison export to proceed.

---

## Diagnostics & Commands Tab

Provides a raw SCPI command interface for advanced users and troubleshooting.

- Enter any SCPI command and click **Send**.
- The response and any error messages are logged in the diagnostics log pane.
- Use this tab to verify instrument identity, query register states, or test new command strings without affecting the sweep workflow.

---

## Trial & License System

On the first launch after installation, a 14-day trial period begins automatically.

- The license dialog shows: trial status, days remaining, and the device ID.
- Click **Continue Trial** to use the software during the trial window.
- To activate, enter a valid activation key (format: `SYNAPT-V3-<key>`) and click **Activate**.
- Once the trial expires, the **Continue Trial** button is disabled and a valid key is required.

License state is stored locally at:

```
%APPDATA%\SynAptIp\license.json
```

No internet connection is required for license validation.

---

## Instrument Setup Assumptions

Before running sweeps, the instrument front panel must be configured manually:

- **Primary display:** Z (ohms)
- **Secondary display:** θ (theta) in degrees, or TD (DEG) mode
- **Range mode:** set on front panel
- **Speed mode:** set on front panel

The software does not automatically configure display mode. The **"I confirm the instrument is set to Z / TD on the front panel"** checkbox must be checked before a sweep run is allowed.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| No COM ports listed | Driver not installed or cable disconnected | Install USB-Serial driver; reconnect cable |
| Connection fails | Wrong COM port or baud rate | Try different port; check Device Manager |
| Sweep produces no data | Instrument not in Z/TD mode | Configure front panel; re-check assumption checkbox |
| JPG export produces blank plot | No valid data points in loaded file | Verify CSV columns; check file format |
| Comparison export disabled | Fewer than 2 slots loaded | Load at least 2 valid CSV files |
| License dialog on every launch (trial) | Expected behavior within trial period | Click Continue Trial or enter activation key |

---

*SynAptIp Technologies · 2026*
