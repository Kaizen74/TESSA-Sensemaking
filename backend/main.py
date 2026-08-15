"""FastAPI application.

Endpoints arrive with the phase that needs them, per PRD §6 — do not add routes
ahead of the current phase. ``tests/test_health.py`` pins the allowed route set.

From Phase 4 the app also serves the built frontend, because a capture link is
only a capture link if a phone that scans its QR reaches the wizard. Both the
admin app and the respondent's page then come from one address on the Tailscale
mesh (constraint 4).
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend import __version__, settings
from backend.routers import capture, capture_links, frameworks, imports, public

app = FastAPI(title="Narrative Lens", version=__version__)

app.include_router(frameworks.router)
app.include_router(capture.router)
app.include_router(capture_links.router)
app.include_router(imports.router)
app.include_router(public.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Liveness probe. The launcher opens this while the app is starting."""
    return {"status": "ok", "app": "Narrative Lens", "version": __version__}


def mount_frontend(application: FastAPI) -> bool:
    """Serve ``frontend/dist`` if it has been built.

    Returns whether anything was mounted, so the launcher and the tests can say
    something useful when the frontend has not been built yet rather than
    serving a blank page.

    Unknown paths fall through to ``index.html`` so the respondent's ``/c/{token}``
    route survives a page reload — a single-page app owns its own routing, and a
    phone reloading mid-story must not get a 404.
    """
    dist = settings.FRONTEND_DIST
    index = dist / "index.html"
    if not index.is_file():
        return False

    assets = dist / "assets"
    if assets.is_dir():
        application.mount("/assets", StaticFiles(directory=assets), name="assets")

    # response_model=None: this route returns a file or a JSON error, and
    # FastAPI would otherwise try to build a schema from that union.
    @application.get("/{full_path:path}", include_in_schema=False, response_model=None)
    def serve_spa(full_path: str) -> FileResponse | JSONResponse:
        # An unmatched /api path is a missing endpoint, not a page. Returning
        # index.html there would hand a caller HTML where it expects JSON.
        if full_path.startswith("api/"):
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": "endpoint_not_found",
                        "message": "Narrative Lens does not have that address.",
                        "action": "Reload the page. If it keeps happening, restart the app.",
                    }
                },
            )

        candidate = (dist / full_path).resolve()
        # Only ever serve files from inside dist, whatever the path claims.
        if full_path and candidate.is_file() and dist.resolve() in candidate.parents:
            return FileResponse(candidate)

        return FileResponse(index)

    return True


mount_frontend(app)
