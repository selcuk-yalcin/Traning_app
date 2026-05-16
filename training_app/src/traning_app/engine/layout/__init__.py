"""Backward-compatible shim — prefer ``traning_app.engine.agents``."""

from traning_app.engine.agents import (
    Theme,
    ThemeColors,
    ThemeFonts,
    apply_theme_to_deck,
    load_theme,
)

__all__ = [
    "Theme",
    "ThemeColors",
    "ThemeFonts",
    "load_theme",
    "apply_theme_to_deck",
]
