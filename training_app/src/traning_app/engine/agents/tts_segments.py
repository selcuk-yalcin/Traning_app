"""Synthesize per-slide narration and update the audio manifest."""

from __future__ import annotations

import logging

from traning_app.engine.agents.audio_manifest import AudioManifest, AudioSegment
from traning_app.engine.agents.tts import synthesize
from traning_app.engine.media.audio_probe import probe_duration_sec
from traning_app.engine.media.paths import job_audio_dir

log = logging.getLogger(__name__)


def segment_narration_text(slide: dict) -> str:
    parts: list[str] = []
    if slide.get("title"):
        parts.append(str(slide["title"]).strip())
    if slide.get("subtitle"):
        parts.append(str(slide["subtitle"]).strip())
    for b in slide.get("bullets") or []:
        if b:
            parts.append(str(b).strip())
    if slide.get("notes"):
        parts.append(str(slide["notes"]).strip())
    if slide.get("left"):
        parts.append(str(slide["left"]).strip())
    if slide.get("right"):
        parts.append(str(slide["right"]).strip())
    return ". ".join(p for p in parts if p)


def synthesize_manifest_audio(
    manifest: AudioManifest,
    deck: dict,
    job_id: str,
    *,
    provider: str = "openai",
    voice_id: str | None = None,
) -> AudioManifest:
    """Write ``slide_NNN.mp3`` files and refresh ``duration_sec`` / ``audio_path``."""
    slides = list(deck.get("slides") or [])
    adir = job_audio_dir(job_id)
    updated: list[AudioSegment] = []

    for seg in manifest.segments:
        slide = slides[seg.slide_index] if seg.slide_index < len(slides) else {}
        text = segment_narration_text(slide) if isinstance(slide, dict) else ""
        if not text:
            text = (seg.text_preview or "").strip()
        if not text:
            updated.append(seg)
            continue
        text = text[:4096]
        out_path = adir / f"slide_{seg.slide_index:03d}.mp3"
        try:
            audio = synthesize(text, voice_id=voice_id or "", provider=provider)
            out_path.write_bytes(audio)
            dur = round(probe_duration_sec(out_path), 2)
            updated.append(
                seg.model_copy(
                    update={
                        "audio_path": str(out_path.resolve()),
                        "duration_sec": dur,
                        "text_preview": text[:500],
                    }
                )
            )
        except Exception as e:
            log.warning("TTS segment %s failed: %s", seg.slide_index, e)
            updated.append(seg)

    return AudioManifest(
        version=manifest.version,
        run_id=job_id,
        segments=updated,
    )
