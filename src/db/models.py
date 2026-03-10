from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config.settings import settings


# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSONB,
        list[str]: ARRAY(String),
    }


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ContentSource(Base):
    __tablename__ = "content_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # article, supplement_profile, manual, rss
    title: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    language: Mapped[str] = mapped_column(String(5), default="en")
    track: Mapped[str] = mapped_column(String(5), default="eu")
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    theme_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("themes.id", ondelete="SET NULL"), index=True
    )
    track: Mapped[str] = mapped_column(String(5), nullable=False)
    language: Mapped[str] = mapped_column(String(5), nullable=False)

    # Content
    post_type: Mapped[str] = mapped_column(String(50), default="text")  # text, image, video, carousel
    text_content: Mapped[str | None] = mapped_column(Text)
    text_prompt: Mapped[str | None] = mapped_column(Text)
    text_model: Mapped[str | None] = mapped_column(String(100))

    # Media
    media_type: Mapped[str | None] = mapped_column(String(20))  # none, image, video, carousel
    media_urls: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    media_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Scheduling
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Status: draft → review → approved → publishing → published → failed → rejected
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    approved_by: Mapped[str | None] = mapped_column(String(100))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Admin bot message tracking
    review_message_id: Mapped[int | None] = mapped_column(Integer)
    review_chat_id: Mapped[int | None] = mapped_column(Integer)

    # Generation params
    generation_params: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PostPublication(Base):
    __tablename__ = "post_publications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(30), nullable=False)  # telegram, instagram_post, instagram_reel, youtube_short

    # Platform-specific content
    platform_text: Mapped[str | None] = mapped_column(Text)
    platform_media_url: Mapped[str | None] = mapped_column(Text)

    # Status: pending → queued → publishing → published → failed → manual
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    platform_post_id: Mapped[str | None] = mapped_column(String(200))
    platform_url: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Manual posting support
    manual_message_id: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    track: Mapped[str] = mapped_column(String(5), nullable=False)
    platform: Mapped[str] = mapped_column(String(30), nullable=False)
    account_name: Mapped[str | None] = mapped_column(String(200))
    credentials: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ContentTemplate(Base):
    __tablename__ = "content_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    track: Mapped[str] = mapped_column(String(5), nullable=False)
    platform: Mapped[str] = mapped_column(String(30), nullable=False)
    template_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    target_platforms: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    cadence_type: Mapped[str] = mapped_column(String(20), default="manual")
    cadence_rule: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    generation_context: Mapped[str | None] = mapped_column(Text)
    default_prompt_template: Mapped[str | None] = mapped_column(Text)
    color: Mapped[str] = mapped_column(String(20), default="#3B82F6")
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    track: Mapped[str] = mapped_column(String(5), default="eu")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ApiUser(Base):
    __tablename__ = "api_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AppSetting(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
