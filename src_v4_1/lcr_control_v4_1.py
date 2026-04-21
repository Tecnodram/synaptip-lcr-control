"""
lcr_control_v4_1.py - SynAptIp Nyquist Analyzer V4.1 Entry Point
SynAptIp Technologies
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

_V4_1_DIR = (_BUNDLE_DIR / "src_v4_1") if getattr(sys, "frozen", False) else _HERE
_V4_DIR = (_BUNDLE_DIR / "src_v4") if getattr(sys, "frozen", False) else (_HERE.parent / "src_v4")
_V3_6_DIR = (_BUNDLE_DIR / "src_v3_6") if getattr(sys, "frozen", False) else (_HERE.parent / "src_v3_6")
_V3_5_DIR = (_BUNDLE_DIR / "src_v3_5") if getattr(sys, "frozen", False) else (_HERE.parent / "src_v3_5")
_V3_DIR = (_BUNDLE_DIR / "src_v3") if getattr(sys, "frozen", False) else (_HERE.parent / "src_v3")


def _startup_log_path() -> Path:
    return _BASE_DIR / "startup_v4_1.log"


def _log(message: str) -> None:
    try:
        _startup_log_path().parent.mkdir(parents=True, exist_ok=True)
        with _startup_log_path().open("a", encoding="utf-8") as fp:
            fp.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")
    except Exception:
        pass


def _exception_hook(exc_type, exc_value, exc_tb) -> None:
    _log("Unhandled exception")
    _log("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))


sys.excepthook = _exception_hook
sys.path[0:0] = [str(_V4_1_DIR), str(_V4_DIR), str(_V3_6_DIR), str(_V3_DIR), str(_V3_5_DIR)]

from PySide6.QtWidgets import QApplication

from licensing.license_manager import LicenseManagerV36
from ui_v36.license_dialog_v36 import LicenseDialogV36
from ui_v41.main_window_v4_1 import MainWindowV4_1


APP_NAME = "SynAptIp Nyquist Analyzer V4.1"
APP_VERSION = "4.1.0"
APP_ORG = "SynAptIp"


def main() -> int:
    try:
        os.chdir(_BASE_DIR)
    except Exception:
        _log("Could not set working directory to base dir")

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORG)

    if os.environ.get("SYNAPTIP_LICENSE_DISABLED", "0") != "1":
        try:
            license_manager = LicenseManagerV36()
            license_dialog = LicenseDialogV36(license_manager)
            if license_dialog.exec() != LicenseDialogV36.DialogCode.Accepted:
                return 0
        except Exception:
            _log("License flow exception (fail-open for reliability)")
            _log(traceback.format_exc())

    window = MainWindowV4_1()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

