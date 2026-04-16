"""SyncLog — audit trail for every integration call."""

from __future__ import annotations

import enum
import uuid
from typing import Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, JSONType, TimestampMixin, UUIDPrimaryKeyMixin


class SyncLogStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


class SyncLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sync_logs"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    integration: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50))
    entity_id: Mapped[str | None] = mapped_column(String(255))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[SyncLogStatus] = mapped_column(
        SAEnum(SyncLogStatus, name="sync_log_status", values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    request_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONType)
    response_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONType)
    error_message: Mapped[str | None] = mapped_column(String(2000))
