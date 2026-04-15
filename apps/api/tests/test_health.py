"""Smoke tests for the app factory."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_healthz() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_openapi_served() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/openapi.json")
    assert r.status_code == 200
    body = r.json()
    # All resource routers should be present
    paths = set(body["paths"].keys())
    for expected in (
        "/api/v1/leads",
        "/api/v1/clients",
        "/api/v1/invoices",
        "/api/v1/bookings",
        "/api/v1/automations",
        "/api/v1/analytics/overview",
        "/api/v1/webhooks/meta",
    ):
        assert expected in paths, f"Missing route: {expected}"
