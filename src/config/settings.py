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

    # --- API ---
    api_secret_key: str = "change-me-in-production"
    api_cors_origins: str = "http://localhost:5173,http://localhost:3000"
    api_default_admin_username: str = "admin"
    api_default_admin_password: str = ""

    @property
    def admin_user_ids(self) -> set[int]:
        if not self.tg_admin_user_ids:
            return set()
        return {int(uid.strip()) for uid in self.tg_admin_user_ids.split(",") if uid.strip()}

    @property
    def hashtags_list(self) -> list[str]:
        return [h.strip() for h in self.default_hashtags.split(",") if h.strip()]


def _coerce(value: str, field_name: str) -> object:
    """Coerce a string override value to the type declared on Settings."""
    try:
        annotation = Settings.model_fields[field_name].annotation
    except KeyError:
        return value

    # Normalise Union types like `int | None` → check for NoneType presence
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", ())

    # Handle `int | None` (UnionType / Optional[int])
    if origin is type(None) or (args and type(None) in args):
        # Find the real type among the args (the non-None one)
        real_args = [a for a in args if a is not type(None)]
        if not value:
            return None
        if real_args:
            return _coerce_primitive(value, real_args[0])
        return value

    return _coerce_primitive(value, annotation)


def _coerce_primitive(value: str, typ: type) -> object:
    """Coerce a non-None string to a primitive type."""
    if typ is str:
        return value
    if typ is int:
        return int(value)
    if typ is float:
        return float(value)
    if typ is bool:
        return value.lower() in ("true", "1", "yes")
    # Unknown / composite type — return as-is
    return value


class DynamicSettings:
    """
    Wraps the static ``Settings`` pydantic model and allows runtime overrides
    loaded from the database.  All attribute access falls back to the base
    ``Settings`` instance when no override is present.
    """

    def __init__(self) -> None:
        self._base: Settings = Settings()
        self._overrides: dict[str, str] = {}

    async def load_from_db(self) -> None:
        """Load all overrides from the database into the in-memory cache.

        Uses lazy imports to avoid circular-import issues between
        ``src.config.settings`` and ``src.db.*``.
        """
        from src.db.models import async_session  # noqa: PLC0415
        from src.db.settings_repo import SettingsRepo  # noqa: PLC0415

        async with async_session() as session:
            repo = SettingsRepo(session)
            self._overrides = await repo.get_all()

    def update_override(self, key: str, value: str) -> None:
        """Update a single in-memory override (e.g. after a live settings save)."""
        self._overrides[key] = value

    def _get_raw(self, name: str) -> str:
        """Return the raw string value: override first, then base-model string."""
        raw = self._overrides.get(name, "")
        if raw:
            return raw
        # Fall back to the base Settings value (convert to str for uniformity)
        return str(getattr(self._base, name))

    @property
    def admin_user_ids(self) -> set[int]:
        raw = self._get_raw("tg_admin_user_ids")
        if not raw:
            return set()
        return {int(uid.strip()) for uid in raw.split(",") if uid.strip()}

    @property
    def hashtags_list(self) -> list[str]:
        raw = self._get_raw("default_hashtags")
        return [h.strip() for h in raw.split(",") if h.strip()]

    def __getattr__(self, name: str) -> object:
        # Guard: internal attributes (_base, _overrides, etc.) must bypass this
        # handler to avoid infinite recursion during __init__.
        if name.startswith("_"):
            return object.__getattribute__(self, name)

        # Check in-memory overrides first (non-empty value wins)
        raw = object.__getattribute__(self, "_overrides").get(name, "")
        if raw:
            return _coerce(raw, name)

        # Fall back to the static base settings
        return getattr(object.__getattribute__(self, "_base"), name)


settings = DynamicSettings()
