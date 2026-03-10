"""Calendar schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.api.schemas.post import PostResponse


class CalendarDayResponse(BaseModel):
    date: str  # YYYY-MM-DD
    posts: list[PostResponse]


class RescheduleItem(BaseModel):
    post_id: UUID
    new_scheduled_at: datetime


class RescheduleRequest(BaseModel):
    items: list[RescheduleItem]
