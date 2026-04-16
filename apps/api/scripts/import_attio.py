"""Import all Attio people → leads and companies → clients into the database.

Run with:
    uv run python scripts/import_attio.py
"""

from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv()

from app.core.db import SessionLocal
from app.models import Client, ClientStatus, Lead, LeadStatus, Organization

ATTIO_API_KEY = os.environ["ATTIO_API_KEY"]
HEADERS = {
    "Authorization": f"Bearer {ATTIO_API_KEY}",
    "Content-Type": "application/json",
}
BASE = "https://api.attio.com/v2"

# Map Attio person status titles → LeadStatus
STATUS_MAP: dict[str, LeadStatus] = {
    "cold lead / lost lead": LeadStatus.LOST,
    "lost": LeadStatus.LOST,
    "follow up / re-follow up": LeadStatus.CONTACTED,
    "follow up": LeadStatus.CONTACTED,
    "contacted": LeadStatus.CONTACTED,
    "qualified": LeadStatus.QUALIFIED,
    "converted": LeadStatus.CONVERTED,
    "client": LeadStatus.CONVERTED,
    "new": LeadStatus.NEW,
}


def map_status(attio_title: str | None) -> LeadStatus:
    if not attio_title:
        return LeadStatus.NEW
    return STATUS_MAP.get(attio_title.lower(), LeadStatus.NEW)


async def fetch_all(client: httpx.AsyncClient, object_slug: str) -> list[dict]:
    records: list[dict] = []
    cursor: str | None = None
    page = 1
    while True:
        body: dict = {"limit": 500}
        if cursor:
            body["cursor"] = cursor
        resp = await client.post(f"{BASE}/objects/{object_slug}/records/query", json=body)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("data", [])
        records.extend(batch)
        print(f"  [{object_slug}] page {page}: fetched {len(batch)} records (total so far: {len(records)})")
        next_cursor = data.get("next_cursor")
        if not next_cursor or len(batch) == 0:
            break
        cursor = next_cursor
        page += 1
    return records


def extract_value(values: dict, key: str, subkey: str = "value") -> str | None:
    entries = values.get(key, [])
    if not entries:
        return None
    entry = entries[0]
    return entry.get(subkey)


async def main() -> None:
    async with SessionLocal() as session:
        # Ensure default org exists
        org = (
            await session.execute(select(Organization).where(Organization.slug == "default"))
        ).scalar_one_or_none()
        if not org:
            print("No default org found. Run seed.py first.")
            return
        org_id = org.id
        print(f"Using org: {org.name} (id={org_id})")

        async with httpx.AsyncClient(headers=HEADERS, timeout=30) as attio:
            # ── COMPANIES → CLIENTS ───────────────────────────────────────────
            print("\nFetching companies from Attio...")
            companies = await fetch_all(attio, "companies")
            print(f"Total companies: {len(companies)}")

            # Build a lookup: attio record_id → client db id (for people import)
            attio_company_to_client: dict[str, uuid.UUID] = {}

            clients_to_add: list[Client] = []
            for company in companies:
                record_id = company["id"]["record_id"]
                values = company.get("values", {})
                name = extract_value(values, "name") or "Unknown Company"
                # Get first email from team members if available — skip for now
                client = Client(
                    id=uuid.uuid4(),
                    organization_id=org_id,
                    name=name,
                    company=name,
                    status=ClientStatus.ACTIVE,
                    attio_record_id=record_id,
                )
                clients_to_add.append(client)
                attio_company_to_client[record_id] = client.id

            session.add_all(clients_to_add)
            await session.flush()
            print(f"Inserted {len(clients_to_add)} clients.")

            # ── PEOPLE → LEADS ────────────────────────────────────────────────
            print("\nFetching people from Attio...")
            people = await fetch_all(attio, "people")
            print(f"Total people: {len(people)}")

            leads_to_add: list[Lead] = []
            for person in people:
                record_id = person["id"]["record_id"]
                values = person.get("values", {})

                # Name
                name_entries = values.get("name", [])
                first_name = ""
                last_name = ""
                if name_entries:
                    first_name = name_entries[0].get("first_name") or ""
                    last_name = name_entries[0].get("last_name") or ""

                # Email
                email_entries = values.get("email_addresses", [])
                email = None
                if email_entries:
                    email = email_entries[0].get("email_address")
                if not email:
                    # Synthesize a placeholder so NOT NULL is satisfied
                    safe = (first_name + last_name).lower().replace(" ", "") or record_id[:8]
                    email = f"{safe}@attio.import"

                # Company name from reference
                company_ref = values.get("company", [])
                company_name = None
                if company_ref:
                    target_id = company_ref[0].get("target_record_id")
                    if target_id and target_id in attio_company_to_client:
                        # Find the client name
                        for c in clients_to_add:
                            if str(c.attio_record_id) == target_id:
                                company_name = c.company
                                break

                # Job title
                job_title = extract_value(values, "job_title")

                # Status
                status_entries = values.get("status", [])
                attio_status_title = None
                if status_entries:
                    status_obj = status_entries[0].get("status", {})
                    attio_status_title = status_obj.get("title")
                lead_status = map_status(attio_status_title)

                # Source — infer from social fields
                source = "attio_import"
                if values.get("linkedin"):
                    source = "linkedin"
                elif values.get("instagram"):
                    source = "instagram"

                # Note
                note_entries = values.get("note", [])
                message = extract_value(values, "note") if note_entries else None
                if job_title and not message:
                    message = job_title

                lead = Lead(
                    id=uuid.uuid4(),
                    organization_id=org_id,
                    email=email,
                    first_name=first_name or "Unknown",
                    last_name=last_name,
                    company=company_name,
                    source=source,
                    message=message,
                    status=lead_status,
                    attio_record_id=record_id,
                )
                leads_to_add.append(lead)

            session.add_all(leads_to_add)
            await session.commit()
            print(f"Inserted {len(leads_to_add)} leads.")

    print("\nImport complete!")
    print(f"  • {len(clients_to_add)} clients (from Attio companies)")
    print(f"  • {len(leads_to_add)} leads (from Attio people)")


if __name__ == "__main__":
    asyncio.run(main())
