"""Load configuration from environment variables (.env via pydantic-settings)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None

    mongodb_uri: str | None = None
    mongodb_db: str = "presentation_engine"
    redis_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
