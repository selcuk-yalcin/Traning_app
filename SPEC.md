# Traning_app — Technical Specification

**Version:** 0.2  
**Scope:** Multimodal, agentic **presentation generation engine** for **education and training** use cases.  
**Out of scope for this repo:** Full product UI, user administration, billing — handled by [`admin_pan`](https://github.com/selcuk-yalcin/admin_pan) (Git submodule at `./admin_pan`).

---

## 1. Purpose

Build backend logic that turns **natural-language instructions plus optional documents and images** into a structured slide deck, with:

- Transparent **multi-step agent progress** (planning → research/synthesis → per-slide generation → layout).
- **Multiple models** (LLM + vision / OCR) behind a single **router** with tiers (e.g. Standard / Pro / Ultra).
- **Reading visuals**: describe images, extract text where needed, and suggest **safe regions** for overlaid text so teaching content stays legible.
- A stable machine-readable **deck representation** and **PowerPoint export**.

Reference UX patterns (not implemented verbatim here): prompt + file upload, outline generation, slide editor with Export as PPT — similar in spirit to tools like [presentations.ai](https://app.presentations.ai).

---

## 2. Repository boundaries

| Responsibility | This repo (`Traning_app`) | `admin_pan` submodule |
|----------------|---------------------------|-------------------------|
| Orchestration, ingest, generation, PPTX | Yes | No |
| API keys, org/workspace admin, end-user auth UI | Via integration contract | Yes |
| Deck/project listing in production UI | Consumes APIs | Primary owner |
| Optional thin demo UI for engine testing | Allowed | — |

This repository must remain **importable as a service/library**: clear package boundaries, configuration via environment variables, no hard dependency on admin UI internals.

---

## 3. Functional requirements

### 3.1 Inputs

- **Text prompt:** goals, audience, tone, language (fixed or auto-detect).
- **Files:** PDF (papers, curricula, notes), images (diagrams, boards, photos).
- **Controls:** target slide length band, model tier, optional “role” or persona for tone (e.g. instructor, instructional designer).

### 3.2 Processing

- **PDF:** extract text; if scan-heavy, rasterize pages and run OCR; attach provenance (page ranges).
- **Images:** validate type/size; generate thumbnails; run **VLM** for summary and optional **text-safe zones**; optional dedicated OCR for dense text.
- **Unified context:** merge all sources into chunked, attributed context for downstream agents.

### 3.3 Agent pipeline

Minimum logical stages (each emits **events** for UI streaming):

1. **Planning / “thinking”** — decompose topic, propose outline and slide roles (intro, concept, comparison, summary, quiz optional).
2. **Research / synthesis** — consolidate facts from context only (external web search is optional / later phase).
3. **Slide generation** — for each slide, produce structured blocks (title, bullets, table rows, image slots, speaker notes optional).
4. **Layout hints** — map content to template slots and theme tokens (colors, fonts).

State machine (informative): `idle` → `planning` → `research` → `generating` → `layout` → `done` | `failed`.

### 3.4 Outputs

- **Deck JSON (canonical):** versioned schema — slides, blocks, styles, assets references.
- **PPTX file:** generated from Deck JSON via a dedicated exporter; layouts aligned with a **finite template set** in MVP.
- **Progress stream:** SSE or WebSocket (or poll fallback) with structured events (`stage`, `detail`, `progress`, `slide_index`, `error_code`).

### 3.5 Education-specific behaviour

- Prefer **clear learning progression**: objectives early, concepts before details, recap and optional **check-your-understanding** slide.
- Terminology consistency within a run (optional lightweight glossary pass).
- Support multilingual delivery when language is set or detected.

---

## 4. Multimodal and multi-model requirements

### 4.1 Vision and “reading over images”

- **VLM calls** must support: short description, key entities, and simple **region hints** (e.g. quadrants or bounding boxes normalized 0–1) for text placement.
- **Cost controls:** max images per job, max pixels per image, configurable caps per tier.

### 4.2 Model router

- Single internal API abstracting providers: `complete_text`, `complete_vision` (text + one or more images).
- **Tier mapping:** configuration maps `standard | pro | ultra` to `{provider, model_id, limits}` with fallback rules.
- No provider-specific logic leaking into orchestration beyond adapter modules.

---

## 5. External interfaces (normative for implementers)

- **HTTP API** (OpenAPI recommended): e.g. `POST /presentations/generate`, `GET /presentations/{id}/events`, `GET /presentations/{id}/deck`, `GET /presentations/{id}/export/pptx`.
- **Authentication:** validate tokens or service secrets agreed with `admin_pan`; reject unauthenticated calls.
- **Quotas:** honor headers or side-car responses from admin services when specified.

Exact JSON Schemas for Deck and events are defined in code/docs alongside implementation (see project TODO).

---

## 6. Non-functional requirements

- **Latency:** generation may be long-running; use async jobs and streaming events.
- **Reliability:** persist partial results where useful; idempotent job identifiers.
- **Security:** file type/size validation; sanitize extracted text passed back into prompts; secrets only via env.
- **Observability:** structured logs with `run_id`, timings, token and vision-call counts.

---

## 7. MVP vs later

**MVP**

- Text + PDF + images ingest; VLM + OCR path for scans.
- Orchestrator with streaming stages; Deck JSON v1; PPTX export for a **small** template library.
- Router with two tiers minimum and hard budgets.

**Later**

- Web search or citation tooling for research stage.
- Richer layout engine and template marketplace metadata.
- Real-time collaborative editing (out of scope for this engine).

---

## 8. Risks

- PPTX parity with complex web layouts is limited — scope templates explicitly.
- Multimodal costs — enforce caps and surface estimates to `admin_pan` when integrated.

---

## 9. Submodule

- `admin_pan` at repository root: `https://github.com/selcuk-yalcin/admin_pan.git`  
- Clone with: `git clone --recurse-submodules …` or `git submodule update --init --recursive`.

---

*Maintain this file as the authoritative English specification for the Traning_app engine.*
