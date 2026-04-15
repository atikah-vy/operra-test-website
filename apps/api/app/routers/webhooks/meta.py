"""Meta webhook handler — GET for verification challenge, POST for events."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.webhooks.processor import ingest
from app.webhooks.signatures import verify_meta

logger = logging.getLogger("operra.webhooks.meta")
router = APIRouter(prefix="/webhooks/meta", tags=["webhooks"])


@router.get("")
async def meta_verify(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
) -> PlainTextResponse:
    """Meta subscription verification handshake."""
    if not settings.meta_verify_token:
        raise HTTPException(status_code=503, detail="META_VERIFY_TOKEN not set")
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_verify_token:
        return PlainTextResponse(content=hub_challenge or "")
    raise HTTPException(status_code=403, detail="Verify token mismatch")


@router.post("")
async def meta_webhook(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    x_hub_signature_256: Annotated[
        str | None, Header(alias="x-hub-signature-256")
    ] = None,
) -> dict[str, Any]:
    body = await request.body()
    if not settings.meta_app_secret:
        raise HTTPException(status_code=503, detail="META_APP_SECRET not set")
    if not verify_meta(settings.meta_app_secret, body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid Meta signature")

    payload = await request.json()
    entries = payload.get("entry") or []
    event_type = payload.get("object") or "meta"

    # Meta payloads can be batched; use first entry's id + time as external id
    if entries:
        first = entries[0]
        external_id = f"{first.get('id', 'unknown')}:{first.get('time', '')}"
    else:
        external_id = str(uuid.uuid4())

    async def _noop(*_args: Any, **_kwargs: Any) -> None:
        logger.info("Meta webhook recorded: object=%s entries=%d", event_type, len(entries))

    await ingest(
        session,
        source="meta",
        external_id=external_id,
        event_type=event_type,
        payload=payload,
        handler=_noop,
    )
    return {"ok": True}
