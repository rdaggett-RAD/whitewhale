import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.base import TimestampMixin, UUIDMixin


class WwIcpConfig(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ww_icp_configs"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, server_default="Default ICP")
    # Company filters
    industries: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    company_stages: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    employee_min: Mapped[int | None] = mapped_column(Integer)
    employee_max: Mapped[int | None] = mapped_column(Integer)
    geos: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    keywords_include: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    keywords_exclude: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    # Signal preferences
    watch_job_postings: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    watch_exec_changes: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    watch_news_pr: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    watch_funding: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    watch_acquisitions: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    # Scoring
    min_signal_score: Mapped[int] = mapped_column(Integer, server_default="60", default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)


class WwServiceCategory(UUIDMixin, Base):
    __tablename__ = "ww_service_categories"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    signal_patterns: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", default=0)


class WwSignalRoutingRule(UUIDMixin, Base):
    __tablename__ = "ww_signal_routing_rules"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    signal_type: Mapped[str] = mapped_column(Text, nullable=False)
    service_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_service_categories.id")
    )
    default_persona_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    default_angle_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    default_voice_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    default_channel: Mapped[str] = mapped_column(Text, server_default="email", default="email")
    auto_queue_draft: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    priority: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
