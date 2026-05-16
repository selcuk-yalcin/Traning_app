"""FFmpeg / MoviePy — Layer 4 (audio + slide timing → MP4)."""

from traning_app.engine.agents.audio_manifest import AudioManifest, AudioSegment
from traning_app.engine.media.sync import render_mp4

__all__ = ["AudioManifest", "AudioSegment", "render_mp4"]
