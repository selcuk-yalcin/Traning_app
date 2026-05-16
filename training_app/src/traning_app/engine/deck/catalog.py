"""Load template catalog (learning intent + prompt addenda)."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources

from pydantic import BaseModel, Field


class TemplateCatalogEntry(BaseModel):
    title: str
    audience: str | None = None
    duration_minutes: int | None = None
    assessment_style: str | None = None
    mandatory_topics: list[str] = Field(default_factory=list)
    system_prompt_addendum: str = ""


@lru_cache
def load_template_catalog() -> dict[str, TemplateCatalogEntry]:
    raw = (
        resources.files("traning_app")
        .joinpath("templates", "catalog.json")
        .read_text(encoding="utf-8")
    )
    data = json.loads(raw)
    return {k: TemplateCatalogEntry.model_validate(v) for k, v in data.items()}


def get_catalog_entry(template_id: str) -> TemplateCatalogEntry | None:
    return load_template_catalog().get(template_id)
