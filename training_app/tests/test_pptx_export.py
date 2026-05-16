"""Tests for Deck JSON → PPTX export."""

from pathlib import Path

from traning_app.engine.deck.loaders import list_builtin_template_ids, load_builtin_deck_template
from traning_app.engine.agents.pptx_export import deck_to_pptx


def test_deck_to_pptx_minimal(tmp_path: Path) -> None:
    deck = {
        "version": "1",
        "meta": {"title": "Test"},
        "slides": [
            {"type": "title", "title": "Hello", "subtitle": "World"},
            {
                "type": "bullets",
                "title": "Items",
                "bullets": ["A", "B"],
                "notes": "Speaker note",
            },
        ],
    }
    out = tmp_path / "out.pptx"
    deck_to_pptx(deck, str(out))
    assert out.is_file()
    assert out.stat().st_size > 2000


def test_builtin_templates_roundtrip(tmp_path: Path) -> None:
    ids = list_builtin_template_ids()
    assert "occ-safety" in ids
    assert "fire-protection" in ids
    for tid in ids:
        deck = load_builtin_deck_template(tid)
        assert deck["meta"]["template_id"] == tid
        out = tmp_path / f"{tid}.pptx"
        deck_to_pptx(deck, str(out))
        assert out.stat().st_size > 5000


def test_export_with_empty_base_template(tmp_path: Path) -> None:
    from pptx import Presentation

    base = tmp_path / "base.pptx"
    Presentation().save(str(base))

    deck = load_builtin_deck_template("occ-safety")
    out = tmp_path / "from_base.pptx"
    deck_to_pptx(deck, str(out), template_path=str(base))
    assert out.stat().st_size > 5000
