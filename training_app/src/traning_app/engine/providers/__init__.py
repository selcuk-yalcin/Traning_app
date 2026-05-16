"""Backward-compatible shims — prefer ``traning_app.engine.agents``."""

from traning_app.engine.agents import (
    complete_text,
    describe_image,
    generate_slide_image,
    resolve_model,
    search_photos,
    synthesize,
)

__all__ = [
    "complete_text",
    "resolve_model",
    "describe_image",
    "generate_slide_image",
    "search_photos",
    "synthesize",
]
