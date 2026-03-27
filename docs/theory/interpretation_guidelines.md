# Interpretation Guidelines

**SynAptIp Technologies — Internal Theory Documentation**

---

## Purpose

The smart interpretation module in V3.5 produces automated, cautious technical commentary  
on EIS datasets.  These guidelines define the language policy, what claims are permitted,  
and what must always be hedged.

---

## Language Policy

### Permitted hedged language

The following phrases are permitted and encouraged:

- "appears to suggest"
- "is consistent with"
- "may indicate"
- "the data is compatible with"
- "could be interpreted as"
- "suggests the possibility of"

### Forbidden definitive language

The following categories of claim must never be used:

- Direct material identification: ~~"this is a capacitor"~~
- Guaranteed quantification: ~~"the capacitance is exactly X"~~
- Definite fault identification: ~~"the device is faulty"~~
- Clinical or safety claims of any kind

---

## What the Automation Can Reasonably State

### Phase-based behavior

| Phase range | Permitted statement |
|-------------|---------------------|
| θ near 0° | "predominantly resistive behavior is suggested" |
| θ near −90° | "a strongly capacitive response appears consistent with the data" |
| Intermediate | "mixed resistive-capacitive character is indicated" |

### Nyquist arc

| Feature | Permitted statement |
|---------|---------------------|
| Semicircular arc | "a capacitive relaxation arc is suggested" |
| Flat trajectory | "resistive behavior may dominate" |
| Distorted arc | "distributed relaxation or CPE behavior may be present" |

### DC bias dependence

| Observation | Permitted statement |
|-------------|---------------------|
| Z′ changes with bias | "impedance appears to vary with DC bias, which may indicate a non-linear or bias-dependent element" |
| No significant change | "the impedance response appears relatively stable across the tested bias conditions" |

### Characteristic frequency

When the maximum of −Z″ is identifiable, it is reported as "the frequency at which the maximum imaginary impedance occurs", not as a confirmed "resonance" or "pole".

---

## Disclaimer (mandatory in all reports)

Every auto-generated report must include this disclaimer:

> This report is generated automatically from numerical analysis.  
> All statements use cautious, hedged language and should not be treated  
> as definitive engineering or scientific conclusions.  
> Human expert review is recommended for critical applications.

---

## Dispersion / Outlier Notation

If cleaning removed > 20% of points, the report must note:

> A significant fraction of points was removed during cleaning.  
> Conclusions should be treated with caution.

If 5–20% were removed:

> Some outlier points were removed. The removed_points.csv file is available for review.

---

*This documentation is for internal reference only and is not intended for end-user distribution without review.*
