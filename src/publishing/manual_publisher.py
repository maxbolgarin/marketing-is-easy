"""Manual posting publisher — sends content to admin chat for copy-paste posting.

Used when:
- Instagram API is not configured or fails
- Post requires manual action on a platform
"""

from __future__ import annotations

import uuid
from pathlib import Path

import structlog
from aiogram import Bot
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from src.config.settings import settings
from src.db.models import Post

log = structlog.get_logger()

_PLATFORM_INSTRUCTIONS = {
    "instagram_post": (
        "1. Open Instagram on your phone\n"
        "2. Tap [+] → Post\n"
        "3. Select the image above\n"
        "4. Paste the caption below\n"
        "5. Tap Share"
    ),
    "instagram_reel": (
        "1. Open Instagram on your phone\n"
        "2. Tap [+] → Reel\n"
        "3. Select the video above\n"
        "4. Paste the caption below\n"
        "5. Tap Share"
    ),
    "youtube_short": (
        "1. Open YouTube Studio\n"
        "2. Tap Create → Upload\n"
        "3. Select the video above\n"
        "4. Paste title/description below\n"
        "5. Set visibility → Publish"
    ),
}


class ManualPublisher:
    """Send post content to admin Telegram chat for manual copy-paste publishing."""

    async def send_for_manual_posting(
        self,
        bot: Bot,
        post: Post,
        platform: str,
        pub_id: uuid.UUID | None = None,
    ) -> int:
        """Send image/video + formatted caption to admin chat.

        Returns the Telegram message_id of the "Mark as Posted" message.
        """
        log.info("manual_posting_send", post_id=str(post.id), platform=platform)

        admin_chat = settings.tg_admin_chat_id
        thread_id = settings.tg_admin_thread_id
        platform_label = platform.replace("_", " ").title()

        # 1. Header message
        header = (
            f"📋 <b>Manual Post Required — {platform_label}</b>\n\n"
            f"Post ID: <code>{str(post.id)[:8]}</code>"
        )
        await bot.send_message(
            admin_chat, header, parse_mode="HTML", message_thread_id=thread_id,
        )

        # 2. Send media file if present
        if post.media_urls:
            media_path = Path(post.media_urls[0])
            if media_path.exists():
                if post.media_type == "video":
                    await bot.send_video(
                        admin_chat, FSInputFile(media_path), message_thread_id=thread_id,
                    )
                else:
                    await bot.send_photo(
                        admin_chat, FSInputFile(media_path), message_thread_id=thread_id,
                    )
            else:
                await bot.send_message(
                    admin_chat,
                    f"⚠️ Media file not found: <code>{media_path}</code>",
                    parse_mode="HTML",
                    message_thread_id=thread_id,
                )

        # 3. Caption to copy
        caption = post.text_content or ""
        caption_msg = (
            f"📝 <b>Caption (copy below):</b>\n\n"
            f"<code>{caption[:4000]}</code>"
        )
        await bot.send_message(
            admin_chat, caption_msg, parse_mode="HTML", message_thread_id=thread_id,
        )

        # 4. Platform instructions
        instructions = _PLATFORM_INSTRUCTIONS.get(platform, "Post manually on the platform.")
        await bot.send_message(
            admin_chat, f"📌 <b>Steps:</b>\n{instructions}", parse_mode="HTML",
            message_thread_id=thread_id,
        )

        # 5. "Mark as Posted" button
        callback = f"manual_posted:{pub_id}" if pub_id else f"manual_posted_post:{post.id}"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Mark as Posted", callback_data=callback)],
            ]
        )
        confirm_msg = await bot.send_message(
            admin_chat,
            f"After posting manually on <b>{platform_label}</b>, click the button below.",
            parse_mode="HTML",
            reply_markup=keyboard,
            message_thread_id=thread_id,
        )

        log.info(
            "manual_posting_sent",
            post_id=str(post.id),
            platform=platform,
            confirm_message_id=confirm_msg.message_id,
        )
        return confirm_msg.message_id
