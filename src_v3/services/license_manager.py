"""
license_manager.py
SynAptIp Technologies

Lightweight offline license manager:
- Trial window (prevents unlimited unlicensed usage)
- Device-bound activation key validation
- Robust fail-safe behavior (never crashes app)
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
from dataclasses import dataclass

from services.device_fingerprint import get_device_id
from services.license_storage import load_state, save_state


# Embedded signing secret for offline validation.
# Note: this is intentionally lightweight, not tamper-proof DRM.
_SIGNING_SECRET = "SynAptIp-V3-License-Offline-Validation-2026"
_TRIAL_DAYS = 14
_KEY_PREFIX = "SYNAPT-V3-"


@dataclass
class LicenseStatus:
    allowed: bool
    activated: bool
    trial: bool
    days_left: int
    reason: str
    device_id: str


class LicenseManager:
    """Optional/injectable licensing facade used by startup/UI."""

    def __init__(self) -> None:
        self._device_id = get_device_id()

    @property
    def device_id(self) -> str:
        return self._device_id

    def evaluate_status(self) -> LicenseStatus:
        """Evaluate current access state. Always returns a valid status."""
        try:
            state = load_state()

            key = str(state.get("activation_key", "")).strip()
            if key:
                valid, message = self._validate_key(key, self._device_id)
                if valid:
                    return LicenseStatus(
                        allowed=True,
                        activated=True,
                        trial=False,
                        days_left=9999,
                        reason="Activated",
                        device_id=self._device_id,
                    )

            now = dt.datetime.utcnow().date()
            first_run_raw = str(state.get("first_run_utc", "")).strip()
            if not first_run_raw:
                first_run = now
                state["first_run_utc"] = first_run.isoformat()
                save_state(state)
            else:
                first_run = _parse_date(first_run_raw) or now

            elapsed_days = max(0, (now - first_run).days)
            days_left = max(0, _TRIAL_DAYS - elapsed_days)
            allowed = days_left > 0
            reason = "Trial active" if allowed else "Trial expired"

            return LicenseStatus(
                allowed=allowed,
                activated=False,
                trial=True,
                days_left=days_left,
                reason=reason,
                device_id=self._device_id,
            )
        except Exception:
            # Fail-open for reliability: never crash or hard-block app.
            return LicenseStatus(
                allowed=True,
                activated=False,
                trial=True,
                days_left=1,
                reason="Licensing unavailable (safe mode)",
                device_id=self._device_id,
            )

    def activate(self, key: str) -> tuple[bool, str]:
        """Attempt activation with an offline key."""
        try:
            cleaned = (key or "").strip()
            valid, message = self._validate_key(cleaned, self._device_id)
            if not valid:
                return False, message

            state = load_state()
            state["activation_key"] = cleaned
            state["activated_at_utc"] = dt.datetime.utcnow().isoformat(timespec="seconds")
            if not save_state(state):
                return False, "Activation key valid, but storage failed"
            return True, "Activation successful"
        except Exception:
            return False, "Activation failed unexpectedly"

    def clear_activation(self) -> bool:
        try:
            state = load_state()
            state.pop("activation_key", None)
            state.pop("activated_at_utc", None)
            return save_state(state)
        except Exception:
            return False

    def _validate_key(self, key: str, device_id: str) -> tuple[bool, str]:
        if not key.startswith(_KEY_PREFIX):
            return False, "Invalid key format"

        body = key[len(_KEY_PREFIX) :]
        if "." not in body:
            return False, "Invalid key payload"

        payload_b64, signature = body.rsplit(".", 1)

        expected_sig = hmac.new(
            _SIGNING_SECRET.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()[:24]

        if not hmac.compare_digest(signature.lower(), expected_sig.lower()):
            return False, "Signature mismatch"

        payload = _decode_payload(payload_b64)
        if not payload:
            return False, "Corrupt payload"

        target_device = str(payload.get("device_id", "")).strip()
        expiry = str(payload.get("expires_utc", "")).strip()

        if target_device != device_id:
            return False, "This key is for a different device"

        exp_date = _parse_date(expiry)
        if exp_date is None:
            return False, "Invalid expiry"

        if dt.datetime.utcnow().date() > exp_date:
            return False, "License expired"

        return True, "Valid"


def _parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except Exception:
        return None


def _decode_payload(payload_b64: str) -> dict | None:
    try:
        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("utf-8"))
        data = json.loads(raw.decode("utf-8"))
        if isinstance(data, dict):
            return data
        return None
    except Exception:
        return None


def build_activation_key(device_id: str, expires_utc: str) -> str:
    """
    Helper for issuing keys (for internal/admin tooling).

    Returns key in format:
      SYNAPT-V3-<payload_b64>.<sig24>
    """
    payload = {
        "device_id": device_id,
        "expires_utc": expires_utc,
        "plan": "standard",
    }
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8").rstrip("=")
    sig = hmac.new(
        _SIGNING_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:24]
    return f"{_KEY_PREFIX}{payload_b64}.{sig}"
