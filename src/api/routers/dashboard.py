"""Dashboard endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.api.deps import get_db
from src.api.schemas.dashboard import AttentionResponse, StatsResponse, UpcomingResponse
from src.api.schemas.post import PostResponse
from src.api.schemas.theme import ThemeResponse
from src.db.models import ApiUser
from src.db.repo import PostRepo
from src.db.theme_repo import ThemeRepo

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    week_end = week_start + timedelta(days=7)
    scheduled_this_week = await repo.count_by_status(
        ["approved", "scheduled"],
        date_from=week_start,
        date_to=week_end,
        date_field="scheduled_at",
    )
    pending_review = await repo.count_by_status(["review"])
    published_this_month = await repo.count_by_status(["published"], date_from=month_start)
    failed = await repo.count_by_status(["failed"])

    return StatsResponse(
        scheduled_this_week=scheduled_this_week,
        pending_review=pending_review,
        published_this_month=published_this_month,
        failed=failed,
    )


@router.get("/upcoming", response_model=UpcomingResponse)
async def get_upcoming(
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    now = datetime.now(timezone.utc)
    posts = await repo.get_posts_for_calendar(start=now, end=now + timedelta(hours=48))
    return UpcomingResponse(posts=[PostResponse.model_validate(p) for p in posts])


@router.get("/attention", response_model=AttentionResponse)
async def get_attention(
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    pending = await repo.get_posts_in_review()
    failed_posts, _ = await repo.get_posts_filtered(limit=20, status="failed")
    return AttentionResponse(
        pending_review=[PostResponse.model_validate(p) for p in pending],
        failed=[PostResponse.model_validate(p) for p in failed_posts],
    )
