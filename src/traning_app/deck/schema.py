"""Pydantic models for Deck JSON v1 — extend as SPEC solidifies."""

from pydantic import BaseModel


class DeckMeta(BaseModel):
    title: str
    language: str | None = None
    template_id: str | None = None


class Deck(BaseModel):
    version: str = "1"
    meta: DeckMeta
    slides: list[dict] = []
