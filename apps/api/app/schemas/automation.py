"""Automation schemas."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedModel


class AutomationCreate(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    trigger: dict[str, Any]
    actions: list[dict[str, Any]] = Field(default_factory=list)
    is_active: bool = True


class AutomationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    trigger: dict[str, Any] | None = None
    actions: list[dict[str, Any]] | None = None
    is_active: bool | None = None


class AutomationRead(TimestampedModel):
    organization_id: UUID
    name: str
    description: str | None
    trigger: dict[str, Any]
    actions: list[dict[str, Any]]
    is_active: bool
    run_count: int
