"""Deck JSON schema (canonical presentation model)."""

from traning_app.engine.deck.catalog import get_catalog_entry, load_template_catalog
from traning_app.engine.deck.loaders import list_builtin_template_ids, load_builtin_deck_template
from traning_app.engine.deck.schema import Deck, DeckMeta

__all__ = [
    "list_builtin_template_ids",
    "load_builtin_deck_template",
    "load_template_catalog",
    "get_catalog_entry",
    "Deck",
    "DeckMeta",
]
