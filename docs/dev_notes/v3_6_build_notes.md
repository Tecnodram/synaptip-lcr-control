# V3.6 Build Notes
SynAptIp Technologies

---

## Comando de build

```bash
# Desde la raíz del proyecto con venv activo:
pyinstaller --noconfirm --clean lcr_control_v3_6.spec

# O usar el script:
build_v3_6.bat
```

## Salida

```
dist/SynAptIp_Nyquist_Analyzer_V3_6.exe
dist/SynAptIp_Nyquist_Analyzer_V3_6/
    SynAptIp_Nyquist_Analyzer_V3_6.exe
    assets/
    example_data/
```

## Resolución de paths en el spec

El spec agrega al sys.path en orden (para alinearse con runtime):
```python
pathex=[src_v3_6_root, src_v3_root, src_v3_5_root]
```

Esto garantiza que PyInstaller encuentre todos los módulos en el orden correcto.

## Hiddenimports clave para V3.6

```python
'licensing'                   # nuevo namespace V3.6
'licensing.device_fingerprint'
'licensing.license_manager'
'licensing.license_storage'
'ui_v36'
'ui_v36.license_dialog_v36'
'ui_v36.main_window_v3_6'
'ui_v36.compare_panel'
```

Más todos los hiddenimports heredados de V3.5 y V3.

## Archivos existentes NO afectados

| Exe | Status |
|---|---|
| `dist/SynAptIp_LCR_Control_V2_3.exe` | Intacto |
| `dist/SynAptIp_LCR_Control_V3.exe` | Intacto |
| `dist/SynAptIp_Nyquist_Analyzer_V3_5.exe` | Intacto |
| `release_v3_5/SynAptIp_Nyquist_Analyzer_V3_5.exe` | Intacto |

## Variable de entorno para testing

```bash
set SYNAPTIP_LICENSE_DISABLED=1
python src_v3_6/lcr_control_v3_6.py
```

Omite el diálogo de licencia al iniciar — útil para desarrollo y CI.

## Dependencias requeridas

Mismas que V3.5 + ninguna adicional:
- PySide6
- pandas
- numpy
- matplotlib
- pyserial
- pyinstaller (solo para build)
