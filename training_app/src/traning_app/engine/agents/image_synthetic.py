"""Slide image generation — OpenAI Images API or OpenRouter chat+image."""

from __future__ import annotations

import base64
import json
import re
from typing import Any

from traning_app.config.settings import get_settings
from traning_app.engine.agents.openrouter_client import resolve_api_credentials, use_openrouter
from traning_app.engine.agents.router import resolve_image_model


def _png_from_data_url(url: str) -> bytes:
    if not url.startswith("data:"):
        raise RuntimeError("Expected base64 data URL from image model")
    _, _, payload = url.partition(",")
    return base64.standard_b64decode(payload)


def _extract_image_bytes(data: dict[str, Any]) -> bytes:
    try:
        message = data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected image chat response: {data!r}") from e
    images = message.get("images") or []
    for item in images:
        iu = item.get("image_url") or item.get("imageUrl") or {}
        url = iu.get("url") or ""
        if url:
            return _png_from_data_url(url)
    content = message.get("content")
    if isinstance(content, str):
        m = re.search(r"data:image/[^;]+;base64,[A-Za-z0-9+/=]+", content)
        if m:
            return _png_from_data_url(m.group(0))
    raise RuntimeError(f"No image in model response: {data!r}")


def generate_slide_image(
    prompt: str, *, model: str | None = None, tier: str = "standard"
) -> bytes:
    """
    Return PNG bytes for ``prompt``.

    With ``OPENROUTER_API_KEY``: ``/chat/completions`` + ``modalities: ["image"]``.
    Otherwise: OpenAI ``/images/generations`` (DALL·E class).
    """
    if use_openrouter():
        return _generate_via_openrouter(prompt, model=model, tier=tier)
    return _generate_via_openai_images(prompt, model=model)


def _generate_via_openrouter(
    prompt: str, *, model: str | None = None, tier: str = "standard"
) -> bytes:
    import httpx

    api_key, base, extra = resolve_api_credentials()
    mid = model or resolve_image_model(tier)
    url = f"{base}/chat/completions"
    payload: dict[str, Any] = {
        "model": mid,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Professional workplace safety training slide illustration, "
                    "clean and readable, no watermarks: "
                    + (prompt or "").strip()[:3500]
                ),
            }
        ],
        "modalities": ["image"],
        "image_config": {"aspect_ratio": "16:9", "image_size": "1K"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **extra,
    }
    with httpx.Client(timeout=180.0) as client:
        r = client.post(url, headers=headers, content=json.dumps(payload))
        r.raise_for_status()
        return _extract_image_bytes(r.json())


def _generate_via_openai_images(prompt: str, *, model: str | None = None) -> bytes:
    import httpx

    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured for image generation")

    mid = model or settings.openai_image_model
    base = settings.openai_base_url.rstrip("/")
    url = f"{base}/images/generations"
    payload: dict[str, Any] = {
        "model": mid,
        "prompt": (prompt or "").strip()[:4000],
        "n": 1,
        "size": "1024x1024",
        "response_format": "b64_json",
    }
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=180.0) as client:
        r = client.post(url, headers=headers, content=json.dumps(payload))
        r.raise_for_status()
        data = r.json()
    try:
        b64 = data["data"][0]["b64_json"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected images response: {data!r}") from e
    return base64.standard_b64decode(b64)
