"""Route tier (standard / pro / ultra) to concrete models and budgets."""

from typing import Any


def resolve_model(tier: str, modality: str) -> dict[str, Any]:
    raise NotImplementedError
