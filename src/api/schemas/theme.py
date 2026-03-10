"""Theme schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ThemeResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    status: str
    target_platforms: list[str] = []
    cadence_type: str
    cadence_rule: dict[str, Any] = {}
    start_date: datetime | None = None
    end_date: datetime | None = None
    generation_context: str | None = None
    default_prompt_template: str | None = None
    color: str
    template_id: UUID | None = None
    track: str
    created_at: datetime
    updated_at: datetime
    # Computed
    post_count: int = 0
    published_count: int = 0
    next_publish_at: datetime | None = None

    model_config = {"from_attributes": True}


class ThemeCreateRequest(BaseModel):
    name: str
    description: str | None = None
    status: str = "draft"
    target_platforms: list[str] = []
    cadence_type: str = "manual"
    cadence_rule: dict[str, Any] = {}
    start_date: datetime | None = None
    end_date: datetime | None = None
    generation_context: str | None = None
    default_prompt_template: str | None = None
    color: str = "#3B82F6"
    template_id: UUID | None = None
    track: str = "eu"


class ThemeUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    target_platforms: list[str] | None = None
    cadence_type: str | None = None
    cadence_rule: dict[str, Any] | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    generation_context: str | None = None
    default_prompt_template: str | None = None
    color: str | None = None
    template_id: UUID | None = None


class BatchGenerateRequest(BaseModel):
    count: int = 5
    date_from: datetime | None = None
    date_to: datetime | None = None
    cadence_time: str = "09:00"
    post_type: str = "text"
    media_style: str = "text"  # text | ai | card
