"""Bukku (Malaysian accounting) adapter for invoice sync."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.core.config import settings
from app.integrations.base import HttpClient, IntegrationResult


class BukkuAdapter:
    """Bukku API adapter for invoicing.

    Docs: https://help.bukku.my/developer-api
    """

    BASE_URL = "https://api.bukku.my/v1"

    def __init__(self) -> None:
        self._api_key = settings.bukku_api_key
        self._company_id = settings.bukku_company_id

    @property
    def configured(self) -> bool:
        return bool(self._api_key and self._company_id)

    def _http(self) -> HttpClient:
        return HttpClient(
            self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "X-Company-Id": self._company_id,
                "Content-Type": "application/json",
            },
        )

    async def create_invoice(
        self,
        *,
        invoice_number: str,
        client_name: str,
        amount: Decimal,
        currency: str = "MYR",
        line_items: list[dict[str, Any]] | None = None,
        due_date: str | None = None,
    ) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured(
                "BUKKU_API_KEY or BUKKU_COMPANY_ID not set"
            )
        payload = {
            "number": invoice_number,
            "contact": {"name": client_name},
            "currency_code": currency,
            "total_amount": str(amount),
            "items": line_items or [],
            "due_date": due_date,
        }
        return await self._http().request("POST", "/invoices", json=payload)

    async def get_invoice(self, bukku_invoice_id: str) -> IntegrationResult[dict[str, Any]]:
        if not self.configured:
            return IntegrationResult.not_configured("BUKKU not configured")
        return await self._http().request("GET", f"/invoices/{bukku_invoice_id}")
