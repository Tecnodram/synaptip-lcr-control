# Bode Plots — Theoretical Basis

**SynAptIp Technologies — Internal Theory Documentation**

---

## What is a Bode Plot?

A Bode plot consists of **two separate frequency-domain representations** of impedance:

1. **Bode magnitude plot**: |Z| (Ω) vs. frequency (Hz) — typically on log-log axes
2. **Bode phase plot**: θ (°) vs. frequency (Hz) — typically on a log-linear axis

Unlike the Nyquist plot, Bode plots **explicitly show frequency**, making it straightforward to identify at which frequencies particular features occur.

---

## Bode Magnitude — |Z| vs Frequency

The magnitude |Z| represents the total opposition to alternating current at each frequency.

| Behavior | Signature |
|----------|-----------|
| Pure resistor | |Z| constant across frequency |
| Pure capacitor | |Z| decreases linearly with frequency (slope −1 on log-log) |
| Series RC | Flat at high frequency (R dominates), rising at low frequency (C dominates) |
| Parallel RC | Flat at low frequency (R dominates), rising at high frequency |

---

## Bode Phase — θ vs Frequency

The phase angle θ indicates the relative phase shift between voltage and current.

| θ value | Interpretation |
|---------|----------------|
| ≈ 0° | Predominantly resistive |
| ≈ −90° | Predominantly capacitive |
| Intermediate | Mixed resistive-capacitive, transition region |
| > 0° | Inductive contribution |

---

## Characteristic Frequency

The transition frequency (often called f_c or f_characteristic) is the frequency where the resistive and capacitive contributions are approximately equal.  
At this frequency, the phase is typically near −45° for a simple RC system.

---

## Common Cautions

- Bode plots are most informative when the frequency range spans several decades.
- Phase noise is often amplified at frequency extremes (very high or very low frequency).
- Bode and Nyquist plots contain equivalent information for linear time-invariant systems, but each highlights different aspects of the response.

---

*This documentation is for internal reference only and is not intended for end-user distribution without review.*
