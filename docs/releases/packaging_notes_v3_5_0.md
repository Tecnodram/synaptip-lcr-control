# Packaging Notes (v3.5.0)

## Windows Packaging Method

- Build script: build_v3_5.bat
- Spec file: lcr_control_v3_5.spec
- Packager: PyInstaller
- Target output folder:
  - dist/SynAptIp_Nyquist_Analyzer_V3_5/

## Startup Robustness Summary

- Frozen startup path handling resolves executable base path via sys.executable.
- Frozen bundle module path resolution uses sys._MEIPASS.
- Startup is decoupled from caller CWD.
- Startup tracing is written to:
  - startup_v3_5.log (in executable folder)

## Known Non-Blocking Packaging Warnings

- Platform-conditional optional imports reported by PyInstaller (for non-Windows components) may appear in warn-lcr_control_v3_5.txt.
- These warnings are non-blocking for Windows runtime when launch and validation checks pass.

## Dist Folder Structure

dist/
  SynAptIp_Nyquist_Analyzer_V3_5/
    SynAptIp_Nyquist_Analyzer_V3_5.exe
    assets/
    example_data/
    validation/
