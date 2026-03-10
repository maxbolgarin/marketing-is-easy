from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SettingMeta:
    """Metadata describing a single configurable setting."""

    label: str
    group: str
    is_secret: bool = False


# ---------------------------------------------------------------------------
# Registry of all settings that can be changed at runtime through the UI
# ---------------------------------------------------------------------------

CONFIGURABLE_SETTINGS: dict[str, SettingMeta] = {
    # Telegram
    "tg_bot_token": SettingMeta("Telegram Bot Token", "telegram", is_secret=True),
    "tg_admin_chat_id": SettingMeta("Admin Chat ID", "telegram"),
    "tg_admin_thread_id": SettingMeta("Admin Thread ID", "telegram"),
    "tg_channel_id": SettingMeta("Channel ID", "telegram"),
    "tg_admin_user_ids": SettingMeta("Admin User IDs", "telegram"),
    # AI & Generation
    "openrouter_api_key": SettingMeta("OpenRouter API Key", "ai", is_secret=True),
    "openrouter_text_model": SettingMeta("Text Generation Model", "ai"),
    "openrouter_image_model": SettingMeta("Image Generation Model", "ai"),
    "openai_api_key": SettingMeta("OpenAI API Key", "ai", is_secret=True),
    # Instagram
    "instagram_access_token": SettingMeta("Access Token", "instagram", is_secret=True),
    "instagram_business_account_id": SettingMeta("Business Account ID", "instagram"),
    # YouTube
    "youtube_client_id": SettingMeta("Client ID", "youtube", is_secret=True),
    "youtube_client_secret": SettingMeta("Client Secret", "youtube", is_secret=True),
    "youtube_refresh_token": SettingMeta("Refresh Token", "youtube", is_secret=True),
    # Brand & Content
    "brand_name": SettingMeta("Brand Name", "brand"),
    "content_tone": SettingMeta("Content Tone", "brand"),
    "default_hashtags": SettingMeta("Default Hashtags", "brand"),
    "track": SettingMeta("Track", "brand"),
    "language": SettingMeta("Language", "brand"),
}

GROUP_LABELS: dict[str, str] = {
    "telegram": "Telegram",
    "ai": "AI & Generation",
    "instagram": "Instagram",
    "youtube": "YouTube",
    "brand": "Brand & Content",
}

GROUP_ORDER: list[str] = ["telegram", "ai", "instagram", "youtube", "brand"]
