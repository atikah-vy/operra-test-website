"""Attio CRM adapter (v2 API)."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.integrations.base import HttpClient, IntegrationResult


class AttioAdapter:
    """Thin client for Attio workspace records.

    Docs: https://docs.attio.com/rest-api
    """

    BASE_URL = "https://api.attio.com/v2"

    def __init__(self) -> None:
        self._api_key = settings.attio_api_key

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

    async def upsert_person(
        self, *, email: str, first_name: str | None = None, last_name: str | None = None
    ) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured("ATTIO_API_KEY not set")

        payload = {
            "data": {
                "values": {
                    "email_addresses": [{"email_address": email}],
                    "name": [
                        {
                            "first_name": first_name or "",
                            "last_name": last_name or "",
                            "full_name": " ".join(
                                filter(None, [first_name, last_name])
                            ) or email,
                        }
                    ],
                }
            }
        }
        return await self._http().request(
            "PUT",
            "/objects/people/records?matching_attribute=email_addresses",
            json=payload,
        )

    async def upsert_company(
        self, *, name: str, domain: str | None = None
    ) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured("ATTIO_API_KEY not set")

        values: dict[str, Any] = {"name": [{"value": name}]}
        if domain:
            values["domains"] = [{"domain": domain}]
        payload = {"data": {"values": values}}
        return await self._http().request(
            "PUT",
            "/objects/companies/records?matching_attribute=domains",
            json=payload,
        )

    async def get_record(self, object_slug: str, record_id: str) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured("ATTIO_API_KEY not set")
        return await self._http().request(
            "GET", f"/objects/{object_slug}/records/{record_id}"
        )
