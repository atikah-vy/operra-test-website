"""Push leads / clients to Attio and persist the returned record id."""

from __future__ import annotations

import logging
import time
from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.core.db import SessionLocal
from app.integrations.attio import AttioAdapter
from app.models import Client, Lead, SyncLog, SyncLogStatus

logger = logging.getLogger("operra.jobs.attio_sync")


async def attio_sync_lead(_ctx: dict[str, Any], lead_id: str) -> dict[str, Any]:
    return await _sync("lead", UUID(lead_id))


async def attio_sync_client(_ctx: dict[str, Any], client_id: str) -> dict[str, Any]:
    return await _sync("client", UUID(client_id))


async def _sync(entity_type: str, entity_id: UUID) -> dict[str, Any]:
    attio = AttioAdapter()
    started = time.perf_counter()

    async with SessionLocal() as session:
        if entity_type == "lead":
            row = (
                await session.execute(select(Lead).where(Lead.id == entity_id))
            ).scalar_one_or_none()
        else:
            row = (
                await session.execute(select(Client).where(Client.id == entity_id))
            ).scalar_one_or_none()

        if row is None:
            logger.warning("%s %s not found — skip attio sync", entity_type, entity_id)
            return {"skipped": True, "reason": "entity_missing"}

        email = getattr(row, "email", None) or getattr(row, "contact_email", None)
        first = getattr(row, "first_name", None)
        last = getattr(row, "last_name", None) or getattr(row, "name", None)

        if not email:
            return {"skipped": True, "reason": "no_email"}

        result = await attio.upsert_person(email=email, first_name=first, last_name=last)
        duration_ms = int((time.perf_counter() - started) * 1000)

        if result.skipped:
            status = SyncLogStatus.SUCCESS
            error = result.error
        elif result.ok:
            record_id = None
            if isinstance(result.data, dict):
                record_id = (result.data.get("data") or {}).get("id", {}).get("record_id")
            if record_id:
                row.attio_record_id = record_id
            status = SyncLogStatus.SUCCESS
            error = None
        else:
            status = SyncLogStatus.FAILURE
            error = result.error

        session.add(
            SyncLog(
                organization_id=row.organization_id,
                integration="attio",
                action="upsert_person",
                entity_type=entity_type,
                entity_id=str(entity_id),
                duration_ms=duration_ms,
                status=status,
                request_payload={"email": email},
                response_payload=result.data if isinstance(result.data, dict) else None,
                error_message=error,
            )
        )
        await session.commit()

    return {
        "ok": result.ok,
        "skipped": result.skipped,
        "duration_ms": duration_ms,
    }
