"""Job-scoped paths under ``storage/exports``."""

from __future__ import annotations

from pathlib import Path

from traning_app.config.settings import get_settings


def exports_root() -> Path:
    settings = get_settings()
    root = Path(getattr(settings, "storage_exports_dir", None) or "storage/exports")
    if not root.is_absolute():
        # training_app/ as cwd when API runs from project root
        base = Path(__file__).resolve().parents[4]
        root = base / root
    root.mkdir(parents=True, exist_ok=True)
    return root


def job_dir(job_id: str) -> Path:
    d = exports_root() / job_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def job_audio_dir(job_id: str) -> Path:
    d = job_dir(job_id) / "audio"
    d.mkdir(parents=True, exist_ok=True)
    return d


def job_mp4_path(job_id: str) -> Path:
    return job_dir(job_id) / f"{job_id}.mp4"
