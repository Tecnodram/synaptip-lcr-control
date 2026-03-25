# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path(SPECPATH)
src_root = project_root / 'src'
version_file = project_root / 'packaging' / 'windows' / 'dc_bias_probe_version.txt'

a = Analysis(
    ['src\\dc_bias_probe.py'],
    pathex=[str(src_root)],
    binaries=[],
    datas=[('assets/icons/SynAptIp_DC_Bias_Probe.ico', 'assets/icons')],
    hiddenimports=[],
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
    name='SynAptIp_DC_Bias_Probe',
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
    icon='assets/icons/SynAptIp_DC_Bias_Probe.ico',
    version=str(version_file),
)
