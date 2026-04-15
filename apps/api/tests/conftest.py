"""Pytest fixtures — in-memory SQLite for fast unit tests.

For production-grade integration tests against Postgres, override DATABASE_URL
and swap the engine here.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Point config at SQLite before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("CLERK_JWKS_URL", "https://example.test/.well-known/jwks.json")
os.environ.setdefault("CLERK_ISSUER", "https://example.test")
os.environ.setdefault("CLERK_WEBHOOK_SIGNING_SECRET", "whsec_test")
os.environ.setdefault("ATTIO_WEBHOOK_SECRET", "attio_secret")
os.environ.setdefault("CALCOM_WEBHOOK_SECRET", "calcom_secret")
os.environ.setdefault("META_APP_SECRET", "meta_secret")
os.environ.setdefault("META_VERIFY_TOKEN", "meta_verify")

from app.core import db as core_db  # noqa: E402
from app.deps.auth import AuthContext, get_current_auth  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Organization, User, UserRole  # noqa: E402


@pytest_asyncio.fixture
async def engine() -> AsyncIterator[Any]:
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine: Any) -> AsyncIterator[AsyncSession]:
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as s:
        yield s


@pytest_asyncio.fixture
async def demo_org(session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        clerk_organization_id="org_test",
        name="Test Org",
        slug="default",
        plan="free",
    )
    session.add(org)
    await session.commit()
    await session.refresh(org)
    return org


@pytest_asyncio.fixture
async def admin_user(session: AsyncSession, demo_org: Organization) -> User:
    u = User(
        id=uuid.uuid4(),
        clerk_user_id="user_admin",
        organization_id=demo_org.id,
        email="admin@test.local",
        first_name="Ad",
        last_name="Min",
        role=UserRole.ADMIN,
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


@pytest.fixture
def client_factory(engine: Any, admin_user: User, demo_org: Organization):
    """Build an AsyncClient with auth + DB overrides wired up."""

    async def _make(role: UserRole = UserRole.ADMIN) -> AsyncClient:
        admin_user.role = role  # mutate per test

        # Override DB
        maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async def _session() -> AsyncIterator[AsyncSession]:
            async with maker() as s:
                yield s

        app.dependency_overrides[core_db.get_session] = _session

        # Override auth dep
        async def _auth() -> AuthContext:
            from app.core.clerk import ClerkClaims

            return AuthContext(
                user=admin_user,
                organization=demo_org,
                claims=ClerkClaims(
                    clerk_user_id=admin_user.clerk_user_id,
                    clerk_org_id=demo_org.clerk_organization_id,
                    clerk_org_role="org:admin",
                    email=admin_user.email,
                    raw={},
                ),
            )

        app.dependency_overrides[get_current_auth] = _auth

        return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    yield _make
    app.dependency_overrides.clear()
