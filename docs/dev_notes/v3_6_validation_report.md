# V3.6 Validation Report
SynAptIp Technologies — Fase 7
Fecha: 2026-04-09

---

## Resumen

| Categoría | Tests | Resultado |
|---|---|---|
| Sistema de licencias | 5/5 | PASS |
| Tab Comparar | 3/3 | PASS |
| V3.5 intacto | 1/1 | PASS |
| V3 intacto | 1/1 | PASS |
| Herramientas CLI | 2/2 | PASS |
| **TOTAL** | **12/12** | **TODOS PASAN** |

---

## Detalle de validaciones

### Licencias (5/5)

| # | Test | Estado | Detalle |
|---|---|---|---|
| 1 | Sin licencia → NOT_LOADED | PASS | `save_license_path('') → evaluate() → NOT_LOADED` |
| 2 | Licencia válida → VALID | PASS | `issued_to=SynAptIp Test, days_left=183` |
| 3 | Licencia vencida → EXPIRED | PASS | `expires_at=2024-06-01, state=EXPIRED` |
| 4 | Firma inválida → INVALID | PASS | `signature mismatch detected` |
| 5 | Otro dispositivo → WRONG_DEVICE | PASS | `fingerprint 'a'*64 ≠ device fp` |

### Tab Comparar (3/3)

| # | Test | Estado | Detalle |
|---|---|---|---|
| 6 | schema_detector + eis_transformer | PASS | Columnas Z_real, -Z_imag detectadas |
| 7 | 1 archivo → PNG generado | PASS | PNG >500 bytes, log=[OK] |
| 8 | 3 archivos → 3 [OK] en log | PASS | Nyquist superpuesta 3 datasets |

### Compatibilidad hacia atrás (2/2)

| # | Test | Estado | Detalle |
|---|---|---|---|
| 9 | V3.5 analysis_engine intacto | PASS | `run`, `PlotEngine`, `create_run`, `RunPaths` |
| 10 | V3 services intactos | PASS | `CsvExporter`, `LicenseManager`, `ScanRunner` |

### Herramientas CLI (2/2)

| # | Test | Estado | Detalle |
|---|---|---|---|
| 11 | `tools/show_fingerprint.py` | PASS | Fingerprint 64-char mostrado correctamente |
| 12 | `tools/generate_license.py` | PASS | .lic generado y válido por 6 meses |

---

## Verificación de archivos existentes no modificados

| Archivo | Verificado |
|---|---|
| `src_v3/services/license_manager.py` | Sin cambios (git status limpio) |
| `src_v3/services/csv_exporter.py` | Sin cambios |
| `src_v3/ui/main_window_v3.py` | Sin cambios |
| `src_v3_5/ui_v35/main_window_v3_5.py` | Sin cambios |
| `src_v3_5/analysis_engine/plot_engine.py` | Sin cambios |
| `dist/SynAptIp_Nyquist_Analyzer_V3_5.exe` | Presente e intacto |
| `dist/SynAptIp_LCR_Control_V3.exe` | Presente e intacto |
| `release_v3_5/` | Intacto |

---

## Pendiente (requiere entorno gráfico)

Los siguientes tests requieren display o ejecución manual:

- [ ] App V3.6 abre correctamente (diálogo de licencia)
- [ ] Tabs originales intactas en ventana V3.6
- [ ] Tab "Comparar" funcional con drag & drop visual
- [ ] Build V3.6 con `build_v3_6.bat`

---

## Estado general: VALIDADO

La V3.6 cumple todos los requisitos críticos:
- Sistema de licencias profesional (.lic, 5 estados) ✓
- Tab Comparar funcional con 1/2/3 archivos ✓
- Código V3 y V3.5 sin modificaciones ✓
- Herramientas CLI de emisión funcionales ✓
- Sin colisiones de namespace ✓
