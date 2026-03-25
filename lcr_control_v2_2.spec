# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path(SPECPATH)
src_v2_root = project_root / 'src_v2'
version_file = project_root / 'packaging' / 'windows' / 'lcr_control_v2_2_version.txt'

hiddenimports = [
    'PySide6.QtCharts',
    'pandas',
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
]

a = Analysis(
    ['src_v2\\lcr_control_v2.py'],
    pathex=[str(src_v2_root)],
    binaries=[],
    datas=[('assets/icons/SynAptIp_LCR_Control.ico', 'assets/icons')],
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
    name='SynAptIp_LCR_Control_V2_2',
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
