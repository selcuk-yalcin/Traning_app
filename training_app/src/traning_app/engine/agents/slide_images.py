"""Optional AI slide imagery (OpenRouter / DALL·E)."""

from __future__ import annotations

import base64
import logging

from traning_app.engine.agents.image_synthetic import generate_slide_image
from traning_app.engine.media.paths import job_dir

log = logging.getLogger(__name__)


def _image_prompt(slide: dict, deck: dict) -> str:
    meta = deck.get("meta") or {}
    title = str(slide.get("title") or meta.get("title") or "Training slide")
    stype = str(slide.get("type") or "content")
    bullets = slide.get("bullets") or []
    hint = ""
    if bullets:
        hint = "; key points: " + ", ".join(str(b) for b in bullets[:4])
    return (
        f"Workplace safety training slide ({stype}): {title}{hint}. "
        "Professional, clear, no text in image, suitable for 16:9 presentation."
    )


def enrich_deck_with_images(
    deck: dict,
    job_id: str,
    *,
    tier: str = "standard",
    max_images: int = 3,
) -> dict:
    """
    Add ``image_path`` (PNG on disk) to up to ``max_images`` slides without imagery.

    Targets ``title``, ``section``, and first ``bullets`` slides.
    """
    slides = deck.get("slides")
    if not isinstance(slides, list) or max_images <= 0:
        return deck

    img_dir = job_dir(job_id) / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    priority_types = ("title", "section", "bullets", "content")

    for i, slide in enumerate(slides):
        if count >= max_images or not isinstance(slide, dict):
            continue
        if slide.get("image_path") or slide.get("image_url"):
            continue
        stype = str(slide.get("type") or "content")
        if stype not in priority_types:
            continue
        prompt = _image_prompt(slide, deck)
        try:
            png = generate_slide_image(prompt, tier=tier)
            path = img_dir / f"slide_{i:03d}.png"
            path.write_bytes(png)
            slide["image_path"] = str(path.resolve())
            slide["image_mime"] = "image/png"
            count += 1
        except Exception as e:
            log.warning("Slide image %s skipped: %s", i, e)

    return deck
