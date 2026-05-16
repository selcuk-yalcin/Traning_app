"""Per-slide narration segments for mux (plan Layer 4 — sync)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AudioSegment(BaseModel):
    """One timed audio clip aligned to a slide index."""

    slide_index: int = Field(ge=0)
    audio_path: str | None = None
    audio_url: str | None = None
    duration_sec: float | None = Field(default=None, ge=0)
    text_preview: str | None = Field(
        default=None,
        description="Source snippet for TTS / pacing (not full narration).",
    )


class AudioManifest(BaseModel):
    """Ordered segments consumed by FFmpeg / MoviePy merge."""

    version: str = "1"
    run_id: str | None = None
    segments: list[AudioSegment] = Field(default_factory=list)


def manifest_from_deck_notes(deck: dict) -> AudioManifest:
    """
    Build segment timing estimates from slide ``notes`` or ``title`` (Layer 3 → Layer 4).

    Heuristic: ~2.5 spoken words/sec until FFmpeg mux attaches measured durations.
    """
    segments: list[AudioSegment] = []
    slides = list(deck.get("slides") or [])
    for i, slide in enumerate(slides):
        if not isinstance(slide, dict):
            continue
        text = (slide.get("notes") or slide.get("title") or "").strip()
        if not text:
            continue
        preview = text[:500]
        words = max(1, len(text.split()))
        dur = max(1.5, min(180.0, words / 2.5))
        segments.append(
            AudioSegment(
                slide_index=i,
                duration_sec=round(dur, 2),
                text_preview=preview,
            )
        )
    return AudioManifest(segments=segments)
