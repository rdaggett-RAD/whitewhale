import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.base import TimestampMixin, UUIDMixin


class WwLinkedinAccount(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ww_linkedin_accounts"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_users.id")
    )
    unipile_account_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    linkedin_member_id: Mapped[str | None] = mapped_column(Text)
    linkedin_name: Mapped[str | None] = mapped_column(Text)
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, server_default="active", default="active")
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    connection_count: Mapped[int] = mapped_column(Integer, server_default="0", default=0)


class WwLinkedinConnection(UUIDMixin, Base):
    __tablename__ = "ww_linkedin_connections"
    __table_args__ = (UniqueConstraint("linkedin_account_id", "linkedin_member_id"),)

    linkedin_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_linkedin_accounts.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    # Person data
    linkedin_member_id: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(Text)
    headline: Mapped[str | None] = mapped_column(Text)
    current_title: Mapped[str | None] = mapped_column(Text)
    current_company: Mapped[str | None] = mapped_column(Text)
    current_company_domain: Mapped[str | None] = mapped_column(Text)
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    profile_image_url: Mapped[str | None] = mapped_column(Text)
    # Connection metadata
    connected_since: Mapped[date | None] = mapped_column(Date)
    connection_degree: Mapped[int] = mapped_column(Integer, server_default="1", default=1)
    # Synced state
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class WwConnectionOpportunity(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ww_connection_opportunities"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    connection_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_linkedin_connections.id")
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_companies.id")
    )
    white_whale_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_white_whales.id")
    )
    # Opportunity classification
    opportunity_type: Mapped[str] = mapped_column(Text, nullable=False)
    opportunity_summary: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[int | None] = mapped_column(Integer)
    # Status
    status: Mapped[str] = mapped_column(Text, server_default="new", default="new")
