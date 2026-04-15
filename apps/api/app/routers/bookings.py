"""Bookings router."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.deps.auth import AuthContext, require_permission
from app.models import Booking
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate
from app.schemas.common import Page

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=Page[BookingRead])
async def list_bookings(
    auth: Annotated[AuthContext, Depends(require_permission("bookings:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    start_after: datetime | None = Query(default=None),
    start_before: datetime | None = Query(default=None),
) -> Page[BookingRead]:
    conditions = [Booking.organization_id == auth.organization_id]
    if start_after:
        conditions.append(Booking.start_time >= start_after)
    if start_before:
        conditions.append(Booking.start_time <= start_before)

    base = select(Booking).where(and_(*conditions))
    total = (
        await session.execute(select(func.count()).select_from(base.subquery()))
    ).scalar_one()
    rows = (
        await session.execute(
            base.order_by(Booking.start_time.asc()).offset(offset).limit(limit)
        )
    ).scalars().all()
    return Page[BookingRead](
        items=[BookingRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("bookings:read"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BookingRead:
    b = await _get_org_booking(session, booking_id, auth.organization_id)
    return BookingRead.model_validate(b)


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    auth: Annotated[AuthContext, Depends(require_permission("bookings:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BookingRead:
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=422, detail="end_time must be after start_time")
    b = Booking(organization_id=auth.organization_id, **payload.model_dump())
    session.add(b)
    await session.commit()
    await session.refresh(b)
    return BookingRead.model_validate(b)


@router.patch("/{booking_id}", response_model=BookingRead)
async def update_booking(
    booking_id: UUID,
    payload: BookingUpdate,
    auth: Annotated[AuthContext, Depends(require_permission("bookings:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BookingRead:
    b = await _get_org_booking(session, booking_id, auth.organization_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(b, k, v)
    await session.commit()
    await session.refresh(b)
    return BookingRead.model_validate(b)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: UUID,
    auth: Annotated[AuthContext, Depends(require_permission("bookings:write"))],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    b = await _get_org_booking(session, booking_id, auth.organization_id)
    await session.delete(b)
    await session.commit()


async def _get_org_booking(session: AsyncSession, booking_id: UUID, org_id: UUID) -> Booking:
    b = (
        await session.execute(
            select(Booking).where(
                Booking.id == booking_id, Booking.organization_id == org_id
            )
        )
    ).scalar_one_or_none()
    if b is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return b
