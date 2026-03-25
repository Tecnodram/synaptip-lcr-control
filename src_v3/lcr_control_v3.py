"""
lcr_control_v3.py — SynAptIp LCR Control V3 Entry Point
SynAptIp Technologies

AI, Scientific Software & Instrument Intelligence

Run:
    cd src_v3
    python lcr_control_v3.py

Or from repo root:
    python src_v3/lcr_control_v3.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure src_v3 is on sys.path so that `from services.x` and `from ui.x` resolve correctly.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from PySide6.QtWidgets import QApplication

from services.license_manager import LicenseManager
from ui.license_dialog import LicenseDialog
from ui.main_window_v3 import MainWindowV3


APP_NAME = "SynAptIp LCR Control V3"
APP_VERSION = "3.0.0"
APP_ORG = "SynAptIp"


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORG)

    # Licensing is optional/injectable and must never crash startup.
    if os.environ.get("SYNAPTIP_LICENSE_DISABLED", "0") != "1":
        try:
            license_manager = LicenseManager()
            license_dialog = LicenseDialog(license_manager)
            if license_dialog.exec() != LicenseDialog.DialogCode.Accepted:
                return 0
        except Exception:
            # Fail-open in case licensing layer is unavailable.
            pass

    window = MainWindowV3()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
