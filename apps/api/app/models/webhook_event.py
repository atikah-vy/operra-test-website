"""WebhookEvent — idempotent ingestion ledger."""

from __future__ import annotations

import enum
import uuid
from typing import Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, JSONType, TimestampMixin, UUIDPrimaryKeyMixin


class WebhookEventStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class WebhookEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "webhook_events"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_webhook_source_external"),)

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # attio, calcom, meta, clerk
    event_type: Mapped[str | None] = mapped_column(String(100))
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONType, nullable=False)
    status: Mapped[WebhookEventStatus] = mapped_column(
        SAEnum(WebhookEventStatus, name="webhook_event_status", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=WebhookEventStatus.PENDING,
    )
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(String(2000))
