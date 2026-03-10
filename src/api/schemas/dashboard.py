"""Dashboard schemas."""

from __future__ import annotations

from pydantic import BaseModel

from src.api.schemas.post import PostResponse
from src.api.schemas.theme import ThemeResponse


class StatsResponse(BaseModel):
    scheduled_this_week: int
    pending_review: int
    published_this_month: int
    failed: int


class UpcomingResponse(BaseModel):
    posts: list[PostResponse]


class AttentionResponse(BaseModel):
    pending_review: list[PostResponse]
    failed: list[PostResponse]


class DashboardResponse(BaseModel):
    stats: StatsResponse
    upcoming: list[PostResponse]
    pending_review: list[PostResponse]
    failed: list[PostResponse]
    active_themes: list[ThemeResponse]
