"""Automations router."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.deps.auth import AuthContext, require_permission
from app.models import Automation
from app.schemas.automation import AutomationCreate, AutomationRead, AutomationUpdate
from app.schemas.common import Page

router = APIRouter(prefix="/automations", tags=["automations"])


@router.get("", response_model=Page[AutomationRead])
async def list_automations(
    auth: Annotated[AuthContext, Depends(require_permission("automations:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> Page[AutomationRead]:
    base = select(Automation).where(Automation.organization_id == auth.organization_id)
    total = (
        await session.execute(select(func.count()).select_from(base.subquery()))
    ).scalar_one()
    rows = (
        await session.execute(
            base.order_by(Automation.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()
    return Page[AutomationRead](
        items=[AutomationRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{automation_id}", response_model=AutomationRead)
async def get_automation(
    automation_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("automations:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AutomationRead:
    a = await _get_org_automation(session, automation_id, auth.organization_id)
    return AutomationRead.model_validate(a)


@router.post("", response_model=AutomationRead, status_code=status.HTTP_201_CREATED)
async def create_automation(
    payload: AutomationCreate,
    auth: Annotated[AuthContext, Depends(require_permission("automations:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AutomationRead:
    a = Automation(organization_id=auth.organization_id, **payload.model_dump())
    session.add(a)
    await session.commit()
    await session.refresh(a)
    return AutomationRead.model_validate(a)


@router.patch("/{automation_id}", response_model=AutomationRead)
async def update_automation(
    automation_id: UUID,
    payload: AutomationUpdate,
    auth: Annotated[AuthContext, Depends(require_permission("automations:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AutomationRead:
    a = await _get_org_automation(session, automation_id, auth.organization_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    await session.commit()
    await session.refresh(a)
    return AutomationRead.model_validate(a)


@router.delete("/{automation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation(
    automation_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("automations:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    a = await _get_org_automation(session, automation_id, auth.organization_id)
    await session.delete(a)
    await session.commit()


async def _get_org_automation(
    session: AsyncSession, automation_id: UUID, org_id: UUID
) -> Automation:
    a = (
        await session.execute(
            select(Automation).where(
                Automation.id == automation_id, Automation.organization_id == org_id
            )
        )
    ).scalar_one_or_none()
    if a is None:
        raise HTTPException(status_code=404, detail="Automation not found")
    return a
