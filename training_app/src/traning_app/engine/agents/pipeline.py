"""Tek giriş noktası: üretim işi (planlama → araştırma → slayt → tema → bitti)."""

from __future__ import annotations

import copy
import logging
from typing import Any

from traning_app.engine.agents.audio_manifest import manifest_from_deck_notes
from traning_app.engine.agents.deck_theme import apply_theme_to_deck
from traning_app.engine.agents.router import resolve_model
from traning_app.engine.deck.catalog import get_catalog_entry
from traning_app.engine.deck.json_extract import extract_json_object
from traning_app.engine.deck.loaders import list_builtin_template_ids, load_builtin_deck_template
from traning_app.engine.deck.schema import Deck
from traning_app.engine.events.types import AgentEvent
from traning_app.engine.ingest.context import build_unified_context
from traning_app.engine.ingest.intake import resolve_sources_for_job
from traning_app.engine.ingest.validation import sanitize_text
from traning_app.engine.orchestrator.state_machine import JobStage
from traning_app.engine.orchestrator.store import get_job_store

log = logging.getLogger(__name__)


def _slide_count_hint(slide_length: str | None) -> str:
    s = (slide_length or "auto").strip().lower()
    return {
        "auto": "Roughly 12–18 slides unless the sources clearly need fewer.",
        "summary": "At most 2 slides: one title and one dense summary slide.",
        "short": "About 2–5 slides total.",
        "medium": "About 6–15 slides total.",
        "long": "About 15+ slides if the material supports it.",
    }.get(s, "Roughly 12–18 slides unless the sources clearly need fewer.")


def _emit(job_id: str, *, stage: str, **kwargs: Any) -> None:
    store = get_job_store()
    store.append_event(job_id, AgentEvent(stage=stage, **kwargs))


def _deck_from_llm(
    *,
    unified_context: str,
    user_prompt: str,
    language: str | None,
    template_id: str,
    tier: str,
    slide_length: str | None = None,
) -> dict[str, Any]:
    from traning_app.engine.agents.llm import complete_text

    catalog = get_catalog_entry(template_id)
    addendum = catalog.system_prompt_addendum if catalog else ""
    model_cfg = resolve_model(tier, "text")
    system = (
        "You are an expert instructional designer for workplace training decks. "
        "Return ONLY valid JSON (no markdown outside JSON). The JSON must match "
        'Deck JSON v1: keys "version" (string "1"), "meta" (object with "title", '
        '"language", "template_id"), "slides" (array). Each slide has "type": '
        "one of title, section, bullets, content, two_column. "
        "Use education flow: objectives → concepts → examples → recap. "
        f"{addendum}"
    )
    hint = _slide_count_hint(slide_length)
    user = (
        f"Language for slide titles and bullets: {language or 'tr'}.\n"
        f"Template id: {template_id}.\n"
        f"Target deck size: {hint}\n"
        f"Author instructions:\n{sanitize_text(user_prompt, max_len=8000)}\n\n"
        f"Unified source context (cite only when supported):\n"
        f"{sanitize_text(unified_context, max_len=60000)}\n\n"
        "Include at least one title slide and one recap when more than one slide is used. "
        'Slides use "bullets" with a "bullets" string array or "two_column" with '
        '"left" and "right" strings.'
    )
    raw = complete_text(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        model=model_cfg["model_id"],
        max_tokens=min(model_cfg["max_tokens"], 12000),
        temperature=0.35,
    )
    parsed = extract_json_object(raw)
    deck = Deck.model_validate(parsed)
    return deck.model_dump()


