"""
schema_detector.py — Column Detection & Normalization
SynAptIp Nyquist Analyzer V3.5
SynAptIp Technologies

Safely maps raw CSV column names to canonical internal names.
Supports all known export formats from V2, V2.3, and V3.

Canonical columns (all lowercase with underscores):
    freq_hz        — measurement frequency in Hz
    z_ohm          — impedance magnitude |Z| in Ohm
    theta_deg      — impedance phase angle in degrees
    z_real         — real part of impedance (Z') in Ohm
    z_imag         — imaginary part of impedance (Z'') in Ohm
    minus_z_imag   — negative imaginary part (−Z'') in Ohm
    dc_bias        — DC bias voltage in V (optional)
    status         — measurement status / validity flag (optional)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Alias maps: canonical_name -> list[possible column name variants]
# ---------------------------------------------------------------------------
_ALIASES: dict[str, list[str]] = {
    "freq_hz": [
        "freq_hz", "freq", "frequency", "frequency_hz", "f_hz", "f",
        "freqhz", "freq(hz)", "frequency(hz)",
    ],
    "z_ohm": [
        "z_ohm", "z", "zmag", "z_mag", "|z|", "z_magnitude",
        "impedance", "z_ohm_mag", "magnitude", "mag_ohm",
    ],
    "theta_deg": [
        "theta_deg", "theta", "phase", "phase_deg", "angle_deg",
        "phi_deg", "phi", "angle", "phase_angle", "theta(deg)",
    ],
    "z_real": [
        "z_real", "zreal", "z_re", "z_prime", "real_z", "re_z",
        "z'", "z_real_ohm", "primary",
    ],
    "z_imag": [
        "z_imag", "zimag", "z_im", "z_double_prime", "imag_z", "im_z",
        "z''", "z_imag_ohm", "secondary",
    ],
    "minus_z_imag": [
        "minus_z_imag", "-z_imag", "-zimag", "neg_z_imag", "minus_zimag",
        "-z''", "mzimag", "neg_imag",
    ],
    "dc_bias": [
        "dc_bias", "bias", "bias_v", "dc_bias_v", "vbias", "v_bias",
        "dcbias", "dc_bias_volt", "bias_volt", "dc_v", "dc",
    ],
    "status": [
        "status", "valid", "flag", "quality", "meas_status", "measurement_status",
        "stat", "validity",
    ],
}


@dataclass
class DetectedSchema:
    """Result of schema detection on a DataFrame."""

    # Resolved column name mappings (canonical -> actual df column)
    column_map: dict[str, str] = field(default_factory=dict)

    # What coordinate mode was used to resolve impedance
    # "z_theta"    -> z_ohm + theta_deg present
    # "real_imag"  -> z_real + z_imag present
    # "minus_imag" -> z_real + minus_z_imag present (converted)
    # "incomplete" -> insufficient data
    impedance_mode: str = "incomplete"

    has_dc_bias: bool = False
    has_status: bool = False
    has_freq: bool = False

    warnings: list[str] = field(default_factory=list)

    def canonical(self, name: str) -> Optional[str]:
        """Return the actual DataFrame column for a canonical name, or None."""
        return self.column_map.get(name)

    def has(self, name: str) -> bool:
        return name in self.column_map


def detect_schema(df: pd.DataFrame) -> DetectedSchema:
    """
    Analyse the columns of *df* and return a DetectedSchema.

    This never raises — on any error it returns an 'incomplete' schema
    with a warning message attached.
    """
    schema = DetectedSchema()

    try:
        # Normalise actual column names for comparison
        norm_map: dict[str, str] = {
            _normalise(c): c for c in df.columns
        }

        for canonical, aliases in _ALIASES.items():
            for alias in aliases:
                key = _normalise(alias)
                if key in norm_map:
                    schema.column_map[canonical] = norm_map[key]
                    break

        # Determine frequency availability
        schema.has_freq = schema.has("freq_hz")
        if not schema.has_freq:
            schema.warnings.append("No frequency column detected.")

        # Determine impedance coordinate mode
        if schema.has("z_real") and schema.has("z_imag"):
            schema.impedance_mode = "real_imag"
        elif schema.has("z_real") and schema.has("minus_z_imag"):
            schema.impedance_mode = "minus_imag"
        elif schema.has("z_ohm") and schema.has("theta_deg"):
            schema.impedance_mode = "z_theta"
        else:
            schema.impedance_mode = "incomplete"
            schema.warnings.append(
                "Insufficient impedance columns. "
                "Need (z_real + z_imag) or (z_ohm + theta_deg)."
            )

        schema.has_dc_bias = schema.has("dc_bias")
        schema.has_status = schema.has("status")

    except Exception as exc:  # pragma: no cover
        schema.impedance_mode = "incomplete"
        schema.warnings.append(f"Schema detection error: {exc}")

    return schema


def _normalise(name: str) -> str:
    """Lower-case, strip whitespace and common punctuation."""
    return (
        name.lower()
        .strip()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "_")
        .replace("\\", "_")
    )
