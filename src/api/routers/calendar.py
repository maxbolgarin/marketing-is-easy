"""Calendar endpoints."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.api.deps import get_db
from src.api.schemas.calendar import CalendarDayResponse, RescheduleRequest
from src.api.schemas.common import MessageResponse
from src.api.schemas.post import PostResponse
from src.db.models import ApiUser
from src.db.repo import PostRepo

router = APIRouter()


@router.get("", response_model=list[CalendarDayResponse])
async def get_calendar(
    start: datetime = Query(...),
    end: datetime = Query(...),
    track: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    posts = await repo.get_posts_for_calendar(start=start, end=end, track=track)

    by_day: dict[str, list] = defaultdict(list)
    for post in posts:
        day = post.scheduled_at.strftime("%Y-%m-%d")
        by_day[day].append(PostResponse.model_validate(post))

    return [CalendarDayResponse(date=day, posts=items) for day, items in sorted(by_day.items())]


@router.patch("/reschedule", response_model=MessageResponse)
async def reschedule(
    body: RescheduleRequest,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    for item in body.items:
        post = await repo.get_post(item.post_id)
        if not post:
            raise HTTPException(status_code=404, detail=f"Post {item.post_id} not found")
        await repo.update_post_schedule(item.post_id, item.new_scheduled_at)
    return MessageResponse(message=f"Rescheduled {len(body.items)} post(s)")
