from traning_app.engine.agents.audio_manifest import manifest_from_deck_notes
from traning_app.engine.agents.tts_segments import segment_narration_text


def test_segment_narration_text_combines_fields() -> None:
    slide = {
        "title": "Fire exits",
        "bullets": ["Keep clear", "Signage"],
        "notes": "Emphasize drills.",
    }
    t = segment_narration_text(slide)
    assert "Fire exits" in t
    assert "Keep clear" in t
    assert "drills" in t


def test_manifest_nonempty_for_titled_slides() -> None:
    deck = {"slides": [{"type": "title", "title": "Intro"}]}
    m = manifest_from_deck_notes(deck)
    assert len(m.segments) == 1
