"""Load configuration from environment variables (.env via pydantic-settings)."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None
    openrouter_http_referer: str | None = None
    openrouter_site_url: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    llm_model_standard: str | None = Field(default=None, validation_alias="MODEL_TIER_STANDARD")
    llm_model_pro: str | None = Field(default=None, validation_alias="MODEL_TIER_PRO")
    llm_model_ultra: str | None = Field(default=None, validation_alias="MODEL_TIER_ULTRA")

    vision_model_openai: str | None = Field(default=None, validation_alias="VISION_MODEL_OPENAI")
    openai_image_model: str = Field(default="dall-e-3", validation_alias="OPENAI_IMAGE_MODEL")
    openrouter_image_model: str | None = Field(
        default=None, validation_alias="OPENROUTER_IMAGE_MODEL"
    )

    unsplash_access_key: str | None = None

    openai_tts_model: str = Field(default="tts-1", validation_alias="OPENAI_TTS_MODEL")
    openai_tts_voice: str = Field(default="alloy", validation_alias="OPENAI_TTS_VOICE")
    openrouter_tts_model: str | None = Field(default=None, validation_alias="OPENROUTER_TTS_MODEL")
    elevenlabs_api_key: str | None = None
    elevenlabs_default_voice_id: str = "21m00Tcm4TlvDq8ikWAM"

    storage_exports_dir: str = Field(default="storage/exports", validation_alias="STORAGE_EXPORTS_DIR")
    ffmpeg_binary: str = Field(default="ffmpeg", validation_alias="FFMPEG_BINARY")

    mongodb_uri: str | None = None
    mongodb_db: str = "presentation_engine"
    redis_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
