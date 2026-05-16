"""Vision-language calls for image understanding (OpenAI-compatible multimodal chat)."""

from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path

from traning_app.engine.agents.openrouter_client import resolve_api_credentials
from traning_app.engine.agents.router import resolve_model


def describe_image(image_path: str, *, model: str | None = None, tier: str = "standard") -> str:
    """
    Return a concise description of ``image_path`` for training / accessibility context.

    Uses ``/chat/completions`` with an ``image_url`` (base64 data URL). Uses OpenRouter when configured.
    """
    import httpx

    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    api_key, base_default, extra = resolve_api_credentials()

    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or "image/jpeg"
    raw = path.read_bytes()
    if len(raw) > 20 * 1024 * 1024:
        raise ValueError("Image file exceeds 20 MiB limit.")
    b64 = base64.standard_b64encode(raw).decode("ascii")
    data_url = f"data:{mime};base64,{b64}"

    cfg = resolve_model(tier, "vision")
    mid = model or cfg["model_id"]
    base = str(cfg.get("base_url") or base_default).rstrip("/")
    url = f"{base}/chat/completions"

    messages = [
        {
            "role": "system",
            "content": (
                "You help build workplace training decks. Describe the image for slide notes: "
                "main subjects, any safety-relevant elements, text or diagrams worth citing, "
                "and suggested on-slide caption (one sentence)."
            ),
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this image in 2–6 short paragraphs, plain text.",
                },
                {"type": "image_url", "image_url": {"url": data_url, "detail": "low"}},
            ],
        },
    ]
    payload: dict = {
        "model": mid,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **extra,
    }
    with httpx.Client(timeout=120.0) as client:
        r = client.post(url, headers=headers, content=json.dumps(payload))
        r.raise_for_status()
        data = r.json()
    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected vision chat response: {data!r}") from e
