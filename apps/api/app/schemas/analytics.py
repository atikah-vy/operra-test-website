"""Analytics / dashboard overview schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.models import BookingStatus, LeadStatus


class StatBlock(BaseModel):
    leads_total: int
    leads_new: int
    clients_active: int
    revenue_month: Decimal
    upcoming_bookings: int


class RecentLead(BaseModel):
    id: UUID
    email: str
    first_name: str | None
    last_name: str | None
    status: LeadStatus
    source: str
    created_at: datetime


class UpcomingBooking(BaseModel):
    id: UUID
    title: str
    start_time: datetime
    end_time: datetime
    attendee_email: str | None
    status: BookingStatus


class DashboardOverview(BaseModel):
    stats: StatBlock
    recent_leads: list[RecentLead]
    upcoming_bookings_list: list[UpcomingBooking]
