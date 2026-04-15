"""Lead — prospects captured from marketing."""

from __future__ import annotations

import enum
import uuid
from typing import Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, JSONType, TimestampMixin, UUIDPrimaryKeyMixin


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class Lead(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "leads"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    company: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    message: Mapped[str | None] = mapped_column(String(2000))
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus, name="lead_status"), nullable=False, default=LeadStatus.NEW
    )
    apollo_enrichment_data: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True)
    attio_record_id: Mapped[str | None] = mapped_column(String(255))
