"""PDF text extraction (Layer 1). Uses ``pypdf`` when available."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path


def extract_text_from_pdf(path: str | Path) -> str:
    """Read a PDF file from disk and return concatenated page text."""
    data = Path(path).read_bytes()
    return extract_text_from_pdf_bytes(data)


def extract_text_from_pdf_bytes(data: bytes) -> str:
    """Extract text from PDF bytes (upload / base64 pipeline)."""
    if not data:
        return ""
    try:
        from pypdf import PdfReader
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "PDF ingest requires the 'pypdf' package (see pyproject.toml dependencies)."
        ) from e

    reader = PdfReader(BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        if txt.strip():
            parts.append(txt.strip())
    return "\n\n".join(parts).strip()
