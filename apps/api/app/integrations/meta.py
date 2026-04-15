"""Meta (Facebook/Instagram) Graph API adapter."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.integrations.base import HttpClient, IntegrationResult


class MetaAdapter:
    """Meta Graph API v19 adapter.

    Docs: https://developers.facebook.com/docs/graph-api
    """

    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self) -> None:
        self._page_token = settings.meta_page_access_token
        self._ig_business_id = settings.meta_ig_business_id

    @property
    def configured(self) -> bool:
        return bool(self._page_token)

    def _http(self) -> HttpClient:
        return HttpClient(
            self.BASE_URL, headers={"Content-Type": "application/json"}
        )

    async def create_ig_post(
        self, *, image_url: str, caption: str
    ) -> IntegrationResult[dict[str, Any]]:
        if not self.configured or not self._ig_business_id:
            return IntegrationResult.not_configured(
                "META_PAGE_ACCESS_TOKEN or META_IG_BUSINESS_ID not set"
            )
        # Two-step: create container, then publish.
        container = await self._http().request(
            "POST",
            f"/{self._ig_business_id}/media",
            params={
                "image_url": image_url,
                "caption": caption,
                "access_token": self._page_token,
            },
        )
        if not container.ok or not container.data or "id" not in container.data:
            return container

        creation_id = container.data["id"]
        return await self._http().request(
            "POST",
            f"/{self._ig_business_id}/media_publish",
            params={"creation_id": creation_id, "access_token": self._page_token},
        )

    async def get_page_insights(
        self, page_id: str, *, metric: str = "page_impressions"
    ) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured("META not configured")
        return await self._http().request(
            "GET",
            f"/{page_id}/insights",
            params={"metric": metric, "access_token": self._page_token},
        )
