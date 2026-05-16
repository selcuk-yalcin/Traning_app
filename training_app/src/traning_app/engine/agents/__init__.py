"""
Tek paket: üretim boru hattı, yönlendirme, görsel, tema, TTS, manifest.

Ağır bağımlılıklar (``python-pptx``) için alt modülden import edin::

    from traning_app.engine.agents.pptx_export import deck_to_pptx, deck_to_pptx_bytes
    from traning_app.engine.agents.html_export import deck_to_html, deck_to_html_string

Diğer kullanım::

    from traning_app.engine.agents import run_job, apply_theme_to_deck, complete_text
"""

from traning_app.engine.agents.audio_manifest import (
    AudioManifest,
    AudioSegment,
    manifest_from_deck_notes,
)
from traning_app.engine.agents.deck_theme import apply_theme_to_deck
from traning_app.engine.agents.image_stock import search_photos
from traning_app.engine.agents.image_synthetic import generate_slide_image
from traning_app.engine.agents.llm import complete_text
from traning_app.engine.agents.pipeline import run_job
from traning_app.engine.agents.router import resolve_model
from traning_app.engine.agents.theme import Theme, ThemeColors, ThemeFonts, load_theme
from traning_app.engine.agents.tts import synthesize
from traning_app.engine.agents.vision import describe_image

__all__ = [
    "run_job",
    "complete_text",
    "resolve_model",
    "describe_image",
    "generate_slide_image",
    "search_photos",
    "Theme",
    "ThemeColors",
    "ThemeFonts",
    "load_theme",
    "apply_theme_to_deck",
    "AudioManifest",
    "AudioSegment",
    "manifest_from_deck_notes",
    "synthesize",
]
