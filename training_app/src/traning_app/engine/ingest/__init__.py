"""Input normalization: PDF, URLs, images, prompts → unified context."""

from traning_app.engine.ingest.context import build_unified_context
from traning_app.engine.ingest.intake import resolve_sources_for_job
from traning_app.engine.ingest.validation import (
    assert_sources_size,
    sanitize_text,
    validate_slide_length,
    validate_sources_list,
)

__all__ = [
    "build_unified_context",
    "resolve_sources_for_job",
    "sanitize_text",
    "assert_sources_size",
    "validate_sources_list",
    "validate_slide_length",
]
