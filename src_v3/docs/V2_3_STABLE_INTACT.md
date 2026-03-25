# V2.3 Stable — Intact Confirmation

**SynAptIp Technologies**

---

## Status: UNTOUCHED

The following source directories were **not modified** during V3 development:

| Path | Status |
|------|--------|
| `src/` | ✅ Untouched — Version 1 source |
| `src_v2/` | ✅ Untouched — V2.3 Stable source |

---

## V2.3 Functional Checklist

The following V2.3 capabilities remain fully operational and were NOT affected by V3 work:

- [x] Serial instrument connection (COM port, baud, timeout, terminator)
- [x] Measure Once
- [x] Run Sweep (Frequency Sweep Only & DC Bias List + Sweep)
- [x] Live Results table with auto-export
- [x] Manual instrument controls (Frequency, AC Voltage, DC Bias)
- [x] Nyquist Compare tab (QtCharts in-app preview)
- [x] CSV export (live results, raw, enriched)
- [x] Diagnostics & Commands tab

---

## V3 Isolation Strategy

V3 is fully isolated in `src_v3/`.

The V2.3 service files were **copied** (not moved or modified) into `src_v3/services/`:

| File | Origin | Modification |
|------|--------|-------------|
| `scan_runner.py` | `src_v2/services/scan_runner.py` | None — binary-identical copy |
| `csv_exporter.py` | `src_v2/services/csv_exporter.py` | None — binary-identical copy |
| `unit_conversion.py` | `src_v2/services/unit_conversion.py` | None — binary-identical copy |

All new V3 logic is in new files only:
- `src_v3/services/file_loader.py`
- `src_v3/services/nyquist_transformer.py`
- `src_v3/services/nyquist_plotter.py`
- `src_v3/services/nyquist_export_service.py`
- `src_v3/services/plot_view_helpers.py`
- `src_v3/ui/main_window_v3.py`
- `src_v3/ui/nyquist_analysis_panel.py`
- `src_v3/lcr_control_v3.py`

---

*Verified: March 2026 — SynAptIp Technologies*
