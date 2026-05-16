"""Map Deck JSON through theme tokens (minimal layout pass before export)."""

from __future__ import annotations

from copy import deepcopy

from traning_app.engine.agents.theme import load_theme


def apply_theme_to_deck(deck: dict, *, theme_name: str = "default") -> dict:
    """
    Attach ``meta.theme`` (JSON-serializable) for HTML/PPTX consumers.

    Future: map slide blocks to template regions, image slots, truncation rules.
    """
    theme = load_theme(theme_name)
    out = deepcopy(deck)
    meta = out.setdefault("meta", {})
    meta["theme"] = theme.model_dump()
    return out
