from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window_v2 import MainWindowV2


APP_NAME = "SynAptIp LCR Control V2.3"
APP_VERSION = "2.3.0"


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("SynAptIp")

    window = MainWindowV2()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
