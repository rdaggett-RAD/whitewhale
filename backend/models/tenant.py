import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from models.base import TimestampMixin, UUIDMixin


class WwTenant(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ww_tenants"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(Text, server_default="starter", default="starter")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)

    users: Mapped[list["WwUser"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")


class WwUser(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ww_users"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text, server_default="member", default="member")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)

    tenant: Mapped["WwTenant"] = relationship(back_populates="users")
