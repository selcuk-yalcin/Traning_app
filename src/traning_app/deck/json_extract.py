"""Extract a JSON object from LLM text (markdown fences tolerated)."""

from __future__ import annotations

import json
import re


def extract_json_object(text: str) -> dict:
    """Parse first JSON object from model output."""
    t = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", t, re.IGNORECASE)
    if fence:
        t = fence.group(1).strip()
    start = t.find("{")
    end = t.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("No JSON object found in model output")
    return json.loads(t[start : end + 1])
