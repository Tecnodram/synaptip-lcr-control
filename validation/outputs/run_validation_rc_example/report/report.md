# SynAptIp Nyquist Analyzer V3.5 — Analysis Report

**SynAptIp Technologies**

| Field | Value |
|-------|-------|
| Generated | 2026-03-26 21:28:15 |
| Source | `rc_example.csv` |
| Version | 3.5.0 |

---

## Findings

1. The cleaned dataset contains 97 valid measurement points after the cleaning pipeline removed 3 points (3.0%).
2. The impedance response appears mixed resistive-capacitive (median θ ≈ -16.6°). The median phase angle is between 0° and −90°, suggesting a mixed resistive-capacitive character.
3. The Nyquist plot appears to describe a significant arc in the −Z'' direction, which is consistent with a capacitive loop or charge-transfer process.
4. The minimum Z' value is approximately 729.48 Ω, which may be consistent with a finite series resistance contribution.
5. The maximum −Z'' value of 422 Ω occurs near 98.1 kHz, which may suggest a characteristic relaxation frequency associated with the dominant time constant.

---

## Disclaimer

This report is generated automatically from numerical analysis. All statements use cautious, hedged language and should not be treated as definitive engineering or scientific conclusions. Human expert review is recommended for critical applications.
