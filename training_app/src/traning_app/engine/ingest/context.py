"""Merge prompts, PDF text, URL text, image summaries into one context document."""

from __future__ import annotations

from traning_app.engine.ingest.validation import assert_sources_size, sanitize_text


def build_unified_context(sources: list[dict]) -> str:
    """
    Build a single attributed context string for the research / LLM stages.

    Each source dict should include ``type``:

    - ``prompt`` — ``text``
    - ``pdf`` — ``text`` (extracted body), optional ``label`` / ``title``
    - ``url`` — ``text`` (normalized page text), optional ``url``
    - ``topic`` — ``headings`` (list[str]) minimal seed headings
    - ``image`` — ``summary`` (VLM or placeholder summary)
    - ``intake`` — UI metadata: ``slide_length``, optional ``role``, ``language``, ``tier``

    Engine duty (per plan): validate upstream; this function sanitizes and joins.
    """
    if not sources:
        return ""
    assert_sources_size(sources)
    parts: list[str] = []
    for i, src in enumerate(sources, start=1):
        stype = str(src.get("type") or "prompt").lower()
        header = f"### Source [{i}] type={stype}"
        if stype == "prompt":
            body = sanitize_text(str(src.get("text", "")))
            parts.append(f"{header}\n{body}")
        elif stype == "pdf":
            label = src.get("title") or src.get("label") or "pdf"
            body = sanitize_text(str(src.get("text", "")))
            parts.append(f"{header} label={label}\n{body}")
        elif stype == "url":
            url = src.get("url", "")
            body = sanitize_text(str(src.get("text", "")))
            parts.append(f"{header} url={url}\n{body}")
        elif stype == "topic":
            headings = src.get("headings") or []
            lines = "\n".join(f"- {sanitize_text(str(h), max_len=2000)}" for h in headings)
            parts.append(f"{header}\nTopic headings:\n{lines}")
        elif stype == "intake":
            lines = [
                f"- slide_length: {sanitize_text(str(src.get('slide_length') or 'auto'), max_len=64)}",
            ]
            if src.get("role"):
                lines.append(f"- role: {sanitize_text(str(src['role']), max_len=200)}")
            if src.get("language"):
                lines.append(f"- language: {sanitize_text(str(src['language']), max_len=64)}")
            if src.get("tier"):
                lines.append(f"- tier: {sanitize_text(str(src['tier']), max_len=64)}")
            parts.append(f"{header}\nAuthor / UI intake:\n" + "\n".join(lines))
        elif stype == "image":
            body = sanitize_text(str(src.get("summary", "")))
            parts.append(f"{header}\nImage summary:\n{body}")
        else:
            body = sanitize_text(str(src.get("text", src.get("body", ""))))
            parts.append(f"{header}\n{body}")
    return "\n\n".join(parts).strip()
