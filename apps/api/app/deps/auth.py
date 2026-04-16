"""Auth + RBAC dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clerk import ClerkClaims, verifier
from app.core.db import get_session
from app.models import Organization, User, UserRole

# RBAC matrix — permission → roles allowed
PERMISSIONS: dict[str, set[UserRole]] = {
    "leads:read": {UserRole.OWNER, UserRole.ADMIN, UserRole.SALES},
    "leads:write": {UserRole.OWNER, UserRole.ADMIN, UserRole.SALES},
    "clients:read": {UserRole.OWNER, UserRole.ADMIN, UserRole.SALES},
    "clients:write": {UserRole.OWNER, UserRole.ADMIN, UserRole.SALES},
    "invoices:read": {UserRole.OWNER, UserRole.ADMIN, UserRole.FINANCE},
    "invoices:write": {UserRole.OWNER, UserRole.ADMIN, UserRole.FINANCE},
    "social:read": {UserRole.OWNER, UserRole.ADMIN, UserRole.MARKETING},
    "social:write": {UserRole.OWNER, UserRole.ADMIN, UserRole.MARKETING},
    "bookings:read": {UserRole.OWNER, UserRole.ADMIN, UserRole.SALES},
    "bookings:write": {UserRole.OWNER, UserRole.ADMIN, UserRole.SALES},
    "automations:read": {UserRole.OWNER, UserRole.ADMIN},
    "automations:write": {UserRole.OWNER, UserRole.ADMIN},
    "integrations:manage": {UserRole.OWNER, UserRole.ADMIN},
    "organization:manage": {UserRole.OWNER},
    "users:manage": {UserRole.OWNER, UserRole.ADMIN},
    "analytics:read": {
        UserRole.OWNER,
        UserRole.ADMIN,
        UserRole.SALES,
        UserRole.MARKETING,
        UserRole.FINANCE,
    },
}


@dataclass(frozen=True)
class AuthContext:
    user: User
    organization: Organization
    claims: ClerkClaims

    @property
    def user_id(self) -> UUID:
        return self.user.id

    @property
    def organization_id(self) -> UUID:
        return self.organization.id

    @property
    def role(self) -> UserRole:
        return self.user.role


async def _extract_bearer(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization.split(" ", 1)[1].strip()


async def get_current_auth(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    x_org_id: Annotated[str | None, Header(alias="X-Org-Id")] = None,
    session: AsyncSession = Depends(get_session),
) -> AuthContext:
    token = await _extract_bearer(authorization)
    try:
        claims = verifier.verify(token)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc
    except RuntimeError as exc:
        # Misconfigured JWKS — surface as 503 so ops can see it distinctly
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    # Resolve org: prefer JWT/header org, fall back to the default org (no-org mode)
    active_clerk_org = x_org_id or claims.clerk_org_id
    if active_clerk_org:
        org = (
            await session.execute(
                select(Organization).where(Organization.clerk_organization_id == active_clerk_org)
            )
        ).scalar_one_or_none()
        if org is None:
            raise HTTPException(status_code=403, detail="Organization not provisioned.")
    else:
        # No org in token — fall back to the default org (single-org / no-org mode)
        org = (
            await session.execute(
                select(Organization).where(Organization.slug == "default")
            )
        ).scalar_one_or_none()
        if org is None:
            raise HTTPException(
                status_code=403,
                detail="No default organization found. Run the seed script first.",
            )

    # Find local user — auto-provision on first login if using default org
    user = (
        await session.execute(
            select(User).where(User.clerk_user_id == claims.clerk_user_id)
        )
    ).scalar_one_or_none()
    if user is None:
        import uuid as _uuid
        user = User(
            id=_uuid.uuid4(),
            clerk_user_id=claims.clerk_user_id,
            organization_id=org.id,
            email=claims.email or f"{claims.clerk_user_id}@clerk.local",
            first_name="",
            last_name="",
            role=UserRole.OWNER,
        )
        session.add(user)
        await session.flush()

    if user.organization_id != org.id:
        # Users are scoped to an org locally; if user switches org in Clerk we'd need
        # to support multi-org membership. For now, require 1:1 mapping.
        raise HTTPException(
            status_code=403,
            detail="User does not belong to the active organization.",
        )

    return AuthContext(user=user, organization=org, claims=claims)


def require_permission(permission: str):
    """Dep factory that gates a route by RBAC permission."""
    allowed_roles = PERMISSIONS.get(permission)
    if allowed_roles is None:
        raise ValueError(f"Unknown permission: {permission}")

    async def _dep(auth_ctx: Annotated[AuthContext, Depends(get_current_auth)]) -> AuthContext:
        if auth_ctx.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{auth_ctx.role.value}' lacks permission '{permission}'.",
            )
        return auth_ctx

    return _dep