def run_job(job_id: str) -> None:
    """
    Execute pipeline for a job created via the API.

    Deterministic path: clone bundled ``template_id`` deck, merge user prompt into
    ``meta``, apply theme. LLM path (``use_llm: true``): requires ``OPENAI_API_KEY``.
    """
    store = get_job_store()
    rec = store.get(job_id)
    if rec is None:
        log.warning("run_job: unknown job_id=%s", job_id)
        return

    req = rec.request
    template_id = str(req.get("template_id") or rec.template_id)
    tier = str(req.get("tier") or "standard").strip().lower()
    user_prompt = str(req.get("prompt") or "")
    slide_length = str(req.get("slide_length") or "auto")
    sources: list[dict] = resolve_sources_for_job(dict(req))
    language = req.get("language")
    use_llm = bool(req.get("use_llm"))
    theme_name = str(req.get("theme") or "default")
    use_tts = bool(req.get("use_tts"))
    use_slide_images = bool(req.get("use_slide_images"))
    use_video = bool(req.get("use_video"))
    tts_provider = str(req.get("tts_provider") or "openai").strip().lower()
    tts_voice_id = req.get("tts_voice_id")

    try:
        allowed = list_builtin_template_ids()
        if template_id not in allowed:
            raise ValueError(f"Unknown template_id {template_id!r}; allowed: {allowed}")

        store.set_stage(job_id, JobStage.PLANNING.value)
        catalog = get_catalog_entry(template_id)
        outline: dict[str, Any] = {
            "template_id": template_id,
            "mandatory_topics": list(catalog.mandatory_topics) if catalog else [],
            "duration_minutes": catalog.duration_minutes if catalog else None,
            "assessment_style": catalog.assessment_style if catalog else None,
        }
        _emit(
            job_id,
            stage=JobStage.PLANNING.value,
            detail="Outline seeded from template catalog",
            progress=0.1,
            payload=outline,
        )

        store.set_stage(job_id, JobStage.RESEARCH.value)
        if user_prompt and not any(
            s.get("type") == "prompt" for s in sources if isinstance(s, dict)
        ):
            sources = [{"type": "prompt", "text": user_prompt}, *sources]
        unified = build_unified_context(sources)
        _emit(
            job_id,
            stage=JobStage.RESEARCH.value,
            detail="Unified context assembled",
            progress=0.25,
            payload={"chars": len(unified)},
        )

        store.set_stage(job_id, JobStage.GENERATING.value)
        deck: dict[str, Any]
        if use_llm:
            try:
                deck = _deck_from_llm(
                    unified_context=unified or user_prompt,
                    user_prompt=user_prompt,
                    language=str(language) if language else None,
                    template_id=template_id,
                    tier=tier,
                    slide_length=slide_length,
                )
                deck.setdefault("meta", {})
                deck["meta"]["template_id"] = template_id
                if language:
                    deck["meta"]["language"] = str(language)
                _emit(
                    job_id,
                    stage=JobStage.GENERATING.value,
                    detail="Deck produced via LLM",
                    progress=0.7,
                )
            except Exception as e:
                log.warning("LLM generation failed, falling back: %s", e)
                _emit(
                    job_id,
                    stage=JobStage.GENERATING.value,
                    detail=f"LLM failed ({e}); using bundled template",
                    progress=0.45,
                )
                deck = copy.deepcopy(load_builtin_deck_template(template_id))
                if user_prompt:
                    meta = deck.setdefault("meta", {})
                    meta["instruction_summary"] = sanitize_text(user_prompt, max_len=2000)
        else:
            deck = copy.deepcopy(load_builtin_deck_template(template_id))
            if user_prompt:
                meta = deck.setdefault("meta", {})
                meta["instruction_summary"] = sanitize_text(user_prompt, max_len=2000)
            _emit(
                job_id,
                stage=JobStage.GENERATING.value,
                detail="Deck cloned from bundled JSON template",
                progress=0.65,
            )

        store.set_stage(job_id, JobStage.LAYOUT.value)
        deck = apply_theme_to_deck(deck, theme_name=theme_name)
        _emit(
            job_id,
            stage=JobStage.LAYOUT.value,
            detail=f"Theme applied: {theme_name}",
            progress=0.82,
            payload={"theme": theme_name},
        )

        if use_slide_images:
            try:
                from traning_app.engine.agents.slide_images import enrich_deck_with_images

                max_img = {"standard": 1, "pro": 2, "ultra": 3}.get(tier, 2)
                deck = enrich_deck_with_images(
                    deck, job_id, tier=tier, max_images=max_img
                )
                _emit(
                    job_id,
                    stage=JobStage.LAYOUT.value,
                    detail="Slide images generated",
                    progress=0.86,
                    payload={"use_slide_images": True},
                )
            except Exception as e:
                log.warning("Slide images skipped: %s", e)

        store.set_stage(job_id, JobStage.TTS.value)
        manifest = manifest_from_deck_notes(deck)
        store.set_audio_manifest(job_id, manifest.model_dump())

        if use_tts:
            try:
                from traning_app.engine.agents.tts_segments import synthesize_manifest_audio

                manifest = synthesize_manifest_audio(
                    manifest,
                    deck,
                    job_id,
                    provider=tts_provider,
                    voice_id=str(tts_voice_id) if tts_voice_id else None,
                )
                store.set_audio_manifest(job_id, manifest.model_dump())
                with_audio = sum(1 for s in manifest.segments if s.audio_path)
                _emit(
                    job_id,
                    stage=JobStage.TTS.value,
                    detail=f"Narration synthesized ({with_audio}/{len(manifest.segments)} segments)",
                    progress=0.93,
                    payload={
                        "provider": tts_provider,
                        "segments": len(manifest.segments),
                        "with_audio": with_audio,
                    },
                )
            except Exception as e:
                log.warning("TTS segments failed: %s", e)
                _emit(
                    job_id,
                    stage=JobStage.TTS.value,
                    detail=f"TTS failed ({e}); timing estimates only",
                    progress=0.92,
                    payload={"segments": len(manifest.segments)},
                )
        else:
            _emit(
                job_id,
                stage=JobStage.TTS.value,
                detail="TTS off; audio manifest built from slide text (timing estimates)",
                progress=0.92,
                payload={"segments": len(manifest.segments)},
            )

        if use_video and use_tts:
            try:
                from traning_app.engine.media.sync import render_mp4

                mdict = manifest.model_dump()
                mp4 = render_mp4(job_id, deck, mdict)
                store.set_mp4_path(job_id, mp4)
                _emit(
                    job_id,
                    stage=JobStage.TTS.value,
                    detail="MP4 export ready",
                    progress=0.98,
                    payload={"mp4": mp4},
                )
            except Exception as e:
                log.warning("MP4 render failed: %s", e)
                _emit(
                    job_id,
                    stage=JobStage.TTS.value,
                    detail=f"MP4 skipped ({e})",
                    progress=0.95,
                )

        store.set_deck(job_id, deck)
        store.set_stage(job_id, JobStage.DONE.value)
        _emit(
            job_id,
            stage=JobStage.DONE.value,
            detail="Deck ready for export",
            progress=1.0,
            payload={"slides": len(deck.get("slides", []))},
        )
    except Exception as e:
        log.exception("Job %s failed", job_id)
        store.set_failed(job_id, str(e), error_code="pipeline_error")
