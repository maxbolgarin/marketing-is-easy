from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Track ---
    track: str = "eu"
    language: str = "en"
    brand_name: str = "BioMaxing"
    content_tone: str = "scientific_casual"
    default_hashtags: str = "#biohacking,#supplements,#health,#wellness,#biomaxing"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://social:social_dev_pass@localhost:5432/social_marketing"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Telegram ---
    tg_bot_token: str = ""
    tg_admin_chat_id: int = 0
    tg_admin_thread_id: int | None = None  # message_thread_id for supergroup topics
    tg_channel_id: int = 0
    tg_admin_user_ids: str = ""  # comma-separated

    # --- OpenRouter ---
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_text_model: str = "anthropic/claude-sonnet-4-20250514"
    openrouter_image_model: str = "google/gemini-3.1-flash-image-preview"

    # --- Media Storage ---
    media_storage_path: str = "/app/media"
    media_base_url: str = ""  # public URL prefix, required for Instagram (e.g. https://media.yourdomain.com)

    # --- OpenAI (Video Pipeline) ---
    openai_api_key: str = ""
    openai_text_model: str = "gpt-5-mini"
    openai_image_model: str = "gpt-image-1-mini"
    openai_video_model: str = "sora-2"
    openai_tts_model: str = "gpt-4o-mini-tts"
    openai_tts_voice: str = "alloy"
    openai_transcribe_model: str = "whisper-1"

    # --- Video Settings ---
    video_size: str = "720x1280"
    video_quality: str = "standard"
    video_default_motion_seconds: int = 8
    video_min_scene_seconds: int = 5
    video_max_scene_seconds: int = 10
    video_final_target_seconds: int = 36
    video_motion_scene_count: int = 3
    video_still_scene_count: int = 2
    video_fps: int = 30
    video_enable_motion: bool = True

    # --- Brand (Video Slides) ---
    brand_heading_font: str = ""
    brand_body_font: str = ""
    brand_logo_path: str = ""
    brand_primary_teal: str = "#53D7FF"
    brand_bg: str = "#06141A"
    brand_text_color: str = "#F5FBFF"
    brand_subtle_text: str = "#D6EDF4"

    # --- Audio ---
    bgm_path: str = ""
    bgm_volume: float = 0.10
    voice_volume: float = 1.00

    # --- fal.ai ---
    fal_api_key: str = ""

    # --- Instagram (Phase 2) ---
    instagram_access_token: str = ""
    instagram_business_account_id: str = ""
    instagram_graph_api_url: str = "https://graph.facebook.com/v22.0"

    # --- YouTube (Phase 3) ---
    youtube_client_id: str = ""
    youtube_client_secret: str = ""
    youtube_refresh_token: str = ""

    @property
    def admin_user_ids(self) -> set[int]:
        if not self.tg_admin_user_ids:
            return set()
        return {int(uid.strip()) for uid in self.tg_admin_user_ids.split(",") if uid.strip()}

    @property
    def hashtags_list(self) -> list[str]:
        return [h.strip() for h in self.default_hashtags.split(",") if h.strip()]


settings = Settings()
