# V3.5.0 Release Record

## Release Identity

- Product: SynAptIp Nyquist Analyzer
- Version: 3.5.0
- Git tag: v3.5.0
- Release status: Stable production baseline
- Release date: RELEASE_DATE_PENDING

## Exact Scope of V3.5.0

V3.5.0 is a release-hardening and scientific traceability baseline with:

- frozen V3 compatibility for legacy control and UI paths
- analysis pipeline for schema detection, impedance transformation, cleaning, plotting, interpretation, and export
- metadata enrichment suitable for reproducibility and archival use
- startup robustness for frozen executable launch modes

## Validation Datasets Used

- validation/rc_example.csv
- validation/rc_dcbias_example.csv

## Validation Results

- rc_example.csv:
  - points removed: 3.00%
  - plots generated: 13
  - interpretation findings: 5
- rc_dcbias_example.csv:
  - points removed: 2.00%
  - plots generated: 17
  - interpretation findings: 7
- overall status: VALIDATION PASS

## Packaging Notes

- Packaging method: PyInstaller one-file executable using lcr_control_v3_5.spec.
- Dist target folder:
  - dist/SynAptIp_Nyquist_Analyzer_V3_5/
- Main executable:
  - dist/SynAptIp_Nyquist_Analyzer_V3_5/SynAptIp_Nyquist_Analyzer_V3_5.exe

## Startup Robustness Notes

- Startup no longer depends on external launch CWD.
- Frozen runtime path resolution uses sys.executable and sys._MEIPASS.
- Startup diagnostics are written to:
  - dist/SynAptIp_Nyquist_Analyzer_V3_5/startup_v3_5.log
- Verified launch consistency for:
  - console launch
  - no-console (double-click equivalent) launch

## Release Assets Included

- release_v3_5/SynAptIp_Nyquist_Analyzer_V3_5.exe
- release_v3_5/README_release.md
- release_v3_5/CHANGELOG.md
- release_v3_5/LICENSE.txt
- release_v3_5/ASSET_MANIFEST_v3_5_0.md

## Intentionally Deferred to V4

- circuit fitting workflows
- Kramers-Kronig validation workflows
- advanced interpretation expansion
- major UI modernization beyond V3.5.0 freeze scope
