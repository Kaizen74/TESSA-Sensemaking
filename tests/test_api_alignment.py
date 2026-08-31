"""The frontend and the backend agree about what exists (contract alignment).

Every address the browser can ask for is written in one file — ``api.js`` — and
every address the server answers is in its OpenAPI schema. Nothing in the build
compared the two: a renamed endpoint, a typo in a template string, or a route
removed from a router would compile, lint, build, and only fail in front of the
operator as "something went wrong that Narrative Lens did not expect".

So the two lists are compared directly. Both directions matter:

* every path the frontend calls must exist on the server, and
* every path the server exposes must be called by the frontend or named here as
  deliberately not — an endpoint nothing reaches is either a mistake or a thing
  somebody meant to finish.
"""

from __future__ import annotations

import re
from pathlib import Path

from backend.main import app

API_JS = Path(__file__).resolve().parent.parent / "frontend" / "src" / "api.js"

#: Server paths no screen calls, each for a stated reason.
NOT_CALLED_FROM_THE_APP = {
    # The launcher polls this while the server starts; the app itself never does.
    "/api/health",
    # Opened in a new tab as a print page rather than fetched as data.
    "/api/frameworks/{param}/paper-pack",
    # Rendered by the browser as <img src>, not fetched by the API layer.
    "/api/capture-links/{param}/qr.png",
    # Downloads: given to the browser as a link so it saves the file itself.
    "/api/export/csv",
    "/api/export/brief",
    "/api/export/heard",
}

PLACEHOLDER = "{param}"


def _frontend_paths() -> set[str]:
    """Every ``/api/...`` address api.js can build, with its parameters blanked."""
    source = API_JS.read_text(encoding="utf-8")
    found: set[str] = set()
    for raw in re.findall(r"[`\"'](/api/[^`\"'\s]*)", source):
        # A plain ``${name}`` is a path parameter. Anything more involved is the
        # query-string helper, which is always last and is not part of the
        # address — so the address is what comes before it.
        path = re.sub(r"\$\{[A-Za-z0-9_.]+\}", PLACEHOLDER, raw)
        path = path.split("${")[0].split("?")[0]
        found.add(path.rstrip("/"))
    return found


def _server_paths() -> set[str]:
    return {
        re.sub(r"\{[^}]+\}", PLACEHOLDER, path)
        for path in app.openapi()["paths"]
        if path.startswith("/api")
    }


def test_every_address_the_frontend_calls_exists_on_the_server() -> None:
    missing = _frontend_paths() - _server_paths()

    assert not missing, f"the app calls addresses the server does not have: {sorted(missing)}"


def test_every_endpoint_is_reached_by_something() -> None:
    """An endpoint nothing calls is either dead or half-finished."""
    unreached = _server_paths() - _frontend_paths() - {
        re.sub(r"\{[^}]+\}", PLACEHOLDER, path) for path in NOT_CALLED_FROM_THE_APP
    }

    assert not unreached, f"nothing in the app reaches: {sorted(unreached)}"


def test_the_scan_found_a_real_surface() -> None:
    """A guard on the guard: an empty comparison would pass both tests above."""
    frontend = _frontend_paths()

    assert len(frontend) > 15
    assert "/api/capture" in frontend
    assert f"/api/stories/{PLACEHOLDER}" in frontend
