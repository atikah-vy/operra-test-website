"""Seed a demo organization with users, leads, clients, invoices, bookings, and more.

Run with:
    uv run python scripts/seed.py
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.core.db import SessionLocal
from app.models import (
    Automation,
    Booking,
    BookingStatus,
    Client,
    ClientStatus,
    Invoice,
    InvoiceStatus,
    Lead,
    LeadStatus,
    Organization,
    SocialPost,
    SocialPostStatus,
    User,
    UserRole,
)


async def main() -> None:
    async with SessionLocal() as session:
        existing = (
            await session.execute(
                select(Organization).where(Organization.slug == "default")
            )
        ).scalar_one_or_none()
        if existing:
            print(f"Organization 'default' already exists (id={existing.id}). Skipping seed.")
            return

        org = Organization(
            id=uuid.uuid4(),
            clerk_organization_id="org_demo_default",
            name="Operra Demo",
            slug="default",
            plan="pro",
        )
        session.add(org)
        await session.flush()

        # Users — one per role
        roles: list[tuple[str, UserRole]] = [
            ("owner", UserRole.OWNER),
            ("admin", UserRole.ADMIN),
            ("sales", UserRole.SALES),
            ("marketing", UserRole.MARKETING),
            ("finance", UserRole.FINANCE),
        ]
        for name, role in roles:
            session.add(
                User(
                    id=uuid.uuid4(),
                    clerk_user_id=f"user_demo_{name}",
                    organization_id=org.id,
                    email=f"{name}@operra.demo",
                    first_name=name.capitalize(),
                    last_name="Demo",
                    role=role,
                )
            )

        # Leads
        lead_ids: list[uuid.UUID] = []
        for i, (email, status, source) in enumerate(
            [
                ("alice@acme.com", LeadStatus.NEW, "website"),
                ("bob@beta.io", LeadStatus.CONTACTED, "referral"),
                ("carla@corp.co", LeadStatus.QUALIFIED, "linkedin"),
                ("dave@delta.dev", LeadStatus.CONVERTED, "website"),
                ("eve@epsilon.ai", LeadStatus.LOST, "cold_outreach"),
            ]
        ):
            lid = uuid.uuid4()
            lead_ids.append(lid)
            session.add(
                Lead(
                    id=lid,
                    organization_id=org.id,
                    email=email,
                    first_name=email.split("@")[0].capitalize(),
                    last_name=f"Prospect{i}",
                    company=email.split("@")[1].split(".")[0].title(),
                    source=source,
                    message="Interested in Operra for our agency.",
                    status=status,
                )
            )
        await session.flush()

        # Clients
        client_id = uuid.uuid4()
        session.add(
            Client(
                id=client_id,
                organization_id=org.id,
                converted_from_lead_id=lead_ids[3],
                name="Delta Studios",
                company="Delta Studios Sdn Bhd",
                contact_email="dave@delta.dev",
                contact_phone="+60 12-345 6789",
                status=ClientStatus.ACTIVE,
            )
        )
        await session.flush()

        # Invoices
        now = datetime.now(tz=timezone.utc)
        session.add_all(
            [
                Invoice(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    client_id=client_id,
                    invoice_number="INV-0001",
                    amount=Decimal("4500.00"),
                    currency="MYR",
                    status=InvoiceStatus.PAID,
                    line_items=[
                        {"description": "Retainer — April", "quantity": 1, "unit_price": "4500.00"}
                    ],
                    issued_at=now - timedelta(days=12),
                    due_at=now - timedelta(days=2),
                    paid_at=now - timedelta(days=1),
                ),
                Invoice(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    client_id=client_id,
                    invoice_number="INV-0002",
                    amount=Decimal("2200.00"),
                    currency="MYR",
                    status=InvoiceStatus.SENT,
                    line_items=[
                        {"description": "Campaign audit", "quantity": 1, "unit_price": "2200.00"}
                    ],
                    issued_at=now,
                    due_at=now + timedelta(days=14),
                ),
            ]
        )

        # Bookings
        session.add_all(
            [
                Booking(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    client_id=client_id,
                    title="Discovery call — Delta Studios",
                    attendee_email="dave@delta.dev",
                    start_time=now + timedelta(days=2, hours=10),
                    end_time=now + timedelta(days=2, hours=11),
                    status=BookingStatus.CONFIRMED,
                ),
                Booking(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    lead_id=lead_ids[2],
                    title="Intro — Carla",
                    attendee_email="carla@corp.co",
                    start_time=now + timedelta(days=5, hours=14),
                    end_time=now + timedelta(days=5, hours=15),
                    status=BookingStatus.CONFIRMED,
                ),
            ]
        )

        # Social posts
        session.add_all(
            [
                SocialPost(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    platform="instagram",
                    content="Excited to announce our new campaign launch! 🚀",
                    status=SocialPostStatus.PUBLISHED,
                    published_at=now - timedelta(days=1),
                    metrics={"impressions": 1200, "likes": 87, "comments": 12},
                ),
                SocialPost(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    platform="linkedin",
                    content="How we helped Delta Studios grow their pipeline by 3x.",
                    scheduled_at=now + timedelta(days=1),
                    status=SocialPostStatus.SCHEDULED,
                ),
            ]
        )

        # Automation
        session.add(
            Automation(
                id=uuid.uuid4(),
                organization_id=org.id,
                name="New lead → enrich + sync",
                description="Enrich new leads via Apollo, mirror into Attio CRM.",
                trigger={"type": "lead.created"},
                actions=[
                    {"type": "apollo.enrich_person"},
                    {"type": "attio.upsert_person"},
                ],
                is_active=True,
                run_count=0,
            )
        )

        await session.commit()
        print(f"Seeded Operra Demo org (id={org.id}).")
        print("  • 5 users (owner/admin/sales/marketing/finance)")
        print("  • 5 leads, 1 client, 2 invoices, 2 bookings")
        print("  • 2 social posts, 1 automation")


if __name__ == "__main__":
    asyncio.run(main())
