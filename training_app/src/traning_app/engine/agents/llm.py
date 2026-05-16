"""Text completion via OpenAI-compatible Chat Completions API."""

from __future__ import annotations

import json
from typing import Any

from traning_app.engine.agents.openrouter_client import resolve_api_credentials


def complete_text(
    messages: list[dict[str, str]],
    *,
    model: str,
    max_tokens: int = 4096,
    temperature: float = 0.4,
) -> str:
    """
    Call OpenAI-compatible ``/chat/completions``.

    ``messages`` items use ``role`` and ``content`` keys.
    """
    import httpx

    api_key, base, extra = resolve_api_credentials()
    url = f"{base}/chat/completions"
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
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
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected chat completions response: {data!r}") from e
