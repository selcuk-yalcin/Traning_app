"""Measure audio duration (ffprobe preferred)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from traning_app.config.settings import get_settings


def probe_duration_sec(path: str | Path) -> float:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    settings = get_settings()
    ffmpeg = settings.ffmpeg_binary or "ffmpeg"
    ffprobe = "ffprobe"
    if "ffmpeg" in ffmpeg:
        ffprobe = ffmpeg.replace("ffmpeg", "ffprobe")
    if not shutil.which(ffprobe):
        # ~128 kbps MP3 rough estimate for speech
        size = p.stat().st_size
        return max(1.0, min(180.0, size / 16000.0))
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(p.resolve()),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if out.returncode != 0:
        size = p.stat().st_size
        return max(1.0, min(180.0, size / 16000.0))
    data = json.loads(out.stdout or "{}")
    try:
        return max(0.1, float(data["format"]["duration"]))
    except (KeyError, TypeError, ValueError):
        return max(1.0, p.stat().st_size / 16000.0)


def ffmpeg_available() -> bool:
    settings = get_settings()
    return bool(shutil.which(settings.ffmpeg_binary or "ffmpeg"))
