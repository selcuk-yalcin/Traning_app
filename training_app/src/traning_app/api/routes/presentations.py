"""Presentation generation API (SPEC §5)."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pathlib import Path

from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel, Field, field_validator

from traning_app.engine.deck.loaders import list_builtin_template_ids
from traning_app.engine.agents.html_export import deck_to_html_string
from traning_app.engine.agents.pptx_export import deck_to_pptx_bytes
from traning_app.engine.media.paths import job_dir
from traning_app.engine.orchestrator.store import get_job_store
from traning_app.engine.workers.tasks import run_generation_job
from traning_app.engine.ingest.validation import validate_slide_length

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
    slide_length: str = Field(
        default="auto",
        max_length=32,
        description="auto | summary | short | medium | long",
    )
    role: str | None = Field(
        default=None,
        max_length=128,
        description="Optional audience framing (e.g. design, engineering).",
    )
    use_tts: bool = Field(
        default=False,
        description="If true, synthesize per-slide narration (OpenRouter/OpenAI/ElevenLabs).",
    )
    use_slide_images: bool = Field(
        default=False,
        description="If true, generate AI cover images for up to 1–3 slides (tier-dependent).",
    )
    use_video: bool = Field(
        default=False,
        description="If true with use_tts, mux MP4 via FFmpeg when available.",
    )
    tts_provider: str = Field(default="openai", max_length=32)
    tts_voice_id: str | None = Field(default=None, max_length=128)

    @field_validator("slide_length", mode="before")
    @classmethod
    def normalize_slide_length(cls, v: object) -> str:
        return validate_slide_length(v)

    @field_validator("tier", mode="before")
    @classmethod
    def normalize_tier(cls, v: object) -> str:
        t = str(v or "standard").strip().lower()
        if t not in ("standard", "pro", "ultra"):
            return "standard"
        return t

    @field_validator("tts_provider", mode="before")
    @classmethod
    def normalize_tts_provider(cls, v: object) -> str:
        p = str(v or "openai").strip().lower()
        if p in ("11labs", "eleven"):
            return "elevenlabs"
        return p if p else "openai"


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
        "has_audio_manifest": rec.audio_manifest is not None,
        "has_mp4": bool(rec.mp4_path and Path(rec.mp4_path).is_file()),
        "event_count": len(rec.events),
    }


@router.get("/{job_id}/audio-manifest")
def get_audio_manifest(job_id: str) -> dict[str, Any]:
    rec = get_job_store().get(job_id)
    if rec is None or rec.audio_manifest is None:
        raise HTTPException(status_code=404, detail="Audio manifest not ready")
    return rec.audio_manifest


@router.get("/{job_id}/deck")
def get_deck(job_id: str) -> dict[str, Any]:
    rec = get_job_store().get(job_id)
    if rec is None or rec.deck is None:
        raise HTTPException(status_code=404, detail="Deck not ready")
    return rec.deck


def _assert_safe_under_job(job_id: str, file_path: Path) -> Path:
    root = job_dir(job_id).resolve()
    try:
        resolved = file_path.resolve()
    except OSError:
        raise HTTPException(status_code=404, detail="Invalid path")
    try:
        resolved.relative_to(root)
    except ValueError:
        raise HTTPException(status_code=403, detail="Path outside job directory")
    if not resolved.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return resolved


@router.put("/{job_id}/deck")
def put_deck(job_id: str, body: dict[str, Any]) -> dict[str, str]:
    """Replace job deck (Layer 5 editor save)."""
    store = get_job_store()
    rec = store.get(job_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if rec.stage != "done":
        raise HTTPException(status_code=409, detail="Job not finished")
    if not isinstance(body, dict) or not isinstance(body.get("slides"), list):
        raise HTTPException(status_code=400, detail="Body must include slides array")
    slides = body["slides"]
    for i, s in enumerate(slides):
        if not isinstance(s, dict):
            raise HTTPException(status_code=400, detail=f"slides[{i}] must be object")
    meta = body.get("meta")
    if meta is not None and not isinstance(meta, dict):
        raise HTTPException(status_code=400, detail="meta must be object")
    out = dict(body)
    out.setdefault("version", body.get("version") or "1")
    out["slides"] = [dict(s) for s in slides]
    if isinstance(meta, dict):
        out["meta"] = dict(meta)
    store.set_deck(job_id, out)
    return {"status": "saved"}


@router.get("/{job_id}/slides/{slide_index:int}/image")
def get_slide_image(job_id: str, slide_index: int) -> FileResponse:
    rec = get_job_store().get(job_id)
    if rec is None or rec.deck is None:
        raise HTTPException(status_code=404, detail="Deck not ready")
    slides = rec.deck.get("slides") or []
    if slide_index < 0 or slide_index >= len(slides):
        raise HTTPException(status_code=404, detail="Slide not found")
    spec = slides[slide_index]
    if not isinstance(spec, dict):
        raise HTTPException(status_code=404, detail="Invalid slide")
    path_str = spec.get("image_path")
    if not path_str or not isinstance(path_str, str):
        raise HTTPException(status_code=404, detail="No image for slide")
    path = _assert_safe_under_job(job_id, Path(path_str))
    suffix = path.suffix.lower()
    media = "image/png" if suffix in (".png", "") else "image/jpeg"
    return FileResponse(path, media_type=media)


@router.get("/{job_id}/audio/slide/{slide_index:int}")
def get_slide_audio(job_id: str, slide_index: int) -> FileResponse:
    rec = get_job_store().get(job_id)
    if rec is None or rec.audio_manifest is None:
        raise HTTPException(status_code=404, detail="Audio not ready")
    for seg in rec.audio_manifest.get("segments") or []:
        if not isinstance(seg, dict):
            continue
        if int(seg.get("slide_index", -1)) != slide_index:
            continue
        path_str = seg.get("audio_path")
        if not path_str or not isinstance(path_str, str):
            break
        path = _assert_safe_under_job(job_id, Path(path_str))
        return FileResponse(path, media_type="audio/mpeg", filename=f"slide_{slide_index}.mp3")
    raise HTTPException(status_code=404, detail="No audio for slide")


@router.get("/{job_id}/embed/html")
def embed_html(job_id: str) -> Response:
    """Inline HTML for iframe embed (no Content-Disposition: attachment)."""
    rec = get_job_store().get(job_id)
    if rec is None or rec.deck is None:
        raise HTTPException(status_code=404, detail="Deck not ready")
    html_doc = deck_to_html_string(rec.deck)
    return Response(
        content=html_doc,
        media_type="text/html; charset=utf-8",
    )


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


@router.get("/{job_id}/export/mp4")
def export_mp4(job_id: str) -> FileResponse:
    rec = get_job_store().get(job_id)
    if rec is None or not rec.mp4_path:
        raise HTTPException(status_code=404, detail="MP4 not ready")
    path = Path(rec.mp4_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="MP4 file missing on disk")
    return FileResponse(
        path,
        media_type="video/mp4",
        filename=f"{job_id}.mp4",
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
