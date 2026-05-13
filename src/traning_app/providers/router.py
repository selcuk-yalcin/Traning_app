"""Route tier (standard / pro / ultra) to concrete models and budgets."""

from __future__ import annotations

from typing import Any

from traning_app.config.settings import get_settings


def resolve_model(tier: str, modality: str = "text") -> dict[str, Any]:
    """
    Map product tier to provider defaults (OpenAI-compatible).

    ``modality`` is reserved for ``text`` vs ``vision`` caps.
    """
    _ = modality
    t = (tier or "standard").strip().lower()
    if t not in ("standard", "pro", "ultra"):
        t = "standard"
    settings = get_settings()
    # Allow env overrides without extra schema fields (optional).
    std = getattr(settings, "llm_model_standard", None) or "gpt-4o-mini"
    pro = getattr(settings, "llm_model_pro", None) or "gpt-4o"
    ultra = getattr(settings, "llm_model_ultra", None) or "gpt-4o"
    tier_models = {"standard": std, "pro": pro, "ultra": ultra}
    max_tokens = {"standard": 4096, "pro": 8192, "ultra": 16384}[t]
    max_images = {"standard": 4, "pro": 8, "ultra": 12}[t]
    return {
        "tier": t,
        "provider": "openai",
        "model_id": tier_models[t],
        "max_tokens": max_tokens,
        "max_images": max_images,
        "base_url": getattr(settings, "openai_base_url", None) or "https://api.openai.com/v1",
    }
