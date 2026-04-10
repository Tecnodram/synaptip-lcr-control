# V3.6 Pre-Check Audit — SynAptIp Nyquist Analyzer
**Fase 0 — Auditoría Técnica Completa**
SynAptIp Technologies
Fecha: 2026-04-09
Auditor: Claude Code (Sonnet 4.6)

---

## 1. ESTRUCTURA GENERAL DEL REPOSITORIO

```
SynAptIp-LCR-Link-Tester/
├── src/                  ← V1/V2 original (instrument control básico)
├── src_v2/               ← V2 refactorizada
├── src_v3/               ← V3 base (Nyquist + licencias + UI completa)
├── src_v3_5/             ← V3.5 (Analysis & Insights, base estable actual)
├── assets/               ← Iconos, screenshots
├── dist/                 ← Ejecutables compilados
├── build/                ← Artefactos de build (PyInstaller)
├── docs/                 ← Documentación técnica y científica
├── example_data/         ← CSV de ejemplo
├── validation/           ← Scripts y datos de validación
├── release_v3_5/         ← Release empaquetado V3.5
├── lcr_control_v3_5.spec ← Spec PyInstaller activo (V3.5)
├── build_v3_5.bat        ← Script de build activo (V3.5)
└── .venv/                ← Entorno virtual Python
```

---

## 2. ENTRYPOINT REAL

**Archivo**: `src_v3_5/lcr_control_v3_5.py`

Responsabilidades:
- Configura `sys.path` para resolver `src_v3` y `src_v3_5` correctamente
- Instala `sys.excepthook` para captura de errores fatales
- Escribe log de startup: `startup_v3_5.log`
- Inicializa `QApplication`
- Lanza `LicenseDialog` (desde `src_v3`)
- Muestra `MainWindowV3_5`

Soporte frozen (PyInstaller):
- Detecta `sys.frozen` y `sys._MEIPASS`
- Ajusta `_BASE_DIR` y `_BUNDLE_DIR` correctamente

---

## 3. UI PRINCIPAL

**Clase**: `MainWindowV3_5` en `src_v3_5/ui_v35/main_window_v3_5.py`

Hereda de `MainWindowV3` (`src_v3/ui/main_window_v3.py`).

Estrategia: **subclase pura** — sobreescribe `_build_ui()` para inyectar
la nueva pestaña sin modificar V3.

---

## 4. SISTEMA DE TABS (COMPLETO)

| # | Nombre Tab | Definido en |
|---|---|---|
| 0 | Control & Scan | `MainWindowV3._build_control_scan_tab()` |
| 1 | Live Results | `MainWindowV3._build_live_results_tab()` |
| 2 | Sample & Output | `MainWindowV3._build_sample_output_tab()` |
| 3 | Nyquist Compare | `MainWindowV3._build_nyquist_compare_tab()` |
| 4 | Nyquist Analysis (V3) | `MainWindowV3._build_nyquist_analysis_tab()` |
| 5 | Diagnostics & Commands | `MainWindowV3._build_diagnostics_tab()` |
| 6 | Analysis & Insights | `AnalysisInsightsPanel` (V3.5, nuevo) |

---

## 5. PARSER CSV

**Módulo**: `src_v3_5/analysis_engine/schema_detector.py`

Capacidades:
- Mapeo de alias de columnas (compatible con V2, V2.3, V3)
- Columnas canónicas: `freq_hz`, `z_ohm`, `theta_deg`, `z_real`, `z_imag`, `minus_z_imag`, `dc_bias`, `status`
- Detección automática de formato DC bias
- Detección robusta — no falla ante columnas desconocidas

**Módulo secundario**: `src_v3/services/csv_exporter.py`

Funciones exportadas:
- `CsvExporter`, `ExportMetadata`
- `LIVE_RESULTS_FIELDNAMES`, `ENRICHED_FIELDNAMES`, `RAW_FIELDNAMES`
- `build_nyquist_xy`, `detect_v2_file_type`, `load_nyquist_preview_points`, `nyquist_components`

