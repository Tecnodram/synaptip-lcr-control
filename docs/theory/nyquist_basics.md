# Nyquist Plot — Theoretical Basis

**SynAptIp Technologies — Internal Theory Documentation**

---

## What is a Nyquist Plot?

A Nyquist plot is a standard representation in Electrochemical Impedance Spectroscopy (EIS).  
It displays the imaginary part of impedance against the real part across a range of frequencies.

**Axes:**
- Horizontal (X): Z′ — real part of impedance (Ω)
- Vertical (Y): −Z″ — negative imaginary part of impedance (Ω)

The convention −Z″ on the Y axis ensures that capacitive arcs appear in the **first quadrant** (positive X, positive Y), which is the standard presentation in electrochemistry and materials science.

---

## Interpretation of Features

### Semicircular arc

A semicircular arc in the first quadrant is commonly associated with a parallel R-C circuit element, often called a "Randles cell" component.  
The diameter of the arc along the X axis gives an estimate of the charge-transfer or polarization resistance.

### Warburg diffusion tail

A 45° line at low frequencies may suggest diffusion-limited behavior, as described by the Warburg impedance element.

### Inductive behavior

Points in the fourth quadrant (positive X, negative Y, i.e., positive Z″) may indicate inductive contributions from contact resistance, leads, or electrochemical processes at high frequencies.

### Depressed arcs

A semicircle that appears "depressed" (center below the X axis) often indicates distributed relaxation times, frequently modeled with a Constant Phase Element (CPE) rather than a pure capacitor.

---

## Common Cautions

- Nyquist plots do not show frequency explicitly.  
  Use Bode plots to directly observe frequency dependence.
- The shape of the arc depends strongly on measurement quality, frequency range, and sample preparation.
- Equivalent circuit fitting (not implemented in this tool) provides quantitative estimates but is subject to non-uniqueness.

---

*This documentation is for internal reference only and is not intended for end-user distribution without review.*
