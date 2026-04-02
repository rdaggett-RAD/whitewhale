import uuid
from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, Time, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import UUIDMixin


class WwDeliverySettings(UUIDMixin, Base):
    __tablename__ = "ww_delivery_settings"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    digest_enabled: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    digest_frequency: Mapped[str] = mapped_column(Text, server_default="daily", default="daily")
    digest_email: Mapped[str | None] = mapped_column(Text)
    digest_time: Mapped[time] = mapped_column(Time, server_default="08:00", default=time(8, 0))
    digest_timezone: Mapped[str] = mapped_column(
        Text, server_default="America/Chicago", default="America/Chicago"
    )
    auto_approve: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    from_name: Mapped[str | None] = mapped_column(Text)
    from_email: Mapped[str | None] = mapped_column(Text)
    linkedin_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_linkedin_accounts.id")
    )


class WwSentLog(UUIDMixin, Base):
    __tablename__ = "ww_sent_log"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    action_queue_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_action_queue.id")
    )
    channel: Mapped[str | None] = mapped_column(Text)
    to_name: Mapped[str | None] = mapped_column(Text)
    to_email: Mapped[str | None] = mapped_column(Text)
    to_linkedin_member_id: Mapped[str | None] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(Text)
    body_preview: Mapped[str | None] = mapped_column(Text)
    provider_message_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
