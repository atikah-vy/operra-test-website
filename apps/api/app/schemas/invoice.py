"""Invoice schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models import InvoiceStatus
from app.schemas.common import TimestampedModel


class InvoiceCreate(BaseModel):
    client_id: UUID
    invoice_number: str = Field(max_length=50)
    amount: Decimal = Field(default=Decimal("0"), ge=0)
    currency: str = Field(default="MYR", min_length=3, max_length=3)
    line_items: list[dict[str, Any]] = Field(default_factory=list)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issued_at: datetime | None = None
    due_at: datetime | None = None


class InvoiceUpdate(BaseModel):
    amount: Decimal | None = None
    currency: str | None = None
    line_items: list[dict[str, Any]] | None = None
    status: InvoiceStatus | None = None
    issued_at: datetime | None = None
    due_at: datetime | None = None
    paid_at: datetime | None = None


class InvoiceRead(TimestampedModel):
    organization_id: UUID
    client_id: UUID
    invoice_number: str
    amount: Decimal
    currency: str
    status: InvoiceStatus
    line_items: list[dict[str, Any]]
    issued_at: datetime | None
    due_at: datetime | None
    paid_at: datetime | None
    bukku_invoice_id: str | None
