"""Build .pptx from Deck JSON (python-pptx)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from pptx import Presentation

# Default Office theme layout indices (empty presentation)
_LAYOUT_TITLE = 0  # Title Slide
_LAYOUT_TITLE_CONTENT = 1  # Title and Content
_LAYOUT_SECTION = 2  # Section Header
_LAYOUT_TWO_CONTENT = 3  # Two Content


def _build_presentation(
    deck: dict,
    *,
    template_path: str | Path | None = None,
) -> Presentation:
    if template_path and Path(template_path).is_file():
        prs = Presentation(str(template_path))
    else:
        prs = Presentation()

    slides_spec: list[dict[str, Any]] = list(deck.get("slides") or [])
    meta = deck.get("meta") or {}
    if not slides_spec:
        slides_spec = [
            {
                "type": "title",
                "title": meta.get("title") or "Untitled",
                "subtitle": "",
            }
        ]

    for spec in slides_spec:
        stype = spec.get("type") or "bullets"
        if stype == "title":
            _add_title_slide(prs, spec)
        elif stype == "section":
            _add_section_slide(prs, spec)
        elif stype in ("bullets", "content"):
            _add_content_slide(prs, spec)
        elif stype == "two_column":
            _add_two_column_slide(prs, spec)
        else:
            _add_content_slide(prs, {**spec, "type": "content"})

        notes = spec.get("notes")
        if notes:
            last = prs.slides[-1]
            last.notes_slide.notes_text_frame.text = str(notes)

    return prs


def deck_to_pptx(
    deck: dict,
    output_path: str,
    *,
    template_path: str | Path | None = None,
) -> None:
    """
    Render ``deck`` (Deck JSON v1) to a PowerPoint file.

    Each slide dict supports:

    - ``type`` ``title``: ``title``, optional ``subtitle``.
    - ``type`` ``section``: ``title`` (section header layout).
    - ``type`` ``bullets`` | ``content``: ``title``, ``bullets`` (list[str])
      and/or ``body`` (plain paragraph).
    - ``type`` ``two_column``: ``title``, ``left`` / ``right`` (plain text).
    - Optional ``notes``: speaker notes string.

    If ``template_path`` points to an existing ``.pptx``, it is loaded as the
    base presentation (custom masters). Prefer **empty** decks so slides are
    only those produced here; otherwise new slides are appended after existing
    ones.

    If ``slides`` is empty, a single title slide is created from ``meta.title``.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = _build_presentation(deck, template_path=template_path)
    prs.save(str(out.resolve()))


def deck_to_pptx_bytes(
    deck: dict,
    *,
    template_path: str | Path | None = None,
) -> bytes:
    """Return ``.pptx`` file bytes (for HTTP responses)."""
    prs = _build_presentation(deck, template_path=template_path)
    bio = BytesIO()
    prs.save(bio)
    return bio.getvalue()


def _add_title_slide(prs: Presentation, spec: dict[str, Any]) -> None:
    layout = prs.slide_layouts[_LAYOUT_TITLE]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = str(spec.get("title") or "")
    subtitle = spec.get("subtitle") or ""
    if subtitle and len(slide.placeholders) > 1:
        slide.placeholders[1].text = str(subtitle)


def _add_section_slide(prs: Presentation, spec: dict[str, Any]) -> None:
    layout = prs.slide_layouts[_LAYOUT_SECTION]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = str(spec.get("title") or "")


def _add_content_slide(prs: Presentation, spec: dict[str, Any]) -> None:
    layout = prs.slide_layouts[_LAYOUT_TITLE_CONTENT]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = str(spec.get("title") or "")

    body = slide.placeholders[1]
    tf = body.text_frame

    bullets = spec.get("bullets")
    body_text = spec.get("body")
    if bullets and isinstance(bullets, list) and len(bullets) > 0:
        tf.text = str(bullets[0])
        for line in bullets[1:]:
            p = tf.add_paragraph()
            p.text = str(line)
            p.level = 0
    elif body_text:
        tf.text = str(body_text)
    else:
        tf.text = ""


def _add_two_column_slide(prs: Presentation, spec: dict[str, Any]) -> None:
    layout = prs.slide_layouts[_LAYOUT_TWO_CONTENT]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = str(spec.get("title") or "")
    left = str(spec.get("left") or "")
    right = str(spec.get("right") or "")
    if len(slide.placeholders) > 2:
        slide.placeholders[1].text = left
        slide.placeholders[2].text = right
