"""Enrich a Lead via Apollo, then persist the enrichment payload."""

from __future__ import annotations

import logging
import time
from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.core.db import SessionLocal
from app.integrations.apollo import ApolloAdapter
from app.models import Lead, SyncLog, SyncLogStatus

logger = logging.getLogger("operra.jobs.lead_enrichment")


async def lead_enrichment(_ctx: dict[str, Any], lead_id: str) -> dict[str, Any]:
    lead_uuid = UUID(lead_id)
    apollo = ApolloAdapter()
    started = time.perf_counter()

    async with SessionLocal() as session:
        lead = (
            await session.execute(select(Lead).where(Lead.id == lead_uuid))
        ).scalar_one_or_none()
        if lead is None:
            logger.warning("Lead %s not found — skip enrichment", lead_id)
            return {"skipped": True, "reason": "lead_missing"}

        result = await apollo.enrich_person(
            email=lead.email,
            first_name=lead.first_name,
            last_name=lead.last_name,
            company=lead.company,
        )

        duration_ms = int((time.perf_counter() - started) * 1000)

        if result.skipped:
            status = SyncLogStatus.SUCCESS
            message = result.error
        elif result.ok:
            lead.apollo_enrichment_data = result.data or {}
            status = SyncLogStatus.SUCCESS
            message = None
        else:
            status = SyncLogStatus.FAILURE
            message = result.error

        session.add(
            SyncLog(
                organization_id=lead.organization_id,
                integration="apollo",
                action="enrich_person",
                entity_type="lead",
                entity_id=str(lead.id),
                duration_ms=duration_ms,
                status=status,
                request_payload={"email": lead.email},
                response_payload=result.data if isinstance(result.data, dict) else None,
                error_message=message,
            )
        )
        await session.commit()

    return {
        "ok": result.ok,
        "skipped": result.skipped,
        "duration_ms": duration_ms,
    }
