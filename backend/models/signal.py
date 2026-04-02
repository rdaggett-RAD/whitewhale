import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import UUIDMixin


class WwCompany(UUIDMixin, Base):
    __tablename__ = "ww_companies"
    __table_args__ = (UniqueConstraint("tenant_id", "domain"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str | None] = mapped_column(Text)
    linkedin_company_id: Mapped[str | None] = mapped_column(Text)
    linkedin_company_url: Mapped[str | None] = mapped_column(Text)
    apollo_org_id: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(Text)
    employee_count: Mapped[int | None] = mapped_column(Integer)
    stage: Mapped[str | None] = mapped_column(Text)
    geo: Mapped[str | None] = mapped_column(Text)
    white_whale_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_white_whales.id")
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class WwSignal(UUIDMixin, Base):
    __tablename__ = "ww_signals"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_companies.id")
    )
    white_whale_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_white_whales.id")
    )
    # Signal data
    signal_type: Mapped[str] = mapped_column(Text, nullable=False)
    signal_source: Mapped[str | None] = mapped_column(Text)
    raw_data: Mapped[dict | None] = mapped_column(JSONB)
    signal_summary: Mapped[str] = mapped_column(Text, nullable=False)
    signal_url: Mapped[str | None] = mapped_column(Text)
    signal_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Classification (Claude output)
    service_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_service_categories.id")
    )
    classification_confidence: Mapped[int | None] = mapped_column(Integer)
    classification_rationale: Mapped[str | None] = mapped_column(Text)
    urgency_score: Mapped[int | None] = mapped_column(Integer)
    # Connection overlay
    has_connection: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    connection_count: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
    opportunity_type: Mapped[str | None] = mapped_column(Text)
    # Lifecycle
    status: Mapped[str] = mapped_column(Text, server_default="new", default="new")
    dismissed_reason: Mapped[str | None] = mapped_column(Text)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class WwSignalConnection(UUIDMixin, Base):
    __tablename__ = "ww_signal_connections"

    signal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_signals.id", ondelete="CASCADE"), nullable=False
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_linkedin_connections.id"), nullable=False
    )
    match_type: Mapped[str | None] = mapped_column(Text)
    opportunity_type: Mapped[str | None] = mapped_column(Text)
    flagged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class WwSignalDedup(UUIDMixin, Base):
    __tablename__ = "ww_signal_dedup"
    __table_args__ = (UniqueConstraint("tenant_id", "signal_fingerprint"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    company_domain: Mapped[str] = mapped_column(Text, nullable=False)
    signal_type: Mapped[str] = mapped_column(Text, nullable=False)
    signal_fingerprint: Mapped[str] = mapped_column(Text, nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
