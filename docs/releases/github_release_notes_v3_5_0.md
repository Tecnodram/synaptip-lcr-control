# SynAptIp Nyquist Analyzer v3.5.0

## Release Summary

Version 3.5.0 is the stable release baseline for SynAptIp Nyquist Analyzer, focused on validated EIS analysis workflows, reproducible export structure, and robust Windows executable startup behavior.

## Key Capabilities

- Nyquist analysis outputs from cleaned impedance data.
- Bode magnitude and phase outputs with grouped DC-bias support.
- Derived-domain outputs (Z', -Z'', admittance, capacitance).
- Auditable cleaning pipeline with removed-point tagging.
- Heuristic interpretation report generation (text and markdown).
- Metadata-rich run outputs for reproducibility and archival traceability.

## Validation Summary

Validation was performed using:

- validation/rc_example.csv
- validation/rc_dcbias_example.csv

Result summary:

- rc_example.csv: 13 plots generated, 3.00% points removed, interpretation generated
- rc_dcbias_example.csv: 17 plots generated, 2.00% points removed, interpretation generated
- final status: VALIDATION PASS

## Packaged Assets

- SynAptIp_Nyquist_Analyzer_V3_5.exe (Windows executable)
- README_release.md
- CHANGELOG.md
- LICENSE.txt
- ASSET_MANIFEST_v3_5_0.md

## Intended Use

This release is intended for scientific impedance workflows requiring stable, repeatable analysis outputs and structured export artifacts suitable for reporting and archival citation.

## Known Limitations

- Equivalent-circuit fitting is not included in this release.
- Kramers-Kronig validation is not included in this release.
- Interpretation remains heuristic and should not be treated as definitive scientific judgment.

## Citation and Archival Note

This release is prepared for GitHub Release publication and Zenodo archival.

- Concept DOI: CONCEPT_DOI_PENDING
- Version DOI: VERSION_DOI_PENDING

After Zenodo ingestion, update README, CITATION.cff, and release records with final DOI values.
