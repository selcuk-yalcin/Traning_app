"""Shared OpenRouter HTTP config (LLM, vision, image, TTS)."""

from __future__ import annotations

from traning_app.config.settings import get_settings


def use_openrouter() -> bool:
    return bool(get_settings().openrouter_api_key)


def resolve_api_credentials() -> tuple[str, str, dict[str, str]]:
    """
    Return ``(api_key, base_url, extra_headers)``.

    Prefers ``OPENROUTER_API_KEY`` when set; otherwise falls back to OpenAI-native URL/key.
    """
    settings = get_settings()
    if settings.openrouter_api_key:
        extra: dict[str, str] = {}
        if settings.openrouter_http_referer:
            extra["HTTP-Referer"] = settings.openrouter_http_referer
        if settings.openrouter_site_url:
            extra["X-Title"] = settings.openrouter_site_url
        return (
            settings.openrouter_api_key,
            "https://openrouter.ai/api/v1",
            extra,
        )
    if settings.openai_api_key:
        return settings.openai_api_key, settings.openai_base_url.rstrip("/"), {}
    raise RuntimeError("Configure OPENROUTER_API_KEY or OPENAI_API_KEY")
