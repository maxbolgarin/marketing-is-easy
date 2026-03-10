"""Handlers for post review flow: approve, reject, edit, schedule, regenerate."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import structlog
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.config.settings import settings
from src.db.models import async_session
from src.db.repo import PostRepo, PublicationRepo
from src.admin_bot.formatters.post_formatter import format_post_preview, format_post_published
from src.admin_bot.keyboards.inline import (
    review_keyboard,
    image_review_keyboard,
    video_review_keyboard,
    schedule_keyboard,
    confirm_publish_keyboard,
)
from src.publishing.telegram_publisher import TelegramPublisher

log = structlog.get_logger()

router = Router()


# ---------------------------------------------------------------------------
# FSM states for edit flow
# ---------------------------------------------------------------------------

class EditStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_feedback = State()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_user_ids


def parse_post_id(callback_data: str) -> uuid.UUID | None:
    """Extract post UUID from callback_data like 'approve_now:uuid'."""
    try:
        _, pid = callback_data.split(":", 1)
        return uuid.UUID(pid)
    except (ValueError, AttributeError):
        return None


# ---------------------------------------------------------------------------
# Send post for review
# ---------------------------------------------------------------------------

def _review_keyboard_for_post(post):
    """Return the appropriate review keyboard based on post media type."""
    if post.media_type == "video":
        return video_review_keyboard(post.id)
    if post.media_type == "image":
        return image_review_keyboard(post.id)
    return review_keyboard(post.id)


async def send_post_for_review(bot: Bot, post_id: uuid.UUID) -> None:
    """Send a post to the admin chat for review."""
    from pathlib import Path

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.get_post(post_id)
        if not post:
            log.error("post_not_found_for_review", post_id=str(post_id))
            return

        preview = format_post_preview(post)
        keyboard = _review_keyboard_for_post(post)

        if post.media_type == "video" and post.media_urls:
            video_path = Path(post.media_urls[0])
            if video_path.exists():
                caption = preview[:1020] + "…" if len(preview) > 1024 else preview
                msg = await bot.send_video(
                    chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
                    video=FSInputFile(video_path),
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
            else:
                msg = await bot.send_message(
                    chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
                    text=f"⚠️ Video file missing: {video_path}\n\n{preview}",
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
        elif post.media_type == "image" and post.media_urls:
            media_path = Path(post.media_urls[0])
            if media_path.exists():
                # Caption is limited to 1024 chars for photos in Telegram
                caption = preview[:1020] + "…" if len(preview) > 1024 else preview
                msg = await bot.send_photo(
                    chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
                    photo=FSInputFile(media_path),
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
            else:
                # File missing — send text with warning
                msg = await bot.send_message(
                    chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
                    text=f"⚠️ Image file missing: {media_path}\n\n{preview}",
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
        else:
            msg = await bot.send_message(
                chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
                text=preview,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

        # Track which message shows this post
        await repo.set_review_message(post.id, msg.message_id, msg.chat.id)
        log.info("post_sent_for_review", post_id=str(post.id), message_id=msg.message_id)


# ---------------------------------------------------------------------------
# Callback handlers
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("approve_now:"))
async def on_approve_now(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    post_id = parse_post_id(callback.data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    await callback.answer("Publishing...")

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.update_post_status(
            post_id, "approved", approved_by=callback.from_user.full_name
        )
        if not post:
            await callback.message.edit_text("Post not found.")
            return

        # Publish to Telegram channel
        publisher = TelegramPublisher(bot=callback.bot)
        try:
            if post.media_type == "video" and post.media_urls:
                video_caption = (post.generation_params or {}).get(
                    "video_caption", post.text_content or ""
                )
                result = await publisher.publish_video(
                    post.media_urls[0], caption=video_caption
                )
            elif post.media_type == "image" and post.media_urls:
                result = await publisher.publish_photo(
                    post.media_urls[0], caption=post.text_content
                )
            else:
                result = await publisher.publish_text(post.text_content or "")

            # Record Telegram publication
            pub_repo = PublicationRepo(session)
            await pub_repo.create_publication(
                post_id=post.id,
                platform="telegram",
                platform_text=post.text_content,
                status="published",
            )

            await repo.update_post_status(post.id, "published")

            # Update admin message
            confirmation = format_post_published(
                post, "Telegram", result.get("platform_url")
            )
            await callback.message.edit_text(confirmation, parse_mode="HTML")

            log.info("post_published", post_id=str(post.id), platform="telegram")

            # Try Instagram if configured and post has an image
            if post.media_type == "image" and post.media_urls and settings.instagram_access_token:
                await _try_publish_instagram(callback.bot, post, pub_repo)

            # Try YouTube if configured and post is a video
            if post.media_type == "video" and post.media_urls and settings.youtube_refresh_token:
                await _try_publish_youtube(callback.bot, post, pub_repo)

        except Exception as e:
            log.error("publish_failed", post_id=str(post.id), error=str(e))
            await repo.update_post_status(post.id, "failed")
            await callback.message.edit_text(
                f"❌ Publishing failed: {e}\n\nPost ID: <code>{str(post.id)[:8]}</code>",
                parse_mode="HTML",
                reply_markup=_review_keyboard_for_post(post),
            )


@router.callback_query(F.data.startswith("schedule:"))
async def on_schedule(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    post_id = parse_post_id(callback.data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=schedule_keyboard(post_id))


@router.callback_query(F.data.startswith("sched_"))
async def on_schedule_time(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    data = callback.data
    post_id = parse_post_id(data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    now = datetime.now(timezone.utc)

    if data.startswith("sched_1h:"):
        scheduled = now + timedelta(hours=1)
    elif data.startswith("sched_3h:"):
        scheduled = now + timedelta(hours=3)
    elif data.startswith("sched_tom9:"):
        tomorrow = now + timedelta(days=1)
        scheduled = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    elif data.startswith("sched_tom18:"):
        tomorrow = now + timedelta(days=1)
        scheduled = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)
    else:
        await callback.answer("Unknown schedule option")
        return

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.update_post_schedule(post_id, scheduled)
        if post:
            await repo.update_post_status(
                post_id, "approved", approved_by=callback.from_user.full_name
            )
            time_str = scheduled.strftime("%Y-%m-%d %H:%M UTC")
            await callback.message.edit_text(
                f"✅ <b>Scheduled!</b>\n\n"
                f"Will publish at: {time_str}\n"
                f"Post ID: <code>{str(post.id)[:8]}</code>",
                parse_mode="HTML",
            )
            log.info("post_scheduled", post_id=str(post.id), scheduled_at=time_str)
        else:
            await callback.answer("Post not found")


@router.callback_query(F.data.startswith("back_review:"))
async def on_back_to_review(callback: CallbackQuery):
    post_id = parse_post_id(callback.data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.get_post(post_id)
        if post:
            preview = format_post_preview(post)
            await callback.message.edit_text(
                preview, parse_mode="HTML", reply_markup=review_keyboard(post.id)
            )
    await callback.answer()


@router.callback_query(F.data.startswith("reject:"))
async def on_reject(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    post_id = parse_post_id(callback.data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    async with async_session() as session:
        repo = PostRepo(session)
        await repo.update_post_status(post_id, "rejected")

    await callback.message.edit_text(
        f"🚫 <b>Rejected</b>\nPost ID: <code>{str(post_id)[:8]}</code>",
        parse_mode="HTML",
    )
    await callback.answer("Post rejected")
    log.info("post_rejected", post_id=str(post_id))


@router.callback_query(F.data.startswith("edit:"))
async def on_edit(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    post_id = parse_post_id(callback.data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    await state.set_state(EditStates.waiting_for_text)
    await state.update_data(editing_post_id=str(post_id))

    await callback.message.reply(
        "✏️ Send me the edited text for this post.\n"
        "Send the full replacement text, or reply with /cancel to abort."
    )
    await callback.answer()


@router.message(EditStates.waiting_for_text)
async def on_edit_text_received(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("Edit cancelled.")
        return

    data = await state.get_data()
    post_id = uuid.UUID(data["editing_post_id"])

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.update_post_text(post_id, message.text)

    await state.clear()

    if post:
        preview = format_post_preview(post)
        await message.reply(
            f"✅ Text updated!\n\n{preview}",
            parse_mode="HTML",
            reply_markup=review_keyboard(post.id),
        )
    else:
        await message.reply("Post not found.")


@router.callback_query(F.data.startswith("regenerate:"))
async def on_regenerate(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    post_id = parse_post_id(callback.data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    await callback.answer("Regenerating...")

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.get_post(post_id)
        if not post or not post.generation_params:
            await callback.message.reply("Cannot regenerate: missing generation parameters.")
            return

    # Enqueue regeneration task via Redis
    from src.workers.task_queue import enqueue_task

    await enqueue_task(
        "regenerate_post",
        {"post_id": str(post_id)},
    )

    await callback.message.reply(
        f"🔄 Regeneration queued for post <code>{str(post_id)[:8]}</code>",
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("regen_image:"))
async def on_regen_image(callback: CallbackQuery):
    """Regenerate only the image for an image post."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    post_id = parse_post_id(callback.data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    await callback.answer("Regenerating image...")

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.get_post(post_id)
        if not post or not post.generation_params:
            await callback.message.reply("Cannot regenerate: missing generation parameters.")
            return

    from src.workers.task_queue import enqueue_task

    await enqueue_task(
        "generate_image",
        {
            "post_id": str(post_id),
            "media_style": post.generation_params.get("media_style", "ai"),
        },
    )

    await callback.message.reply(
        f"🖼 Image regeneration queued for post <code>{str(post_id)[:8]}</code>",
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("plat_ig:"))
async def on_publish_instagram(callback: CallbackQuery):
    """Manually trigger Instagram publishing for a post."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    post_id = parse_post_id(callback.data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    await callback.answer("Publishing to Instagram...")

    async with async_session() as session:
        repo = PostRepo(session)
        pub_repo = PublicationRepo(session)
        post = await repo.get_post(post_id)
        if not post:
            await callback.message.reply("Post not found.")
            return

        await _try_publish_instagram(callback.bot, post, pub_repo)

    await callback.message.reply(
        f"Instagram publishing initiated for post <code>{str(post_id)[:8]}</code>",
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("manual_posted:"))
async def on_manual_posted(callback: CallbackQuery):
    """Admin confirms they posted manually on a platform."""
    try:
        _, pub_id_str = callback.data.split(":", 1)
        pub_id = uuid.UUID(pub_id_str)
    except (ValueError, AttributeError):
        await callback.answer("Invalid publication ID")
        return

    async with async_session() as session:
        pub_repo = PublicationRepo(session)
        await pub_repo.update_publication_status(pub_id, "manual")

    await callback.message.edit_text(
        "✅ <b>Marked as posted manually.</b>",
        parse_mode="HTML",
    )
    await callback.answer("Marked as posted!")
    log.info("manual_posted_confirmed", pub_id=str(pub_id))


@router.callback_query(F.data.startswith("manual_posted_post:"))
async def on_manual_posted_by_post(callback: CallbackQuery):
    """Admin confirms manual post when we only have post_id (no pub record yet)."""
    try:
        _, post_id_str = callback.data.split(":", 1)
        post_id = uuid.UUID(post_id_str)
    except (ValueError, AttributeError):
        await callback.answer("Invalid post ID")
        return

    async with async_session() as session:
        pub_repo = PublicationRepo(session)
        pub = await pub_repo.create_publication(
            post_id=post_id,
            platform="instagram_post",
            status="manual",
        )

    await callback.message.edit_text(
        "✅ <b>Marked as posted manually on Instagram.</b>",
        parse_mode="HTML",
    )
    await callback.answer("Marked as posted!")
    log.info("manual_posted_confirmed_by_post", post_id=str(post_id))


# ---------------------------------------------------------------------------
# Instagram publishing helper
# ---------------------------------------------------------------------------

async def _try_publish_instagram(bot, post, pub_repo: PublicationRepo) -> None:
    """Attempt Instagram publish; fallback to manual publisher on failure."""
    from src.content_engine.generators.image_generator import ImageGenerator
    from src.publishing.instagram_publisher import InstagramPublisher, InstagramPublishError
    from src.publishing.manual_publisher import ManualPublisher

    if not (post.media_type == "image" and post.media_urls):
        log.warning("ig_publish_skipped_no_image", post_id=str(post.id))
        return

    if not settings.media_base_url:
        log.warning("ig_publish_skipped_no_base_url", post_id=str(post.id))
        # Fall through to manual
        manual = ManualPublisher()
        pub = await pub_repo.create_publication(
            post_id=post.id, platform="instagram_post", status="manual"
        )
        await manual.send_for_manual_posting(bot, post, "instagram_post", pub.id)
        return

    try:
        img_gen = ImageGenerator()
        image_url = img_gen.local_path_to_url(post.media_urls[0])

        ig = InstagramPublisher()
        result = await ig.publish_photo(image_url, post.text_content or "")

        await pub_repo.create_publication(
            post_id=post.id,
            platform="instagram_post",
            platform_text=post.text_content,
            platform_media_url=image_url,
            status="published",
            platform_post_id=result.get("platform_post_id"),
            platform_url=result.get("platform_url"),
        )

        await bot.send_message(
            chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
            text=(
                f"📷 <b>Instagram published!</b>\n"
                f'<a href="{result.get("platform_url")}">View post</a>\n'
                f"Post ID: <code>{str(post.id)[:8]}</code>"
            ),
            parse_mode="HTML",
        )
        log.info("ig_published", post_id=str(post.id))

    except Exception as e:
        log.error("ig_publish_failed", post_id=str(post.id), error=str(e))
        manual = ManualPublisher()
        pub = await pub_repo.create_publication(
            post_id=post.id, platform="instagram_post", status="pending"
        )
        await manual.send_for_manual_posting(bot, post, "instagram_post", pub.id)
        await bot.send_message(
            chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
            text=(
                f"⚠️ Instagram auto-publish failed: {e}\n"
                f"Manual posting instructions sent above."
            ),
            parse_mode="HTML",
        )


# ---------------------------------------------------------------------------
# Video regeneration handler
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("regen_video:"))
async def on_regen_video(callback: CallbackQuery):
    """Regenerate the video for a post."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    post_id = parse_post_id(callback.data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    await callback.answer("Regenerating video...")

    async with async_session() as session:
        repo = PostRepo(session)
        post = await repo.get_post(post_id)
        if not post or not post.generation_params:
            await callback.message.reply("Cannot regenerate: missing generation parameters.")
            return

    from src.workers.task_queue import enqueue_video_task

    task_id = await enqueue_video_task({"post_id": str(post_id)})

    await callback.message.reply(
        f"🎬 Video regeneration queued for post <code>{str(post_id)[:8]}</code>\n"
        f"Task ID: <code>{task_id[:8]}</code>",
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# YouTube publishing helper
# ---------------------------------------------------------------------------

async def _try_publish_youtube(bot, post, pub_repo: PublicationRepo) -> None:
    """Attempt YouTube Short publish; notify admin on failure."""
    if not (post.media_type == "video" and post.media_urls):
        return

    try:
        from src.publishing.youtube_publisher import YouTubePublisher, YouTubePublishError

        yt = YouTubePublisher()
        gen_params = post.generation_params or {}
        caption = gen_params.get("video_caption", post.text_content or "")
        title = gen_params.get("topic", "")[:100] or "BioMaxing Short"

        result = await yt.publish_short(
            video_path=post.media_urls[0],
            title=title,
            description=caption,
            tags=settings.hashtags_list,
        )

        await pub_repo.create_publication(
            post_id=post.id,
            platform="youtube_short",
            platform_text=caption,
            status="published",
            platform_post_id=result.get("platform_post_id"),
            platform_url=result.get("platform_url"),
        )

        await bot.send_message(
            chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
            text=(
                f"🎬 <b>YouTube Short published!</b>\n"
                f'<a href="{result.get("platform_url")}">View short</a>\n'
                f"Post ID: <code>{str(post.id)[:8]}</code>"
            ),
            parse_mode="HTML",
        )
        log.info("yt_published", post_id=str(post.id))

    except Exception as e:
        log.error("yt_publish_failed", post_id=str(post.id), error=str(e))
        await bot.send_message(
            chat_id=settings.tg_admin_chat_id,
                    message_thread_id=settings.tg_admin_thread_id,
            text=(
                f"⚠️ YouTube auto-publish failed: {e}\n"
                f"Post ID: <code>{str(post.id)[:8]}</code>\n"
                f"You can upload the video manually from the file above."
            ),
            parse_mode="HTML",
        )


# ---------------------------------------------------------------------------
# YouTube manual publish handler
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("plat_yt:"))
async def on_publish_youtube(callback: CallbackQuery):
    """Manually trigger YouTube publishing for a video post."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return

    post_id = parse_post_id(callback.data)
    if not post_id:
        await callback.answer("Invalid post ID")
        return

    await callback.answer("Publishing to YouTube...")

    async with async_session() as session:
        repo = PostRepo(session)
        pub_repo = PublicationRepo(session)
        post = await repo.get_post(post_id)
        if not post:
            await callback.message.reply("Post not found.")
            return

        await _try_publish_youtube(callback.bot, post, pub_repo)

    await callback.message.reply(
        f"YouTube publishing initiated for post <code>{str(post_id)[:8]}</code>",
        parse_mode="HTML",
    )
