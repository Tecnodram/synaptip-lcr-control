# User Manual V2

## Overview

SynAptIp LCR Control V2.3 is an isolated Version 2 application under src_v2.

Current tabs:
- Control & Scan
- Live Results
- Sample & Output
- Nyquist Compare
- Diagnostics & Commands

Version 2.3 keeps scan/control workflow, diagnostics, and Nyquist visualization in one interface while preserving Version 1 separately.

## Connection

1. Select a COM port.
2. Set baud rate, timeout, and terminator.
3. Click Connect.
4. Confirm connection status in the Connection panel.

Use Refresh Ports to re-scan available serial ports.

## Manual Instrument Control

Manual controls are provided for confirmed lab command paths:
- Frequency value and unit selector (Hz / kHz / MHz)
- Apply Frequency
- AC VOLT control
- DC Bias ON
- DC Bias OFF
- DC Bias Voltage value
- Apply :BIAS:VOLTage
- Optional Bias Verify (:BIAS?, :BIAS:STAT?, :BIAS:VOLT?)

Instrument setup assumptions for measurement:
- Main display: Z ohm
- Secondary display: theta / TD DEG
- Range mode: front-panel setting
- Speed mode: front-panel setting

Current V2 acquisition assumes the instrument front panel is configured to Z / TD (or theta) mode before running measurements.
V2 does not currently claim confirmed remote commands for selecting main/secondary function, speed, or range.

## Frequency Sweep

Run mode: Frequency Sweep Only

Behavior:
- Executes one sweep from start to stop using configured step size.
- Uses selected sweep unit (Hz/kHz/MHz).
- DC bias is not applied as a list sweep in this mode.

Recommended workflow:
1. Set start/stop/step and unit.
2. Click Preview Run Plan.
3. Click Run.
4. Use Stop if needed.

## DC Bias List + Frequency Sweep

Run mode: DC Bias List + Frequency Sweep

Behavior:
- Uses the editable DC Bias List field (default: -1,-0.5,0,0.5,1).
- Executes one full frequency sweep for each listed bias value in order.
- Logs run plan and measurement activity in Live Log.

Recommended workflow:
1. Set sweep range and unit.
2. Enter DC bias list as comma-separated values.
3. Click Preview Run Plan and verify bias order and point estimate.
4. Click Run.
5. Use Stop for controlled interruption.

## Nyquist Compare

Nyquist Compare supports up to 3 selected files simultaneously.

Per slot:
- file display
- Browse
- Clear

Actions:
- Refresh Nyquist: parse selected files and redraw comparison
- Clear Status: clear parser/load status messages

Supported file types:
- Type A raw instrument-compatible CSV
- Type B enriched CSV

Nyquist convention:
- X = z_real
- Y = -z_imag

If one slot is invalid, unsupported, or empty, valid slots still render.

## Output Files

Version 2.3 stores active run rows in one in-memory source and uses that same source for Live Results and export.

Run export timing:
- Run does not create a CSV at run start.
- CSV is written only after full run completion when rows were collected.
- If no rows were collected, export is skipped and logged.

Helper action:
- Export current live results now

The exported CSV contains the live measurement columns used by the table, including raw_response and failure status fields.

## Notes / Pending Improvements

- Capture and persist instrument identity string directly into metadata at run time.
- Optional run summary panel in UI for completed sweeps.
- Optional point decimation for very large Nyquist visualizations.
- Extended validation for duplicate bias values and out-of-range bias entries.
