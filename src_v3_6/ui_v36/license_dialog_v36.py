"""
license_dialog_v36.py — V3.6 Professional License Dialog
SynAptIp Technologies

Elegant startup dialog for V3.6 file-based license system.

Shows:
  - Product name and version
  - License state (valid / expired / invalid / not loaded)
  - Expiration date and days remaining
  - Issued to / license type
  - Device fingerprint (selectable text)
  - Button to load .lic file
  - Continue / Exit buttons

Never crashes the calling code.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from licensing.license_manager import LicenseManagerV36, LicenseResult, LicenseState


# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
_COLOR_VALID    = "#065f46"   # dark green
_COLOR_EXPIRED  = "#991b1b"   # dark red
_COLOR_WARN     = "#92400e"   # amber
_COLOR_NEUTRAL  = "#374151"   # slate
_BG_CARD        = "#f8fafc"
_BG_FINGERPRINT = "#f1f5f9"
_BORDER_CARD    = "#e2e8f0"


class LicenseDialogV36(QDialog):
    """
    V3.6 startup license dialog.

    Accepted → app may start.
    Rejected → app should exit.
    """

    def __init__(self, manager: LicenseManagerV36, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._manager = manager
        self._result: LicenseResult = self._manager.evaluate()

        self.setWindowTitle("SynAptIp Nyquist Analyzer V3.6 — License")
        self.setMinimumWidth(660)
        self.setMinimumHeight(420)
        self._build_ui()
        self._refresh()

    # ------------------------------------------------------------------ #
    # UI construction                                                       #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(16)

        # --- Header ---
        root.addWidget(self._make_header())

        # --- Status card ---
        self._status_card = self._make_status_card()
        root.addWidget(self._status_card)

        # --- Details card ---
        self._details_card = self._make_details_card()
        root.addWidget(self._details_card)

        # --- Fingerprint card ---
        root.addWidget(self._make_fingerprint_card())

        root.addStretch(1)

        # --- Buttons ---
        root.addLayout(self._make_button_row())

        self.setStyleSheet(self._stylesheet())

    def _make_header(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        title = QLabel("SynAptIp Technologies")
        title.setObjectName("dlgTitle")

        subtitle = QLabel("AI, Scientific Software & Instrument Intelligence")
        subtitle.setObjectName("dlgSubtitle")

        product = QLabel("SynAptIp Nyquist Analyzer V3.6")
        product.setObjectName("dlgProduct")

        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addWidget(product)
        return w

    def _make_status_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("statusCard")
        card.setFrameShape(QFrame.Shape.StyledPanel)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 12)

        self._state_label = QLabel()
        self._state_label.setObjectName("stateLabel")
        self._state_label.setWordWrap(True)

        self._expiry_label = QLabel()
        self._expiry_label.setObjectName("expiryLabel")

        lay.addWidget(self._state_label)
        lay.addWidget(self._expiry_label)
        return card

    def _make_details_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("detailsCard")
        card.setFrameShape(QFrame.Shape.StyledPanel)
        grid_lay = QVBoxLayout(card)
        grid_lay.setContentsMargins(16, 10, 16, 10)
        grid_lay.setSpacing(4)

        self._issued_to_label   = QLabel()
        self._license_type_label = QLabel()
        self._issued_at_label   = QLabel()

        for lbl in (self._issued_to_label, self._license_type_label, self._issued_at_label):
            lbl.setObjectName("detailLabel")
            grid_lay.addWidget(lbl)

        return card

    def _make_fingerprint_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("fingerprintCard")
        card.setFrameShape(QFrame.Shape.StyledPanel)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 8, 16, 8)
        lay.setSpacing(2)

        hdr = QLabel("Device Fingerprint")
        hdr.setObjectName("fingerprintHdr")

        self._fingerprint_label = QLabel(self._manager.device_fingerprint)
        self._fingerprint_label.setObjectName("fingerprintValue")
        self._fingerprint_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._fingerprint_label.setWordWrap(True)

        lay.addWidget(hdr)
        lay.addWidget(self._fingerprint_label)
        return card

    def _make_button_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        self._load_btn    = QPushButton("Cargar licencia (.lic)")
        self._continue_btn = QPushButton("Continuar")
        self._exit_btn    = QPushButton("Salir")

        self._load_btn.setObjectName("loadBtn")
        self._continue_btn.setObjectName("continueBtn")
        self._exit_btn.setObjectName("exitBtn")

        self._load_btn.clicked.connect(self._on_load)
        self._continue_btn.clicked.connect(self._on_continue)
        self._exit_btn.clicked.connect(self.reject)

        row.addWidget(self._load_btn)
        row.addStretch(1)
        row.addWidget(self._continue_btn)
        row.addWidget(self._exit_btn)
        return row

    # ------------------------------------------------------------------ #
    # State refresh                                                         #
    # ------------------------------------------------------------------ #

    def _refresh(self) -> None:
        r = self._result
        state = r.state

        if state == LicenseState.VALID:
            state_txt   = f"Licencia activa — {r.message}"
            state_color = _COLOR_VALID
            expiry_txt  = f"Vence: {r.expires_at}   ({r.days_left} día(s) restante(s))"
            can_continue = True

        elif state == LicenseState.EXPIRED:
            state_txt   = f"Licencia vencida — {r.message}"
            state_color = _COLOR_EXPIRED
            expiry_txt  = f"Venció el: {r.expires_at}"
            can_continue = False

        elif state == LicenseState.WRONG_DEVICE:
            state_txt   = "Licencia no válida para este equipo."
            state_color = _COLOR_EXPIRED
            expiry_txt  = ""
            can_continue = False

        elif state == LicenseState.NOT_LOADED:
            state_txt   = "Sin licencia cargada. Cargue un archivo .lic para activar."
            state_color = _COLOR_WARN
            expiry_txt  = ""
            can_continue = False

        elif state == LicenseState.CORRUPT:
            state_txt   = f"Archivo de licencia corrupto: {r.message}"
            state_color = _COLOR_EXPIRED
            expiry_txt  = ""
            can_continue = False

        else:  # INVALID
            state_txt   = f"Licencia inválida: {r.message}"
            state_color = _COLOR_EXPIRED
            expiry_txt  = ""
            can_continue = False

        self._state_label.setText(state_txt)
        self._state_label.setStyleSheet(
            f"font-weight: 700; font-size: 11pt; color: {state_color};"
        )
        self._expiry_label.setText(expiry_txt)
        self._expiry_label.setVisible(bool(expiry_txt))

        self._issued_to_label.setText(
            f"Emitido a:   {r.issued_to}" if r.issued_to else "Emitido a:   —"
        )
        self._license_type_label.setText(
            f"Tipo:        {r.license_type}" if r.license_type else "Tipo:        —"
        )
        self._issued_at_label.setText(
            f"Emitido el:  {r.issued_at}" if r.issued_at else "Emitido el:  —"
        )

        self._continue_btn.setEnabled(can_continue)

    # ------------------------------------------------------------------ #
    # Button handlers                                                       #
    # ------------------------------------------------------------------ #

    def _on_load(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de licencia",
            "",
            "Archivos de licencia (*.lic);;Todos los archivos (*)",
        )
        if not path_str:
            return

        result = self._manager.load_from_file(Path(path_str))
        self._result = result

        if result.is_valid:
            QMessageBox.information(
                self,
                "Licencia cargada",
                f"Licencia válida.\n\nEmitida a: {result.issued_to}\n"
                f"Vence: {result.expires_at} ({result.days_left} día(s))",
            )
        else:
            QMessageBox.warning(
                self,
                "Licencia inválida",
                f"No se pudo cargar la licencia:\n\n{result.message}",
            )

        self._refresh()

    def _on_continue(self) -> None:
        r = self._manager.evaluate()
        self._result = r
        if r.is_valid:
            self.accept()
        else:
            self._refresh()
            QMessageBox.warning(
                self,
                "Licencia requerida",
                "Se requiere una licencia válida para continuar.",
            )

    # ------------------------------------------------------------------ #
    # Stylesheet                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _stylesheet() -> str:
        return f"""
        QDialog {{
            background-color: #ffffff;
            font-family: Segoe UI, Arial, sans-serif;
        }}
        QLabel#dlgTitle {{
            font-size: 18pt;
            font-weight: 700;
            color: #0f172a;
        }}
        QLabel#dlgSubtitle {{
            font-size: 9pt;
            color: #64748b;
        }}
        QLabel#dlgProduct {{
            font-size: 13pt;
            font-weight: 600;
            color: #1e40af;
            margin-top: 4px;
        }}
        QFrame#statusCard, QFrame#detailsCard {{
            background-color: {_BG_CARD};
            border: 1px solid {_BORDER_CARD};
            border-radius: 8px;
        }}
        QFrame#fingerprintCard {{
            background-color: {_BG_FINGERPRINT};
            border: 1px solid {_BORDER_CARD};
            border-radius: 8px;
        }}
        QLabel#fingerprintHdr {{
            font-size: 8pt;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
        }}
        QLabel#fingerprintValue {{
            font-family: Consolas, Courier New, monospace;
            font-size: 8.5pt;
            color: #334155;
        }}
        QLabel#detailLabel {{
            font-size: 9pt;
            color: #374151;
        }}
        QLabel#expiryLabel {{
            font-size: 9pt;
            color: #374151;
            margin-top: 4px;
        }}
        QPushButton {{
            border-radius: 6px;
            padding: 7px 18px;
            font-size: 9pt;
            font-weight: 600;
        }}
        QPushButton#loadBtn {{
            background-color: #1d4ed8;
            color: #ffffff;
            border: none;
        }}
        QPushButton#loadBtn:hover {{ background-color: #1e40af; }}
        QPushButton#continueBtn {{
            background-color: #059669;
            color: #ffffff;
            border: none;
        }}
        QPushButton#continueBtn:hover {{ background-color: #047857; }}
        QPushButton#continueBtn:disabled {{
            background-color: #94a3b8;
            color: #ffffff;
        }}
        QPushButton#exitBtn {{
            background-color: transparent;
            color: #64748b;
            border: 1px solid #cbd5e1;
        }}
        QPushButton#exitBtn:hover {{
            background-color: #f1f5f9;
        }}
        """
