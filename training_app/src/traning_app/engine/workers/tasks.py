"""Queue task entrypoints (implement with chosen broker)."""


def run_generation_job(job_id: str) -> None:
    """Entry point for worker / FastAPI BackgroundTasks."""
    from traning_app.engine.agents.pipeline import run_job

    run_job(job_id)
