"""HTML → rough plain text for URL ingest (no external deps)."""

from __future__ import annotations

import re


def html_to_plain(html: str, *, max_out: int = 500_000) -> str:
    """Drop script/style, strip tags, collapse whitespace."""
    if not html:
        return ""
    t = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    t = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", t)
    t = re.sub(r"(?is)<!--.*?-->", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > max_out:
        t = t[: max_out - 20] + " …[truncated]"
    return t
