"""Clerk webhook handler — syncs users/orgs into local DB.

Events handled:
  - user.created, user.updated
  - organization.created, organization.updated
  - organizationMembership.created, organizationMembership.updated
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.models import Organization, User, UserRole
from app.webhooks.processor import ingest

try:
    from svix.webhooks import Webhook as SvixWebhook  # type: ignore
    from svix.webhooks import WebhookVerificationError  # type: ignore
except ImportError:  # pragma: no cover
    SvixWebhook = None  # type: ignore
    WebhookVerificationError = Exception  # type: ignore

logger = logging.getLogger("operra.webhooks.clerk")
router = APIRouter(prefix="/webhooks/clerk", tags=["webhooks"])


@router.post("")
async def clerk_webhook(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    svix_id: Annotated[str | None, Header(alias="svix-id")] = None,
    svix_timestamp: Annotated[str | None, Header(alias="svix-timestamp")] = None,
    svix_signature: Annotated[str | None, Header(alias="svix-signature")] = None,
) -> dict[str, Any]:
    body = await request.body()

    if not settings.clerk_webhook_signing_secret:
        raise HTTPException(status_code=503, detail="CLERK_WEBHOOK_SIGNING_SECRET not set")
    if SvixWebhook is None:
        raise HTTPException(status_code=503, detail="svix package not installed")
    if not (svix_id and svix_timestamp and svix_signature):
        raise HTTPException(status_code=400, detail="Missing svix headers")

    try:
        wh = SvixWebhook(settings.clerk_webhook_signing_secret)
        payload = wh.verify(
            body,
            {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature,
            },
        )
    except WebhookVerificationError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid signature: {exc}") from exc

    event_type: str = payload.get("type", "")
    data: dict[str, Any] = payload.get("data", {})
    external_id = svix_id  # Svix guarantees uniqueness

    async def _handle(sess: AsyncSession, _event: Any) -> None:
        await _dispatch(sess, event_type, data)

    await ingest(
        session,
        source="clerk",
        external_id=external_id,
        event_type=event_type,
        payload=payload,
        handler=_handle,
    )
    return {"ok": True}


async def _dispatch(session: AsyncSession, event_type: str, data: dict[str, Any]) -> None:
    if event_type.startswith("organization.") and event_type != "organizationMembership.created":
        await _upsert_organization(session, data)
    elif event_type.startswith("user."):
        await _upsert_user(session, data)
    elif event_type == "organizationMembership.created":
        await _handle_membership(session, data)
    else:
        logger.info("Clerk event %s ignored", event_type)


async def _upsert_organization(session: AsyncSession, data: dict[str, Any]) -> Organization:
    clerk_org_id = data["id"]
    existing = (
        await session.execute(
            select(Organization).where(Organization.clerk_organization_id == clerk_org_id)
        )
    ).scalar_one_or_none()

    if existing:
        existing.name = data.get("name", existing.name)
        existing.slug = data.get("slug", existing.slug)
        return existing

    org = Organization(
        id=uuid.uuid4(),
        clerk_organization_id=clerk_org_id,
        name=data.get("name") or clerk_org_id,
        slug=data.get("slug") or clerk_org_id,
        plan="free",
    )
    session.add(org)
    return org


async def _upsert_user(session: AsyncSession, data: dict[str, Any]) -> User | None:
    clerk_user_id = data["id"]
    emails = data.get("email_addresses") or []
    email = emails[0].get("email_address") if emails else None
    if not email:
        logger.warning("Clerk user %s has no email — skipping", clerk_user_id)
        return None

    # Requires an active org membership to resolve the local organization.
    memberships = data.get("organization_memberships") or []
    if not memberships:
        logger.info("Clerk user %s created without org membership — defer", clerk_user_id)
        return None

    primary = memberships[0]
    clerk_org_id = primary.get("organization", {}).get("id") or primary.get("organization_id")
    if not clerk_org_id:
        return None

    org = (
        await session.execute(
            select(Organization).where(Organization.clerk_organization_id == clerk_org_id)
        )
    ).scalar_one_or_none()
    if org is None:
        # Create org ahead of user if webhook order is inverted
        org = Organization(
            id=uuid.uuid4(),
            clerk_organization_id=clerk_org_id,
            name=clerk_org_id,
            slug=clerk_org_id,
            plan="free",
        )
        session.add(org)
        await session.flush()

    existing = (
        await session.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    ).scalar_one_or_none()

    role = _map_role(primary.get("role"))
    if existing:
        existing.email = email
        existing.first_name = data.get("first_name")
        existing.last_name = data.get("last_name")
        existing.organization_id = org.id
        existing.role = role
        return existing

    user = User(
        id=uuid.uuid4(),
        clerk_user_id=clerk_user_id,
        organization_id=org.id,
        email=email,
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        role=role,
    )
    session.add(user)
    return user


async def _handle_membership(session: AsyncSession, data: dict[str, Any]) -> None:
    """Attach a user to an org (or update role)."""
    clerk_user_id = (data.get("public_user_data") or {}).get("user_id")
    clerk_org_id = (data.get("organization") or {}).get("id")
    if not (clerk_user_id and clerk_org_id):
        return

    org = (
        await session.execute(
            select(Organization).where(Organization.clerk_organization_id == clerk_org_id)
        )
    ).scalar_one_or_none()
    user = (
        await session.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    ).scalar_one_or_none()
    if not (org and user):
        return

    user.organization_id = org.id
    user.role = _map_role(data.get("role"))


def _map_role(clerk_role: str | None) -> UserRole:
    if not clerk_role:
        return UserRole.ADMIN
    # Clerk: "org:admin" / "org:member" (and custom roles). Default unknown → ADMIN.
    normalized = clerk_role.replace("org:", "").lower()
    mapping = {
        "owner": UserRole.OWNER,
        "admin": UserRole.ADMIN,
        "sales": UserRole.SALES,
        "marketing": UserRole.MARKETING,
        "finance": UserRole.FINANCE,
        "member": UserRole.ADMIN,
    }
    return mapping.get(normalized, UserRole.ADMIN)
