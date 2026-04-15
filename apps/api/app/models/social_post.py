"""SocialPost — Metricool-managed posts."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, JSONType, TimestampMixin, UUIDPrimaryKeyMixin


class SocialPostStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class SocialPost(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "social_posts"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # instagram, facebook, linkedin, etc.
    content: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[SocialPostStatus] = mapped_column(
        SAEnum(SocialPostStatus, name="social_post_status"),
        nullable=False,
        default=SocialPostStatus.DRAFT,
    )
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True)
    metricool_id: Mapped[str | None] = mapped_column(String(255))
