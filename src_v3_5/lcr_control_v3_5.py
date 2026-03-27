"""
lcr_control_v3_5.py — SynAptIp Nyquist Analyzer V3.5 Entry Point
SynAptIp Technologies

AI, Scientific Software & Instrument Intelligence

Run:
    cd src_v3_5
    python lcr_control_v3_5.py

Or from repo root:
    python src_v3_5/lcr_control_v3_5.py

V3.5 extends V3 with the "Analysis & Insights" module.
All V3 functionality is preserved exactly as shipped.
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


_BASE_DIR = _base_dir()
_BUNDLE_DIR = _bundle_dir()
_V3_DIR = (_BUNDLE_DIR / "src_v3") if getattr(sys, "frozen", False) else (_HERE.parent / "src_v3")


def _startup_log_path() -> Path:
    return _BASE_DIR / "startup_v3_5.log"


def _log_startup(message: str) -> None:
    try:
        _startup_log_path().parent.mkdir(parents=True, exist_ok=True)
        line = f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n"
        with _startup_log_path().open("a", encoding="utf-8") as fp:
            fp.write(line)
    except Exception:
        pass


def _exception_hook(exc_type, exc_value, exc_tb) -> None:
    _log_startup("Unhandled exception")
    _log_startup("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))


sys.excepthook = _exception_hook
_log_startup(f"Startup begin | frozen={getattr(sys, 'frozen', False)}")
_log_startup(f"Base dir: {_BASE_DIR}")
_log_startup(f"Bundle dir: {_BUNDLE_DIR}")

for _p in (_HERE, _V3_DIR):
    _ps = str(_p)
    if _ps not in sys.path:
        sys.path.insert(0, _ps)

_log_startup(f"sys.path[0:4]: {sys.path[:4]}")

from PySide6.QtWidgets import QApplication

# License machinery re-used from V3 (same classes, no change)
try:
    from services.license_manager import LicenseManager
    from ui.license_dialog import LicenseDialog
except Exception:
    _log_startup("Import failure for V3 legacy modules")
    _log_startup(traceback.format_exc())
    raise

# V3.5 main window (subclasses V3 main window, lives in ui_v35/)
try:
    from ui_v35.main_window_v3_5 import MainWindowV3_5
except Exception:
    _log_startup("Import failure for V3.5 UI module")
    _log_startup(traceback.format_exc())
    raise


APP_NAME    = "SynAptIp Nyquist Analyzer V3.5"
APP_VERSION = "3.5.0"
APP_ORG     = "SynAptIp"


def main() -> int:
    try:
        # Keep runtime independent of external launch CWD.
        os.chdir(_BASE_DIR)
    except Exception:
        _log_startup("Could not set working directory to base dir")
        _log_startup(traceback.format_exc())

    _log_startup("Initializing QApplication")
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORG)

    if os.environ.get("SYNAPTIP_LICENSE_DISABLED", "0") != "1":
        try:
            _log_startup("Opening license dialog")
            license_manager = LicenseManager()
            license_dialog  = LicenseDialog(license_manager)
            if license_dialog.exec() != LicenseDialog.DialogCode.Accepted:
                _log_startup("License dialog canceled")
                return 0
        except Exception:
            _log_startup("License flow exception (fail-open)")
            _log_startup(traceback.format_exc())

    try:
        _log_startup("Creating main window")
        window = MainWindowV3_5()
        window.show()
        _log_startup("Main window shown")
        return app.exec()
    except Exception:
        _log_startup("Fatal startup exception after QApplication init")
        _log_startup(traceback.format_exc())
        raise


if __name__ == "__main__":
    raise SystemExit(main())
