"""Optional reveal.js / static HTML export."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def _slide_to_html(spec: dict[str, Any]) -> str:
    stype = spec.get("type") or "bullets"
    title = html.escape(str(spec.get("title") or ""))
    if stype == "section":
        return f"<section><h1>{title}</h1></section>"
    if stype == "title":
        sub = html.escape(str(spec.get("subtitle") or ""))
        body = f"<h1>{title}</h1><p class=\"subtitle\">{sub}</p>"
        notes = spec.get("notes")
        if notes:
            body += f"<aside class=\"notes\"><p>{html.escape(str(notes))}</p></aside>"
        return f"<section>{body}</section>"
    parts = [f"<h2>{title}</h2>"]
    if stype == "two_column":
        left = html.escape(str(spec.get("left") or "")).replace("\n", "<br/>")
        right = html.escape(str(spec.get("right") or "")).replace("\n", "<br/>")
        parts.append(
            f'<div class="cols"><div class="col">{left}</div>'
            f'<div class="col">{right}</div></div>'
        )
    else:
        bullets = spec.get("bullets")
        if bullets and isinstance(bullets, list):
            lis = "".join(f"<li>{html.escape(str(b))}</li>" for b in bullets)
            parts.append(f"<ul>{lis}</ul>")
        elif spec.get("body"):
            parts.append(f"<p>{html.escape(str(spec['body']))}</p>")
    notes = spec.get("notes")
    if notes:
        parts.append(
            f"<aside class=\"notes\"><p>{html.escape(str(notes))}</p></aside>"
        )
    return f"<section>{''.join(parts)}</section>"


def _build_html_document(deck: dict) -> str:
    """Single-file HTML using Reveal.js CDN (plan Layer 2 / RV)."""
    meta = deck.get("meta") or {}
    title = html.escape(str(meta.get("title") or "Deck"))
    slides_html = "".join(
        _slide_to_html(s) for s in (deck.get("slides") or []) if isinstance(s, dict)
    )
    deck_json = html.escape(json.dumps(deck, ensure_ascii=False))
    return f"""<!DOCTYPE html>
<html lang="{html.escape(str(meta.get("language") or "en"))}">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.css"/>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/theme/white.css"/>
  <style>
    .reveal .slides section {{ text-align: left; font-size: 0.75em; }}
    .cols {{ display: flex; gap: 2rem; }}
    .col {{ flex: 1; }}
    .subtitle {{ opacity: 0.85; }}
    aside.notes {{ font-size: 0.5em; opacity: 0.7; margin-top: 1rem; }}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      {slides_html}
    </div>
  </div>
  <script type="application/json" id="deck-json">{deck_json}</script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.js"></script>
  <script>Reveal.initialize({{ hash: true, slideNumber: true }});</script>
</body>
</html>
"""


def deck_to_html(deck: dict, output_path: str) -> None:
    """Write HTML deck to ``output_path``."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_build_html_document(deck), encoding="utf-8")


def deck_to_html_string(deck: dict) -> str:
    """Return HTML document as a string (tests / inline responses)."""
    return _build_html_document(deck)
