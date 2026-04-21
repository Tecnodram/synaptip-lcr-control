# V4.1 Release Handoff

V4.1 is the current stable base for SynAptIp Nyquist Analyzer.

## What changed

- V4.1 keeps the stable V4 run logic.
- `Control & Scan` now uses vertical scrolling.
- `Sweep Controls` is organized into:
  - `Linear Sweep`
  - `Log Sweep`
  - `Timing`
- The header now presents the product more professionally and includes the contact email:
  - `synaptip.tech@gmail.com`

## Stable launch points

- Source launcher:
  - [lcr_control_v4_1.py](/C:/Projects/SynAptIp-LCR-Link-Tester/src_v4_1/lcr_control_v4_1.py)
- Main window:
  - [main_window_v4_1.py](/C:/Projects/SynAptIp-LCR-Link-Tester/src_v4_1/ui_v41/main_window_v4_1.py)
- Build script:
  - [build_v4_1.bat](/C:/Projects/SynAptIp-LCR-Link-Tester/build_v4_1.bat)
- PyInstaller spec:
  - [lcr_control_v4_1.spec](/C:/Projects/SynAptIp-LCR-Link-Tester/lcr_control_v4_1.spec)

## Delivery folder

- Release folder:
  - [SynAptIp_Nyquist_Analyzer_V4_1](/C:/Projects/SynAptIp-LCR-Link-Tester/dist/SynAptIp_Nyquist_Analyzer_V4_1)
- Executable:
  - [SynAptIp_Nyquist_Analyzer_V4_1.exe](/C:/Projects/SynAptIp-LCR-Link-Tester/dist/SynAptIp_Nyquist_Analyzer_V4_1/SynAptIp_Nyquist_Analyzer_V4_1.exe)

## Safe restart point for future work

- Use V4.1 as the base for future improvements.
- Prefer changing UI layout before changing run logic.
- Do not modify the runner path unless the frequency plan, bias plan, and preview/run parity are revalidated together.
- If a future version is started, fork from `src_v4_1` instead of `src_v4` or `src_v3_7`.

## Quick validation checklist

- App opens successfully.
- `Frequency Sweep Only` still runs.
- `DC Bias List + Frequency Sweep` still runs.
- `Log Sweep Designer` still previews and runs.
- `DC Bias List + Log Sweep Designer` still sends the generated frequency list to the runner.

