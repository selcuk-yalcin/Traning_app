from pathlib import Path

import pytest

from traning_app.engine.media.audio_probe import ffmpeg_available
from traning_app.engine.media.sync import render_mp4


@pytest.mark.skipif(not ffmpeg_available(), reason="ffmpeg not installed")
def test_render_mp4_minimal(tmp_path) -> None:
    job_id = "test-mux-job"
    deck = {
        "meta": {"title": "Test", "theme": {"colors": {"primary": "#112233"}}},
        "slides": [{"type": "title", "title": "Hello"}],
    }
    manifest = {
        "version": "1",
        "segments": [{"slide_index": 0, "duration_sec": 1.5}],
    }
    out = tmp_path / "out.mp4"
    path = render_mp4(job_id, deck, manifest, output_path=str(out))
    assert Path(path).is_file()
    assert Path(path).stat().st_size > 1000
