"""Cal.com adapter."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.integrations.base import HttpClient, IntegrationResult


class CalcomAdapter:
    """Cal.com API v2.

    Docs: https://cal.com/docs/api-reference/v2
    """

    BASE_URL = "https://api.cal.com/v2"

    def __init__(self) -> None:
        self._api_key = settings.calcom_api_key

    @property
    def configured(self) -> bool:
        return bool(self._api_key)

    def _http(self) -> HttpClient:
        return HttpClient(
            self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )

    async def list_bookings(
        self, *, limit: int = 50, cursor: str | None = None
    ) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured("CALCOM_API_KEY not set")
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._http().request("GET", "/bookings", params=params)

    async def get_booking(self, calcom_booking_id: str) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured("CALCOM_API_KEY not set")
        return await self._http().request("GET", f"/bookings/{calcom_booking_id}")

    async def cancel_booking(
        self, calcom_booking_id: str, *, reason: str | None = None
    ) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured("CALCOM_API_KEY not set")
        return await self._http().request(
            "POST",
            f"/bookings/{calcom_booking_id}/cancel",
            json={"cancellationReason": reason} if reason else None,
        )
