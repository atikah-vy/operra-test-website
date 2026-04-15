"""Auth dependency tests — missing token, malformed token."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_missing_bearer_rejects() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/leads")
    assert r.status_code == 401
    assert r.json()["detail"] == "Missing bearer token"


@pytest.mark.asyncio
async def test_malformed_bearer_rejects() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get(
            "/api/v1/leads", headers={"Authorization": "NotBearer xxx"}
        )
    assert r.status_code == 401
