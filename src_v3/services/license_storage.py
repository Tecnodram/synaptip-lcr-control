"""
license_storage.py
SynAptIp Technologies

Persistent storage for local license/trial state.
Designed to be robust and never throw to callers.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


_APP_DIR_NAME = "SynAptIp"
_STATE_FILE_NAME = "license.json"


def _state_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / _APP_DIR_NAME
    return Path.home() / ".synaptip_lcr_control_v3"


def state_file_path() -> Path:
    return _state_dir() / _STATE_FILE_NAME


def load_state() -> dict[str, Any]:
    """Load state from disk. Returns empty dict on any failure."""
    try:
        p = state_file_path()
        if not p.exists():
            return {}
        raw = p.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        return {}


def save_state(state: dict[str, Any]) -> bool:
    """Save state atomically. Returns False if save failed."""
    try:
        p = state_file_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=True), encoding="utf-8")
        tmp.replace(p)
        return True
    except Exception:
        return False
