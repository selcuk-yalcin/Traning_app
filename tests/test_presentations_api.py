import time

from fastapi.testclient import TestClient

from traning_app.api.main import create_app


def _wait_done(client: TestClient, job_id: str, timeout: float = 5.0) -> dict:
    deadline = time.monotonic() + timeout
    last = {}
    while time.monotonic() < deadline:
        r = client.get(f"/presentations/{job_id}")
        assert r.status_code == 200
        last = r.json()
        if last.get("stage") in ("done", "failed"):
            return last
        time.sleep(0.02)
    raise AssertionError(f"job did not finish: {last!r}")


def test_generate_export_pptx_and_events() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/presentations/generate",
        json={"template_id": "occ-safety", "prompt": "Acil durum prosedürü vurgula"},
    )
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    summary = _wait_done(client, job_id)
    assert summary["stage"] == "done"
    assert summary["has_deck"] is True

    ev = client.get(f"/presentations/{job_id}/events")
    assert ev.status_code == 200
    body = ev.json()
    assert len(body["events"]) >= 4
    stages = {e["stage"] for e in body["events"]}
    assert "planning" in stages and "done" in stages

    deck = client.get(f"/presentations/{job_id}/deck")
    assert deck.status_code == 200
    assert deck.json()["meta"]["theme"]["name"] == "default"

    pptx = client.get(f"/presentations/{job_id}/export/pptx")
    assert pptx.status_code == 200
    assert pptx.content[:2] == b"PK"
    assert "presentationml" in pptx.headers.get("content-type", "")

    html = client.get(f"/presentations/{job_id}/export/html")
    assert html.status_code == 200
    assert b"reveal.js" in html.content


def test_unknown_template_400() -> None:
    client = TestClient(create_app())
    r = client.post("/presentations/generate", json={"template_id": "nope"})
    assert r.status_code == 400
