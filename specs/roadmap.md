# Execution roadmap — Traning_app

**Source of tasks:** root [`TODO.md`](../TODO.md).  
**Requirements:** [`SPEC.md`](../SPEC.md).

This file is a **priority lens** only; detailed checkboxes stay in `TODO.md`.

## Phase A — Foundation

- Repository hygiene: submodule `admin_pan`, `.env.example`, CI stub optional.
- Deck JSON v1 + agent event schema + OpenAPI sketch for generate/events/deck/export.

## Phase B — Ingest and models

- PDF and image pipelines; unified context document.
- Model router with at least one LLM and one VLM path and tier mapping.

## Phase C — Orchestrator

- Full state machine with streaming events; slide-count policies.
- Slide-level generation and layout hints tied to a small template set.

## Phase D — Export and hardening

- PPTX export from Deck JSON; async jobs for long runs.
- Security (upload validation, prompt-injection awareness), observability, integration tests.

## Phase E — Integration

- Contract with `admin_pan` for auth and quotas; minimal usage callbacks if required.

Later phases (external web search, richer templates, collaboration) are **out of MVP** unless promoted in `SPEC.md`.
