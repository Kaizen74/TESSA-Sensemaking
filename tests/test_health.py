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
EXPECTED_API_PATHS_THROUGH_PHASE_2 = {
    # Phase 1
    "/api/health",
    # Phase 2 — Studio and paper pack
    "/api/frameworks",
    "/api/frameworks/{framework_id}",
    "/api/frameworks/{framework_id}/paper-pack",
}


def test_no_routes_beyond_the_current_phase() -> None:
    """Guard against building ahead of the phase plan (PRD §6).

    Enumerated from the OpenAPI schema rather than ``app.routes``: an included
    router appears in ``app.routes`` as a single object with no ``path``, so
    walking that list would silently miss every routed endpoint.
    """
    api_paths = {path for path in app.openapi()["paths"] if path.startswith("/api")}

    assert api_paths == EXPECTED_API_PATHS_THROUGH_PHASE_2
