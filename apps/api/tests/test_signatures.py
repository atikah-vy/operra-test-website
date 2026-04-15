"""Webhook signature verification — timing-safe, negative and positive cases."""

from __future__ import annotations

import hashlib
import hmac

from app.webhooks.signatures import (
    verify_attio,
    verify_calcom,
    verify_hmac_sha256,
    verify_meta,
)


def _sign(secret: str, payload: bytes) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def test_generic_hmac_valid() -> None:
    payload = b'{"event":"x"}'
    sig = _sign("secret", payload)
    assert verify_hmac_sha256("secret", payload, sig) is True


def test_generic_hmac_tampered() -> None:
    payload = b'{"event":"x"}'
    sig = _sign("secret", payload)
    assert verify_hmac_sha256("secret", payload + b"!", sig) is False


def test_missing_secret_rejects() -> None:
    assert verify_hmac_sha256("", b"x", "abc") is False


def test_attio_signature_positive_and_negative() -> None:
    payload = b'{"attio":"event"}'
    good = _sign("s3cret", payload)
    assert verify_attio("s3cret", payload, good) is True
    assert verify_attio("s3cret", payload, "deadbeef") is False


def test_calcom_signature_positive_and_negative() -> None:
    payload = b'{"triggerEvent":"BOOKING_CREATED"}'
    good = _sign("cal_secret", payload)
    assert verify_calcom("cal_secret", payload, good) is True
    assert verify_calcom("cal_secret", payload, None) is False


def test_meta_signature_requires_prefix() -> None:
    payload = b'{"object":"page"}'
    raw = _sign("meta_secret", payload)
    # Meta requires `sha256=` prefix
    assert verify_meta("meta_secret", payload, f"sha256={raw}") is True
    assert verify_meta("meta_secret", payload, raw) is False
    assert verify_meta("meta_secret", payload, "sha256=badbeef") is False
