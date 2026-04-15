"""Webhook signature verifiers (timing-safe)."""

from __future__ import annotations

import hashlib
import hmac
from typing import Final

SIG_PREFIX_META: Final[str] = "sha256="


def verify_hmac_sha256(
    secret: str, payload: bytes, provided_signature: str, *, prefix: str = ""
) -> bool:
    """Generic constant-time HMAC-SHA256 verify.

    If `prefix` is provided (e.g. "sha256="), the supplied signature must start with it.
    """
    if not secret or not provided_signature:
        return False
    sig = provided_signature
    if prefix:
        if not sig.startswith(prefix):
            return False
        sig = sig[len(prefix) :]

    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)


def verify_attio(secret: str, payload: bytes, header: str | None) -> bool:
    if not header:
        return False
    return verify_hmac_sha256(secret, payload, header)


def verify_calcom(secret: str, payload: bytes, header: str | None) -> bool:
    """Cal.com sends hex HMAC-SHA256 in `x-cal-signature-256` (no prefix)."""
    if not header:
        return False
    return verify_hmac_sha256(secret, payload, header)


def verify_meta(secret: str, payload: bytes, header: str | None) -> bool:
    """Meta sends `x-hub-signature-256: sha256=<hex>`."""
    if not header:
        return False
    return verify_hmac_sha256(secret, payload, header, prefix=SIG_PREFIX_META)
