"""Social post schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models import SocialPostStatus
from app.schemas.common import TimestampedModel


class SocialPostCreate(BaseModel):
    platform: str = Field(max_length=50)
    content: str = Field(min_length=1)
    scheduled_at: datetime | None = None
    status: SocialPostStatus = SocialPostStatus.DRAFT


class SocialPostUpdate(BaseModel):
    content: str | None = None
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    status: SocialPostStatus | None = None
    metrics: dict[str, Any] | None = None


class SocialPostRead(TimestampedModel):
    organization_id: UUID
    platform: str
    content: str
    scheduled_at: datetime | None
    published_at: datetime | None
    status: SocialPostStatus
    metrics: dict[str, Any] | None
    metricool_id: str | None
