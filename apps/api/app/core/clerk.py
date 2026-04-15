"""Clerk JWT verification via JWKS.

Fetches and caches the JWKS; verifies RS256 JWTs issued by Clerk; extracts the
Clerk user id (`sub`), the active organization id (`org_id`), and the org role
(`org_role`).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
from jwt import PyJWKClient

from app.core.config import settings


@dataclass(frozen=True)
class ClerkClaims:
    clerk_user_id: str
    clerk_org_id: str | None
    clerk_org_role: str | None
    email: str | None
    raw: dict[str, Any]


class ClerkJWTVerifier:
    """Verifies Clerk-issued JWTs.

    A small class — not a singleton pattern, because JWKS rotates roughly every
    24 hours and `PyJWKClient` handles its own caching with a 5-minute TTL.
    """

    def __init__(self, jwks_url: str | None = None, issuer: str | None = None) -> None:
        self._jwks_url = jwks_url or settings.clerk_jwks_url
        self._issuer = issuer or settings.clerk_issuer
        self._jwk_client: PyJWKClient | None = None

    @property
    def jwk_client(self) -> PyJWKClient:
        if self._jwk_client is None:
            if not self._jwks_url:
                raise RuntimeError(
                    "CLERK_JWKS_URL is not configured — cannot verify JWTs."
                )
            self._jwk_client = PyJWKClient(self._jwks_url, cache_keys=True, lifespan=300)
        return self._jwk_client

    def verify(self, token: str) -> ClerkClaims:
        signing_key = self.jwk_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=["RS256"],
            issuer=self._issuer or None,
            options={
                "require": ["exp", "iat", "sub"],
                "verify_iss": bool(self._issuer),
                "verify_aud": False,
            },
        )
        # Clerk includes azp (authorized party) — we don't enforce here since
        # Clerk JWTs are not bound to a specific audience; the JWKS + issuer
        # check is the authoritative trust anchor.
        now = int(time.time())
        if claims.get("exp", 0) <= now:
            raise jwt.ExpiredSignatureError("Token expired")

        return ClerkClaims(
            clerk_user_id=claims["sub"],
            clerk_org_id=claims.get("org_id"),
            clerk_org_role=claims.get("org_role"),
            email=claims.get("email"),
            raw=claims,
        )


# Module-level verifier (constructed once, reused).
verifier = ClerkJWTVerifier()


async def fetch_clerk_user_email(clerk_user_id: str) -> str | None:
    """Fallback: fetch a user's primary email via Clerk's Backend API.

    Used by the webhook handler when an event doesn't include email addresses.
    """
    if not settings.clerk_secret_key:
        return None
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"https://api.clerk.com/v1/users/{clerk_user_id}",
            headers={"Authorization": f"Bearer {settings.clerk_secret_key}"},
        )
        if r.status_code != 200:
            return None
        data = r.json()
        primary_id = data.get("primary_email_address_id")
        for addr in data.get("email_addresses", []):
            if addr.get("id") == primary_id:
                return addr.get("email_address")
    return None
