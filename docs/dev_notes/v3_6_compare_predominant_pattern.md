# V3.6 Compare Tab — Predominant Pattern Summary
SynAptIp Technologies — Phase 6 Documentation
Date: 2026-04-09

---

## 1. Purpose

The **Pattern Summary** is a new view exclusive to the Compare tab (not present in V3.5 Analysis & Insights). Its goal is to provide a **quick diagnostic fingerprint** of each loaded file without requiring the user to interpret individual Nyquist or Bode plots manually.

Scientific context: in EIS, the characteristic frequency f_c (also called corner frequency or peak frequency) separates the resistive and capacitive dominant regions of the impedance spectrum. Files with different f_c values have fundamentally different RC time constants and thus different physical/electrochemical behaviors.

---

## 2. Computed Metrics

### 2.1 Characteristic Frequency (f_c)

```
f_c = freq_hz[ argmax(minus_Z_imag_ohm) ]
```

Physical interpretation: the frequency at which −Z'' reaches its maximum on the Nyquist plot. This is the top of the semicircle. At this point, the resistive and reactive contributions are equal, and the system transitions between high-frequency (resistive) and low-frequency (capacitive) behavior.

**Column required:** `minus_Z_imag_ohm` (COL_MZ_IMG), `freq_hz` (COL_FREQ)

**Units:** Hz

### 2.2 RC Time Constant (tau)

```
tau = 1 / (2 * pi * f_c)
```

Physical interpretation: the relaxation time of the dominant RC circuit element. Larger tau → slower electrochemical process (e.g., thick dielectric layer, slow ion transport). Smaller tau → faster process (e.g., thin film, high conductivity electrolyte).

**Units:** seconds — displayed with SI prefix (ns, us, ms, s)

**SI prefix formatter:**
```python
def _fmt_si(val_s: float) -> str:
    if val_s < 1e-6: return f"{val_s*1e9:.2f} ns"
    if val_s < 1e-3: return f"{val_s*1e6:.2f} us"
    if val_s < 1:    return f"{val_s*1e3:.2f} ms"
    return f"{val_s:.3f} s"
```

### 2.3 DC Resistance Estimate (R_dc)

```
R_dc = max(Z_real_ohm)
```

Physical interpretation: the real part of impedance at the lowest measured frequency approximates the DC resistance of the system. For a simple Randles circuit, this equals R_solution + R_charge_transfer.

**Column required:** `Z_real_ohm` (COL_Z_REAL)

**Units:** Ω — displayed with SI prefix (mΩ, Ω, kΩ, MΩ)

**Note:** This is an estimate. For precise DC resistance, a dedicated DC sweep is required. The label in the summary table reads `R_est` to make the approximation explicit.

### 2.4 Dominant Frequency Behavior

```
if f_c > 10_000 Hz:   behavior = "High-f dominant"
elif f_c > 1_000 Hz:  behavior = "Mid-f dominant"
else:                 behavior = "Low-f dominant"
```

Physical interpretation:
- **High-f dominant** (f_c > 10 kHz): System response governed by fast processes — thin film, low series resistance, geometric capacitance
- **Mid-f dominant** (1 kHz < f_c ≤ 10 kHz): Intermediate processes — moderate dielectric layers, moderate ionic transport
- **Low-f dominant** (f_c ≤ 1 kHz): Slow processes — thick dielectric, Warburg diffusion, slow charge transfer

---

## 3. Pattern Summary Figure Layout

Three panels, left to right:

### Panel 1: Nyquist with f_c markers

- Standard Nyquist overlay (same as the Nyquist plot type)
- Each file additionally plots a star marker at `(Z_real[i_fc], minus_Z_imag[i_fc])`
- Star marker: matplotlib path `(5, 1, 0)`, markersize=13, matching file color
- Helps visually locate where f_c falls on each semicircle

### Panel 2: |Z| vs Frequency with f_c lines

- Standard Bode |Z| overlay (log-log)
- Each file additionally plots a vertical dashed line at `x = f_c`
- Line style: dashed, alpha=0.4, matching file color
- Annotates f_c position on the frequency axis

### Panel 3: Metrics Table

- `ax.axis("off")` — table rendered directly on axes, no visible frame
- Columns: `File | f_c (Hz) | tau | R_est | Behavior`
- Rows: one per successfully processed file
- Cell padding set by matplotlib `cellLoc="center"`, `colWidths` auto-sized
- Header row: bold weight, light blue background
- Data rows: alternating white / light gray for readability

**Files that fail metric computation** (e.g., all −Z'' values ≤ 0, or frequency column absent) are omitted from all three panels with a log message `[SKIP] <file>: cannot compute f_c`.

---

## 4. Scientific Caveats

The Pattern Summary is a **screening tool**, not a substitute for full equivalent circuit fitting. Limitations:

1. f_c detection assumes a single dominant semicircle. Multi-arc spectra (multiple RC elements) will yield the f_c of the dominant arc only.
2. R_dc estimation (`max(Z')`) is only accurate if the lowest measured frequency approaches DC (typically < 1 Hz). Higher low-frequency limits will underestimate R_dc.
3. Behavior classification thresholds (10 kHz, 1 kHz) are general EIS conventions, not calibrated to any specific material system.

These limitations are communicated via the label `R_est` and the behavior classification names using the word "dominant" (not "determined").

---

## 5. New vs. Reused Logic

| Component | Source |
|---|---|
| Nyquist panel rendering | Reuses `_plot_nyquist()` internal logic |
| Bode |Z| panel rendering | Reuses `_plot_freq_compare()` with `COL_Z_MAG` |
| f_c computation | New — `_compute_file_metrics()` in `compare_panel.py` |
| tau computation | New — derived from f_c |
| R_dc estimation | New — `max(COL_Z_REAL)` |
| Table rendering | New — `ax.table()` call |

No new analysis engine modules were created. All logic is self-contained in `compare_panel.py` to maintain the additive architecture invariant.

