"""Attio webhook handler — record.created, record.updated."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.webhooks.processor import ingest
from app.webhooks.signatures import verify_attio

logger = logging.getLogger("operra.webhooks.attio")
router = APIRouter(prefix="/webhooks/attio", tags=["webhooks"])


@router.post("")
async def attio_webhook(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    x_attio_signature: Annotated[str | None, Header(alias="x-attio-signature")] = None,
) -> dict[str, Any]:
    body = await request.body()
    if not settings.attio_webhook_secret:
        raise HTTPException(status_code=503, detail="ATTIO_WEBHOOK_SECRET not set")
    if not verify_attio(settings.attio_webhook_secret, body, x_attio_signature):
        raise HTTPException(status_code=401, detail="Invalid Attio signature")

    payload = await request.json()
    event_type = payload.get("event_type") or payload.get("type")
    external_id = (
        payload.get("id")
        or payload.get("event_id")
        or str(uuid.uuid4())
    )

    async def _noop(*_args: Any, **_kwargs: Any) -> None:
        logger.info("Attio event recorded: type=%s", event_type)

    await ingest(
        session,
        source="attio",
        external_id=external_id,
        event_type=event_type,
        payload=payload,
        handler=_noop,
    )
    return {"ok": True}
