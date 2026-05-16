import pytest

from traning_app.engine.deck.catalog import get_catalog_entry, load_template_catalog
from traning_app.engine.ingest.context import build_unified_context
from traning_app.engine.ingest.validation import assert_sources_size, sanitize_text


def test_sanitize_text_strips_nul() -> None:
    assert sanitize_text("a\x00b") == "ab"


def test_build_unified_context_orders_sources() -> None:
    ctx = build_unified_context(
        [
            {"type": "topic", "headings": ["A", "B"]},
            {"type": "prompt", "text": "Do X"},
        ]
    )
    assert "Source [1]" in ctx and "topic" in ctx
    assert "Source [2]" in ctx and "Do X" in ctx


def test_catalog_loads() -> None:
    cat = load_template_catalog()
    assert "occ-safety" in cat
    assert get_catalog_entry("fire-protection") is not None


def test_sources_too_large() -> None:
    big = [{"type": "prompt", "text": "x" * 200_000}]
    with pytest.raises(ValueError):
        assert_sources_size(big)
