"""ElevenLabs TTS."""

from __future__ import annotations

import json

from traning_app.config.settings import get_settings


def synthesize_elevenlabs(text: str, *, voice_id: str) -> bytes:
    """POST ``/v1/text-to-speech/{voice_id}`` — returns MPEG audio bytes."""
    import httpx

    settings = get_settings()
    if not settings.elevenlabs_api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not configured")

    vid = (voice_id or settings.elevenlabs_default_voice_id).strip()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}"
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    body = {
        "text": (text or "")[:5000],
        "model_id": "eleven_multilingual_v2",
    }
    with httpx.Client(timeout=120.0) as client:
        r = client.post(url, headers=headers, content=json.dumps(body))
        r.raise_for_status()
        return r.content
