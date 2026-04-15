"""Clients router."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.deps.auth import AuthContext, require_permission
from app.models import Client
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.schemas.common import Page

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=Page[ClientRead])
async def list_clients(
    auth: Annotated[AuthContext, Depends(require_permission("clients:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> Page[ClientRead]:
    base = select(Client).where(Client.organization_id == auth.organization_id)
    total = (
        await session.execute(select(func.count()).select_from(base.subquery()))
    ).scalar_one()
    rows = (
        await session.execute(
            base.order_by(Client.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()
    return Page[ClientRead](
        items=[ClientRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("clients:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ClientRead:
    client = await _get_org_client(session, client_id, auth.organization_id)
    return ClientRead.model_validate(client)


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    auth: Annotated[AuthContext, Depends(require_permission("clients:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ClientRead:
    client = Client(organization_id=auth.organization_id, **payload.model_dump())
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return ClientRead.model_validate(client)


@router.patch("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: UUID,
    payload: ClientUpdate,
    auth: Annotated[AuthContext, Depends(require_permission("clients:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ClientRead:
    client = await _get_org_client(session, client_id, auth.organization_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(client, k, v)
    await session.commit()
    await session.refresh(client)
    return ClientRead.model_validate(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("clients:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    client = await _get_org_client(session, client_id, auth.organization_id)
    await session.delete(client)
    await session.commit()


async def _get_org_client(session: AsyncSession, client_id: UUID, org_id: UUID) -> Client:
    client = (
        await session.execute(
            select(Client).where(Client.id == client_id, Client.organization_id == org_id)
        )
    ).scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client
