from __future__ import annotations


_UNIT_TO_MULTIPLIER: dict[str, float] = {
    "Hz": 1.0,
    "kHz": 1_000.0,
    "MHz": 1_000_000.0,
}


def frequency_to_hz(value: float, unit: str) -> float:
    """Convert a frequency value from Hz/kHz/MHz into Hz."""
    if unit not in _UNIT_TO_MULTIPLIER:
        raise ValueError(f"Unsupported frequency unit: {unit}")
    return value * _UNIT_TO_MULTIPLIER[unit]


def hz_to_unit(value_hz: float, unit: str) -> float:
    """Convert a frequency value in Hz into a selected display unit."""
    if unit not in _UNIT_TO_MULTIPLIER:
        raise ValueError(f"Unsupported frequency unit: {unit}")
    return value_hz / _UNIT_TO_MULTIPLIER[unit]


def sanitize_step_hz(step_hz: float) -> float:
    """Avoid zero or negative step values that would stall sweep loops."""
    if step_hz <= 0:
        raise ValueError("Sweep step must be greater than zero")
    return step_hz
