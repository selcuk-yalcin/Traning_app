"""Fetch and normalize URL content (Layer 1 — respect robots/TOS in production)."""

from __future__ import annotations

from urllib.parse import urlparse

from traning_app.engine.ingest.constants import MAX_URL_RESPONSE_BYTES
from traning_app.engine.ingest.html_plain import html_to_plain


def fetch_url_text(url: str, *, timeout: float = 20.0) -> str:
    """
    GET ``url`` and return plain text suitable for unified context.

    MVP: HTML pages only; rejects non-http(s) schemes. Caller should cache/rate-limit in prod.
    """
    import httpx

    raw = (url or "").strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http(s) URLs are allowed for ingest.")
    headers = {
        "User-Agent": "TraningApp-Ingest/1.0 (+https://github.com/selcuk-yalcin/Traning_app)",
        "Accept": "text/html,application/xhtml+xml;q=0.9,text/plain;q=0.8,*/*;q=0.5",
    }
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        r = client.get(raw, headers=headers)
        r.raise_for_status()
        body = r.content
        ctype = (r.headers.get("content-type") or "").lower()
    if len(body) > MAX_URL_RESPONSE_BYTES:
        raise ValueError(
            f"URL response exceeds max size ({MAX_URL_RESPONSE_BYTES} bytes)."
        )
    text = body.decode("utf-8", errors="replace")
    if "html" in ctype or text.lstrip().lower().startswith("<!doctype html") or "<html" in text[:2000].lower():
        return html_to_plain(text)
    return text.strip()
