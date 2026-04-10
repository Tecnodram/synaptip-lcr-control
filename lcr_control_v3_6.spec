# -*- mode: python ; coding: utf-8 -*-
# lcr_control_v3_6.spec — SynAptIp Nyquist Analyzer V3.6
# SynAptIp Technologies
#
# Build command (from project root with venv active):
#   pyinstaller --noconfirm --clean lcr_control_v3_6.spec
#
# Output: dist/SynAptIp_Nyquist_Analyzer_V3_6.exe

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

project_root  = Path(SPECPATH)
src_v3_6_root = project_root / 'src_v3_6'
src_v3_5_root = project_root / 'src_v3_5'
src_v3_root   = project_root / 'src_v3'

# Match runtime import precedence: [V3.6, V3, V3.5]
# V3.6 wins for: licensing/, ui_v36/
# V3   wins for: services/, ui/
# V3.5 wins for: analysis_engine/, ui_v35/
for path in [str(src_v3_5_root), str(src_v3_root), str(src_v3_6_root)]:
    if path not in sys.path:
        sys.path.insert(0, path)

hiddenimports = [
    # Qt
    'PySide6.QtWidgets',
    'PySide6.QtCharts',
    'PySide6.QtCore',
    'PySide6.QtGui',
    # Data
    'pandas',
    'pandas.io.formats.style',
    'numpy',
    # Matplotlib
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.figure',
    'matplotlib.cm',
    'matplotlib.colors',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends.backend_pdf',
    # Serial
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
    # V3.6 licensing (unique namespace)
    'licensing',
    'licensing.device_fingerprint',
    'licensing.license_manager',
    'licensing.license_storage',
    # V3.6 UI
    'ui_v36',
    'ui_v36.license_dialog_v36',
    'ui_v36.main_window_v3_6',
    'ui_v36.compare_panel',
    # V3.5 analysis modules
    'analysis_engine',
    'analysis_engine.schema_detector',
    'analysis_engine.eis_transformer',
    'analysis_engine.cleaning_pipeline',
    'analysis_engine.plot_engine',
    'analysis_engine.interpretation_engine',
    'analysis_engine.export_manager',
    # V3.5 UI
    'ui_v35',
    'ui_v35.analysis_insights_panel',
    'ui_v35.main_window_v3_5',
]

hiddenimports += collect_submodules('services')
hiddenimports += collect_submodules('ui')
hiddenimports = sorted(set(hiddenimports))

a = Analysis(
    [str(src_v3_6_root / 'lcr_control_v3_6.py')],
    pathex=[
        str(src_v3_6_root),
        str(src_v3_root),
        str(src_v3_5_root),
    ],
    binaries=[],
    datas=[
        ('assets/icons/SynAptIp_LCR_Control.ico', 'assets/icons'),
        ('assets/icons', 'assets/icons'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SynAptIp_Nyquist_Analyzer_V3_6',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/SynAptIp_LCR_Control.ico',
)
