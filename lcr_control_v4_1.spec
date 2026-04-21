# -*- mode: python ; coding: utf-8 -*-
# lcr_control_v4_1.spec - SynAptIp Nyquist Analyzer V4.1

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

project_root = Path(SPECPATH)
src_v4_1_root = project_root / "src_v4_1"
src_v4_root = project_root / "src_v4"
src_v3_6_root = project_root / "src_v3_6"
src_v3_5_root = project_root / "src_v3_5"
src_v3_root = project_root / "src_v3"

for path in [str(src_v3_5_root), str(src_v3_root), str(src_v3_6_root), str(src_v4_root), str(src_v4_1_root)]:
    if path not in sys.path:
        sys.path.insert(0, path)

hiddenimports = [
    "PySide6.QtWidgets",
    "PySide6.QtCharts",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "pandas",
    "pandas.io.formats.style",
    "numpy",
    "matplotlib",
    "matplotlib.pyplot",
    "matplotlib.figure",
    "matplotlib.cm",
    "matplotlib.colors",
    "matplotlib.backends.backend_agg",
    "matplotlib.backends.backend_pdf",
    "serial",
    "serial.tools",
    "serial.tools.list_ports",
    "licensing.license_manager",
    "licensing.license_storage",
    "ui_v36.license_dialog_v36",
    "ui_v4.main_window_v4",
    "ui_v41.main_window_v4_1",
    "ui_v35.analysis_insights_panel",
    "analysis_engine",
    "services.csv_exporter",
    "services.scan_runner",
    "services.unit_conversion",
    "services.nyquist_plotter",
    "services.nyquist_transformer",
    "services.nyquist_export_service",
    "services.plot_view_helpers",
    "services.file_loader",
    "services.device_fingerprint",
    "ui.nyquist_analysis_panel",
]

hiddenimports += collect_submodules("PySide6")
hiddenimports += collect_submodules("matplotlib")
hiddenimports += collect_submodules("pandas")
hiddenimports += collect_submodules("numpy")
hiddenimports += collect_submodules("serial")
hiddenimports += collect_submodules("ui")
hiddenimports += collect_submodules("services")
hiddenimports += collect_submodules("ui_v35")
hiddenimports += collect_submodules("ui_v36")
hiddenimports += collect_submodules("ui_v4")
hiddenimports += collect_submodules("ui_v41")
hiddenimports += collect_submodules("licensing")
hiddenimports += collect_submodules("analysis_engine")

a = Analysis(
    ["src_v4_1/lcr_control_v4_1.py"],
    pathex=[
        str(project_root),
        str(src_v4_1_root),
        str(src_v4_root),
        str(src_v3_6_root),
        str(src_v3_root),
        str(src_v3_5_root),
    ],
    binaries=[],
    datas=[
        ("assets", "assets"),
        ("example_data", "example_data"),
        ("licenses", "licenses"),
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
    name="SynAptIp_Nyquist_Analyzer_V4_1",
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
    icon="assets/icons/SynAptIp_LCR_Control.ico",
)

