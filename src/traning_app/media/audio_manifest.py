"""Per-slide narration segments for mux (plan Layer 4 — sync)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AudioSegment(BaseModel):
    """One timed audio clip aligned to a slide index."""

    slide_index: int = Field(ge=0)
    audio_path: str | None = None
    audio_url: str | None = None
    duration_sec: float | None = Field(default=None, ge=0)


class AudioManifest(BaseModel):
    """Ordered segments consumed by FFmpeg / MoviePy merge."""

    version: str = "1"
    run_id: str | None = None
    segments: list[AudioSegment] = Field(default_factory=list)
