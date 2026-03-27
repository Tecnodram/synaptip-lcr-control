# Admittance and Capacitance — Theoretical Basis

**SynAptIp Technologies — Internal Theory Documentation**

---

## Admittance

Admittance Y is the reciprocal of impedance Z:

```
Y = 1/Z = G + jB
```

Where:
- **G** (Siemens) = conductance = real part of admittance
- **B** (Siemens) = susceptance = imaginary part of admittance

### Computation from Z

Given Z = Z′ + jZ″:

```
G =  Z′ / (Z′² + Z″²)
B = −Z″ / (Z′² + Z″²)
```

### Admittance magnitude

```
|Y| = √(G² + B²) = 1/|Z|
```

### Admittance phase

```
θ_Y = arctan(B/G) = −θ_Z
```

For a purely capacitive element, θ_Y ≈ +90°.  
For a purely resistive element, θ_Y ≈ 0°.

---

## Capacitance

### Series capacitance

The series model represents the effective capacitance assuming the dominant circuit model is a series R-C:

```
C_series = −1 / (ω · Z″)
```

Where ω = 2πf is the angular frequency.

`C_series` is meaningful where Z″ < 0 (capacitive quadrant) and ω > 0.

### Parallel capacitance

The parallel model represents the effective capacitance assuming a parallel R-C structure:

```
C_parallel = B / ω = −Z″ / (ω · |Z|²)
```

`C_parallel` is derived from the imaginary part of admittance.

---

## When to Use Which

| Model | Use case |
|-------|----------|
| C_series | When the impedance is predominantly series, e.g., a thin film capacitor |
| C_parallel | When the impedance suggests a parallel R-C structure |

For practical materials characterization, it is common to plot both and compare.  
If C_series ≈ C_parallel at a given frequency, the simple model may be a good approximation.

---

## Numerical Safety

Both C_series and C_parallel involve division by ω, which becomes undefined at f = 0.  
The cleaning pipeline removes f ≤ 0 rows before capacitance is computed.  
NaN is stored wherever the denominator is zero or the result is non-physical.

---

*This documentation is for internal reference only and is not intended for end-user distribution without review.*
