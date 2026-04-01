"""initial schema

Revision ID: 58c79e3bc02f
Revises:
Create Date: 2026-04-01 23:03:14.845800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "58c79e3bc02f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Tenants & Users ---
    op.create_table(
        "ww_tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), unique=True, nullable=False),
        sa.Column("plan", sa.Text(), server_default="starter"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ww_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.Text(), unique=True, nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("full_name", sa.Text()),
        sa.Column("role", sa.Text(), server_default="member"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- ICP Configuration ---
    op.create_table(
        "ww_icp_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False, server_default="Default ICP"),
        sa.Column("industries", postgresql.ARRAY(sa.Text())),
        sa.Column("company_stages", postgresql.ARRAY(sa.Text())),
        sa.Column("employee_min", sa.Integer()),
        sa.Column("employee_max", sa.Integer()),
        sa.Column("geos", postgresql.ARRAY(sa.Text())),
        sa.Column("keywords_include", postgresql.ARRAY(sa.Text())),
        sa.Column("keywords_exclude", postgresql.ARRAY(sa.Text())),
        sa.Column("watch_job_postings", sa.Boolean(), server_default="true"),
        sa.Column("watch_exec_changes", sa.Boolean(), server_default="true"),
        sa.Column("watch_news_pr", sa.Boolean(), server_default="true"),
        sa.Column("watch_funding", sa.Boolean(), server_default="true"),
        sa.Column("watch_acquisitions", sa.Boolean(), server_default="true"),
        sa.Column("min_signal_score", sa.Integer(), server_default="60"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ww_service_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("signal_patterns", postgresql.ARRAY(sa.Text())),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
    )

    op.create_table(
        "ww_signal_routing_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("signal_type", sa.Text(), nullable=False),
        sa.Column("service_category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_service_categories.id")),
        sa.Column("default_persona_id", postgresql.UUID(as_uuid=True)),
        sa.Column("default_angle_id", postgresql.UUID(as_uuid=True)),
        sa.Column("default_voice_id", postgresql.UUID(as_uuid=True)),
        sa.Column("default_channel", sa.Text(), server_default="email"),
        sa.Column("auto_queue_draft", sa.Boolean(), server_default="true"),
        sa.Column("priority", sa.Integer(), server_default="0"),
    )

    # --- White Whales ---
    op.create_table(
        "ww_white_whales",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_users.id")),
        sa.Column("company_name", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text()),
        sa.Column("linkedin_company_id", sa.Text()),
        sa.Column("linkedin_company_url", sa.Text()),
        sa.Column("apollo_org_id", sa.Text()),
        sa.Column("why_they_matter", sa.Text()),
        sa.Column("ideal_entry_point", sa.Text()),
        sa.Column("internal_notes", sa.Text()),
        sa.Column("status", sa.Text(), server_default="cold"),
        sa.Column("priority_tier", sa.Integer(), server_default="2"),
        sa.Column("signal_sensitivity", sa.Text(), server_default="all"),
        sa.Column("custom_signal_types", postgresql.ARRAY(sa.Text())),
        sa.Column("last_signal_at", sa.DateTime(timezone=True)),
        sa.Column("last_contacted_at", sa.DateTime(timezone=True)),
        sa.Column("last_replied_at", sa.DateTime(timezone=True)),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ww_whale_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("whale_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_white_whales.id", ondelete="CASCADE"), nullable=False),
        sa.Column("full_name", sa.Text()),
        sa.Column("title", sa.Text()),
        sa.Column("email", sa.Text()),
        sa.Column("linkedin_url", sa.Text()),
        sa.Column("linkedin_member_id", sa.Text()),
        sa.Column("connection_degree", sa.Integer()),
        sa.Column("connected_via", sa.Text()),
        sa.Column("is_connection", sa.Boolean(), server_default="false"),
        sa.Column("connection_synced_at", sa.DateTime(timezone=True)),
        sa.Column("source", sa.Text()),
        sa.Column("is_primary", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- Companies & Signals ---
    op.create_table(
        "ww_companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_name", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text()),
        sa.Column("linkedin_company_id", sa.Text()),
        sa.Column("linkedin_company_url", sa.Text()),
        sa.Column("apollo_org_id", sa.Text()),
        sa.Column("industry", sa.Text()),
        sa.Column("employee_count", sa.Integer()),
        sa.Column("stage", sa.Text()),
        sa.Column("geo", sa.Text()),
        sa.Column("white_whale_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_white_whales.id")),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "domain"),
    )

    op.create_table(
        "ww_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_companies.id")),
        sa.Column("white_whale_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_white_whales.id")),
        sa.Column("signal_type", sa.Text(), nullable=False),
        sa.Column("signal_source", sa.Text()),
        sa.Column("raw_data", postgresql.JSONB()),
        sa.Column("signal_summary", sa.Text(), nullable=False),
        sa.Column("signal_url", sa.Text()),
        sa.Column("signal_date", sa.DateTime(timezone=True)),
        sa.Column("service_category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_service_categories.id")),
        sa.Column("classification_confidence", sa.Integer()),
        sa.Column("classification_rationale", sa.Text()),
        sa.Column("urgency_score", sa.Integer()),
        sa.Column("has_connection", sa.Boolean(), server_default="false"),
        sa.Column("connection_count", sa.Integer(), server_default="0"),
        sa.Column("opportunity_type", sa.Text()),
        sa.Column("status", sa.Text(), server_default="new"),
        sa.Column("dismissed_reason", sa.Text()),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "ww_signal_dedup",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_domain", sa.Text(), nullable=False),
        sa.Column("signal_type", sa.Text(), nullable=False),
        sa.Column("signal_fingerprint", sa.Text(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "signal_fingerprint"),
    )

    # --- LinkedIn ---
    op.create_table(
        "ww_linkedin_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_users.id")),
        sa.Column("unipile_account_id", sa.Text(), unique=True, nullable=False),
        sa.Column("linkedin_member_id", sa.Text()),
        sa.Column("linkedin_name", sa.Text()),
        sa.Column("linkedin_url", sa.Text()),
        sa.Column("status", sa.Text(), server_default="active"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True)),
        sa.Column("connection_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ww_linkedin_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("linkedin_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_linkedin_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("linkedin_member_id", sa.Text(), nullable=False),
        sa.Column("full_name", sa.Text()),
        sa.Column("headline", sa.Text()),
        sa.Column("current_title", sa.Text()),
        sa.Column("current_company", sa.Text()),
        sa.Column("current_company_domain", sa.Text()),
        sa.Column("linkedin_url", sa.Text()),
        sa.Column("profile_image_url", sa.Text()),
        sa.Column("connected_since", sa.Date()),
        sa.Column("connection_degree", sa.Integer(), server_default="1"),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("linkedin_account_id", "linkedin_member_id"),
    )

    op.create_table(
        "ww_signal_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_signals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_linkedin_connections.id"), nullable=False),
        sa.Column("match_type", sa.Text()),
        sa.Column("opportunity_type", sa.Text()),
        sa.Column("flagged_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ww_connection_opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_linkedin_connections.id")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_companies.id")),
        sa.Column("white_whale_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_white_whales.id")),
        sa.Column("opportunity_type", sa.Text(), nullable=False),
        sa.Column("opportunity_summary", sa.Text()),
        sa.Column("confidence_score", sa.Integer()),
        sa.Column("status", sa.Text(), server_default="new"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- Prompt System ---
    op.create_table(
        "ww_prompt_personas",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("sender_name", sa.Text(), nullable=False),
        sa.Column("sender_title", sa.Text(), nullable=False),
        sa.Column("sender_company", sa.Text(), nullable=False),
        sa.Column("sender_bio_short", sa.Text()),
        sa.Column("signature_block", sa.Text()),
        sa.Column("is_default", sa.Boolean(), server_default="false"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ww_prompt_value_props",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_service_categories.id")),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("one_liner", sa.Text(), nullable=False),
        sa.Column("proof_points", postgresql.JSONB()),
        sa.Column("ideal_for", sa.Text()),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
    )

    op.create_table(
        "ww_prompt_angles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("best_for_signals", postgresql.ARRAY(sa.Text())),
        sa.Column("best_for_channels", postgresql.ARRAY(sa.Text())),
        sa.Column("is_default", sa.Boolean(), server_default="false"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
    )

    op.create_table(
        "ww_prompt_voices",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("words_to_avoid", postgresql.ARRAY(sa.Text())),
        sa.Column("words_to_use", postgresql.ARRAY(sa.Text())),
        sa.Column("example_sentences", postgresql.ARRAY(sa.Text())),
        sa.Column("is_default", sa.Boolean(), server_default="false"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
    )

    op.create_table(
        "ww_prompt_constraints",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("max_words", sa.Integer()),
        sa.Column("max_chars", sa.Integer()),
        sa.Column("forbidden_phrases", postgresql.ARRAY(sa.Text())),
        sa.Column("required_elements", postgresql.ARRAY(sa.Text())),
        sa.Column("output_format", sa.Text(), server_default="json"),
    )

    # --- Action Queue ---
    op.create_table(
        "ww_action_queue",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_signals.id")),
        sa.Column("white_whale_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_white_whales.id")),
        sa.Column("whale_contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_whale_contacts.id")),
        sa.Column("connection_opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_connection_opportunities.id")),
        sa.Column("contact_name", sa.Text()),
        sa.Column("contact_title", sa.Text()),
        sa.Column("contact_company", sa.Text()),
        sa.Column("contact_email", sa.Text()),
        sa.Column("contact_linkedin_url", sa.Text()),
        sa.Column("contact_linkedin_member_id", sa.Text()),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("persona_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_prompt_personas.id")),
        sa.Column("angle_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_prompt_angles.id")),
        sa.Column("voice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_prompt_voices.id")),
        sa.Column("draft_subject", sa.Text()),
        sa.Column("draft_body", sa.Text()),
        sa.Column("draft_connection_note", sa.Text()),
        sa.Column("draft_generated_at", sa.DateTime(timezone=True)),
        sa.Column("draft_generation_count", sa.Integer(), server_default="1"),
        sa.Column("status", sa.Text(), server_default="pending"),
        sa.Column("urgency", sa.Text(), server_default="normal"),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_users.id")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("send_error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ww_sequences",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("steps", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ww_sequence_enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_sequences.id")),
        sa.Column("whale_contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_whale_contacts.id")),
        sa.Column("current_step", sa.Integer(), server_default="0"),
        sa.Column("status", sa.Text(), server_default="active"),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("next_step_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    # --- Delivery ---
    op.create_table(
        "ww_delivery_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("digest_enabled", sa.Boolean(), server_default="true"),
        sa.Column("digest_frequency", sa.Text(), server_default="daily"),
        sa.Column("digest_email", sa.Text()),
        sa.Column("digest_time", sa.Time(), server_default="08:00"),
        sa.Column("digest_timezone", sa.Text(), server_default="America/Chicago"),
        sa.Column("auto_approve", sa.Boolean(), server_default="false"),
        sa.Column("from_name", sa.Text()),
        sa.Column("from_email", sa.Text()),
        sa.Column("linkedin_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_linkedin_accounts.id")),
    )

    op.create_table(
        "ww_sent_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action_queue_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ww_action_queue.id")),
        sa.Column("channel", sa.Text()),
        sa.Column("to_name", sa.Text()),
        sa.Column("to_email", sa.Text()),
        sa.Column("to_linkedin_member_id", sa.Text()),
        sa.Column("subject", sa.Text()),
        sa.Column("body_preview", sa.Text()),
        sa.Column("provider_message_id", sa.Text()),
        sa.Column("status", sa.Text()),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("ww_sent_log")
    op.drop_table("ww_delivery_settings")
    op.drop_table("ww_sequence_enrollments")
    op.drop_table("ww_sequences")
    op.drop_table("ww_action_queue")
    op.drop_table("ww_prompt_constraints")
    op.drop_table("ww_prompt_voices")
    op.drop_table("ww_prompt_angles")
    op.drop_table("ww_prompt_value_props")
    op.drop_table("ww_prompt_personas")
    op.drop_table("ww_connection_opportunities")
    op.drop_table("ww_signal_connections")
    op.drop_table("ww_linkedin_connections")
    op.drop_table("ww_linkedin_accounts")
    op.drop_table("ww_signal_dedup")
    op.drop_table("ww_signals")
    op.drop_table("ww_companies")
    op.drop_table("ww_whale_contacts")
    op.drop_table("ww_white_whales")
    op.drop_table("ww_signal_routing_rules")
    op.drop_table("ww_service_categories")
    op.drop_table("ww_icp_configs")
    op.drop_table("ww_users")
    op.drop_table("ww_tenants")
