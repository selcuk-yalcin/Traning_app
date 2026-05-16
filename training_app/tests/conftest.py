import pytest

from traning_app.engine.orchestrator.store import reset_job_store_for_tests


@pytest.fixture(autouse=True)
def _reset_job_store() -> None:
    reset_job_store_for_tests()
    yield
