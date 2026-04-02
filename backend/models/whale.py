import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from models.base import UUIDMixin


class WwWhiteWhale(UUIDMixin, Base):
    __tablename__ = "ww_white_whales"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_users.id")
    )
    # Company identity
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str | None] = mapped_column(Text)
    linkedin_company_id: Mapped[str | None] = mapped_column(Text)
    linkedin_company_url: Mapped[str | None] = mapped_column(Text)
    apollo_org_id: Mapped[str | None] = mapped_column(Text)
    # Context
    why_they_matter: Mapped[str | None] = mapped_column(Text)
    ideal_entry_point: Mapped[str | None] = mapped_column(Text)
    internal_notes: Mapped[str | None] = mapped_column(Text)
    # Status
    status: Mapped[str] = mapped_column(Text, server_default="cold", default="cold")
    priority_tier: Mapped[int] = mapped_column(Integer, server_default="2", default=2)
    # Signal settings
    signal_sensitivity: Mapped[str] = mapped_column(Text, server_default="all", default="all")
    custom_signal_types: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    # Tracking
    last_signal_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    contacts: Mapped[list["WwWhaleContact"]] = relationship(
        back_populates="whale", cascade="all, delete-orphan"
    )


class WwWhaleContact(UUIDMixin, Base):
    __tablename__ = "ww_whale_contacts"

    whale_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_white_whales.id", ondelete="CASCADE"), nullable=False
    )
    # Person
    full_name: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    linkedin_member_id: Mapped[str | None] = mapped_column(Text)
    # Connection status
    connection_degree: Mapped[int | None] = mapped_column(Integer)
    connected_via: Mapped[str | None] = mapped_column(Text)
    is_connection: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    connection_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Source
    source: Mapped[str | None] = mapped_column(Text)
    is_primary: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    whale: Mapped["WwWhiteWhale"] = relationship(back_populates="contacts")
