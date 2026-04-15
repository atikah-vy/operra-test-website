"""Verify that webhook ingestion is idempotent on (source, external_id)."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WebhookEvent, WebhookEventStatus
from app.webhooks.processor import ingest


@pytest.mark.asyncio
async def test_replay_dedup(session: AsyncSession) -> None:
    calls = []

    async def handler(sess: AsyncSession, event: WebhookEvent) -> None:
        calls.append(event.id)

    payload = {"evt": "a"}

    e1 = await ingest(
        session,
        source="calcom",
        external_id="evt_1",
        event_type="BOOKING_CREATED",
        payload=payload,
        handler=handler,
    )
    assert e1.status == WebhookEventStatus.PROCESSED
    assert len(calls) == 1

    e2 = await ingest(
        session,
        source="calcom",
        external_id="evt_1",
        event_type="BOOKING_CREATED",
        payload=payload,
        handler=handler,
    )
    # Handler must NOT run again — dedup short-circuits
    assert len(calls) == 1
    assert e2.id == e1.id

    # Exactly one row persisted
    count = (
        await session.execute(select(func.count(WebhookEvent.id)))
    ).scalar_one()
    assert count == 1


@pytest.mark.asyncio
async def test_handler_failure_marks_failed(session: AsyncSession) -> None:
    async def bad_handler(_sess: AsyncSession, _event: WebhookEvent) -> None:
        raise RuntimeError("downstream exploded")

    with pytest.raises(RuntimeError):
        await ingest(
            session,
            source="attio",
            external_id="evt_bad",
            event_type="record.created",
            payload={"x": 1},
            handler=bad_handler,
        )

    row = (
        await session.execute(
            select(WebhookEvent).where(WebhookEvent.external_id == "evt_bad")
        )
    ).scalar_one()
    assert row.status == WebhookEventStatus.FAILED
    assert row.last_error and "downstream exploded" in row.last_error
