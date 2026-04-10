# V3.6 Branching & Evolution Strategy
**Fase 1 — Congelación de Base**
SynAptIp Technologies
Fecha: 2026-04-09

---

## 1. SNAPSHOT DE SEGURIDAD

Se ha creado el siguiente tag git como referencia inmutable de la base V3.5:

```
git tag: v3.5.0-base-for-v3.6
commit:  e352a4e  (release: v3.5.0 Nyquist DC Bias Analyzer, validated, stable)
```

Para restaurar la base en cualquier momento:
```bash
git checkout v3.5.0-base-for-v3.6
```

Para ver diferencias entre base y V3.6:
```bash
git diff v3.5.0-base-for-v3.6 HEAD
```

---

## 2. REGLA PRINCIPAL DE EVOLUCIÓN

> **NINGÚN archivo de `src_v3/` o `src_v3_5/` será modificado.**

La V3.6 se construye enteramente en directorios nuevos:

```
src_v3_6/          ← todo código nuevo V3.6
tools/             ← herramientas de administración (nuevas)
```

Archivos existentes afectados (solo adiciones, ninguna modificación):
- `lcr_control_v3_6.spec`  ← nuevo, copia base del v3.5
- `build_v3_6.bat`         ← nuevo, copia base del v3.5

---

## 3. ÁRBOL DE HERENCIA DE LA APLICACIÓN

```
QMainWindow
└── MainWindowV3  [src_v3/ui/main_window_v3.py]  — NO TOCAR
    └── MainWindowV3_5  [src_v3_5/ui_v35/main_window_v3_5.py]  — NO TOCAR
        └── MainWindowV3_6  [src_v3_6/ui_v36/main_window_v3_6.py]  ← NUEVO
```

Cada nivel solo agrega. Nunca modifica el nivel anterior.

---

## 4. ÁRBOL DE HERENCIA DE LICENCIAS

```
V3 License (src_v3/services/)      — sistema simple, trial + key HMAC
V3.5 License (reutiliza V3)        — sin cambios
V3.6 License (src_v3_6/services/licensing/)  ← NUEVO sistema profesional .lic
```

El sistema V3.6 es completamente independiente.
No modifica ni hereda del sistema V3.

---

## 5. RESOLUCIÓN DE sys.path EN V3.6

El entrypoint `src_v3_6/lcr_control_v3_6.py` configurará sys.path en este orden:

```
[0] src_v3_6/         ← V3.6: ui_v36/, services/licensing/
[1] src_v3_5/         ← V3.5: analysis_engine/, ui_v35/
[2] src_v3/           ← V3:   services/, ui/
```

Esto permite importar módulos de V3 y V3.5 sin copiarlos ni modificarlos.

Namespaces únicos por versión:
- `ui/`              → V3 (license_dialog, nyquist_analysis_panel, main_window_v3)
- `ui_v35/`          → V3.5 (analysis_insights_panel, main_window_v3_5)
- `ui_v36/`          → V3.6 (compare_panel, license_dialog_v36, main_window_v3_6)
- `services/`        → V3 (csv_exporter, scan_runner, device_fingerprint, license_manager...)
- `analysis_engine/` → V3.5 (schema_detector, plot_engine, eis_transformer...)
- `services/licensing/` → V3.6 (NUEVO, independiente)

---

## 6. ALCANCE DE CAMBIOS V3.6

### Archivos NUEVOS (solo creación):

```
src_v3_6/__init__.py
src_v3_6/lcr_control_v3_6.py
src_v3_6/services/__init__.py
src_v3_6/services/licensing/__init__.py
src_v3_6/services/licensing/device_fingerprint.py
src_v3_6/services/licensing/license_manager.py
src_v3_6/services/licensing/license_storage.py
src_v3_6/ui_v36/__init__.py
src_v3_6/ui_v36/main_window_v3_6.py
src_v3_6/ui_v36/license_dialog_v36.py
src_v3_6/ui_v36/compare_panel.py
tools/__init__.py
tools/generate_license.py
tools/show_fingerprint.py
lcr_control_v3_6.spec
build_v3_6.bat
docs/dev_notes/v3_6_changes_summary.md
docs/dev_notes/v3_6_licensing.md
docs/dev_notes/v3_6_compare_tab.md
docs/dev_notes/v3_6_build_notes.md
docs/dev_notes/v3_6_license_emission_guide.md
docs/dev_notes/v3_6_validation_report.md
```

### Archivos EXISTENTES modificados: **NINGUNO**

---

## 7. CRITERIOS DE REVERSIBILIDAD

Para revertir completamente a V3.5 en cualquier momento:

```bash
# Opción 1: eliminar solo los nuevos directorios
rm -rf src_v3_6/ tools/
# + eliminar lcr_control_v3_6.spec, build_v3_6.bat

# Opción 2: restaurar al tag de base
git checkout v3.5.0-base-for-v3.6

# Verificar integridad V3.5
python src_v3_5/lcr_control_v3_5.py
```

---

## 8. ESTADO: BASE CONGELADA

- Tag `v3.5.0-base-for-v3.6` creado en commit `e352a4e`
- Rama `main` activa — V3.6 evoluciona directamente (sin branch separado)
- Toda modificación V3.6 será aditiva y trazable via `git diff`

**AUTORIZACIÓN: CONTINUAR CON FASE 2 — Sistema de Licencias.**
