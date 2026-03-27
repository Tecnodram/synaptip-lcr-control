# SynAptIp Nyquist Analyzer V3.5 Release

Version: 3.5.0
Status: Stable release
Platform: Windows 10 / 11 (64-bit)

## Contents

- SynAptIp_Nyquist_Analyzer_V3_5.exe
- assets/
- validation/
- example_data/
- LICENSE.txt
- CHANGELOG.md

## Release Scope

This release hardens the V3.5 Analysis & Insights workflow for production use without changing the established V3 and V3.5 analysis architecture.

Included release outputs support:

- Nyquist plots
- Bode plots
- derived impedance-domain plots
- DC bias comparative analysis
- cleaning summaries and removed-point tracking
- heuristic interpretation report generation
- metadata export for reproducibility

## Validation

The bundled validation folder contains:

- rc_example.csv
- rc_dcbias_example.csv
- validate_v3_5.py

Run validation from the release root with:

```bat
python validation\validate_v3_5.py
```

Expected terminal conclusion:

```text
VALIDATION PASS
```

## Reproducible Workflow

1. Launch the executable.
2. Open the Analysis & Insights tab.
3. Load a CSV dataset.
4. Select an output folder.
5. Run analysis.
6. Review the generated run folder including raw, cleaned, figures, report, and metadata outputs.