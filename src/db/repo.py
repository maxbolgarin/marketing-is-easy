from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ContentSource, Post, PostPublication


class PostRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(
        self,
        track: str,
        language: str,
        text_content: str,
        post_type: str = "text",
        source_id: uuid.UUID | None = None,
        text_prompt: str | None = None,
        text_model: str | None = None,
        media_type: str | None = None,
        media_urls: list[str] | None = None,
        generation_params: dict | None = None,
        status: str = "review",
    ) -> Post:
        post = Post(
            track=track,
            language=language,
            post_type=post_type,
            text_content=text_content,
            source_id=source_id,
            text_prompt=text_prompt,
            text_model=text_model,
            media_type=media_type,
            media_urls=media_urls,
            generation_params=generation_params or {},
            status=status,
        )
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def get_post(self, post_id: uuid.UUID) -> Post | None:
        return await self.session.get(Post, post_id)

    async def update_post_status(
        self,
        post_id: uuid.UUID,
        status: str,
        approved_by: str | None = None,
    ) -> Post | None:
        post = await self.get_post(post_id)
        if not post:
            return None
        post.status = status
        if approved_by:
            post.approved_by = approved_by
            post.approved_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def update_post_media(
        self,
        post_id: uuid.UUID,
        media_type: str,
        media_urls: list[str],
    ) -> Post | None:
        post = await self.get_post(post_id)
        if not post:
            return None
        post.media_type = media_type
        post.media_urls = media_urls
        post.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def update_post_text(self, post_id: uuid.UUID, text_content: str) -> Post | None:
        post = await self.get_post(post_id)
        if not post:
            return None
        post.text_content = text_content
        post.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def update_post_schedule(self, post_id: uuid.UUID, scheduled_at: datetime) -> Post | None:
        post = await self.get_post(post_id)
        if not post:
            return None
        post.scheduled_at = scheduled_at
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def set_review_message(self, post_id: uuid.UUID, message_id: int, chat_id: int) -> None:
        post = await self.get_post(post_id)
        if post:
            post.review_message_id = message_id
            post.review_chat_id = chat_id
            await self.session.commit()

    async def get_approved_posts_due(self, now: datetime | None = None) -> list[Post]:
        """Get posts that are approved and due for publishing."""
        now = now or datetime.now(timezone.utc)
        stmt = (
            select(Post)
            .where(Post.status == "approved")
            .where(Post.scheduled_at <= now)
            .order_by(Post.scheduled_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_posts_in_review(self, track: str | None = None) -> list[Post]:
        stmt = select(Post).where(Post.status == "review").order_by(Post.created_at.desc())
        if track:
            stmt = stmt.where(Post.track == track)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_post_generation_params(
        self, post_id: uuid.UUID, params: dict
    ) -> Post | None:
        post = await self.get_post(post_id)
        if not post:
            return None
        post.generation_params = {**(post.generation_params or {}), **params}
        post.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def get_recent_posts(self, limit: int = 20, track: str | None = None) -> list[Post]:
        stmt = select(Post).order_by(Post.created_at.desc()).limit(limit)
        if track:
            stmt = stmt.where(Post.track == track)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class PublicationRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_publication(
        self,
        post_id: uuid.UUID,
        platform: str,
        platform_text: str | None = None,
        platform_media_url: str | None = None,
        status: str = "pending",
        platform_post_id: str | None = None,
        platform_url: str | None = None,
    ) -> PostPublication:
        from datetime import datetime, timezone as _tz
        pub = PostPublication(
            post_id=post_id,
            platform=platform,
            platform_text=platform_text,
            platform_media_url=platform_media_url,
            status=status,
            platform_post_id=platform_post_id,
            platform_url=platform_url,
            published_at=datetime.now(_tz.utc) if status == "published" else None,
        )
        self.session.add(pub)
        await self.session.commit()
        await self.session.refresh(pub)
        return pub

    async def get_pending_publications(self, platform: str | None = None) -> list[PostPublication]:
        stmt = select(PostPublication).where(PostPublication.status == "queued")
        if platform:
            stmt = stmt.where(PostPublication.platform == platform)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_publication_status(
        self,
        pub_id: uuid.UUID,
        status: str,
        platform_post_id: str | None = None,
        platform_url: str | None = None,
        error_message: str | None = None,
    ) -> PostPublication | None:
        pub = await self.session.get(PostPublication, pub_id)
        if not pub:
            return None
        pub.status = status
        if platform_post_id:
            pub.platform_post_id = platform_post_id
        if platform_url:
            pub.platform_url = platform_url
        if error_message:
            pub.error_message = error_message
        if status == "published":
            pub.published_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(pub)
        return pub

    async def get_publications_for_post(self, post_id: uuid.UUID) -> list[PostPublication]:
        stmt = select(PostPublication).where(PostPublication.post_id == post_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ContentSourceRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_source(
        self,
        source_type: str,
        title: str,
        body: str | None = None,
        metadata: dict | None = None,
        language: str = "en",
        track: str = "eu",
    ) -> ContentSource:
        source = ContentSource(
            source_type=source_type,
            title=title,
            body=body,
            metadata_=metadata or {},
            language=language,
            track=track,
        )
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return source

    async def get_unused_sources(self, track: str, limit: int = 10) -> list[ContentSource]:
        stmt = (
            select(ContentSource)
            .where(ContentSource.track == track)
            .where(ContentSource.used_count == 0)
            .order_by(ContentSource.created_at)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_used(self, source_id: uuid.UUID) -> None:
        source = await self.session.get(ContentSource, source_id)
        if source:
            source.used_count += 1
            await self.session.commit()
