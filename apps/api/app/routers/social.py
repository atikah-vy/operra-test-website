"""Social posts router."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.deps.auth import AuthContext, require_permission
from app.models import SocialPost, SocialPostStatus
from app.schemas.common import Page
from app.schemas.social import SocialPostCreate, SocialPostRead, SocialPostUpdate

router = APIRouter(prefix="/social", tags=["social"])


@router.get("/posts", response_model=Page[SocialPostRead])
async def list_posts(
    auth: Annotated[AuthContext, Depends(require_permission("social:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status_filter: SocialPostStatus | None = Query(default=None, alias="status"),
    platform: str | None = Query(default=None),
) -> Page[SocialPostRead]:
    base = select(SocialPost).where(SocialPost.organization_id == auth.organization_id)
    if status_filter is not None:
        base = base.where(SocialPost.status == status_filter)
    if platform:
        base = base.where(SocialPost.platform == platform)

    total = (
        await session.execute(select(func.count()).select_from(base.subquery()))
    ).scalar_one()
    rows = (
        await session.execute(
            base.order_by(SocialPost.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()
    return Page[SocialPostRead](
        items=[SocialPostRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/posts", response_model=SocialPostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: SocialPostCreate,
    auth: Annotated[AuthContext, Depends(require_permission("social:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SocialPostRead:
    post = SocialPost(organization_id=auth.organization_id, **payload.model_dump())
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return SocialPostRead.model_validate(post)


@router.patch("/posts/{post_id}", response_model=SocialPostRead)
async def update_post(
    post_id: UUID,
    payload: SocialPostUpdate,
    auth: Annotated[AuthContext, Depends(require_permission("social:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SocialPostRead:
    post = await _get_org_post(session, post_id, auth.organization_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(post, k, v)
    await session.commit()
    await session.refresh(post)
    return SocialPostRead.model_validate(post)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("social:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    post = await _get_org_post(session, post_id, auth.organization_id)
    await session.delete(post)
    await session.commit()


async def _get_org_post(session: AsyncSession, post_id: UUID, org_id: UUID) -> SocialPost:
    post = (
        await session.execute(
            select(SocialPost).where(
                SocialPost.id == post_id, SocialPost.organization_id == org_id
            )
        )
    ).scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Social post not found")
    return post
