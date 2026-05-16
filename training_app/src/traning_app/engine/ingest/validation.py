"""Size and sanity checks for ingest payloads (plan Layer 1)."""

from __future__ import annotations

import re

from traning_app.engine.ingest.constants import (
    ALLOWED_SOURCE_TYPES,
    MAX_BASE64_PDF_CHARS,
    MAX_PDF_BYTES,
    MAX_SINGLE_SOURCE_CHARS,
    MAX_SOURCES_IN_JOB,
    MAX_UNIFIED_CONTEXT_CHARS,
    SLIDE_LENGTH_ALIASES,
)


def sanitize_text(text: str, *, max_len: int = MAX_SINGLE_SOURCE_CHARS) -> str:
    """Strip control characters and NUL; cap length for prompt safety."""
    if not text:
        return ""
    t = text.replace("\x00", "")
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", t)
    if len(t) > max_len:
        t = t[: max_len - 20] + "\n…[truncated]"
    return t


def assert_sources_size(sources: list[dict]) -> None:
    """Raise ValueError if aggregate text would exceed unified context cap."""
    total = 0
    for s in sources:
        if "text" in s and isinstance(s["text"], str):
            total += len(s["text"])
        if "summary" in s and isinstance(s["summary"], str):
            total += len(s["summary"])
        if s.get("type") == "topic" and isinstance(s.get("headings"), list):
            total += sum(len(str(h)) for h in s["headings"])
    if total > MAX_UNIFIED_CONTEXT_CHARS:
        raise ValueError(
            f"Sources exceed max unified context size ({MAX_UNIFIED_CONTEXT_CHARS} chars)."
        )


def validate_slide_length(value: object) -> str:
    v = str(value or "auto").strip().lower()
    if v not in SLIDE_LENGTH_ALIASES:
        return "auto"
    return v


def validate_sources_list(sources: list[dict]) -> None:
    """Structural checks before expansion (URL fetch, PDF decode)."""
    if len(sources) > MAX_SOURCES_IN_JOB:
        raise ValueError(
            f"Too many sources ({len(sources)}); max is {MAX_SOURCES_IN_JOB}."
        )
    for i, s in enumerate(sources):
        if not isinstance(s, dict):
            raise ValueError(f"Source[{i}] must be an object.")
        st = str(s.get("type") or "prompt").lower()
        if st not in ALLOWED_SOURCE_TYPES:
            raise ValueError(
                f"Source[{i}] has unknown type {st!r}; allowed: {sorted(ALLOWED_SOURCE_TYPES)}"
            )
        if st == "url":
            if not (s.get("url") or s.get("text")):
                raise ValueError(f"Source[{i}] (url) needs 'url' or pre-filled 'text'.")
        elif st == "pdf":
            if not s.get("text"):
                raise ValueError(f"Source[{i}] (pdf) needs extracted 'text'.")
        elif st == "pdf_base64":
            raw_b64 = s.get("data") or s.get("base64")
            if not isinstance(raw_b64, str) or not raw_b64.strip():
                raise ValueError(f"Source[{i}] (pdf_base64) needs non-empty 'data' (base64).")
            if len(raw_b64) > MAX_BASE64_PDF_CHARS:
                raise ValueError("pdf_base64 payload is too large.")
        elif st == "prompt":
            if not str(s.get("text", "")).strip():
                raise ValueError(f"Source[{i}] (prompt) needs non-empty 'text'.")
        elif st == "topic":
            h = s.get("headings")
            if not isinstance(h, list) or not h:
                raise ValueError(f"Source[{i}] (topic) needs non-empty 'headings' list.")
        elif st == "image":
            if not str(s.get("summary", "")).strip():
                raise ValueError(f"Source[{i}] (image) needs non-empty 'summary'.")
