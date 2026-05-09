# Tech stack — Traning_app engine

**Scope:** This document describes the **intended stack for the Traning_app presentation engine** in this repository. It does not describe all technologies inside the [`admin_pan`](../admin_pan/) submodule.

## Language and packaging

- **Python 3.12+** for orchestration, ingest, workers, and PPTX generation.
- Package layout TBD (`src/` or `packages/`); pin dependencies via `pyproject.toml` or `requirements.txt` when implementation starts.

## API and realtime

- **HTTP API:** FastAPI or equivalent for REST + optional **SSE** for job progress.
- **Long jobs:** Redis (or compatible broker) + worker process (**Celery**, **RQ**, or **arq**).

## AI layer

- **LLM** and **VLM** via provider adapters (OpenAI-compatible APIs acceptable).
- Optional **OCR** for scanned PDFs (dedicated OCR lib or cloud API behind an interface).
- **Router module:** maps quality tier → model IDs, temperature, max tokens, vision caps.

## Documents and media

- PDF: text extraction libraries (e.g. pypdf / pdfminer); rendering + OCR for image-only pages as needed.
- Images: Pillow or equivalent for resize/thumbnail; strict MIME and size limits.

## Export

- **python-pptx** (or successor) for `.pptx` from Deck JSON; template-driven layouts for MVP.

## Storage

- Ephemeral upload store (local or S3-compatible); no requirement for this repo to own long-term user asset catalog (may delegate to admin stack).

## Deployment (informative)

- Container-friendly API + worker split; secrets via environment variables only.
