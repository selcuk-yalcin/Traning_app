"""Layer 1 — normalize API/job ``request`` into ``sources`` for ``build_unified_context``."""

from __future__ import annotations

import base64
import binascii
import logging
from typing import Any

from traning_app.engine.ingest.constants import MAX_PDF_BYTES
from traning_app.engine.ingest.pdf import extract_text_from_pdf_bytes
from traning_app.engine.ingest.url import fetch_url_text
from traning_app.engine.ingest.validation import validate_slide_length, validate_sources_list

log = logging.getLogger(__name__)


def _expand_source(src: dict[str, Any]) -> dict[str, Any]:
    """Return a concrete source dict (pdf/url) ready for ``build_unified_context``."""
    st = str(src.get("type") or "prompt").lower()
    if st == "url" and src.get("url") and not str(src.get("text", "")).strip():
        try:
            text = fetch_url_text(str(src["url"]))
        except Exception as e:
            log.warning("URL fetch failed for %s: %s", src.get("url"), e)
            text = f"[URL fetch failed: {e}]"
        out = {**src, "type": "url", "text": text}
        return out
    if st == "pdf_base64":
        raw_b64 = str(src.get("data") or src.get("base64") or "")
        try:
            data = base64.b64decode(raw_b64, validate=True)
        except (binascii.Error, ValueError) as e:
            raise ValueError("Invalid base64 in pdf_base64 source.") from e
        if len(data) > MAX_PDF_BYTES:
            raise ValueError(f"PDF exceeds max size ({MAX_PDF_BYTES} bytes).")
        try:
            text = extract_text_from_pdf_bytes(data)
        except Exception as e:
            raise ValueError(f"PDF text extraction failed: {e}") from e
        label = src.get("filename") or src.get("label") or "upload.pdf"
        return {"type": "pdf", "text": text, "title": label}
    return dict(src)


def resolve_sources_for_job(request: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Build the ordered ``sources`` list for research / unified context.

    - Prepends an ``intake`` pseudo-source (slide length, role, language, tier) when any set.
    - Expands ``url`` (fetch if text empty) and ``pdf_base64`` → ``pdf`` with extracted text.
    """
    raw_sources = list(request.get("sources") or [])
    validate_sources_list(raw_sources)

    out: list[dict[str, Any]] = []
    slide_length = validate_slide_length(request.get("slide_length"))
    role = request.get("role")
    language = request.get("language")
    tier = request.get("tier")
    intake: dict[str, Any] = {"type": "intake", "slide_length": slide_length}
    if role:
        intake["role"] = str(role)[:128]
    if language:
        intake["language"] = str(language)[:32]
    if tier:
        intake["tier"] = str(tier)[:32]
    out.append(intake)

    for src in raw_sources:
        out.append(_expand_source(src))
    return out
