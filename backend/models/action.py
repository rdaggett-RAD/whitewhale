import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin, UUIDMixin


class WwActionQueue(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ww_action_queue"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    signal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_signals.id")
    )
    white_whale_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_white_whales.id")
    )
    whale_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_whale_contacts.id")
    )
    connection_opportunity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_connection_opportunities.id")
    )
    # Contact (resolved at queue time)
    contact_name: Mapped[str | None] = mapped_column(Text)
    contact_title: Mapped[str | None] = mapped_column(Text)
    contact_company: Mapped[str | None] = mapped_column(Text)
    contact_email: Mapped[str | None] = mapped_column(Text)
    contact_linkedin_url: Mapped[str | None] = mapped_column(Text)
    contact_linkedin_member_id: Mapped[str | None] = mapped_column(Text)
    # Draft config
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    persona_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_prompt_personas.id")
    )
    angle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_prompt_angles.id")
    )
    voice_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_prompt_voices.id")
    )
    # Draft content (Claude output)
    draft_subject: Mapped[str | None] = mapped_column(Text)
    draft_body: Mapped[str | None] = mapped_column(Text)
    draft_connection_note: Mapped[str | None] = mapped_column(Text)
    draft_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    draft_generation_count: Mapped[int] = mapped_column(Integer, server_default="1", default=1)
    # Status
    status: Mapped[str] = mapped_column(Text, server_default="pending", default="pending")
    urgency: Mapped[str] = mapped_column(Text, server_default="normal", default="normal")
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_users.id")
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    send_error: Mapped[str | None] = mapped_column(Text)


class WwSequence(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ww_sequences"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    steps: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)


class WwSequenceEnrollment(UUIDMixin, Base):
    __tablename__ = "ww_sequence_enrollments"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    sequence_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_sequences.id")
    )
    whale_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_whale_contacts.id")
    )
    current_step: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
    status: Mapped[str] = mapped_column(Text, server_default="active", default="active")
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    next_step_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
