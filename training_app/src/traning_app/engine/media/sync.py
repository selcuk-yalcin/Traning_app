"""Synchronize narration audio with slide durations for video export (Layer 4)."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any

from traning_app.config.settings import get_settings
from traning_app.engine.media.audio_probe import ffmpeg_available
from traning_app.engine.media.paths import job_dir, job_mp4_path

log = logging.getLogger(__name__)


def _ffmpeg_bin() -> str:
    return get_settings().ffmpeg_binary or "ffmpeg"


def _slide_color(deck: dict) -> str:
    meta = deck.get("meta") or {}
    theme = meta.get("theme") or {}
    colors = theme.get("colors") or {}
    primary = colors.get("primary") or "#1e3a5f"
    if isinstance(primary, str) and primary.startswith("#"):
        return "0x" + primary[1:]
    return "0x1e3a5f"


def _segment_duration(seg: dict) -> float:
    d = seg.get("duration_sec")
    if d is not None:
        try:
            return max(1.0, min(300.0, float(d)))
        except (TypeError, ValueError):
            pass
    return 4.0


def _build_part_clip(
    *,
    ffmpeg: str,
    seg: dict,
    deck: dict,
    work_dir: Path,
) -> Path:
    idx = int(seg.get("slide_index", 0))
    dur = _segment_duration(seg)
    out = work_dir / f"part_{idx:03d}.mp4"
    color = _slide_color(deck)
    audio_path = seg.get("audio_path")
    has_audio = audio_path and Path(str(audio_path)).is_file()

    if has_audio:
        cmd = [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c={color}:s=1280x720:r=24",
            "-i",
            str(audio_path),
            "-t",
            str(dur),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(out),
        ]
    else:
        cmd = [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c={color}:s=1280x720:r=24:d={dur}",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-t",
            str(dur),
            str(out),
        ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"ffmpeg segment failed (slide {idx}): {proc.stderr[-800:] if proc.stderr else proc.returncode}"
        )
    return out


def render_mp4(
    job_id: str,
    deck: dict,
    audio_manifest: dict[str, Any],
    output_path: str | None = None,
) -> str:
    """
    Mux per-slide clips into one MP4.

    ``audio_manifest`` is the serialized ``AudioManifest`` (``segments`` list).
    Returns absolute path to the MP4 file.
    """
    if not ffmpeg_available():
        raise RuntimeError(
            "ffmpeg not found on PATH; set FFMPEG_BINARY or install ffmpeg (plan Layer 4)."
        )

    segments = list(audio_manifest.get("segments") or [])
    if not segments:
        raise ValueError("Audio manifest has no segments")

    ffmpeg = _ffmpeg_bin()
    work_dir = job_dir(job_id) / "mux"
    work_dir.mkdir(parents=True, exist_ok=True)
    out = Path(output_path) if output_path else job_mp4_path(job_id)
    out.parent.mkdir(parents=True, exist_ok=True)

    parts: list[Path] = []
    for seg in sorted(segments, key=lambda s: int(s.get("slide_index", 0))):
        if not isinstance(seg, dict):
            continue
        parts.append(
            _build_part_clip(ffmpeg=ffmpeg, seg=seg, deck=deck, work_dir=work_dir)
        )

    if not parts:
        raise ValueError("No video parts produced")

    if len(parts) == 1:
        parts[0].replace(out)
        return str(out.resolve())

    list_file = work_dir / "concat.txt"
    lines = [f"file '{p.resolve().as_posix()}'" for p in parts]
    list_file.write_text("\n".join(lines), encoding="utf-8")

    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        # Re-encode if stream copy fails
        cmd = [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(out),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(
                f"ffmpeg concat failed: {proc.stderr[-800:] if proc.stderr else proc.returncode}"
            )

    return str(out.resolve())
