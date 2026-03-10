"""Theme endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.api.deps import get_db
from src.api.schemas.common import PaginatedResponse
from src.api.schemas.theme import (
    BatchGenerateRequest,
    ThemeCreateRequest,
    ThemeResponse,
    ThemeUpdateRequest,
)
from src.db.models import ApiUser
from src.db.repo import PostRepo
from src.db.theme_repo import ThemeRepo
from src.workers.task_queue import enqueue_task

router = APIRouter()


async def _theme_response(theme, repo: ThemeRepo) -> ThemeResponse:
    stats = await repo.get_theme_stats(theme.id)
    resp = ThemeResponse.model_validate(theme)
    resp.post_count = stats["post_count"]
    resp.published_count = stats["published_count"]
    resp.next_publish_at = stats["next_publish_at"]
    return resp


@router.get("", response_model=PaginatedResponse[ThemeResponse])
async def list_themes(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
    track: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = ThemeRepo(db)
    themes, total = await repo.list_themes(track=track, status=status_filter, limit=limit, offset=offset)
    items = [await _theme_response(t, repo) for t in themes]
    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
async def create_theme(
    body: ThemeCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = ThemeRepo(db)
    theme = await repo.create_theme(**body.model_dump())
    return await _theme_response(theme, repo)


@router.get("/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = ThemeRepo(db)
    theme = await repo.get_theme(theme_id)
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    return await _theme_response(theme, repo)


@router.patch("/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    theme_id: uuid.UUID,
    body: ThemeUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = ThemeRepo(db)
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    theme = await repo.update_theme(theme_id, **update_data)
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    return await _theme_response(theme, repo)


@router.delete("/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_theme(
    theme_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = ThemeRepo(db)
    if not await repo.delete_theme(theme_id):
        raise HTTPException(status_code=404, detail="Theme not found")


@router.post("/{theme_id}/batch-generate", response_model=list[dict])
async def batch_generate(
    theme_id: uuid.UUID,
    body: BatchGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    theme_repo = ThemeRepo(db)
    theme = await theme_repo.get_theme(theme_id)
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    post_repo = PostRepo(db)
    created = []

    for i in range(body.count):
        scheduled_at = None
        if body.date_from:
            scheduled_at = body.date_from + timedelta(days=i)
            if body.cadence_time:
                try:
                    parts = body.cadence_time.split(":")
                    if len(parts) != 2:
                        raise ValueError("Invalid format")
                    h, m = int(parts[0]), int(parts[1])
                    if not (0 <= h < 24 and 0 <= m < 60):
                        raise ValueError("Invalid hour/minute range")
                    scheduled_at = scheduled_at.replace(hour=h, minute=m, second=0)
                except (ValueError, IndexError):
                    raise HTTPException(
                        status_code=400,
                        detail="cadence_time must be in HH:MM format (00:00-23:59)",
                    )

        post = await post_repo.create_post(
            track=theme.track,
            language="en",
            text_content="",
            post_type=body.post_type,
            generation_params={
                "post_type": "free_topic",
                "topic": f"{theme.name} #{i + 1}",
                "media_style": body.media_style,
                "theme_context": theme.generation_context or "",
            },
            status="draft",
            theme_id=theme.id,
            scheduled_at=scheduled_at,
        )

        task_id = await enqueue_task("regenerate_post", {"post_id": str(post.id)})
        created.append({"post_id": str(post.id), "task_id": task_id})

    return created