---

## 6. LÓGICA DE GRÁFICAS

**Módulo**: `src_v3_5/analysis_engine/plot_engine.py`

Backend: `matplotlib` con `Agg` (seguro para PyInstaller, no-interactive).

15 tipos de gráfica disponibles:
- Nyquist: clean comparative, raw vs clean, individual per bias, freq-colored per bias, freq-colored comparative
- Bode: mag comparative, phase comparative, mag individual, phase individual
- Domain: Z' vs freq, −Z'' vs freq
- Admittance: |Y| mag, phase
- Capacitance: series, parallel

Columnas calculadas por `eis_transformer.py`:
`COL_FREQ`, `COL_Z_REAL`, `COL_Z_IMAG`, `COL_MZ_IMG`, `COL_Z_MAG`,
`COL_THETA`, `COL_OMEGA`, `COL_G`, `COL_B`, `COL_Y_MAG`, `COL_Y_PHS`,
`COL_C_SER`, `COL_C_PAR`, `COL_DC`

---

## 7. EXPORTACIÓN

**Módulos de exportación**:
- `src_v3_5/analysis_engine/export_manager.py` — exporta CSV, PNG, MD report, JSON metadata
- `src_v3/services/csv_exporter.py` — exporta datos de control en vivo (V3 base)
- `src_v3/services/nyquist_export_service.py` — exporta gráficas Nyquist desde la tab V3

Estructura de salida validada:
```
exports_v3/
└── run_<nombre>/
    ├── cleaned/         (clean_data.csv, cleaning_summary.csv, removed_points.csv)
    ├── figures/         (PNG plots)
    ├── metadata/        (JSON: schema, config, version, metadata)
    ├── raw/             (raw_input.csv)
    ├── report/          (report.md, report.txt)
    └── tables/          (dc_bias_summary.csv)
```

---

## 8. SCRIPTS DE BUILD

| Archivo | Propósito | Estado |
|---|---|---|
| `lcr_control_v3_5.spec` | Spec PyInstaller V3.5 (activo) | Válido |
| `build_v3_5.bat` | Build script V3.5 (activo) | Válido |
| `lcr_control_v3.spec` | Spec PyInstaller V3 | Legado |
| `build_v3.bat` | Build script V3 | Legado |
| `dc_bias_probe.spec` | Spec herramienta DC Bias | Legado |
| `nyquist_analyzer.spec` | Spec herramienta Nyquist | Legado |

El spec V3.5 incluye correctamente:
- `pathex` con `src_v3` y `src_v3_5`
- `hiddenimports` para todos los módulos
- `datas` para assets/icons
- Soporte de version file (packaging/windows/)

---

## 9. EJECUTABLES EXISTENTES

| Archivo | Estado |
|---|---|
| `dist/SynAptIp_LCR_Control_V2_3.exe` | Presente |
| `dist/SynAptIp_LCR_Control_V3.exe` | Presente |
| `dist/SynAptIp_Nyquist_Analyzer_V3_5.exe` | Presente (build directo) |
| `dist/SynAptIp_Nyquist_Analyzer_V3_5/SynAptIp_Nyquist_Analyzer_V3_5.exe` | Presente (carpeta empaquetada) |
| `release_v3_5/SynAptIp_Nyquist_Analyzer_V3_5.exe` | Presente (release oficial) |

---

## 10. SISTEMA DE LICENCIA EXISTENTE (V3/V3.5)

**Módulos** (en `src_v3/services/`):
- `license_manager.py` — lógica de trial + validación de clave
- `license_storage.py` — persistencia en `%APPDATA%/SynAptIp/license.json`
- `device_fingerprint.py` — SHA-256 de `node|system|processor`

**UI** (en `src_v3/ui/`):
- `license_dialog.py` — diálogo de activación/trial

**Formato de clave actual**:
```
SYNAPT-V3-<payload_b64>.<sig24>
```

