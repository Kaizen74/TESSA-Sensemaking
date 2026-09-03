"""The one endpoint Phase 1 ships."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend import __version__
from backend.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "Narrative Lens",
        "version": __version__,
    }


def test_health_is_fast_enough_for_the_200ms_budget() -> None:
    """PRD §4 budgets 200ms for non-AI endpoints; health should be far under."""
    import time

    start = time.perf_counter()
    client.get("/api/health")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 200


#: Every API path the app is allowed to expose at the current phase (PRD §6).
#: Grow this list only when the phase that owns the endpoint is being built —
#: it is the guard against building ahead of the plan.
EXPECTED_API_PATHS = {
    # Phase 1
    "/api/health",
    # Phase 2 — Studio and paper pack
    "/api/frameworks",
    "/api/frameworks/{framework_id}",
    "/api/frameworks/{framework_id}/paper-pack",
    # Phase 3 — local capture and paper batch entry
    "/api/capture",
    # Phase 4 — remote links, kiosk, voice
    "/api/capture-links",
    "/api/capture-links/{link_id}/revoke",
    "/api/capture-links/{link_id}/qr.png",
    "/api/public/capture/{token}",
    # Phase 5 — ingestion and Stage A
    "/api/import",
    "/api/import/{job_id}",
    "/api/import/{job_id}/organise",
    "/api/import/{job_id}/mapping",
    # Phase 6 — Stage B and the validation queue
    "/api/import/{job_id}/propose",
    "/api/queue",
    "/api/queue/{anecdote_id}",
    # Phase 7 — supporting charts and exports. /api/export/heard is the
    # respondent-facing "What We Heard" and belongs to Phase 9.
    "/api/patterns/{framework_id}",
    "/api/export/csv",
    "/api/export/brief",
    # Phase 9 — the summary that goes back to the respondents
    "/api/export/heard",
    # PRD §1.6 and §5.4 — the story browser. In scope for v1.3 and the one
    # scope item §6 never assigned to a phase; built in the post-Phase-9
    # completeness pass.
    "/api/stories/{framework_id}",
    "/api/stories/{anecdote_id}/marks",
    # Phase 8 — the landscape suite
    "/api/landscape/{framework_id}/{triad_id}",
    "/api/explorer/{framework_id}",
    "/api/clusters/{framework_id}",
    # Meaningfulness delta, phase B — the data-quality signals. Pure local
    # counting; nothing on this path can reach a language model.
    "/api/quality/{framework_id}",
    # Meaningfulness delta, phase C — the framework design linter. The one AI
    # call that reads the questions rather than the answers.
    "/api/frameworks/{framework_id}/lint",
    # Meaningfulness delta, phase D — what a room concluded, stored beside the
    # pattern and never merged into it (constraint 16).
    "/api/interpretations",
    # Meaningfulness delta, phase E — the languages the Studio can offer.
    "/api/frameworks/languages",
}


def test_no_routes_beyond_the_current_phase() -> None:
    """Guard against building ahead of the phase plan (PRD §6).

    Enumerated from the OpenAPI schema rather than ``app.routes``: an included
    router appears in ``app.routes`` as a single object with no ``path``, so
    walking that list would silently miss every routed endpoint.
    """
    api_paths = {path for path in app.openapi()["paths"] if path.startswith("/api")}

    assert api_paths == EXPECTED_API_PATHS
