"""Presentation generation API (SPEC §5)."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field, field_validator

from traning_app.deck.loaders import list_builtin_template_ids
from traning_app.export.html_export import deck_to_html_string
from traning_app.export.pptx_export import deck_to_pptx_bytes
from traning_app.orchestrator.store import get_job_store
from traning_app.workers.tasks import run_generation_job

router = APIRouter(prefix="/presentations", tags=["presentations"])


class GeneratePresentationRequest(BaseModel):
    """Start a generation job (async; poll ``/{job_id}`` or ``/events``)."""

    template_id: str = Field(
        ...,
        description="Bundled starter id, e.g. occ-safety or fire-protection",
    )
    prompt: str = Field(default="", max_length=16000)
    sources: list[dict[str, Any]] = Field(default_factory=list)
    tier: str = Field(default="standard", max_length=16)
    language: str | None = Field(default="tr", max_length=16)
    use_llm: bool = Field(
        default=False,
        description="If true and OPENAI_API_KEY is set, expand deck via LLM; else bundled JSON.",
    )
    theme: str = Field(default="default", max_length=64)

    @field_validator("tier", mode="before")
    @classmethod
    def normalize_tier(cls, v: object) -> str:
        t = str(v or "standard").strip().lower()
        if t not in ("standard", "pro", "ultra"):
            return "standard"
        return t


@router.post("/generate")
def generate_presentation(
    body: GeneratePresentationRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    allowed = list_builtin_template_ids()
    if body.template_id not in allowed:
        raise HTTPException(
            400,
            detail=f"Unknown template_id; allowed: {allowed}",
        )
    store = get_job_store()
    job_id = store.create_job(
        template_id=body.template_id,
        request=body.model_dump(),
    )
    background_tasks.add_task(run_generation_job, job_id)
    return {"job_id": job_id, "status": "queued"}


@router.get("/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    rec = get_job_store().get(job_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job_id,
        "stage": rec.stage,
        "template_id": rec.template_id,
        "error": rec.error,
        "has_deck": rec.deck is not None,
        "event_count": len(rec.events),
    }


@router.get("/{job_id}/deck")
def get_deck(job_id: str) -> dict[str, Any]:
    rec = get_job_store().get(job_id)
    if rec is None or rec.deck is None:
        raise HTTPException(status_code=404, detail="Deck not ready")
    return rec.deck


@router.get("/{job_id}/events")
def list_events(job_id: str) -> dict[str, Any]:
    rec = get_job_store().get(job_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job_id,
        "stage": rec.stage,
        "events": rec.events,
    }


@router.get("/{job_id}/events/stream")
async def stream_events(job_id: str) -> StreamingResponse:
    """Server-Sent Events stream of job events until ``done`` or ``failed``."""

    async def gen() -> Any:
        seen = 0
        while True:
            rec = get_job_store().get(job_id)
            if rec is None:
                yield f"data: {json.dumps({'error': 'not_found'})}\n\n"
                return
            batch = rec.events[seen:]
            seen = len(rec.events)
            for ev in batch:
                yield f"data: {json.dumps(ev)}\n\n"
            if rec.stage in ("done", "failed"):
                return
            await asyncio.sleep(0.05)

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/{job_id}/export/pptx")
def export_pptx(job_id: str) -> Response:
    rec = get_job_store().get(job_id)
    if rec is None or rec.deck is None:
        raise HTTPException(status_code=404, detail="Deck not ready")
    data = deck_to_pptx_bytes(rec.deck)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={
            "Content-Disposition": f'attachment; filename="{job_id}.pptx"',
        },
    )


@router.get("/{job_id}/export/html")
def export_html(job_id: str) -> Response:
    rec = get_job_store().get(job_id)
    if rec is None or rec.deck is None:
        raise HTTPException(status_code=404, detail="Deck not ready")
    html_doc = deck_to_html_string(rec.deck)
    return Response(
        content=html_doc,
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{job_id}.html"'},
    )