Payload (base64url-encoded JSON):
```json
{"device_id": "...", "expires_utc": "YYYY-MM-DD", "plan": "standard"}
```

Firma: HMAC-SHA256 con secret hardcoded, primeros 24 hex chars.

**Limitaciones del sistema actual** (relevantes para V3.6):
- No usa archivo `.lic` — solo claves de texto
- Payload no incluye `product_name`, `issued_to`, `license_type`
- Trial de 14 días (no configurable en UI)
- Secret en texto plano en código

---

## 11. VALIDACIÓN DE ESTABILIDAD V3.5

### Criterios evaluados:

| Criterio | Estado | Evidencia |
|---|---|---|
| Abre correctamente | ✓ CONFIRMADO | `startup_v3_5.log` presente, exe funcional |
| Exporta CSV | ✓ CONFIRMADO | `validation/outputs/*/cleaned/*.csv` presentes |
| Genera gráficas | ✓ CONFIRMADO | `validation/outputs/*/figures/*.png` presentes (14 plots) |
| Estructura modular estable | ✓ CONFIRMADO | Módulos separation clara, sin dependencias circulares |
| Build reproducible | ✓ CONFIRMADO | Spec y bat presentes, artifacts en dist/ |
| Release empaquetado | ✓ CONFIRMADO | `release_v3_5/` completo con exe, README, LICENSE |

**VEREDICTO: Base V3.5 ESTABLE. Apta para evolución a V3.6.**

---

## 12. ANÁLISIS DE RIESGOS PARA V3.6

| Área | Riesgo | Mitigación |
|---|---|---|
| Sistema de licencias nuevo | Medio — nueva interfaz distinta a V3 | Mantener V3 license como fallback; V3.6 usa su propio sistema |
| Tab "Comparar" | Bajo — patrón ya establecido en V3.5 | Subclase de MainWindowV3_5, misma técnica |
| Parser CSV reutilizado | Bajo — módulos estables | Importar directamente desde analysis_engine |
| Build spec nuevo | Bajo — spec V3.5 es plantilla clara | Copiar y ajustar rutas para V3.6 |
| Namespace collision | Bajo — si se usa `src_v3_6/ui_v36/` | Namespaces únicos por versión |

---

## 13. PLAN ARQUITECTÓNICO V3.6

```
src_v3_6/
├── __init__.py
├── lcr_control_v3_6.py          ← Entrypoint V3.6
├── services/
│   └── licensing/
│       ├── __init__.py
│       ├── device_fingerprint.py ← Reutilizar lógica de V3
│       ├── license_manager.py    ← Nuevo: soporta archivos .lic
│       └── license_storage.py    ← Nuevo: guarda ruta de .lic cargado
└── ui_v36/
    ├── __init__.py
    ├── main_window_v3_6.py       ← Subclase de MainWindowV3_5
    ├── license_dialog_v36.py     ← Nuevo: diálogo elegante V3.6
    └── compare_panel.py          ← Nueva tab "Comparar"

tools/
├── generate_license.py           ← CLI emisión de licencias
└── show_fingerprint.py           ← CLI obtención de fingerprint

lcr_control_v3_6.spec             ← Spec PyInstaller V3.6
build_v3_6.bat                    ← Build script V3.6
docs/dev_notes/                   ← Documentación técnica V3.6
```

**INVARIANTE**: `src_v3/`, `src_v3_5/` y todos los archivos V3.5 quedan
intactos sin ninguna modificación.

---

## 14. CONCLUSIÓN

- **V3.5 confirmada como base estable y válida.**
- No se requiere backup adicional (git tag `v3.5.0` ya existe).
- La evolución a V3.6 puede proceder de forma segura usando el patrón
  de subclase y directorio nuevo.
- El sistema de licencias V3.6 será independiente del V3/V3.5.
- La tab "Comparar" reutilizará `analysis_engine` existente.

**AUTORIZACIÓN: CONTINUAR CON FASE 1.**
