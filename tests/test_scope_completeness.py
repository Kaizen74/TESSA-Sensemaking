"""Every item of PRD §1's scope is actually reachable in the app.

This file exists because of what a phase plan cannot catch. PRD §6 schedules
nine phases, each with its own gate, and all nine were green — while three items
of §1's scope had no phase at all and so were never built: the story browser
(§1.6), the QR of the active link on the admin home (§1.8, acceptance criterion
1), and the supporting-charts PNG (§1.7). Nothing was failing. Nothing was
looking.

So the scope is checked against the code directly, one assertion per item. The
checks are deliberately shallow — a screen exists, an endpoint answers, a button
is wired — because their job is to notice an *absence*. What each feature does
when it is there is tested in its own file.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app

SRC = Path(__file__).resolve().parent.parent / "frontend" / "src"


def _source(*parts: str) -> str:
    return (SRC.joinpath(*parts)).read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# §1.5 and §5.4 — the Patterns tab's four ways of looking
# --------------------------------------------------------------------------


def test_the_patterns_tab_offers_every_view_the_prd_names() -> None:
    """§5.4: "Landscape (default) · Supporting charts · 3D Explorer · Story browser"."""
    patterns = _source("patterns", "Patterns.jsx")

    for label in ("Landscape", "Supporting charts", "3D Explorer", "Story browser"):
        assert f'label: "{label}"' in patterns, label
    # And the landscape is the one it opens on (§5b: zero clicks to a default).
    assert "useState(VIEW_LANDSCAPE)" in patterns


# --------------------------------------------------------------------------
# §1.6 — the story browser
# --------------------------------------------------------------------------


def test_the_story_browser_is_reachable_and_answers() -> None:
    paths = set(app.openapi()["paths"])

    assert "/api/stories/{framework_id}" in paths
    assert "/api/stories/{anecdote_id}/marks" in paths
    assert (SRC / "patterns" / "StoryBrowser.jsx").is_file()


def test_the_browser_can_search_tag_star_and_export_selected() -> None:
    """The four verbs §1.6 lists, each with something in the code doing it."""
    browser = _source("patterns", "StoryBrowser.jsx")

    assert 'type="search"' in browser
    assert "starred" in browser
    assert "TagEditor" in browser
    assert "ids: chosen.join" in browser


# --------------------------------------------------------------------------
# §1.7 — the exports
# --------------------------------------------------------------------------


def test_every_export_the_scope_lists_exists() -> None:
    """Dataset CSV · contour PNG · supporting-charts PNG · brief · what we heard."""
    paths = set(app.openapi()["paths"])
    snapshot = _source("patterns", "snapshot.js")
    patterns = _source("patterns", "Patterns.jsx")

    assert {"/api/export/csv", "/api/export/brief", "/api/export/heard"} <= paths
    assert "export function saveContourSnapshot" in snapshot
    assert "export async function saveChartsSnapshot" in snapshot
    # Both pictures are offered on the screen, not just implemented.
    assert "Save the contour as a picture" in patterns
    assert "Save these charts as a picture" in patterns


# --------------------------------------------------------------------------
# §1.8 — one-click launch, QR on the home screen
# --------------------------------------------------------------------------


def test_the_home_screen_carries_the_active_links_qr() -> None:
    """Acceptance criterion 1 ends "QR on home", and the home screen is the Studio."""
    studio = _source("studio", "Studio.jsx")
    component = _source("studio", "ActiveLinkQr.jsx")

    assert "<ActiveLinkQr />" in studio
    assert "captureLinkQrUrl" in component
    # It says something useful when no link is open, rather than nothing at all.
    assert "No link is open" in component


def test_the_launcher_opens_the_app_rather_than_its_health_check() -> None:
    launcher = (
        Path(__file__).resolve().parent.parent / "Start Narrative Lens.bat"
    ).read_text(encoding="utf-8")

    assert 'set "NL_URL=http://%NL_HOST%:%NL_PORT%/"' in launcher
    assert 'start "" "%NL_URL%"' in launcher
    # And it waits for the server rather than guessing at a number of seconds.
    assert "NL_HEALTH" in launcher


# --------------------------------------------------------------------------
# The rest of §1, in one pass over the routes
# --------------------------------------------------------------------------


def test_every_scope_item_has_an_endpoint_behind_it(client: TestClient) -> None:
    """One assertion per numbered item of §1 that the API is responsible for."""
    paths = set(app.openapi()["paths"])

    # 1 the Studio · 2 capture, paper pack, batch entry · 3 ingestion
    assert {"/api/frameworks", "/api/frameworks/{framework_id}"} <= paths
    assert "/api/frameworks/{framework_id}/paper-pack" in paths
    assert {"/api/capture", "/api/capture-links", "/api/public/capture/{token}"} <= paths
    assert {"/api/import", "/api/import/{job_id}/organise"} <= paths
    assert {"/api/import/{job_id}/mapping", "/api/import/{job_id}/propose"} <= paths
    # 4 the validation queue · 5 patterns, landscape, explorer, clusters
    assert {"/api/queue", "/api/queue/{anecdote_id}"} <= paths
    assert "/api/patterns/{framework_id}" in paths
    assert "/api/landscape/{framework_id}/{triad_id}" in paths
    assert {"/api/explorer/{framework_id}", "/api/clusters/{framework_id}"} <= paths
    # 6 the story browser · 7 the exports
    assert "/api/stories/{framework_id}" in paths
    assert {"/api/export/csv", "/api/export/brief", "/api/export/heard"} <= paths
    # 8 one-click launch — the health check the launcher waits on
    assert client.get("/api/health").json()["status"] == "ok"
