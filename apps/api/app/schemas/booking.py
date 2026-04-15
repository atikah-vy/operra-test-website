"""Booking schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import BookingStatus
from app.schemas.common import TimestampedModel


class BookingCreate(BaseModel):
    title: str = Field(max_length=255)
    attendee_email: EmailStr | None = None
    start_time: datetime
    end_time: datetime
    client_id: UUID | None = None
    lead_id: UUID | None = None
    status: BookingStatus = BookingStatus.CONFIRMED


class BookingUpdate(BaseModel):
    title: str | None = None
    attendee_email: EmailStr | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: BookingStatus | None = None


class BookingRead(TimestampedModel):
    organization_id: UUID
    client_id: UUID | None
    lead_id: UUID | None
    title: str
    attendee_email: str | None
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    calcom_booking_id: str | None
