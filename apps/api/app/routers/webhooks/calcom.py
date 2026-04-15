"""Cal.com webhook handler — syncs bookings into local DB."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.models import Booking, BookingStatus, Organization
from app.webhooks.processor import ingest
from app.webhooks.signatures import verify_calcom

logger = logging.getLogger("operra.webhooks.calcom")
router = APIRouter(prefix="/webhooks/calcom", tags=["webhooks"])


@router.post("")
async def calcom_webhook(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    x_cal_signature: Annotated[str | None, Header(alias="x-cal-signature-256")] = None,
) -> dict[str, Any]:
    body = await request.body()
    if not settings.calcom_webhook_secret:
        raise HTTPException(status_code=503, detail="CALCOM_WEBHOOK_SECRET not set")
    if not verify_calcom(settings.calcom_webhook_secret, body, x_cal_signature):
        raise HTTPException(status_code=401, detail="Invalid Cal.com signature")

    payload = await request.json()
    trigger = payload.get("triggerEvent") or payload.get("type")
    data = payload.get("payload") or {}
    calcom_booking_id = str(data.get("bookingId") or data.get("uid") or uuid.uuid4())

    async def _handle(sess: AsyncSession, _event: Any) -> None:
        await _upsert_booking(sess, trigger, data)

    await ingest(
        session,
        source="calcom",
        external_id=calcom_booking_id,
        event_type=trigger,
        payload=payload,
        handler=_handle,
    )
    return {"ok": True}


async def _upsert_booking(
    session: AsyncSession, trigger: str | None, data: dict[str, Any]
) -> None:
    calcom_booking_id = str(data.get("bookingId") or data.get("uid") or "")
    if not calcom_booking_id:
        logger.warning("Cal.com payload missing booking id — skip")
        return

    # Resolve org via metadata (customer must set it on the event type) or default public org
    org_slug = (data.get("metadata") or {}).get("org_slug") or settings.public_lead_org_slug
    org = (
        await session.execute(
            select(Organization).where(Organization.slug == org_slug)
        )
    ).scalar_one_or_none()
    if org is None:
        logger.warning("No org %s for cal.com booking — skipping", org_slug)
        return

    existing = (
        await session.execute(
            select(Booking).where(Booking.calcom_booking_id == calcom_booking_id)
        )
    ).scalar_one_or_none()

    status = _map_status(trigger)
    start = _parse_dt(data.get("startTime"))
    end = _parse_dt(data.get("endTime"))
    title = data.get("title") or "Meeting"
    attendees = data.get("attendees") or []
    attendee_email = (attendees[0] or {}).get("email") if attendees else None

    if existing:
        if start:
            existing.start_time = start
        if end:
            existing.end_time = end
        existing.status = status
        existing.title = title
        existing.attendee_email = attendee_email
        return

    if not (start and end):
        logger.warning("Cal.com booking %s missing times — skip insert", calcom_booking_id)
        return

    booking = Booking(
        id=uuid.uuid4(),
        organization_id=org.id,
        title=title,
        attendee_email=attendee_email,
        start_time=start,
        end_time=end,
        status=status,
        calcom_booking_id=calcom_booking_id,
    )
    session.add(booking)


def _map_status(trigger: str | None) -> BookingStatus:
    mapping = {
        "BOOKING_CREATED": BookingStatus.CONFIRMED,
        "BOOKING_CONFIRMED": BookingStatus.CONFIRMED,
        "BOOKING_RESCHEDULED": BookingStatus.RESCHEDULED,
        "BOOKING_CANCELLED": BookingStatus.CANCELLED,
        "MEETING_ENDED": BookingStatus.COMPLETED,
    }
    return mapping.get((trigger or "").upper(), BookingStatus.CONFIRMED)


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
