"""FastAPI application.

Phase 1 exposes ``/api/health`` only. Endpoints arrive with the phase that needs
them, per PRD §6 — do not add routes ahead of the current phase.
"""

from __future__ import annotations

from fastapi import FastAPI

from backend import __version__
from backend.routers import frameworks

app = FastAPI(title="Narrative Lens", version=__version__)

app.include_router(frameworks.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Liveness probe. The launcher opens this while the app has no frontend."""
    return {"status": "ok", "app": "Narrative Lens", "version": __version__}
