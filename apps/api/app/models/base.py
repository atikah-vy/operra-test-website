"""SQLAlchemy declarative base + shared mixins."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Cross-dialect JSON column: JSONB on Postgres (so GIN indexes + ? operators work),
# plain JSON elsewhere so the SQLite-based test suite can use the same models.
JSONType = JSON().with_variant(PG_JSONB(), "postgresql")


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(UTC),
    )
