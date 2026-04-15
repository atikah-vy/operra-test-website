"""Integration base: shared HttpClient + IntegrationResult envelope."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger("operra.integrations")

T = TypeVar("T")

DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3


class NotConfiguredError(RuntimeError):
    """Raised when an adapter is invoked without the required credentials."""


@dataclass
class IntegrationResult(Generic[T]):
    """Uniform envelope for integration adapter returns.

    `ok`      — did the call succeed (or was it cleanly skipped because not configured)?
    `data`    — payload when available
    `status`  — HTTP status (if any)
    `error`   — error string if the call failed
    `skipped` — True when the adapter is not configured; downstream treats this
                as a no-op rather than a failure.
    """

    ok: bool
    data: T | None = None
    status: int | None = None
    error: str | None = None
    skipped: bool = False
    rate_limit: dict[str, str] = field(default_factory=dict)

    @classmethod
    def not_configured(cls, message: str = "not configured") -> "IntegrationResult[T]":
        return cls(ok=True, skipped=True, error=message)

    @classmethod
    def success(
        cls, data: T, status: int = 200, rate_limit: dict[str, str] | None = None
    ) -> "IntegrationResult[T]":
        return cls(ok=True, data=data, status=status, rate_limit=rate_limit or {})

    @classmethod
    def failure(cls, error: str, status: int | None = None) -> "IntegrationResult[T]":
        return cls(ok=False, error=error, status=status)


class HttpClient:
    """Thin wrapper around httpx.AsyncClient with retries and rate-limit parsing.

    One client per adapter instance; callers should `async with adapter.http:` or rely on
    the adapter's context manager. For ergonomic one-shot calls, use the `request()`
    helper which opens a short-lived client.
    """

    def __init__(
        self,
        base_url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | list[Any] | None = None,
        params: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> IntegrationResult[Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {**self.headers, **(extra_headers or {})}

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(self.max_retries),
                wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
                retry=retry_if_exception_type((httpx.HTTPError,)),
                reraise=True,
            ):
                with attempt:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.request(
                            method, url, json=json, params=params, headers=headers
                        )
                        rate_limit = _extract_rate_limit(response.headers)
                        if response.status_code >= 500:
                            response.raise_for_status()
                        if response.status_code >= 400:
                            return IntegrationResult.failure(
                                error=response.text, status=response.status_code
                            )
                        data = _safe_json(response)
                        return IntegrationResult.success(
                            data=data,
                            status=response.status_code,
                            rate_limit=rate_limit,
                        )
        except httpx.HTTPError as exc:
            logger.warning("HTTP error calling %s %s: %s", method, url, exc)
            return IntegrationResult.failure(error=str(exc))

        # Unreachable — AsyncRetrying either returns inside the loop or raises.
        return IntegrationResult.failure(error="request exhausted retries")


def _safe_json(response: httpx.Response) -> Any:
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


def _extract_rate_limit(headers: httpx.Headers) -> dict[str, str]:
    keys = (
        "x-ratelimit-limit",
        "x-ratelimit-remaining",
        "x-ratelimit-reset",
        "retry-after",
    )
    return {k: headers[k] for k in keys if k in headers}
