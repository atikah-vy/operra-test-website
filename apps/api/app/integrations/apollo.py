"""Apollo.io adapter for lead enrichment."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.integrations.base import HttpClient, IntegrationResult


class ApolloAdapter:
    """Apollo.io people-match enrichment.

    Docs: https://apolloio.github.io/apollo-api-docs/
    """

    BASE_URL = "https://api.apollo.io/api/v1"

    def __init__(self) -> None:
        self._api_key = settings.apollo_api_key

    @property
    def configured(self) -> bool:
        return bool(self._api_key)

    def _http(self) -> HttpClient:
        return HttpClient(
            self.BASE_URL,
            headers={"Cache-Control": "no-cache", "Content-Type": "application/json"},
        )

    async def enrich_person(
        self,
        *,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        company: str | None = None,
    ) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured("APOLLO_API_KEY not set")

        payload: dict[str, Any] = {
            "api_key": self._api_key,
            "email": email,
        }
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if company:
            payload["organization_name"] = company

        return await self._http().request("POST", "/people/match", json=payload)
