"""
device_fingerprint.py
SynAptIp Technologies

Device fingerprint utility for offline license binding.
"""
from __future__ import annotations

import hashlib
import platform


def get_device_id() -> str:
    """
    Return a stable SHA-256 fingerprint based on host traits.

    Uses machine name, OS, and CPU info as requested.
    """
    raw = f"{platform.node()}|{platform.system()}|{platform.processor()}"
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()
