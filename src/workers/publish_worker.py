"""Background worker that publishes scheduled posts when they're due.

Run: python -m src.workers.publish_worker
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

import structlog
from aiogram import Bot

from src.config.settings import settings
from src.db.models import engine, Base, async_session
from src.db.repo import PostRepo, PublicationRepo
from src.publishing.telegram_publisher import TelegramPublisher
from src.admin_bot.formatters.post_formatter import format_post_published

log = structlog.get_logger()


async def publish_post(post_id: uuid.UUID) -> None:
    """Publish a single post to all configured platforms."""
    if not settings.tg_bot_token:
        log.warning("publish_skipped", reason="tg_bot_token is empty", post_id=str(post_id))
        return

    bot = Bot(token=settings.tg_bot_token)

    try:
        async with async_session() as session:
            repo = PostRepo(session)
            pub_repo = PublicationRepo(session)
            post = await repo.get_post(post_id)

            if not post or post.status != "approved":
                log.warning("post_not_publishable", post_id=str(post_id), status=post.status if post else None)
                return

            # Mark as publishing
            await repo.update_post_status(post_id, "publishing")

            # --- Telegram Channel ---
            publisher = TelegramPublisher(bot=bot)
            try:
                if post.media_type == "image" and post.media_urls:
                    result = await publisher.publish_photo(
                        post.media_urls[0],
                        caption=post.text_content,
                    )
                elif post.media_type == "video" and post.media_urls:
                    result = await publisher.publish_video(
                        post.media_urls[0],
                        caption=post.text_content,
                    )
                else:
                    result = await publisher.publish_text(post.text_content or "")

                await pub_repo.create_publication(
                    post_id=post.id,
                    platform="telegram",
                    platform_text=post.text_content,
                    status="published",
                )

                await repo.update_post_status(post.id, "published")

                # Notify admin
                confirmation = format_post_published(post, "Telegram", result.get("platform_url"))
                await bot.send_message(
                    chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
                    text=confirmation,
                    parse_mode="HTML",
                )

                log.info("scheduled_post_published", post_id=str(post.id))

                # Try Instagram if configured and post has image
                if post.media_type == "image" and post.media_urls and settings.instagram_access_token:
                    from src.admin_bot.handlers.review import _try_publish_instagram
                    await _try_publish_instagram(bot, post, pub_repo)

            except Exception as e:
                log.error("scheduled_publish_failed", post_id=str(post.id), error=str(e))

                await pub_repo.create_publication(
                    post_id=post.id,
                    platform="telegram",
                    status="failed",
                )
                await repo.update_post_status(post.id, "failed")

                await bot.send_message(
                    chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
                    text=f"❌ Scheduled publish failed for <code>{str(post.id)[:8]}</code>:\n{e}",
                    parse_mode="HTML",
                )

    finally:
        await bot.session.close()


async def check_and_publish() -> int:
    """Check for due posts and publish them. Returns count published."""
    now = datetime.now(timezone.utc)
    count = 0

    async with async_session() as session:
        repo = PostRepo(session)
        due_posts = await repo.get_approved_posts_due(now)

    for post in due_posts:
        try:
            await publish_post(post.id)
            count += 1
        except Exception as e:
            log.error("publish_cycle_error", post_id=str(post.id), error=str(e))

    return count


async def run():
    """Run publish worker as a background task."""
    log.info("publish_worker_started")
    try:
        while True:
            published = await check_and_publish()
            if published:
                log.info("publish_cycle_complete", count=published)

            # Check every 30 seconds
            await asyncio.sleep(30)
    except asyncio.CancelledError:
        log.info("publish_worker_stopping")


async def main():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
    )

    log.info("publish_worker_started")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await run()


if __name__ == "__main__":
    asyncio.run(main())
