"""Lead schemas."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import LeadStatus
from app.schemas.common import TimestampedModel


class LeadCreate(BaseModel):
    email: EmailStr
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    company: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=50)
    source: str = Field(default="unknown", max_length=50)
    message: str | None = Field(default=None, max_length=2000)


class LeadPublicCreate(LeadCreate):
    """Public (unauthenticated) lead submission from marketing site."""

    org_slug: str | None = Field(default=None, max_length=255)


class LeadUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None
    phone: str | None = None
    status: LeadStatus | None = None
    message: str | None = None


class LeadRead(TimestampedModel):
    organization_id: UUID
    email: str
    first_name: str | None
    last_name: str | None
    company: str | None
    phone: str | None
    source: str
    message: str | None
    status: LeadStatus
    apollo_enrichment_data: dict[str, Any] | None
    attio_record_id: str | None
