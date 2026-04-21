# -*- mode: python ; coding: utf-8 -*-
# lcr_control_v3_7.spec — SynAptIp Nyquist Analyzer V3.7
# SynAptIp Technologies
#
# Build command (from project root with venv active):
#   pyinstaller --noconfirm --clean lcr_control_v3_7.spec
#
# Output: dist/SynAptIp_Nyquist_Analyzer_V3_7.exe

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

project_root  = Path(SPECPATH)
src_v3_7_root = project_root / 'src_v3_7'
src_v3_6_root = project_root / 'src_v3_6'
src_v3_5_root = project_root / 'src_v3_5'
src_v3_root   = project_root / 'src_v3'

# Match runtime import precedence: [V3.7, V3.6, V3, V3.5]
# V3.7 wins for: ui_v37/
# V3.6 wins for: licensing/, ui_v36/
# V3   wins for: services/, ui/
# V3.5 wins for: analysis_engine/, ui_v35/
for path in [str(src_v3_5_root), str(src_v3_root), str(src_v3_6_root), str(src_v3_7_root)]:
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
    # V3.6 licensing (inherited)
    'licensing.license_manager',
    'licensing.license_storage',
    'ui_v36.license_dialog_v36',
    # V3.7 UI components
    'ui_v37.log_sweep_designer',
    'ui_v37.main_window_v3_7',
    # V3.5 analysis (inherited)
    'ui_v35.analysis_insights_panel',
    'analysis_engine',
    # V3 services (inherited)
    'services.csv_exporter',
    'services.scan_runner',
    'services.unit_conversion',
    'services.nyquist_plotter',
    'services.nyquist_transformer',
    'services.nyquist_export_service',
    'services.plot_view_helpers',
    'services.file_loader',
    'services.device_fingerprint',
    # V3 UI (inherited)
    'ui.nyquist_analysis_panel',
    'ui.nyquist_compare_panel',
    'ui.nyquist_analysis_panel',
]

# Collect all submodules for complex packages
hiddenimports += collect_submodules('PySide6')
hiddenimports += collect_submodules('matplotlib')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('numpy')
hiddenimports += collect_submodules('serial')
hiddenimports += collect_submodules('ui')
hiddenimports += collect_submodules('services')
hiddenimports += collect_submodules('ui_v35')
hiddenimports += collect_submodules('ui_v36')
hiddenimports += collect_submodules('ui_v37')
hiddenimports += collect_submodules('licensing')
hiddenimports += collect_submodules('analysis_engine')

a = Analysis(
    ['src_v3_7/lcr_control_v3_7.py'],
    pathex=[
        str(project_root),
        str(src_v3_7_root),
        str(src_v3_6_root),
        str(src_v3_root),
        str(src_v3_5_root),
    ],
    binaries=[],
    datas=[
        # Assets
        ('assets', 'assets'),
        # Example data
        ('example_data', 'example_data'),
        # Licenses
        ('licenses', 'licenses'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SynAptIp_Nyquist_Analyzer_V3_7',
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
