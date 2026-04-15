"""Metricool adapter for social post scheduling."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.config import settings
from app.integrations.base import HttpClient, IntegrationResult


class MetricoolAdapter:
    """Metricool API v1 adapter.

    Docs: https://app.metricool.com/api/docs
    """

    BASE_URL = "https://app.metricool.com/api/v1"

    def __init__(self) -> None:
        self._api_token = settings.metricool_api_token
        self._user_id = settings.metricool_user_id

    @property
    def configured(self) -> bool:
        return bool(self._api_token and self._user_id)

    def _http(self) -> HttpClient:
        return HttpClient(
            self.BASE_URL,
            headers={"X-Mc-Auth": self._api_token, "Content-Type": "application/json"},
        )

    async def schedule_post(
        self,
        *,
        platform: str,
        content: str,
        scheduled_at: datetime,
        media_urls: list[str] | None = None,
    ) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured(
                "METRICOOL_API_TOKEN or METRICOOL_USER_ID not set"
            )
        payload = {
            "text": content,
            "providers": [platform],
            "publicationDate": scheduled_at.isoformat(),
            "media": media_urls or [],
        }
        return await self._http().request(
            "POST", f"/scheduler/posts?userId={self._user_id}", json=payload
        )

    async def get_post_metrics(self, post_id: str) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured("METRICOOL not configured")
        return await self._http().request(
            "GET", f"/scheduler/posts/{post_id}?userId={self._user_id}"
        )
