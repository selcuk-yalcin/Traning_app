"""Text-to-speech: ElevenLabs, OpenAI TTS, Azure/Google adapters."""


def synthesize(text: str, *, voice_id: str, provider: str) -> bytes:
    raise NotImplementedError
