"""Size and sanity checks for ingest payloads (plan Layer 1)."""

from __future__ import annotations

import re

# Conservative defaults; tune via env later.
MAX_UNIFIED_CONTEXT_CHARS = 120_000
MAX_SINGLE_SOURCE_CHARS = 80_000


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
