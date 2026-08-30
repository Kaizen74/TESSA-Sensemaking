"""FastAPI application.

Endpoints arrive with the phase that needs them, per PRD §6 — do not add routes
ahead of the current phase. ``tests/test_health.py`` pins the allowed route set.

From Phase 4 the app also serves the built frontend, because a capture link is
only a capture link if a phone that scans its QR reaches the wizard. Both the
admin app and the respondent's page then come from one address on the Tailscale
mesh (constraint 4).
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend import __version__, settings
from backend.routers import (
    capture,
    capture_links,
    exports,
    frameworks,
    imports,
    landscape,
    patterns,
    public,
    queue,
    stories,
)

log = logging.getLogger("narrative_lens")

app = FastAPI(title="Narrative Lens", version=__version__)

app.include_router(frameworks.router)
app.include_router(capture.router)
app.include_router(capture_links.router)
app.include_router(imports.router)
app.include_router(queue.router)
app.include_router(patterns.router)
app.include_router(landscape.router)
app.include_router(exports.router)
app.include_router(stories.router)
app.include_router(public.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Liveness probe. The launcher opens this while the app is starting."""
    return {"status": "ok", "app": "Narrative Lens", "version": __version__}


# --------------------------------------------------------------------------
# Every failure leaves by the same door (PRD §4, constraint 7)
# --------------------------------------------------------------------------
#
# The app's own refusals are written for the operator one by one. These handlers
# cover the rest — a mistyped address, a request the page malformed, a fault in
# the app itself — so there is no path that answers with a stack trace, a
# validator's field dump, or the word "Internal Server Error". The operator
# never sees a message nobody wrote.


def _envelope(status: int, code: str, message: str, action: str, headers=None) -> JSONResponse:
    """The one error shape, exactly as PRD §4 states it."""
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "action": action}},
        headers=headers,
    )


#: Plain sentences for the refusals the framework makes before any of our code
#: runs. Anything not listed falls through to the last line of this table.
_BY_STATUS: dict[int, tuple[str, str, str]] = {
    404: (
        "endpoint_not_found",
        "Narrative Lens does not have that address.",
        "Reload the page. If it keeps happening, restart the app.",
    ),
    405: (
        "wrong_kind_of_request",
        "That part of Narrative Lens was asked to do something it does not do.",
        "Reload the page and use the buttons on it rather than the address bar.",
    ),
    413: (
        "upload_too_large",
        "That upload was too large to accept.",
        "Split the file into smaller parts and import them one at a time.",
    ),
    429: (
        "too_many_requests",
        "Narrative Lens is being asked for more than it can keep up with.",
        "Wait a minute and try again.",
    ),
}

_FALLBACK = (
    "request_refused",
    "Narrative Lens could not do that.",
    "Reload the page and try again. If it keeps happening, restart the app.",
)


@app.exception_handler(StarletteHTTPException)
def plain_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Our own refusals pass straight through; the framework's get translated."""
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail, headers=exc.headers)

    code, message, action = _BY_STATUS.get(exc.status_code, _FALLBACK)
    return _envelope(exc.status_code, code, message, action, headers=exc.headers)


@app.exception_handler(RequestValidationError)
def plain_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """A body or query the page built wrongly.

    The operator cannot fix a validator's field dump, and should never be shown
    one. They can reload, and they can report what it said — so the sentence
    names the part that was wrong in ordinary words and stops there.
    """
    parts = [
        str(item)
        for error in exc.errors()
        for item in error.get("loc", ())
        if isinstance(item, str) and item not in {"body", "query", "path"}
    ]
    named = f" The part it could not read was “{parts[0]}”." if parts else ""
    # The status code is left as the framework set it. What changes here is the
    # body: a validator's field dump is not something a non-technical operator
    # can act on, and constraint 7 says every error must be.
    return _envelope(
        422,
        "request_not_understood",
        f"Narrative Lens could not make sense of what the page asked for.{named}",
        "Reload the page and try again. If it keeps happening, restart the app.",
    )


@app.exception_handler(Exception)
def plain_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """A fault in the app itself. Logged in full, reported in one sentence."""
    log.exception("Unhandled failure on %s %s", request.method, request.url.path)
    return _envelope(
        500,
        "unexpected_problem",
        "Narrative Lens hit a problem it did not expect and stopped, rather than "
        "half-do something.",
        "Try again. If it keeps happening, close the app and start it again with "
        "the Narrative Lens shortcut.",
    )


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
            return _envelope(404, *_BY_STATUS[404])

        candidate = (dist / full_path).resolve()
        # Only ever serve files from inside dist, whatever the path claims.
        if full_path and candidate.is_file() and dist.resolve() in candidate.parents:
            return FileResponse(candidate)

        return FileResponse(index)

    return True


mount_frontend(app)
