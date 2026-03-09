"""Background worker for content generation tasks.

Run: python -m src.workers.generation_worker
"""

from __future__ import annotations

import asyncio
import uuid

import structlog

from src.config.settings import settings
from src.db.models import engine, Base, async_session
from src.db.repo import PostRepo
from src.content_engine.generators.text_generator import TextGenerator
from src.content_engine.prompts.post_prompts import PROMPT_TYPES
from src.workers.task_queue import dequeue_task, close_redis

log = structlog.get_logger()


async def handle_regenerate(payload: dict) -> None:
    """Regenerate a post's text content."""
    post_id = uuid.UUID(payload["post_id"])

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.get_post(post_id)
        if not post:
            log.error("regenerate_post_not_found", post_id=str(post_id))
            return

        gen_params = post.generation_params or {}
        post_type = gen_params.get("post_type", "free_topic")
        topic = gen_params.get("topic", "")

        # Rebuild prompt
        prompt_fn = PROMPT_TYPES.get(post_type, PROMPT_TYPES["free_topic"])
        kwargs = {
            "brand_name": settings.brand_name,
            "tone": settings.content_tone,
            "language": "English",
        }

        if post_type == "supplement_spotlight":
            kwargs["supplement_name"] = topic
            kwargs["supplement_info"] = topic
        elif post_type in ("educational_tip", "free_topic"):
            kwargs["topic"] = topic
        elif post_type == "myth_busting":
            kwargs["myth"] = topic
        elif post_type == "research_highlight":
            kwargs["finding"] = topic

        prompt = prompt_fn(**kwargs)
        generator = TextGenerator()
        text, metadata = await generator.generate(prompt, temperature=0.8)  # slightly higher for variety

        await repo.update_post_text(post_id, text)
        await repo.update_post_status(post_id, "review")

        log.info("post_regenerated", post_id=str(post_id))

        # Notify admin bot
        from aiogram import Bot

        bot = Bot(token=settings.tg_bot_token)
        try:
            from src.admin_bot.handlers.review import send_post_for_review

            await send_post_for_review(bot, post_id)
        finally:
            await bot.session.close()


async def handle_generate_image(payload: dict) -> None:
    """Regenerate the image for an existing post."""
    post_id = uuid.UUID(payload["post_id"])
    media_style = payload.get("media_style", "ai")  # 'ai' or 'card'

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.get_post(post_id)
        if not post:
            log.error("generate_image_post_not_found", post_id=str(post_id))
            return

        gen_params = post.generation_params or {}
        topic = gen_params.get("topic", "")

        if media_style == "ai":
            from src.content_engine.generators.image_generator import ImageGenerator
            img_gen = ImageGenerator()
            image_prompt = (
                f"Professional health and wellness marketing image for: {topic}. "
                "Clean, modern, minimal, no text in the image, photorealistic or artistic illustration style."
            )
            local_path = await img_gen.generate(image_prompt, aspect_ratio="1:1")
        else:
            from src.content_engine.generators.image_composer import ImageComposer
            composer = ImageComposer()
            local_path = composer.compose_tip_card(
                title=topic[:80],
                body=(post.text_content or "")[:300],
            )

        await repo.update_post_media(post_id, "image", [local_path])
        await repo.update_post_status(post_id, "review")

        log.info("image_regenerated", post_id=str(post_id), path=local_path)

    # Notify admin
    from aiogram import Bot

    bot = Bot(token=settings.tg_bot_token)
    try:
        from src.admin_bot.handlers.review import send_post_for_review
        await send_post_for_review(bot, post_id)
    finally:
        await bot.session.close()


async def handle_generate_video(payload: dict) -> None:
    """Generate a video for a post via the full video pipeline."""
    post_id = uuid.UUID(payload["post_id"])

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.get_post(post_id)
        if not post:
            log.error("generate_video_post_not_found", post_id=str(post_id))
            return

        gen_params = post.generation_params or {}
        topic = gen_params.get("topic", "")
        content = post.text_content or topic

    from src.content_engine.generators.video.pipeline import generate_video_pipeline

    video_path, cover_path, caption = await generate_video_pipeline(
        post_id=post.id,
        title=topic,
        content=content,
        language=post.language,
        track=post.track,
    )

    async with async_session() as session:
        repo = PostRepo(session)
        await repo.update_post_media(
            post_id, "video", [str(video_path), str(cover_path)]
        )
        post = await repo.get_post(post_id)
        if post:
            params = post.generation_params or {}
            params["video_caption"] = caption
            params["video_path"] = str(video_path)
            params["cover_path"] = str(cover_path)
            post.generation_params = params
            await session.commit()
        await repo.update_post_status(post_id, "review")

    log.info("video_generated", post_id=str(post_id), video=str(video_path))

    # Notify admin bot
    from aiogram import Bot

    bot = Bot(token=settings.tg_bot_token)
    try:
        from src.admin_bot.handlers.review import send_post_for_review

        await send_post_for_review(bot, post_id)
    finally:
        await bot.session.close()


TASK_HANDLERS = {
    "regenerate_post": handle_regenerate,
    "generate_image": handle_generate_image,
    "generate_video": handle_generate_video,
}


async def main():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
    )

    log.info("generation_worker_started")

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        while True:
            task = await dequeue_task(timeout=5)
            if task is None:
                continue

            task_type = task.get("type")
            payload = task.get("payload", {})

            handler = TASK_HANDLERS.get(task_type)
            if handler:
                try:
                    await handler(payload)
                except Exception as e:
                    log.error("task_failed", task_type=task_type, error=str(e))
            else:
                log.warning("unknown_task_type", task_type=task_type)

    except asyncio.CancelledError:
        log.info("generation_worker_stopping")
    finally:
        await close_redis()


if __name__ == "__main__":
    asyncio.run(main())
