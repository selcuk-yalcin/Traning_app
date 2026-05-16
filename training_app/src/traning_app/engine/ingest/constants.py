"""Layer 1 — conservative limits (tune via settings later)."""

from __future__ import annotations

MAX_UNIFIED_CONTEXT_CHARS = 120_000
MAX_SINGLE_SOURCE_CHARS = 80_000
MAX_SOURCES_IN_JOB = 32
MAX_PDF_BYTES = 15 * 1024 * 1024
MAX_URL_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_BASE64_PDF_CHARS = 22 * 1024 * 1024  # ~16 MiB decoded upper bound

ALLOWED_SOURCE_TYPES = frozenset(
    {"prompt", "pdf", "url", "topic", "image", "pdf_base64"}
)

SLIDE_LENGTH_ALIASES = frozenset({"auto", "summary", "short", "medium", "long"})
