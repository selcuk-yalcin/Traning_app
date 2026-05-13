"""Synchronize narration audio with slide durations for video export."""

from __future__ import annotations

from pathlib import Path


def render_mp4(deck_path: str, audio_segments: list[dict], output_path: str) -> None:
    """
    Combine slide timings with audio into MP4 (plan Layer 4).

    MVP: not implemented — wire FFmpeg/MoviePy and slide timing JSON first;
    see ``media/audio_manifest.py`` for the manifest shape.
    """
    _ = Path(deck_path)
    _ = audio_segments
    _ = Path(output_path)
    raise NotImplementedError(
        "MP4 render pipeline not wired yet; export PPTX/HTML and build "
        "AudioManifest segments first (specs/plan.md Layer 4)."
    )
