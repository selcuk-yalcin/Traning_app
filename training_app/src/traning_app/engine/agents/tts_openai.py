"""OpenAI TTS (speech API)."""

from __future__ import annotations

import json

from traning_app.config.settings import get_settings
from traning_app.engine.agents.openrouter_client import resolve_api_credentials
from traning_app.engine.agents.router import resolve_tts_model


def synthesize_openai_tts(text: str, *, voice: str) -> bytes:
    """POST ``/audio/speech`` — OpenRouter or OpenAI; returns MP3 bytes by default."""
    import httpx

    settings = get_settings()
    api_key, base, extra = resolve_api_credentials()
    url = f"{base}/audio/speech"
    v = (voice or settings.openai_tts_voice or "alloy").strip()
    payload = {
        "model": resolve_tts_model(),
        "voice": v,
        "input": (text or "")[:4096],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **extra,
    }
    with httpx.Client(timeout=120.0) as client:
        r = client.post(url, headers=headers, content=json.dumps(payload))
        r.raise_for_status()
        return r.content
