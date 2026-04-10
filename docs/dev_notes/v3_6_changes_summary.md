# V3.6 Changes Summary
SynAptIp Technologies — Fase 6

---

## Archivos NUEVOS creados

### Entrypoint
- `src_v3_6/lcr_control_v3_6.py` — Entry point V3.6

### Sistema de licencias (nuevo, independiente)
- `src_v3_6/licensing/__init__.py`
- `src_v3_6/licensing/device_fingerprint.py` — Fingerprint con MAC + CPU count
- `src_v3_6/licensing/license_manager.py` — Gestor .lic con 5 estados
- `src_v3_6/licensing/license_storage.py` — Persistencia en %APPDATA%

### UI V3.6
- `src_v3_6/ui_v36/__init__.py`
- `src_v3_6/ui_v36/license_dialog_v36.py` — Diálogo elegante V3.6
- `src_v3_6/ui_v36/main_window_v3_6.py` — Ventana principal V3.6
- `src_v3_6/ui_v36/compare_panel.py` — Tab "Comparar"

### Herramientas
- `tools/generate_license.py` — CLI emisión de licencias
- `tools/show_fingerprint.py` — CLI obtención de fingerprint

### Build
- `lcr_control_v3_6.spec` — PyInstaller spec V3.6
- `build_v3_6.bat` — Script de build V3.6

### Licencias generadas
- `licenses/` — Carpeta de licencias emitidas (en .gitignore si contiene datos cliente)

### Documentación
- `docs/dev_notes/v3_6_precheck_audit.md`
- `docs/dev_notes/v3_6_branching_strategy.md`
- `docs/dev_notes/v3_6_changes_summary.md`
- `docs/dev_notes/v3_6_licensing.md`
- `docs/dev_notes/v3_6_compare_tab.md`
- `docs/dev_notes/v3_6_build_notes.md`
- `docs/dev_notes/v3_6_license_emission_guide.md`

---

## Archivos EXISTENTES modificados

**NINGUNO.** La regla crítica se cumple íntegramente.

---

## Módulos reutilizados sin modificación

| Módulo | Origen | Usado por |
|---|---|---|
| `analysis_engine.schema_detector` | V3.5 | compare_panel.py |
| `analysis_engine.eis_transformer` | V3.5 | compare_panel.py |
| `services.csv_exporter` | V3 | MainWindowV3 (herencia) |
| `services.scan_runner` | V3 | MainWindowV3 (herencia) |
| `ui.nyquist_analysis_panel` | V3 | MainWindowV3 (herencia) |
| `ui_v35.analysis_insights_panel` | V3.5 | MainWindowV3_6 |
| `matplotlib` (Agg backend) | V3.5 | compare_panel.py |

---

## Cadena de herencia

```
QMainWindow
└── MainWindowV3           [src_v3/ui/main_window_v3.py]      — SIN TOCAR
    └── MainWindowV3_5     [src_v3_5/ui_v35/main_window_v3_5.py] — SIN TOCAR
        └── MainWindowV3_6 [src_v3_6/ui_v36/main_window_v3_6.py] — NUEVO
```

---

## Resolución de sys.path en runtime

```
[0] src_v3_6  ← licensing/, ui_v36/
[1] src_v3    ← services/, ui/
[2] src_v3_5  ← analysis_engine/, ui_v35/
```

V3.6 usa namespaces únicos (`licensing/`, `ui_v36/`) — sin colisiones.
