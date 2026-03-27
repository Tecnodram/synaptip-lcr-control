# -*- mode: python ; coding: utf-8 -*-
# lcr_control_v3_5.spec — SynAptIp Nyquist Analyzer V3.5
# SynAptIp Technologies
#
# Build command (from project root with venv active):
#   pyinstaller --noconfirm --clean lcr_control_v3_5.spec
#
# Output: dist/SynAptIp_Nyquist_Analyzer_V3_5.exe

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

project_root  = Path(SPECPATH)
src_v3_5_root = project_root / 'src_v3_5'
src_v3_root   = project_root / 'src_v3'
version_file  = project_root / 'packaging' / 'windows' / 'lcr_control_v3_5_version.txt'

# Match source-runtime import precedence: V3 must win for top-level `services`
# and `ui`, while V3.5 uses unique `analysis_engine` and `ui_v35` namespaces.
for path in (str(src_v3_5_root), str(src_v3_root)):
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
    # Matplotlib (required for all plot exports)
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
    # V3.5 analysis modules
    'analysis_engine',
    'analysis_engine.schema_detector',
    'analysis_engine.eis_transformer',
    'analysis_engine.cleaning_pipeline',
    'analysis_engine.plot_engine',
    'analysis_engine.interpretation_engine',
    'analysis_engine.export_manager',
    # V3.5 UI modules
    'ui_v35',
    'ui_v35.analysis_insights_panel',
    'ui_v35.main_window_v3_5',
]

hiddenimports += collect_submodules('services')
hiddenimports += collect_submodules('ui')
hiddenimports = sorted(set(hiddenimports))

a = Analysis(
    [str(src_v3_5_root / 'lcr_control_v3_5.py')],
    # Include both src_v3_5 and src_v3 so all imports resolve correctly
    pathex=[str(src_v3_root), str(src_v3_5_root)],
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
    name='SynAptIp_Nyquist_Analyzer_V3_5',
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
    version=str(version_file) if Path(str(version_file)).exists() else None,
)
