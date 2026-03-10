from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Post, Theme


class ThemeRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_theme(
        self,
        name: str,
        track: str = "eu",
        description: str | None = None,
        status: str = "draft",
        target_platforms: list[str] | None = None,
        cadence_type: str = "manual",
        cadence_rule: dict[str, Any] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        generation_context: str | None = None,
        default_prompt_template: str | None = None,
        color: str = "#3B82F6",
        template_id: uuid.UUID | None = None,
    ) -> Theme:
        theme = Theme(
            name=name,
            track=track,
            description=description,
            status=status,
            target_platforms=target_platforms or [],
            cadence_type=cadence_type,
            cadence_rule=cadence_rule or {},
            start_date=start_date,
            end_date=end_date,
            generation_context=generation_context,
            default_prompt_template=default_prompt_template,
            color=color,
            template_id=template_id,
        )
        self.session.add(theme)
        await self.session.commit()
        await self.session.refresh(theme)
        return theme

    async def get_theme(self, theme_id: uuid.UUID) -> Theme | None:
        return await self.session.get(Theme, theme_id)

    async def list_themes(
        self,
        track: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Theme], int]:
        base = select(Theme)
        if track:
            base = base.where(Theme.track == track)
        if status:
            base = base.where(Theme.status == status)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.session.execute(count_stmt)).scalar() or 0

        stmt = base.order_by(Theme.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def update_theme(self, theme_id: uuid.UUID, **kwargs: Any) -> Theme | None:
        theme = await self.get_theme(theme_id)
        if not theme:
            return None
        for key, value in kwargs.items():
            if hasattr(theme, key) and key not in ("id", "created_at"):
                setattr(theme, key, value)
        theme.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(theme)
        return theme

    async def delete_theme(self, theme_id: uuid.UUID) -> bool:
        theme = await self.get_theme(theme_id)
        if not theme:
            return False
        theme.status = "completed"
        theme.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True

    async def get_theme_stats(self, theme_id: uuid.UUID) -> dict[str, Any]:
        """Return computed stats: post_count, published_count, next_publish_at."""
        post_count_stmt = (
            select(func.count()).select_from(Post).where(Post.theme_id == theme_id)
        )
        published_count_stmt = (
            select(func.count())
            .select_from(Post)
            .where(Post.theme_id == theme_id, Post.status == "published")
        )
        next_publish_stmt = (
            select(func.min(Post.scheduled_at))
            .where(
                Post.theme_id == theme_id,
                Post.status == "approved",
                Post.scheduled_at > datetime.now(timezone.utc),
            )
        )

        post_count = (await self.session.execute(post_count_stmt)).scalar() or 0
        published_count = (await self.session.execute(published_count_stmt)).scalar() or 0
        next_publish_at = (await self.session.execute(next_publish_stmt)).scalar()

        return {
            "post_count": post_count,
            "published_count": published_count,
            "next_publish_at": next_publish_at,
        }
