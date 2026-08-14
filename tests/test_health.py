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


def test_no_routes_beyond_phase_1() -> None:
    """Guard against building ahead of the phase plan (PRD §6)."""
    api_routes = {
        route.path  # type: ignore[attr-defined]
        for route in app.routes
        if getattr(route, "path", "").startswith("/api")
    }
    assert api_routes == {"/api/health"}
