"""Idempotent webhook ingestion engine.

Flow:
    1. Verify signature (caller does this before invoking `ingest`).
    2. Check (source, external_id) — UNIQUE constraint + SELECT dedup handles replays.
    3. Dispatch handler → on success mark status=processed; on failure, mark failed + raise.
    4. Write a sync_logs audit row.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Awaitable, Callable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SyncLog, SyncLogStatus, WebhookEvent, WebhookEventStatus

logger = logging.getLogger("operra.webhooks")

Handler = Callable[[AsyncSession, "WebhookEvent"], Awaitable[None]]


async def ingest(
    session: AsyncSession,
    *,
    source: str,
    external_id: str,
    event_type: str | None,
    payload: dict[str, Any],
    handler: Handler,
    organization_id: Any | None = None,
) -> WebhookEvent:
    """Persist a webhook and run its handler idempotently.

    Dedup strategy: SELECT first for the common case, fall back to relying on
    the UNIQUE(source, external_id) constraint for race conditions. Works on
    both Postgres and SQLite (used in tests).
    """
    existing = await _find_existing(session, source, external_id)
    if existing is not None:
        logger.info(
            "webhook dedup: source=%s external_id=%s status=%s",
            source,
            external_id,
            existing.status,
        )
        return existing

    event = WebhookEvent(
        id=uuid.uuid4(),
        organization_id=organization_id,
        source=source,
        external_id=external_id,
        event_type=event_type,
        payload=payload,
        status=WebhookEventStatus.PENDING,
        attempts=0,
    )
    session.add(event)
    try:
        await session.commit()
    except IntegrityError:
        # Race — another request inserted first; treat as idempotent success.
        await session.rollback()
        winner = await _find_existing(session, source, external_id)
        if winner is not None:
            return winner
        raise

    await session.refresh(event)

    started = time.perf_counter()
    try:
        event.status = WebhookEventStatus.PROCESSING
        event.attempts = (event.attempts or 0) + 1
        await session.commit()

        await handler(session, event)

        event.status = WebhookEventStatus.PROCESSED
        event.last_error = None
        await session.commit()
        _log_sync(
            session,
            source,
            event_type or "webhook",
            SyncLogStatus.SUCCESS,
            duration_ms=int((time.perf_counter() - started) * 1000),
            request_payload=payload,
            organization_id=organization_id,
        )
        await session.commit()
        return event
    except Exception as exc:  # noqa: BLE001
        logger.exception("webhook handler failed for %s/%s", source, external_id)
        event.status = WebhookEventStatus.FAILED
        event.last_error = str(exc)[:2000]
        await session.commit()
        _log_sync(
            session,
            source,
            event_type or "webhook",
            SyncLogStatus.FAILURE,
            duration_ms=int((time.perf_counter() - started) * 1000),
            request_payload=payload,
            error_message=str(exc),
            organization_id=organization_id,
        )
        await session.commit()
        raise


async def _find_existing(
    session: AsyncSession, source: str, external_id: str
) -> WebhookEvent | None:
    return (
        await session.execute(
            select(WebhookEvent).where(
                WebhookEvent.source == source,
                WebhookEvent.external_id == external_id,
            )
        )
    ).scalar_one_or_none()


def _log_sync(
    session: AsyncSession,
    integration: str,
    action: str,
    status: SyncLogStatus,
    *,
    duration_ms: int | None = None,
    request_payload: dict[str, Any] | None = None,
    response_payload: dict[str, Any] | None = None,
    error_message: str | None = None,
    organization_id: Any | None = None,
) -> None:
    log = SyncLog(
        organization_id=organization_id,
        integration=integration,
        action=action,
        status=status,
        duration_ms=duration_ms,
        request_payload=request_payload,
        response_payload=response_payload,
        error_message=error_message,
    )
    session.add(log)
