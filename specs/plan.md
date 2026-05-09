# Product and architecture plan — Traning_app

**Aligned with:** [`SPEC.md`](../SPEC.md) (authoritative).

## Product goal

An **agentic, multimodal backend** that generates **education and training** slide decks from:

- A natural-language brief (audience, objectives, tone).
- Optional **PDFs** and **images** (diagrams, boards, scans).

The system must **read visuals** (vision-language models + OCR when needed), merge evidence into a single teaching-oriented context, run a **staged agent pipeline** with streamable progress, output **Deck JSON**, and produce **PPTX export**.

## Architecture baseline

- **Orchestrator:** state machine driving planning → research/synthesis → slide generation → layout hints; emits structured events for SSE/WebSocket clients.
- **Ingest:** PDF text extraction; image thumbnails and validation; VLM summaries and optional safe text-placement hints; unified chunked context with source attribution.
- **Model router:** tiered access (e.g. Standard / Pro / Ultra) to LLM + VLM adapters; budgets enforced per job.
- **Canonical artifact:** versioned **Deck JSON** consumed by an exporter and any UI (production UI lives outside this repo when integrated with `admin_pan`).

## Boundaries

- **This repo:** generation engine, schemas, export worker logic, integration hooks for auth/quota from admin services.
- **`admin_pan` submodule:** admin UX, user/org settings, and operational surfaces — not reimplemented here.

## Quality bar for education content

- Logical lesson flow (objectives → concepts → examples → recap; optional short check).
- Consistent terminology within a generation run when language is fixed.
