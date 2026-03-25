from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.dc_bias_probe_window import DcBiasProbeWindow


def main() -> int:
    """Application entry point for SynAptIp DC Bias Probe."""
    app = QApplication(sys.argv)
    app.setApplicationName("SynAptIp DC Bias Probe")
    app.setOrganizationName("SynAptIp Technologies")

    window = DcBiasProbeWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
