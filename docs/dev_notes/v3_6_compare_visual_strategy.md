# V3.6 Compare Tab — Visual Strategy
SynAptIp Technologies — Phase 6 Documentation
Date: 2026-04-09

---

## 1. Design Constraints

The Compare tab overlays up to 3 files on a single axes. Key tensions:

- **Color alone is insufficient** — color-blind users; B&W printing
- **Marker alone is insufficient** — overlapping dense data clouds
- **Line style alone is insufficient** — thin styles merge at small sizes
- **Clutter is the primary failure mode** — competing legend, grid, and 3 datasets

Solution: **three-axis differentiation** — color + line style + marker, simultaneously.

---

## 2. File Style Palette

Each file slot gets a unique style triplet. All three attributes differ across all slots:

| Slot | Color | Hex | Line Style | Marker | Line Width | Marker Size |
|---|---|---|---|---|---|---|
| File 1 | Blue | `#1d4ed8` | Solid (`-`) | Circle (`o`) | 1.4 pt | 5 |
| File 2 | Amber | `#b45309` | Dashed (`--`) | Square (`s`) | 1.4 pt | 5 |
| File 3 | Teal | `#065f46` | Dotted (`:`) | Triangle (`^`) | 1.6 pt | 5 |

**Color selection rationale:**
- Blue `#1d4ed8`: primary brand color, high contrast on white
- Amber `#b45309`: warm contrast to blue, passes WCAG AA vs white
- Teal `#065f46`: distinct hue from both, readable in dark/light
- All three are perceptually distinct for common color-blindness types (deuteranopia, protanopia)

**Line style rationale:**
- Solid → primary / reference file
- Dashed → secondary comparison
- Dotted → tertiary, visually lighter weight

**Marker rationale:**
- Circle, square, triangle: three distinct shapes with no rotational ambiguity
- Marker every-Nth point: `markevery=max(1, len(x)//12)` — avoids marker crowding

---

## 3. Figure Layout Principles

### Standard frequency-domain plots (7 of 10)

```
┌─────────────────────────────────────────┐
│  Title (concise, ≤ 60 chars)            │
│                                         │
│  Y axis (log or linear)                 │
│  ─────────────────────────────────────  │
│  X axis (log freq Hz)                   │
│                                         │
│  Legend: upper right, frameon, 3 items  │
└─────────────────────────────────────────┘
figure size: 9 × 5 inches, 110 dpi
```

- Grid: major only, alpha=0.25, linestyle `--`
- No minor grid (reduces noise)
- Font: default matplotlib, title 11pt bold
- Axis labels: 10pt, includes units
- Legend: fontsize 8pt, no shadow, white facecolor

### Nyquist plot

```
┌─────────────────────────────────────────┐
│  Nyquist Comparison                     │
│                                         │
│  −Z'' (Ω)      * equal aspect *        │
│  ─────────────────────────────────────  │
│  Z' (Ω)                                │
│                                         │
│  Legend: upper right                    │
└─────────────────────────────────────────┘
```

- `ax.set_aspect("equal")` — physical semicircle shape preserved
- Y-axis label: `−Z'' (Ω)` with proper minus sign (en-dash)
- Data sorted by frequency ascending before plotting

### Pattern Summary (3-panel)

```
┌──────────────┬──────────────┬──────────────────────────┐
│  Nyquist     │  |Z| + f_c   │  Metrics Table           │
│  + f_c stars │  vlines      │  File | f_c | tau | R_dc │
│              │              │  Behavior                │
└──────────────┴──────────────┴──────────────────────────┘
figure size: 14 × 5 inches, 110 dpi
```

- Star marker at f_char (characteristic frequency): matplotlib path `(5, 1, 0)`, size 180
- Vertical f_char lines: dashed, alpha=0.4, matching file color
- Table: right panel, no visible axes (`ax.axis("off")`), `ax.table()` with auto-column-width
- Panel title font: 10pt bold

---

## 4. Anti-Clutter Rules

| Rule | Implementation |
|---|---|
| Markers sparse, not on every point | `markevery=max(1, len(x)//12)` |
| Grid subtle | `alpha=0.25`, major only |
| Legend compact | `fontsize=8`, no shadow |
| Axis labels concise | e.g. `"|Z| (Ω)"` not `"Impedance magnitude in Ohms"` |
| No annotations on data points | Avoids overlap with 3 files |
| Consistent margins | `tight_layout(pad=1.4)` |
| Figure cleared on replot | `fig.clf()` before each generation |

---

## 5. Graceful Degradation

Missing columns are handled per-plot without crashing:

- If a required column is absent: file is skipped with log message `[SKIP] <file>: missing column <col>`
- If ALL files skip: log shows `[WARN] No plottable data` and empty axes returned
- Nyquist: if `COL_MZ_IMG` missing, file silently skipped
- Pattern Summary: if f_char cannot be computed (no valid peak), file omitted from table

This ensures partial data (e.g., file without admittance columns) does not break comparison of files that do have those columns.

---

## 6. Export

- Format: PNG, 150 dpi (print quality)
- Filename: `compare_<plot_id>_<YYYYMMDD_HHMMSS>.png`
- Output directory: synced from "Sample & Output" tab folder on startup and folder change
- Export disabled until at least one plot has been generated

