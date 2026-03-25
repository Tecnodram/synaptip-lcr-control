from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


TERMINATOR_OPTIONS: list[tuple[str, str]] = [
    (r"\n", "\n"),
    (r"\r\n", "\r\n"),
    (r"\r", "\r"),
]

TERMINATOR_LABELS: dict[str, str] = dict(TERMINATOR_OPTIONS)

# Maps normalised mode strings to (primary_label, secondary_label).
# Extend this as additional measurement modes are confirmed through protocol discovery.
_MODE_LABEL_MAP: dict[str, tuple[str, str]] = {
    "z-\u03b8": ("Z (\u03a9)", "\u03b8 (\u00b0)"),
    "z-t":   ("Z (\u03a9)", "\u03b8 (\u00b0)"),
    "z-th":  ("Z (\u03a9)", "\u03b8 (\u00b0)"),
    "l-q":   ("L (H)",     "Q"),
    "c-d":   ("C (F)",     "D"),
    "r-q":   ("R (\u03a9)", "Q"),
}


@dataclass
class MeasurementResult:
    """
    Structured result of one TRIG \u2192 read measurement cycle.

    Confirmed mapping for EUCOL U2829C in Z-\u03b8 mode:
        primary_value   \u2192 impedance magnitude Z  (\u03a9)
        secondary_value \u2192 phase angle \u03b8           (\u00b0)
        status_flag     \u2192 instrument status code  (0 = normal)
    """

    timestamp: str
    raw_response: str
    primary_value: Optional[float]    # first comma-separated field
    secondary_value: Optional[float]  # second comma-separated field
    status_flag: str                   # third comma-separated field
    mode_assumption: str              # user-supplied mode label at measurement time


def parse_measurement_response(raw: str, mode_assumption: str = "") -> MeasurementResult:
    """
    Parse a comma-separated instrument response into a MeasurementResult.

    Confirmed U2829C TRIG response format:
        +2.18E+05, -6.78E+01, 0

    Python float() handles IEEE scientific notation natively;
    no regex is required for standard instrument responses.
    """
    parts = [p.strip() for p in raw.split(",")]

    primary: Optional[float] = None
    secondary: Optional[float] = None
    status: str = ""

    try:
        primary = float(parts[0]) if parts else None
    except (ValueError, IndexError):
        pass
    try:
        secondary = float(parts[1]) if len(parts) > 1 else None
    except (ValueError, IndexError):
        pass
    try:
        status = parts[2] if len(parts) > 2 else ""
    except IndexError:
        pass

    return MeasurementResult(
        timestamp=timestamp_hms(),
        raw_response=raw,
        primary_value=primary,
        secondary_value=secondary,
        status_flag=status,
        mode_assumption=mode_assumption,
    )


def get_mode_labels(mode_assumption: str) -> tuple[str, str]:
    """
    Return (primary_label, secondary_label) for a given mode assumption string.

    Falls back to generic labels when the mode string is not in the lookup table.
    The UI uses these to annotate result fields with instrument-specific quantity names.
    """
    # Normalise: lowercase, drop spaces and the "(manual assumption)" annotation
    key = (
        mode_assumption.lower()
        .replace(" ", "")
        .replace("(manualassumption)", "")
        .strip()
    )
    for pattern, labels in _MODE_LABEL_MAP.items():
        if pattern.replace(" ", "") in key:
            return labels
    return ("Primary value", "Secondary value")


def timestamp_hms() -> str:
    """Return local timestamp in HH:MM:SS format for user logs."""
    return datetime.now().strftime("%H:%M:%S")


def format_log_line(message: str) -> str:
    """Format a message with a compact wall-clock timestamp."""
    return f"[{timestamp_hms()}] {message}"


def normalize_terminator(label_or_value: str) -> str:
    """
    Convert a UI label or raw value into a serial line terminator sequence.

    Supported values:
    - "\\n"
    - "\\r\\n"
    - "\\r"
    """
    if label_or_value in TERMINATOR_LABELS:
        return TERMINATOR_LABELS[label_or_value]

    if label_or_value in TERMINATOR_LABELS.values():
        return label_or_value

    return "\n"
