"""Client schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import ClientStatus
from app.schemas.common import TimestampedModel


class ClientCreate(BaseModel):
    name: str = Field(max_length=200)
    company: str | None = Field(default=None, max_length=200)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=50)
    converted_from_lead_id: UUID | None = None
    status: ClientStatus = ClientStatus.ACTIVE


class ClientUpdate(BaseModel):
    name: str | None = None
    company: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    status: ClientStatus | None = None


class ClientRead(TimestampedModel):
    organization_id: UUID
    converted_from_lead_id: UUID | None
    name: str
    company: str | None
    contact_email: str | None
    contact_phone: str | None
    status: ClientStatus
    attio_record_id: str | None
