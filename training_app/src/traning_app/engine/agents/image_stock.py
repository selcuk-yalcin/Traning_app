"""Unsplash stock photo search (Layer 2 — stock assets)."""

from __future__ import annotations

import json
from typing import Any

from traning_app.config.settings import get_settings


def search_photos(query: str, *, limit: int = 5) -> list[dict[str, Any]]:
    """
    Search Unsplash and return a list of result dicts (id, urls, description, alt_description).

    Requires ``UNSPLASH_ACCESS_KEY``. Returns an empty list if the key is not set.
    """
    import httpx

    settings = get_settings()
    key = settings.unsplash_access_key
    if not key:
        return []

    q = (query or "").strip()[:200]
    if not q:
        return []

    lim = max(1, min(30, int(limit)))
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {key}"}
    params = {"query": q, "per_page": lim, "orientation": "landscape"}
    with httpx.Client(timeout=30.0) as client:
        r = client.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()

    out: list[dict[str, Any]] = []
    for item in data.get("results") or []:
        out.append(
            {
                "id": item.get("id"),
                "description": item.get("description"),
                "alt_description": item.get("alt_description"),
                "urls": item.get("urls") or {},
                "user": (item.get("user") or {}).get("name"),
            }
        )
    return out
