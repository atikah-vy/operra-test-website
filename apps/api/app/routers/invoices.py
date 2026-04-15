"""Invoices router."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.deps.auth import AuthContext, require_permission
from app.models import Client, Invoice, InvoiceStatus
from app.schemas.common import Page
from app.schemas.invoice import InvoiceCreate, InvoiceRead, InvoiceUpdate

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=Page[InvoiceRead])
async def list_invoices(
    auth: Annotated[AuthContext, Depends(require_permission("invoices:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status_filter: InvoiceStatus | None = Query(default=None, alias="status"),
) -> Page[InvoiceRead]:
    base = select(Invoice).where(Invoice.organization_id == auth.organization_id)
    if status_filter is not None:
        base = base.where(Invoice.status == status_filter)
    total = (
        await session.execute(select(func.count()).select_from(base.subquery()))
    ).scalar_one()
    rows = (
        await session.execute(
            base.order_by(Invoice.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()
    return Page[InvoiceRead](
        items=[InvoiceRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{invoice_id}", response_model=InvoiceRead)
async def get_invoice(
    invoice_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("invoices:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InvoiceRead:
    inv = await _get_org_invoice(session, invoice_id, auth.organization_id)
    return InvoiceRead.model_validate(inv)


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreate,
    auth: Annotated[AuthContext, Depends(require_permission("invoices:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InvoiceRead:
    # Ensure client belongs to same org
    client = (
        await session.execute(
            select(Client).where(
                Client.id == payload.client_id,
                Client.organization_id == auth.organization_id,
            )
        )
    ).scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found in organization")

    inv = Invoice(organization_id=auth.organization_id, **payload.model_dump())
    session.add(inv)
    await session.commit()
    await session.refresh(inv)
    return InvoiceRead.model_validate(inv)


@router.patch("/{invoice_id}", response_model=InvoiceRead)
async def update_invoice(
    invoice_id: UUID,
    payload: InvoiceUpdate,
    auth: Annotated[AuthContext, Depends(require_permission("invoices:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InvoiceRead:
    inv = await _get_org_invoice(session, invoice_id, auth.organization_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(inv, k, v)
    await session.commit()
    await session.refresh(inv)
    return InvoiceRead.model_validate(inv)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("invoices:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    inv = await _get_org_invoice(session, invoice_id, auth.organization_id)
    await session.delete(inv)
    await session.commit()


async def _get_org_invoice(session: AsyncSession, invoice_id: UUID, org_id: UUID) -> Invoice:
    inv = (
        await session.execute(
            select(Invoice).where(
                Invoice.id == invoice_id, Invoice.organization_id == org_id
            )
        )
    ).scalar_one_or_none()
    if inv is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv
