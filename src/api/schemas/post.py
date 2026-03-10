"""Post schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class PublicationResponse(BaseModel):
    id: UUID
    post_id: UUID
    platform: str
    platform_text: str | None = None
    platform_media_url: str | None = None
    status: str
    published_at: datetime | None = None
    platform_post_id: str | None = None
    platform_url: str | None = None
    error_message: str | None = None
    retry_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    id: UUID
    source_id: UUID | None = None
    theme_id: UUID | None = None
    track: str
    language: str
    post_type: str
    text_content: str | None = None
    text_prompt: str | None = None
    text_model: str | None = None
    media_type: str | None = None
    media_urls: list[str] | None = None
    media_metadata: dict[str, Any] = {}
    scheduled_at: datetime | None = None
    status: str
    generation_params: dict[str, Any] = {}
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    publications: list[PublicationResponse] = []

    model_config = {"from_attributes": True}


class PostCreateRequest(BaseModel):
    theme_id: UUID | None = None
    track: str = "eu"
    language: str = "en"
    post_type: str = "text"
    text_content: str | None = None
    text_prompt: str | None = None
    media_type: str | None = None
    scheduled_at: datetime | None = None
    generation_params: dict[str, Any] = {}


class PostUpdateRequest(BaseModel):
    theme_id: UUID | None = None
    text_content: str | None = None
    text_prompt: str | None = None
    media_type: str | None = None
    media_urls: list[str] | None = None
    scheduled_at: datetime | None = None
    status: str | None = None
    generation_params: dict[str, Any] | None = None


class GenerateTextRequest(BaseModel):
    prompt: str | None = None
    model: str | None = None


class GenerateImageRequest(BaseModel):
    prompt: str | None = None
    media_style: str = "ai"  # ai | card


class ApproveRequest(BaseModel):
    scheduled_at: datetime | None = None


class VariantCreateRequest(BaseModel):
    platform: str
    platform_text: str | None = None
    platform_media_url: str | None = None


class VariantUpdateRequest(BaseModel):
    platform_text: str | None = None
    platform_media_url: str | None = None
