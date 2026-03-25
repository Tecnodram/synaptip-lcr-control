# -*- mode: python ; coding: utf-8 -*-
# lcr_control_v3.spec — SynAptIp LCR Control V3
# SynAptIp Technologies
#
# Build command (from project root with venv active):
#   pyinstaller --noconfirm --clean lcr_control_v3.spec
#
# Output: dist/SynAptIp_LCR_Control_V3.exe

from pathlib import Path

project_root = Path(SPECPATH)
src_v3_root  = project_root / 'src_v3'
version_file = project_root / 'packaging' / 'windows' / 'lcr_control_v3_version.txt'

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
    # Matplotlib (optional — JPG export)
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends.backend_pdf',
    # Serial
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
]

a = Analysis(
    [str(src_v3_root / 'lcr_control_v3.py')],
    pathex=[str(src_v3_root)],
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
    name='SynAptIp_LCR_Control_V3',
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
    version=str(version_file),
)
