"""Enterprise cloud TTS (optional — wire when keys exist)."""


def synthesize_azure(text: str, *, voice: str) -> bytes:
    """Azure Speech — not wired in MVP; set ``AZURE_SPEECH_KEY`` / region and implement SDK or REST."""
    raise NotImplementedError(
        "Azure Speech TTS is not implemented in this build. Use provider=openai or elevenlabs."
    )


def synthesize_google(text: str, *, voice: str) -> bytes:
    """Google Cloud Text-to-Speech — not wired in MVP."""
    raise NotImplementedError(
        "Google Cloud TTS is not implemented in this build. Use provider=openai or elevenlabs."
    )
