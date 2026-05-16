"""Provider-agnostic TTS entry."""

from __future__ import annotations

from traning_app.config.settings import get_settings
from traning_app.engine.ingest.validation import sanitize_text


def synthesize(text: str, *, voice_id: str, provider: str) -> bytes:
    """
    Return raw audio bytes for ``text`` using ``provider``.

    Supported ``provider`` values: ``openai``, ``elevenlabs``, ``azure``, ``google``.
    """
    t = sanitize_text(text or "", max_len=4096)
    p = (provider or "openai").strip().lower()
    settings = get_settings()

    if p == "openai":
        from traning_app.engine.agents.tts_openai import synthesize_openai_tts

        voice = (voice_id or settings.openai_tts_voice or "alloy").strip()
        return synthesize_openai_tts(t, voice=voice)

    if p in ("elevenlabs", "11labs", "eleven"):
        from traning_app.engine.agents.tts_elevenlabs import synthesize_elevenlabs

        vid = (voice_id or settings.elevenlabs_default_voice_id).strip()
        return synthesize_elevenlabs(t, voice_id=vid)

    if p == "azure":
        from traning_app.engine.agents.tts_azure_google import synthesize_azure

        return synthesize_azure(t, voice=voice_id or "en-US-JennyNeural")

    if p in ("google", "gcp"):
        from traning_app.engine.agents.tts_azure_google import synthesize_google

        return synthesize_google(t, voice=voice_id or "en-US-Wavenet-D")

    raise ValueError(f"Unknown TTS provider: {provider!r}; use openai or elevenlabs.")
