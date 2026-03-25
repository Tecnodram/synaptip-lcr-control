"""
license_dialog.py
SynAptIp Technologies

Optional startup dialog for activation/trial handling.
Never crashes calling code; caller decides continue/exit behavior.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from services.license_manager import LicenseManager, LicenseStatus


class LicenseDialog(QDialog):
    def __init__(self, manager: LicenseManager, parent=None) -> None:
        super().__init__(parent)
        self._manager = manager
        self._status: LicenseStatus = self._manager.evaluate_status()

        self.setWindowTitle("SynAptIp LCR Control V3 - License")
        self.setMinimumWidth(620)
        self._build_ui()
        self._refresh_status_view()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        title = QLabel("SynAptIp Technologies")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")

        subtitle = QLabel("AI, Scientific Software & Instrument Intelligence")
        subtitle.setStyleSheet("color: #475569;")

        product = QLabel("SynAptIp LCR Control V3")
        product.setStyleSheet("font-size: 14px; font-weight: 600;")

        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)
        self._device_label = QLabel("")
        self._device_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("Paste activation key")

        btn_row = QHBoxLayout()
        self._activate_btn = QPushButton("Activate")
        self._continue_btn = QPushButton("Continue")
        self._exit_btn = QPushButton("Exit")
        btn_row.addWidget(self._activate_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self._continue_btn)
        btn_row.addWidget(self._exit_btn)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(product)
        root.addWidget(self._status_label)
        root.addWidget(self._device_label)
        root.addWidget(self._key_input)
        root.addLayout(btn_row)

        self._activate_btn.clicked.connect(self._on_activate)
        self._continue_btn.clicked.connect(self._on_continue)
        self._exit_btn.clicked.connect(self.reject)

    def _refresh_status_view(self) -> None:
        self._status = self._manager.evaluate_status()

        if self._status.activated:
            txt = "License active. Full access enabled."
            color = "#065f46"
        elif self._status.allowed:
            txt = f"Trial active. Days remaining: {self._status.days_left}"
            color = "#92400e"
        else:
            txt = "Trial expired. Activation key required."
            color = "#991b1b"

        self._status_label.setText(txt)
        self._status_label.setStyleSheet(f"font-weight: 600; color: {color};")
        self._device_label.setText(f"Device ID: {self._status.device_id}")

        self._continue_btn.setEnabled(self._status.allowed)

    def _on_activate(self) -> None:
        ok, message = self._manager.activate(self._key_input.text())
        if ok:
            QMessageBox.information(self, "Activation", message)
        else:
            QMessageBox.warning(self, "Activation", message)
        self._refresh_status_view()

    def _on_continue(self) -> None:
        status = self._manager.evaluate_status()
        if status.allowed:
            self.accept()
        else:
            QMessageBox.warning(self, "License", "Activation key is required to continue.")
