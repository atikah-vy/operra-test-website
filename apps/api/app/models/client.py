"""Client — accounts converted from leads."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ClientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHURNED = "churned"


class Client(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "clients"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    converted_from_lead_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[str | None] = mapped_column(String(200))
    contact_email: Mapped[str | None] = mapped_column(String(320))
    contact_phone: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[ClientStatus] = mapped_column(
        SAEnum(ClientStatus, name="client_status", values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=ClientStatus.ACTIVE
    )
    attio_record_id: Mapped[str | None] = mapped_column(String(255))
