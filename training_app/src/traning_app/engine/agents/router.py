"""Route tier (standard / pro / ultra) to concrete models and budgets."""

from __future__ import annotations

from typing import Any

from traning_app.config.settings import get_settings
from traning_app.engine.agents.openrouter_client import use_openrouter


def resolve_model(tier: str, modality: str = "text") -> dict[str, Any]:
    """
    Map product tier to provider defaults (OpenAI-compatible).

    ``modality`` — ``text`` (chat) or ``vision`` (VLM / multimodal chat).
    """
    t = (tier or "standard").strip().lower()
    if t not in ("standard", "pro", "ultra"):
        t = "standard"
    settings = get_settings()
    or_on = use_openrouter()
    std = settings.llm_model_standard or (
        "openai/gpt-4o-mini" if or_on else "gpt-4o-mini"
    )
    pro = settings.llm_model_pro or ("openai/gpt-4o" if or_on else "gpt-4o")
    ultra = settings.llm_model_ultra or (
        "anthropic/claude-sonnet-4" if or_on else "gpt-4o"
    )
    tier_models = {"standard": std, "pro": pro, "ultra": ultra}
    max_tokens = {"standard": 4096, "pro": 8192, "ultra": 16384}[t]
    max_images = {"standard": 4, "pro": 8, "ultra": 12}[t]
    model_id = tier_models[t]
    if modality.strip().lower() == "vision":
        model_id = settings.vision_model_openai or (
            "google/gemini-2.5-flash" if or_on else "gpt-4o"
        )
    provider = "openrouter" if or_on else "openai"
    base_url = (
        "https://openrouter.ai/api/v1"
        if or_on
        else (settings.openai_base_url or "https://api.openai.com/v1")
    )
    return {
        "tier": t,
        "provider": provider,
        "model_id": model_id,
        "max_tokens": max_tokens,
        "max_images": max_images,
        "base_url": base_url.rstrip("/"),
    }


def resolve_image_model(tier: str = "standard") -> str:
    """Image generation model id (OpenRouter chat+image or native DALL·E)."""
    settings = get_settings()
    if use_openrouter():
        if settings.openrouter_image_model:
            return settings.openrouter_image_model
        by_tier = {
            "standard": "google/gemini-2.5-flash-image",
            "pro": "google/gemini-3.1-flash-image-preview",
            "ultra": "black-forest-labs/flux.2-pro",
        }
        return by_tier.get((tier or "standard").strip().lower(), by_tier["standard"])
    return settings.openai_image_model


def resolve_tts_model() -> str:
    settings = get_settings()
    if use_openrouter() and settings.openrouter_tts_model:
        return settings.openrouter_tts_model
    if use_openrouter():
        return "openai/gpt-4o-mini-tts-2025-12-15"
    return settings.openai_tts_model
