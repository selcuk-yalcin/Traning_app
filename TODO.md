# Traning_app — Comprehensive TODO

Multi-model, agentic education presentation engine. Admin UI lives in [admin_pan](https://github.com/selcuk-yalcin/admin_pan); this list covers **engine + integration + export** only.

---

## 0 — Repository and submodule

- [ ] Create the `Traning_app` (or chosen name) repo on GitHub and attach local `origin`.
- [ ] `git submodule add https://github.com/selcuk-yalcin/admin_pan.git admin_pan` (at repo root, not under `integrations/`).
- [ ] `.gitignore` (Python, venv, `.env`, IDE, temp upload dirs).
- [ ] `.env.example` for development (variable names only; no real secrets).

---

## 1 — Contracts (schema)

- [ ] **Deck JSON v1** schema: presentation meta, slide array, per-slide blocks (title, body, table, image placeholder, chart data).
- [ ] **Agent event schema** (SSE/WebSocket): `stage`, `detail`, `progress`, `slide_index`, `error_code`.
- [ ] **Request/response API** (OpenAPI or equivalent): `POST /presentations/generate`, `GET /presentations/{id}/events`, `GET /presentations/{id}/deck`.
- [ ] Model tier mapping: `tier` → `{provider, model_id, max_tokens}` configuration.

---

## 2 — Ingest (multimodal)

- [ ] Text prompt validation and language detection (or “Auto”).
- [ ] PDF: text extraction (pypdf/pdfminer); optional page render + OCR pipeline.
- [ ] Images: strip EXIF; size limits; thumbnails.
- [ ] Image “reading”: VLM summaries, object/scene tags, **safe regions for text** (simple bounding boxes or grid hints).
- [ ] Unified context document: single “context document” from all sources (chunks + source attribution).

---

## 3 — Orchestrator (agent orchestration)

- [ ] State machine: `idle` → `planning` → `research` → `generating` → `layout` → `done` / `failed`.
- [ ] “Thinking” sub-tasks: topic decomposition, narrative structure, section titles (aligned with timeline UI).
- [ ] Apply slide-count policy: “Let AI decide” / short / medium / long.
- [ ] Research phase: without external search, use ingest context + LLM only; add tooling in a later phase if needed.
- [ ] Error handling: partial deck persistence, retries, meaningful `error_code` for clients.

---

## 4 — Model router (multi-model)

- [ ] Single interface: `complete_text`, `complete_vision` (text + image URL or base64).
- [ ] Provider adapters: at least one LLM + one VLM (e.g. OpenAI-compatible API plus a second provider).
- [ ] Tier: Standard / Pro / Ultra → model and parameter selection.
- [ ] Rate limiting and cost estimation (aligned with admin_pan quotas).

---

## 5 — Content and slide generation

- [ ] Outline generation (numbered sections; reference outline screen).
- [ ] Per slide: title, bullets, table, structured output for comparison layouts.
- [ ] Education tone: learning objectives, short recap, optional quiz slide type.
- [ ] “New slide from prompt”: regeneration endpoint with narrow context for a single slide.

---

## 6 — Layout and theme

- [ ] Theme tokens: colors, font family, spacing (JSON).
- [ ] Simple layout engine: template ID → block regions; truncation rules for overflow.
- [ ] Template catalog (education-heavy) — metadata + preview image path.

---

## 7 — Export PPTX

- [ ] Deck JSON → `.pptx` via **python-pptx** (or chosen library).
- [ ] Title/body, tables, bullets; image placement and aspect ratio.
- [ ] Download URL or synchronous stream; async job for large files.

---

## 8 — Infrastructure and observability

- [ ] Worker queue for long generation jobs.
- [ ] Structured logging (`run_id`, user id from admin_pan).
- [ ] Basic metrics: duration, tokens, vision call count.

---

## 9 — admin_pan integration

- [ ] Authentication: shared secret or JWT contract (finalize with admin_pan).
- [ ] Per-project/user quotas and API key management remain in admin_pan.
- [ ] Optional **minimal** callbacks from this service to admin_pan: usage reports, error counts.

---

## 10 — Quality and security

- [ ] Prompt injection and malicious file checks (type, size, sanity).
- [ ] Optional PII masking rules at ingest.
- [ ] Unit tests: schema validation, router mocks, PPTX smoke test.
- [ ] Integration test: sample PDF + image → short end-to-end deck.

---

## 11 — Optional later phases

- [ ] External “research” tools (web search) with source links on slides.
- [ ] Static HTML export for “Present” mode.
- [ ] Collaboration on the same deck: operational split between admin_pan and a separate realtime layer.

---

*Track progress by checking items off in `TODO.md` at repo root.*
