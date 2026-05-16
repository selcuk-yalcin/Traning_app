"""Load bundled Deck JSON templates by id."""

from __future__ import annotations

import json
from importlib import resources


def list_builtin_template_ids() -> list[str]:
    """Return ids for JSON files shipped under ``templates/decks/``."""
    root = resources.files("traning_app").joinpath("templates", "decks")
    if not root.is_dir():
        return []
    out: list[str] = []
    for p in root.iterdir():
        if p.suffix.lower() == ".json":
            out.append(p.stem)
    return sorted(out)


def load_builtin_deck_template(template_id: str) -> dict:
    """Load a bundled starter deck (JSON). ``template_id`` is the filename stem."""
    path = resources.files("traning_app").joinpath(
        "templates", "decks", f"{template_id}.json"
    )
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw)
