"""Automation — workflow trigger/action rules."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, JSONType, TimestampMixin, UUIDPrimaryKeyMixin


class Automation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "automations"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    trigger: Mapped[dict[str, Any]] = mapped_column(JSONType, nullable=False)
    actions: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    run_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
