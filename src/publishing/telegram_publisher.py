"""Publish posts to a Telegram channel."""

from __future__ import annotations

import structlog
from aiogram import Bot

from src.config.settings import settings
from src.content_engine.generators.platform_adapter import adapt_for_telegram

log = structlog.get_logger()


class TelegramPublisher:
    def __init__(self, bot: Bot | None = None, channel_id: int | None = None):
        self.bot = bot or Bot(token=settings.tg_bot_token)
        self.channel_id = channel_id or settings.tg_channel_id
        self._owns_bot = bot is None  # track if we created the bot

    async def publish_text(
        self,
        text: str,
        hashtags: list[str] | None = None,
    ) -> dict:
        """Publish a text-only post to the Telegram channel.

        Returns dict with message_id and link.
        """
        formatted = adapt_for_telegram(text, hashtags)

        log.info("publishing_to_telegram", channel=self.channel_id, text_len=len(formatted))

        msg = await self.bot.send_message(
            chat_id=self.channel_id,
            text=formatted,
            parse_mode=None,  # plain text for now; switch to HTML if needed
            disable_web_page_preview=True,
        )

        # Build link (works for public channels)
        channel_str = str(self.channel_id)
        if channel_str.startswith("-100"):
            link = f"https://t.me/c/{channel_str[4:]}/{msg.message_id}"
        else:
            link = None

        log.info("telegram_published", message_id=msg.message_id)

        return {
            "message_id": msg.message_id,
            "platform_post_id": str(msg.message_id),
            "platform_url": link,
        }

    async def publish_photo(
        self,
        photo_path: str,
        caption: str | None = None,
        hashtags: list[str] | None = None,
    ) -> dict:
        """Publish a photo post to the Telegram channel."""
        formatted_caption = adapt_for_telegram(caption or "", hashtags) if caption else None

        from aiogram.types import FSInputFile

        photo = FSInputFile(photo_path)

        msg = await self.bot.send_photo(
            chat_id=self.channel_id,
            photo=photo,
            caption=formatted_caption[:1024] if formatted_caption else None,  # caption limit
        )

        return {
            "message_id": msg.message_id,
            "platform_post_id": str(msg.message_id),
        }

    async def publish_video(
        self,
        video_path: str,
        caption: str | None = None,
        hashtags: list[str] | None = None,
    ) -> dict:
        """Publish a video post to the Telegram channel."""
        formatted_caption = adapt_for_telegram(caption or "", hashtags) if caption else None

        from aiogram.types import FSInputFile

        video = FSInputFile(video_path)

        msg = await self.bot.send_video(
            chat_id=self.channel_id,
            video=video,
            caption=formatted_caption[:1024] if formatted_caption else None,
        )

        return {
            "message_id": msg.message_id,
            "platform_post_id": str(msg.message_id),
        }

    async def close(self):
        if self._owns_bot:
            await self.bot.session.close()
