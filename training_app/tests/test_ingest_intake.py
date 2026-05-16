"""Layer 1 — intake resolution and helpers."""

from unittest.mock import patch

import pytest

from traning_app.engine.ingest.context import build_unified_context
from traning_app.engine.ingest.html_plain import html_to_plain
from traning_app.engine.ingest.intake import resolve_sources_for_job
from traning_app.engine.ingest.validation import validate_sources_list, validate_slide_length


def test_html_to_plain_strips_tags() -> None:
    html = "<html><body><p>Hello <b>world</b></p><script>x</script></body></html>"
    assert "Hello" in html_to_plain(html) and "world" in html_to_plain(html)
    assert "script" not in html_to_plain(html).lower()


def test_validate_slide_length_invalid_becomes_auto() -> None:
    assert validate_slide_length("nope") == "auto"
    assert validate_slide_length("short") == "short"


def test_validate_sources_list_rejects_unknown_type() -> None:
    with pytest.raises(ValueError, match="unknown type"):
        validate_sources_list([{"type": "intake", "slide_length": "auto"}])


def test_resolve_sources_prepends_intake_and_expands_url() -> None:
    with patch("traning_app.engine.ingest.intake.fetch_url_text", return_value="Page body"):
        out = resolve_sources_for_job(
            {
                "slide_length": "short",
                "role": "design",
                "language": "tr",
                "tier": "pro",
                "sources": [{"type": "url", "url": "https://example.com/doc"}],
            }
        )
    assert out[0]["type"] == "intake"
    assert out[0]["slide_length"] == "short"
    assert out[0]["role"] == "design"
    assert out[1]["type"] == "url"
    assert out[1]["text"] == "Page body"


def test_build_unified_context_intake_block() -> None:
    ctx = build_unified_context(
        [
            {"type": "intake", "slide_length": "medium", "role": "sales", "language": "en"},
            {"type": "prompt", "text": "Focus on onboarding."},
        ]
    )
    assert "intake" in ctx
    assert "slide_length" in ctx
    assert "sales" in ctx
    assert "onboarding" in ctx
