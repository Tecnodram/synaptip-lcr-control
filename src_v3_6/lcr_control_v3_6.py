"""
lcr_control_v3_6.py — SynAptIp Nyquist Analyzer V3.6 Entry Point
SynAptIp Technologies

AI, Scientific Software & Instrument Intelligence

Run:
    cd src_v3_6
    python lcr_control_v3_6.py

Or from repo root:
    python src_v3_6/lcr_control_v3_6.py

V3.6 extends V3.5 with:
  - Professional file-based license system (.lic files)
  - "Comparar" tab for multi-CSV Nyquist overlay

All V3.5 and V3 functionality is preserved exactly as shipped.
"""
from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return _HERE.parent


def _bundle_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return _HERE


_BASE_DIR   = _base_dir()
_BUNDLE_DIR = _bundle_dir()

# Path resolution order: V3.6 first, then V3.5, then V3
_V3_6_DIR = (_BUNDLE_DIR / "src_v3_6") if getattr(sys, "frozen", False) else _HERE
_V3_5_DIR = (_BUNDLE_DIR / "src_v3_5") if getattr(sys, "frozen", False) else (_HERE.parent / "src_v3_5")
_V3_DIR   = (_BUNDLE_DIR / "src_v3")   if getattr(sys, "frozen", False) else (_HERE.parent / "src_v3")


def _startup_log_path() -> Path:
    return _BASE_DIR / "startup_v3_6.log"


def _log(message: str) -> None:
    try:
        _startup_log_path().parent.mkdir(parents=True, exist_ok=True)
        line = f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n"
        with _startup_log_path().open("a", encoding="utf-8") as fp:
            fp.write(line)
    except Exception:
        pass


def _exception_hook(exc_type, exc_value, exc_tb) -> None:
    _log("Unhandled exception")
    _log("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))


sys.excepthook = _exception_hook
_log(f"Startup begin | frozen={getattr(sys, 'frozen', False)}")
_log(f"Base dir:   {_BASE_DIR}")
_log(f"Bundle dir: {_BUNDLE_DIR}")

# Desired sys.path order: [V3.6, V3, V3.5, ...]
# Rationale:
#   - V3.6 first → wins for: licensing/, ui_v36/
#   - V3   second → wins for: services/, ui/   (src_v3/services shadows src_v3_5/services)
#   - V3.5 third  → wins for: analysis_engine/, ui_v35/  (unique namespaces, no conflict)
# Build this by inserting in REVERSE of desired order (each insert(0) goes to front)
_desired_paths = [str(_V3_6_DIR), str(_V3_DIR), str(_V3_5_DIR)]
for _ps in reversed(_desired_paths):
    if _ps not in sys.path:
        sys.path.insert(0, _ps)

_log(f"sys.path[0:4]: {sys.path[:4]}")

from PySide6.QtWidgets import QApplication

# V3.6 license system (new, independent)
try:
    from licensing.license_manager import LicenseManagerV36
    from ui_v36.license_dialog_v36 import LicenseDialogV36
except Exception:
    _log("Import failure for V3.6 license modules")
    _log(traceback.format_exc())
    raise

# V3.6 main window
try:
    from ui_v36.main_window_v3_6 import MainWindowV3_6
except Exception:
    _log("Import failure for V3.6 UI module")
    _log(traceback.format_exc())
    raise


APP_NAME    = "SynAptIp Nyquist Analyzer V3.6"
APP_VERSION = "3.6.0"
APP_ORG     = "SynAptIp"


def main() -> int:
    try:
        os.chdir(_BASE_DIR)
    except Exception:
        _log("Could not set working directory to base dir")

    _log("Initializing QApplication")
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORG)

    if os.environ.get("SYNAPTIP_LICENSE_DISABLED", "0") != "1":
        try:
            _log("Opening V3.6 license dialog")
            license_manager = LicenseManagerV36()
            license_dialog  = LicenseDialogV36(license_manager)
            if license_dialog.exec() != LicenseDialogV36.DialogCode.Accepted:
                _log("License dialog canceled or rejected")
                return 0
        except Exception:
            _log("License flow exception (fail-open for reliability)")
            _log(traceback.format_exc())

    try:
        _log("Creating V3.6 main window")
        window = MainWindowV3_6()
        window.show()
        _log("Main window shown")
        return app.exec()
    except Exception:
        _log("Fatal startup exception after QApplication init")
        _log(traceback.format_exc())
        raise


if __name__ == "__main__":
    raise SystemExit(main())
