"""Leads router — protected CRUD + public capture endpoint."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.deps.auth import AuthContext, require_permission
from app.models import Lead, LeadStatus, Organization
from app.schemas.common import Page
from app.schemas.lead import LeadCreate, LeadPublicCreate, LeadRead, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])
public_router = APIRouter(prefix="/public/leads", tags=["public"])


@router.get("", response_model=Page[LeadRead])
async def list_leads(
    auth: Annotated[AuthContext, Depends(require_permission("leads:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status_filter: LeadStatus | None = Query(default=None, alias="status"),
) -> Page[LeadRead]:
    base = select(Lead).where(Lead.organization_id == auth.organization_id)
    if status_filter is not None:
        base = base.where(Lead.status == status_filter)

    total = (
        await session.execute(
            select(func.count()).select_from(base.subquery())
        )
    ).scalar_one()

    rows = (
        await session.execute(
            base.order_by(Lead.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()

    return Page[LeadRead](
        items=[LeadRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(
    lead_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("leads:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LeadRead:
    lead = await _get_org_lead(session, lead_id, auth.organization_id)
    return LeadRead.model_validate(lead)


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    auth: Annotated[AuthContext, Depends(require_permission("leads:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LeadRead:
    lead = Lead(
        organization_id=auth.organization_id,
        **payload.model_dump(),
    )
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    await _enqueue_enrichment(lead.id)
    return LeadRead.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadRead)
async def update_lead(
    lead_id: UUID,
    payload: LeadUpdate,
    auth: Annotated[AuthContext, Depends(require_permission("leads:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LeadRead:
    lead = await _get_org_lead(session, lead_id, auth.organization_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(lead, k, v)
    await session.commit()
    await session.refresh(lead)
    return LeadRead.model_validate(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("leads:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    lead = await _get_org_lead(session, lead_id, auth.organization_id)
    await session.delete(lead)
    await session.commit()


@public_router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
async def create_public_lead(
    payload: LeadPublicCreate,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LeadRead:
    """Unauthenticated lead capture from marketing site.

    Lead is attached to the org identified by `org_slug` in the payload, falling back
    to `settings.public_lead_org_slug`.
    """
    slug = payload.org_slug or settings.public_lead_org_slug
    org = (
        await session.execute(select(Organization).where(Organization.slug == slug))
    ).scalar_one_or_none()
    if org is None:
        raise HTTPException(
            status_code=404,
            detail=f"Organization '{slug}' not found. Configure PUBLIC_LEAD_ORG_SLUG.",
        )

    data = payload.model_dump(exclude={"org_slug"})
    lead = Lead(organization_id=org.id, **data)
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    await _enqueue_enrichment(lead.id)
    return LeadRead.model_validate(lead)


async def _get_org_lead(session: AsyncSession, lead_id: UUID, org_id: UUID) -> Lead:
    lead = (
        await session.execute(
            select(Lead).where(Lead.id == lead_id, Lead.organization_id == org_id)
        )
    ).scalar_one_or_none()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


async def _enqueue_enrichment(lead_id: UUID) -> None:
    """Enqueue enrichment + Attio sync jobs. Swallows errors so lead capture always succeeds."""
    try:
        from app.jobs.queue import enqueue

        await enqueue("lead_enrichment", lead_id=str(lead_id))
        await enqueue("attio_sync_lead", lead_id=str(lead_id))
    except Exception:  # pragma: no cover — best-effort enqueue
        pass
