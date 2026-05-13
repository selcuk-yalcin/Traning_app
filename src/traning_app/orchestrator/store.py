"""In-memory job store (MVP — replace with Redis + worker later)."""

from __future__ import annotations

import copy
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any

from traning_app.events.types import AgentEvent


@dataclass
class JobRecord:
    job_id: str
    template_id: str
    request: dict[str, Any]
    stage: str = "queued"
    events: list[dict[str, Any]] = field(default_factory=list)
    deck: dict[str, Any] | None = None
    error: str | None = None


class JobStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, JobRecord] = {}

    def create_job(self, *, template_id: str, request: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        rec = JobRecord(job_id=job_id, template_id=template_id, request=request)
        with self._lock:
            self._jobs[job_id] = rec
        return job_id

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return None
            return JobRecord(
                job_id=rec.job_id,
                template_id=rec.template_id,
                request=copy.deepcopy(rec.request),
                stage=rec.stage,
                events=copy.deepcopy(rec.events),
                deck=copy.deepcopy(rec.deck) if rec.deck else None,
                error=rec.error,
            )

    def _mutate(self, job_id: str, fn) -> None:
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                raise KeyError(job_id)
            fn(rec)

    def set_stage(self, job_id: str, stage: str) -> None:
        def fn(rec: JobRecord) -> None:
            rec.stage = stage

        self._mutate(job_id, fn)

    def append_event(self, job_id: str, event: AgentEvent) -> None:
        def fn(rec: JobRecord) -> None:
            rec.events.append(event.model_dump())

        self._mutate(job_id, fn)

    def set_deck(self, job_id: str, deck: dict[str, Any]) -> None:
        def fn(rec: JobRecord) -> None:
            rec.deck = deck

        self._mutate(job_id, fn)

    def set_failed(self, job_id: str, message: str, *, error_code: str = "job_failed") -> None:
        def fn(rec: JobRecord) -> None:
            rec.stage = "failed"
            rec.error = message
            rec.events.append(
                AgentEvent(
                    stage="failed",
                    detail=message,
                    error_code=error_code,
                ).model_dump()
            )

        self._mutate(job_id, fn)


_store: JobStore | None = None
_store_lock = threading.Lock()


def get_job_store() -> JobStore:
    global _store
    with _store_lock:
        if _store is None:
            _store = JobStore()
        return _store


def reset_job_store_for_tests() -> None:
    """Clear all jobs (tests only)."""
    global _store
    with _store_lock:
        _store = JobStore()
