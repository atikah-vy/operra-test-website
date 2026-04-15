"""Analytics / dashboard overview."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.deps.auth import AuthContext, require_permission
from app.models import (
    Booking,
    BookingStatus,
    Client,
    ClientStatus,
    Invoice,
    InvoiceStatus,
    Lead,
    LeadStatus,
)
from app.schemas.analytics import (
    DashboardOverview,
    RecentLead,
    StatBlock,
    UpcomingBooking,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=DashboardOverview)
async def overview(
    auth: Annotated[AuthContext, Depends(require_permission("analytics:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DashboardOverview:
    org_id = auth.organization_id
    now = datetime.now(tz=timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    leads_total = (
        await session.execute(
            select(func.count(Lead.id)).where(Lead.organization_id == org_id)
        )
    ).scalar_one()
    leads_new = (
        await session.execute(
            select(func.count(Lead.id)).where(
                Lead.organization_id == org_id, Lead.status == LeadStatus.NEW
            )
        )
    ).scalar_one()
    clients_active = (
        await session.execute(
            select(func.count(Client.id)).where(
                Client.organization_id == org_id, Client.status == ClientStatus.ACTIVE
            )
        )
    ).scalar_one()
    revenue_month = (
        await session.execute(
            select(func.coalesce(func.sum(Invoice.amount), 0)).where(
                Invoice.organization_id == org_id,
                Invoice.status == InvoiceStatus.PAID,
                Invoice.paid_at >= month_start,
            )
        )
    ).scalar_one()
    upcoming_count = (
        await session.execute(
            select(func.count(Booking.id)).where(
                Booking.organization_id == org_id,
                Booking.start_time >= now,
                Booking.status == BookingStatus.CONFIRMED,
            )
        )
    ).scalar_one()

    recent_leads_rows = (
        await session.execute(
            select(Lead)
            .where(Lead.organization_id == org_id)
            .order_by(Lead.created_at.desc())
            .limit(5)
        )
    ).scalars().all()

    upcoming_rows = (
        await session.execute(
            select(Booking)
            .where(
                Booking.organization_id == org_id,
                Booking.start_time >= now,
                Booking.start_time <= now + timedelta(days=14),
            )
            .order_by(Booking.start_time.asc())
            .limit(5)
        )
    ).scalars().all()

    return DashboardOverview(
        stats=StatBlock(
            leads_total=leads_total,
            leads_new=leads_new,
            clients_active=clients_active,
            revenue_month=Decimal(revenue_month),
            upcoming_bookings=upcoming_count,
        ),
        recent_leads=[
            RecentLead(
                id=l.id,
                email=l.email,
                first_name=l.first_name,
                last_name=l.last_name,
                status=l.status,
                source=l.source,
                created_at=l.created_at,
            )
            for l in recent_leads_rows
        ],
        upcoming_bookings_list=[
            UpcomingBooking(
                id=b.id,
                title=b.title,
                start_time=b.start_time,
                end_time=b.end_time,
                attendee_email=b.attendee_email,
                status=b.status,
            )
            for b in upcoming_rows
        ],
    )
