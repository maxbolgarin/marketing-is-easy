"""Handlers for content generation commands in admin chat."""

from __future__ import annotations

import structlog
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from src.config.settings import settings
from src.admin_bot.handlers.review import is_admin, send_post_for_review
from src.admin_bot.keyboards.inline import post_type_keyboard, media_type_keyboard
from src.admin_bot.formatters.post_formatter import format_post_list
from src.db.models import async_session
from src.db.repo import PostRepo
from src.content_engine.generators.text_generator import TextGenerator
from src.content_engine.prompts.post_prompts import PROMPT_TYPES

log = structlog.get_logger()

router = Router()


class GenerateStates(StatesGroup):
    waiting_for_topic = State()
    waiting_for_media_type = State()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@router.message(Command("start"))
async def cmd_start(message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("Not authorized.")
        return

    await message.reply(
        "🤖 <b>BioMaxing Social Marketing Bot</b>\n\n"
        "Commands:\n"
        "/generate — Generate a new post\n"
        "/queue — Show posts in review\n"
        "/recent — Show recent posts\n"
        "/help — Show this message",
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    if not is_admin(message.from_user.id):
        return
    await cmd_start(message)


@router.message(Command("generate"))
async def cmd_generate(message: Message):
    """Start the content generation flow."""
    if not is_admin(message.from_user.id):
        await message.reply("Not authorized.")
        return

    await message.reply(
        "What type of post do you want to generate?",
        reply_markup=post_type_keyboard(),
    )


@router.message(Command("queue"))
async def cmd_queue(message: Message):
    """Show posts currently in review."""
    if not is_admin(message.from_user.id):
        return

    async with async_session() as session:
        repo = PostRepo(session)
        posts = await repo.get_posts_in_review(track=settings.track)

    if not posts:
        await message.reply("No posts in review queue.")
        return

    await message.reply(format_post_list(posts), parse_mode="HTML")


@router.message(Command("recent"))
async def cmd_recent(message: Message):
    """Show recent posts."""
    if not is_admin(message.from_user.id):
        return

    async with async_session() as session:
        repo = PostRepo(session)
        posts = await repo.get_recent_posts(limit=15, track=settings.track)

    await message.reply(format_post_list(posts), parse_mode="HTML")


# ---------------------------------------------------------------------------
# Generation flow callbacks
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("gen:"))
async def on_select_post_type(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    post_type = callback.data.split(":", 1)[1]
    await state.update_data(post_type=post_type)
    await state.set_state(GenerateStates.waiting_for_topic)

    prompts = {
        "supplement_spotlight": "Send me the supplement name (and optionally key info):",
        "educational_tip": "Send me the topic for the tip:",
        "myth_busting": "Send me the myth to bust (and optionally the reality):",
        "research_highlight": "Send me the research finding to highlight:",
        "free_topic": "Send me the topic and any instructions:",
    }

    await callback.message.reply(prompts.get(post_type, "Send me the topic:"))
    await callback.answer()


@router.message(GenerateStates.waiting_for_topic)
async def on_topic_received(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("Generation cancelled.")
        return

    data = await state.get_data()
    post_type = data.get("post_type", "free_topic")
    topic = message.text

    # Store topic, ask for media type next
    await state.update_data(topic=topic)
    await state.set_state(GenerateStates.waiting_for_media_type)

    await message.reply(
        "What format should this post be?",
        reply_markup=media_type_keyboard(post_type),
    )


@router.callback_query(F.data.startswith("media_type:"))
async def on_media_type_selected(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    # media_type:{style}:{post_type}  e.g. media_type:ai:educational_tip
    parts = callback.data.split(":", 2)
    if len(parts) != 3:
        await callback.answer("Invalid selection")
        return

    _, media_style, post_type = parts  # text | ai | card

    # Only proceed if we are in the right FSM state (or state was lost after restart)
    data = await state.get_data()
    topic = data.get("topic", "")
    await state.clear()

    await callback.answer()

    if media_style == "video":
        status_msg = await callback.message.reply(
            "⏳ Starting video generation pipeline...\n"
            "This may take 5–30 minutes. You'll be notified when ready for review."
        )
        try:
            await _generate_video_task(
                bot=callback.bot,
                status_msg=status_msg,
                post_type=post_type,
                topic=topic,
            )
        except Exception as e:
            log.error("video_generation_failed", error=str(e), post_type=post_type)
            await status_msg.edit_text(f"❌ Video generation failed: {e}")
        return

    status_msg = await callback.message.reply(
        "⏳ Generating post..." if media_style == "text"
        else "⏳ Generating text and image (this may take 15–30 s)..."
    )

    try:
        await _generate_and_send(
            bot=callback.bot,
            status_msg=status_msg,
            post_type=post_type,
            topic=topic,
            media_style=media_style,
        )
    except Exception as e:
        log.error("generation_failed", error=str(e), post_type=post_type, media_style=media_style)
        await status_msg.edit_text(f"❌ Generation failed: {e}")


async def _generate_and_send(bot, status_msg, post_type: str, topic: str, media_style: str) -> None:
    """Core generation logic shared by the callback handler."""
    # --- Build text prompt ---
    prompt_fn = PROMPT_TYPES.get(post_type, PROMPT_TYPES["free_topic"])
    kwargs = {
        "brand_name": settings.brand_name,
        "tone": settings.content_tone,
        "language": "English",
    }

    if post_type == "supplement_spotlight":
        kwargs["supplement_name"] = topic
        kwargs["supplement_info"] = topic
    elif post_type == "educational_tip":
        kwargs["topic"] = topic
    elif post_type == "myth_busting":
        kwargs["myth"] = topic
    elif post_type == "research_highlight":
        kwargs["finding"] = topic
    elif post_type == "free_topic":
        kwargs["topic"] = topic

    prompt = prompt_fn(**kwargs)

    # --- Generate text ---
    generator = TextGenerator()
    text, metadata = await generator.generate(prompt)

    # --- Generate image if requested ---
    media_type: str | None = None
    media_urls: list[str] | None = None

    if media_style in ("ai", "card"):
        media_type = "image"
        if media_style == "ai":
            from src.content_engine.generators.image_generator import ImageGenerator
            img_gen = ImageGenerator()
            image_prompt = (
                f"Professional health and wellness marketing image for: {topic}. "
                "Clean, modern, minimal, no text in the image, photorealistic or artistic illustration style."
            )
            local_path = await img_gen.generate(image_prompt, aspect_ratio="1:1")
            media_urls = [local_path]
        else:  # branded card
            from src.content_engine.generators.image_composer import ImageComposer
            composer = ImageComposer()
            # Use first ~120 chars as title, rest as body
            title = topic[:80]
            body = text[:300]
            local_path = composer.compose_tip_card(title=title, body=body)
            media_urls = [local_path]

    # --- Save to DB ---
    post_db_type = "image" if media_type == "image" else "text"
    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.create_post(
            track=settings.track,
            language=settings.language,
            text_content=text,
            post_type=post_db_type,
            text_prompt=prompt.user[:2000],
            text_model=metadata.get("model"),
            media_type=media_type,
            media_urls=media_urls,
            generation_params={
                "post_type": post_type,
                "topic": topic,
                "media_style": media_style,
                "metadata": metadata,
            },
            status="review",
        )

    await status_msg.delete()
    await send_post_for_review(bot, post.id)
    log.info("post_generated", post_id=str(post.id), post_type=post_type, media_style=media_style)


async def _generate_video_task(bot, status_msg, post_type: str, topic: str) -> None:
    """Generate text content and enqueue a video generation task."""
    # Generate text content first (used as source material for the video script)
    prompt_fn = PROMPT_TYPES.get(post_type, PROMPT_TYPES["free_topic"])
    kwargs = {
        "brand_name": settings.brand_name,
        "tone": settings.content_tone,
        "language": "English",
    }

    if post_type == "supplement_spotlight":
        kwargs["supplement_name"] = topic
        kwargs["supplement_info"] = topic
    elif post_type == "educational_tip":
        kwargs["topic"] = topic
    elif post_type == "myth_busting":
        kwargs["myth"] = topic
    elif post_type == "research_highlight":
        kwargs["finding"] = topic
    elif post_type == "free_topic":
        kwargs["topic"] = topic

    prompt = prompt_fn(**kwargs)
    generator = TextGenerator()
    text, metadata = await generator.generate(prompt)

    # Save post to DB with status "generating"
    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.create_post(
            track=settings.track,
            language=settings.language,
            text_content=text,
            post_type="video",
            text_prompt=prompt.user[:2000],
            text_model=metadata.get("model"),
            media_type="video",
            generation_params={
                "post_type": post_type,
                "topic": topic,
                "media_style": "video",
                "metadata": metadata,
            },
            status="draft",
        )

    # Enqueue video generation on the dedicated video queue
    from src.workers.task_queue import enqueue_video_task

    task_id = await enqueue_video_task({"post_id": str(post.id)})

    await status_msg.edit_text(
        f"🎬 <b>Video generation queued</b>\n\n"
        f"Post ID: <code>{str(post.id)[:8]}</code>\n"
        f"Task ID: <code>{task_id[:8]}</code>\n\n"
        f"You'll be notified when the video is ready for review.",
        parse_mode="HTML",
    )
    log.info("video_task_enqueued", post_id=str(post.id), task_id=task_id)
