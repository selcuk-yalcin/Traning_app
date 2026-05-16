"""Backward-compatible shim — prefer ``traning_app.engine.agents.*`` submodules."""

from traning_app.engine.agents.html_export import deck_to_html, deck_to_html_string
from traning_app.engine.agents.pptx_export import deck_to_pptx, deck_to_pptx_bytes

__all__ = [
    "deck_to_pptx",
    "deck_to_pptx_bytes",
    "deck_to_html",
    "deck_to_html_string",
]
