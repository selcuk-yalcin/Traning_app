"""Theme tokens (plan Layer 2 — themes and templates)."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources

from pydantic import BaseModel


class ThemeColors(BaseModel):
    primary: str = "#1e3a5f"
    accent: str = "#c2410c"
    background: str = "#f8fafc"
    text: str = "#0f172a"


class ThemeFonts(BaseModel):
    heading: str = "Calibri"
    body: str = "Calibri"


class Theme(BaseModel):
    name: str = "default"
    colors: ThemeColors = ThemeColors()
    fonts: ThemeFonts = ThemeFonts()


@lru_cache
def load_theme(name: str = "default") -> Theme:
    path = resources.files("traning_app").joinpath("templates", "themes", f"{name}.json")
    raw = path.read_text(encoding="utf-8")
    return Theme.model_validate(json.loads(raw))
