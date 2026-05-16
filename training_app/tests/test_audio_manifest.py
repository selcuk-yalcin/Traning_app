import pytest

from traning_app.engine.agents.audio_manifest import manifest_from_deck_notes
from traning_app.engine.agents.router import resolve_model
from traning_app.engine.agents.tts import synthesize


def test_manifest_from_deck_notes_uses_titles() -> None:
    deck = {
        "slides": [
            {"type": "title", "title": "A", "subtitle": ""},
            {"type": "bullets", "title": "B", "bullets": ["x"]},
        ]
    }
    m = manifest_from_deck_notes(deck)
    assert len(m.segments) == 2
    assert m.segments[0].slide_index == 0
    assert m.segments[0].duration_sec is not None
    assert "A" in (m.segments[0].text_preview or "")


def test_manifest_skips_empty_slides() -> None:
    deck = {"slides": [{"type": "bullets", "title": "", "bullets": []}]}
    m = manifest_from_deck_notes(deck)
    assert m.segments == []


def test_synthesize_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError, match="Unknown TTS"):
        synthesize("hi", voice_id="", provider="unknown-tts")


def test_resolve_model_vision_modality() -> None:
    t = resolve_model("standard", "text")
    v = resolve_model("standard", "vision")
    assert t["model_id"] != v["model_id"] or v["model_id"] == "gpt-4o"
