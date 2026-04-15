"""CRUD tests for leads + RBAC gating + public endpoint."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models import UserRole


@pytest.mark.asyncio
async def test_admin_can_create_and_list_leads(client_factory) -> None:
    async with await client_factory(UserRole.ADMIN) as client:
        r = await client.post(
            "/api/v1/leads",
            json={"email": "new@test.dev", "first_name": "New", "source": "manual"},
        )
        assert r.status_code == 201, r.text
        lead_id = r.json()["id"]

        r = await client.get("/api/v1/leads")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert body["items"][0]["id"] == lead_id


@pytest.mark.asyncio
async def test_finance_cannot_write_leads(client_factory) -> None:
    async with await client_factory(UserRole.FINANCE) as client:
        r = await client.post(
            "/api/v1/leads",
            json={"email": "blocked@test.dev"},
        )
        assert r.status_code == 403
        assert "permission" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_marketing_cannot_read_leads(client_factory) -> None:
    async with await client_factory(UserRole.MARKETING) as client:
        r = await client.get("/api/v1/leads")
        assert r.status_code == 403


@pytest.mark.asyncio
async def test_public_lead_capture(client_factory) -> None:
    """Unauthenticated lead submission from the marketing site."""
    async with await client_factory(UserRole.ADMIN) as client:
        r = await client.post(
            "/api/v1/public/leads",
            json={
                "email": "visitor@acme.co",
                "first_name": "Visitor",
                "source": "hero-form",
            },
        )
        assert r.status_code == 201, r.text
        assert r.json()["email"] == "visitor@acme.co"


@pytest.mark.asyncio
async def test_lead_not_found_is_404(client_factory) -> None:
    async with await client_factory(UserRole.ADMIN) as client:
        r = await client.get("/api/v1/leads/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404
