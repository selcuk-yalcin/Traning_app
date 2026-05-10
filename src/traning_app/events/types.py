"""Structured agent events per SPEC."""

from typing import Any

from pydantic import BaseModel


class AgentEvent(BaseModel):
    stage: str
    detail: str | None = None
    progress: float | None = None
    slide_index: int | None = None
    error_code: str | None = None
    payload: dict[str, Any] | None = None
