import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.base import TimestampMixin, UUIDMixin


class WwPromptPersona(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ww_prompt_personas"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    sender_name: Mapped[str] = mapped_column(Text, nullable=False)
    sender_title: Mapped[str] = mapped_column(Text, nullable=False)
    sender_company: Mapped[str] = mapped_column(Text, nullable=False)
    sender_bio_short: Mapped[str | None] = mapped_column(Text)
    signature_block: Mapped[str | None] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)


class WwPromptValueProp(UUIDMixin, Base):
    __tablename__ = "ww_prompt_value_props"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    service_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_service_categories.id")
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    one_liner: Mapped[str] = mapped_column(Text, nullable=False)
    proof_points: Mapped[dict | None] = mapped_column(JSONB)
    ideal_for: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)


class WwPromptAngle(UUIDMixin, Base):
    __tablename__ = "ww_prompt_angles"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    best_for_signals: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    best_for_channels: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    is_default: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)


class WwPromptVoice(UUIDMixin, Base):
    __tablename__ = "ww_prompt_voices"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    words_to_avoid: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    words_to_use: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    example_sentences: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    is_default: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)


class WwPromptConstraint(UUIDMixin, Base):
    __tablename__ = "ww_prompt_constraints"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ww_tenants.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    max_words: Mapped[int | None] = mapped_column(Integer)
    max_chars: Mapped[int | None] = mapped_column(Integer)
    forbidden_phrases: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    required_elements: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    output_format: Mapped[str] = mapped_column(Text, server_default="json", default="json")
