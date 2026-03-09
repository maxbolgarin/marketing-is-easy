"""Adapt post content for different platforms."""

from __future__ import annotations

from src.config.settings import settings


def adapt_for_telegram(text: str, hashtags: list[str] | None = None) -> str:
    """Format post for Telegram channel.

    Telegram supports HTML formatting, 4096 char limit.
    We keep it plain text for now but add hashtags.
    """
    parts = [text.strip()]

    tags = hashtags or settings.hashtags_list
    if tags:
        parts.append("")  # blank line
        parts.append(" ".join(tags))

    result = "\n".join(parts)

    # Telegram message limit
    if len(result) > 4096:
        # Truncate text, keep hashtags
        tag_block = "\n\n" + " ".join(tags) if tags else ""
        max_text = 4096 - len(tag_block) - 3  # 3 for "..."
        result = text[:max_text].rstrip() + "..." + tag_block

    return result


def adapt_for_instagram(text: str, hashtags: list[str] | None = None) -> str:
    """Format caption for Instagram post.

    Instagram caption limit: 2200 characters, max 30 hashtags.
    """
    tags = hashtags or settings.hashtags_list
    # Instagram convention: hashtags go at the end, often separated by dots
    tag_block = "\n.\n.\n.\n" + " ".join(tags[:30]) if tags else ""

    # Leave room for tag block
    max_text = 2200 - len(tag_block)
    if len(text) > max_text:
        text = text[:max_text - 3].rstrip() + "..."

    return text + tag_block


def adapt_for_youtube_description(text: str, hashtags: list[str] | None = None) -> str:
    """Format description for YouTube Shorts.

    YouTube description limit: 5000 characters.
    First 2-3 lines show in the Shorts feed.
    """
    tags = hashtags or settings.hashtags_list

    parts = [text.strip()]
    if tags:
        parts.append("")
        parts.append(" ".join(tags[:15]))  # YouTube allows 15 hashtags in description

    # Add channel CTA
    parts.append("")
    parts.append(f"Follow {settings.brand_name} for more evidence-based health tips!")

    return "\n".join(parts)


PLATFORM_ADAPTERS = {
    "telegram": adapt_for_telegram,
    "instagram_post": adapt_for_instagram,
    "instagram_reel": adapt_for_instagram,
    "youtube_short": adapt_for_youtube_description,
}


def adapt_text(text: str, platform: str, hashtags: list[str] | None = None) -> str:
    """Adapt text content for a specific platform."""
    adapter = PLATFORM_ADAPTERS.get(platform)
    if adapter:
        return adapter(text, hashtags)
    return text
