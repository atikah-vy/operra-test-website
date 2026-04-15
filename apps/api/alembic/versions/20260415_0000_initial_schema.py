"""Initial schema — 10 tables for Operra STL OS.

Revision ID: 20260415_0000
Revises:
Create Date: 2026-04-15 00:00:00

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "20260415_0000"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum type names must match app.models.* so auto-generation of future migrations works.
user_role = sa.Enum(
    "owner", "admin", "sales", "marketing", "finance", name="user_role"
)
lead_status = sa.Enum("new", "contacted", "qualified", "converted", "lost", name="lead_status")
client_status = sa.Enum("active", "inactive", "churned", name="client_status")
invoice_status = sa.Enum("draft", "sent", "paid", "overdue", "void", name="invoice_status")
booking_status = sa.Enum("confirmed", "cancelled", "rescheduled", "completed", name="booking_status")
social_post_status = sa.Enum(
    "draft", "scheduled", "published", "failed", name="social_post_status"
)
webhook_event_status = sa.Enum(
    "pending", "processing", "processed", "failed", name="webhook_event_status"
)
sync_log_status = sa.Enum("success", "failure", "partial", name="sync_log_status")


def upgrade() -> None:
    # Create enums first
    user_role.create(op.get_bind(), checkfirst=True)
    lead_status.create(op.get_bind(), checkfirst=True)
    client_status.create(op.get_bind(), checkfirst=True)
    invoice_status.create(op.get_bind(), checkfirst=True)
    booking_status.create(op.get_bind(), checkfirst=True)
    social_post_status.create(op.get_bind(), checkfirst=True)
    webhook_event_status.create(op.get_bind(), checkfirst=True)
    sync_log_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "organizations",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_organization_id", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("plan", sa.String(50), nullable=False, server_default="free"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_organizations_clerk_organization_id", "organizations", ["clerk_organization_id"])
    op.create_index("ix_organizations_slug", "organizations", ["slug"])

    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_user_id", sa.String(255), nullable=False, unique=True),
        sa.Column(
            "organization_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("first_name", sa.String(100)),
        sa.Column("last_name", sa.String(100)),
        sa.Column("role", user_role, nullable=False, server_default="admin"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_clerk_user_id", "users", ["clerk_user_id"])
    op.create_index("ix_users_organization_id", "users", ["organization_id"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "leads",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("first_name", sa.String(100)),
        sa.Column("last_name", sa.String(100)),
        sa.Column("company", sa.String(200)),
        sa.Column("phone", sa.String(50)),
        sa.Column("source", sa.String(50), nullable=False, server_default="unknown"),
        sa.Column("message", sa.String(2000)),
        sa.Column("status", lead_status, nullable=False, server_default="new"),
        sa.Column("apollo_enrichment_data", pg.JSONB),
        sa.Column("attio_record_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_leads_organization_id", "leads", ["organization_id"])
    op.create_index("ix_leads_email", "leads", ["email"])

    op.create_table(
        "clients",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("converted_from_lead_id", pg.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("company", sa.String(200)),
        sa.Column("contact_email", sa.String(320)),
        sa.Column("contact_phone", sa.String(50)),
        sa.Column("status", client_status, nullable=False, server_default="active"),
        sa.Column("attio_record_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_clients_organization_id", "clients", ["organization_id"])

    op.create_table(
        "invoices",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", pg.UUID(as_uuid=True), sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("invoice_number", sa.String(50), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="MYR"),
        sa.Column("status", invoice_status, nullable=False, server_default="draft"),
        sa.Column("line_items", pg.JSONB, nullable=False, server_default="[]"),
        sa.Column("issued_at", sa.DateTime(timezone=True)),
        sa.Column("due_at", sa.DateTime(timezone=True)),
        sa.Column("paid_at", sa.DateTime(timezone=True)),
        sa.Column("bukku_invoice_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_invoices_organization_id", "invoices", ["organization_id"])

    op.create_table(
        "bookings",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", pg.UUID(as_uuid=True), sa.ForeignKey("clients.id", ondelete="SET NULL")),
        sa.Column("lead_id", pg.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("attendee_email", sa.String(320)),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", booking_status, nullable=False, server_default="confirmed"),
        sa.Column("calcom_booking_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_bookings_organization_id", "bookings", ["organization_id"])
    op.create_index("ix_bookings_start_time", "bookings", ["start_time"])
    op.create_index("ix_bookings_calcom_booking_id", "bookings", ["calcom_booking_id"])

    op.create_table(
        "social_posts",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("status", social_post_status, nullable=False, server_default="draft"),
        sa.Column("metrics", pg.JSONB),
        sa.Column("metricool_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_social_posts_organization_id", "social_posts", ["organization_id"])

    op.create_table(
        "automations",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000)),
        sa.Column("trigger", pg.JSONB, nullable=False),
        sa.Column("actions", pg.JSONB, nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("run_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_automations_organization_id", "automations", ["organization_id"])

    op.create_table(
        "webhook_events",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL")),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("event_type", sa.String(100)),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("payload", pg.JSONB, nullable=False),
        sa.Column("status", webhook_event_status, nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_error", sa.String(2000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source", "external_id", name="uq_webhook_source_external"),
    )
    op.create_index("ix_webhook_events_organization_id", "webhook_events", ["organization_id"])
    op.create_index("ix_webhook_events_source", "webhook_events", ["source"])

    op.create_table(
        "sync_logs",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL")),
        sa.Column("integration", sa.String(50), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50)),
        sa.Column("entity_id", sa.String(255)),
        sa.Column("duration_ms", sa.Integer),
        sa.Column("status", sync_log_status, nullable=False),
        sa.Column("request_payload", pg.JSONB),
        sa.Column("response_payload", pg.JSONB),
        sa.Column("error_message", sa.String(2000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sync_logs_organization_id", "sync_logs", ["organization_id"])
    op.create_index("ix_sync_logs_integration", "sync_logs", ["integration"])


def downgrade() -> None:
    op.drop_table("sync_logs")
    op.drop_table("webhook_events")
    op.drop_table("automations")
    op.drop_table("social_posts")
    op.drop_table("bookings")
    op.drop_table("invoices")
    op.drop_table("clients")
    op.drop_table("leads")
    op.drop_table("users")
    op.drop_table("organizations")

    for e in (
        sync_log_status,
        webhook_event_status,
        social_post_status,
        booking_status,
        invoice_status,
        client_status,
        lead_status,
        user_role,
    ):
        e.drop(op.get_bind(), checkfirst=True)
