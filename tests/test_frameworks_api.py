"""List, create and fetch frameworks (PRD §4)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.framework_schema import CANONICAL_ANONYMITY_TEXT

TRIAD = {"id": "pressure", "title": "What drove this?", "corners": ["Speed", "Care", "Cost"]}


class TestCreate:
    def test_creates_version_one(self, client: TestClient) -> None:
        response = client.post(
            "/api/frameworks",
            json={"name": "Ground handling", "definition": {"triads": [TRIAD]}},
        )

        assert response.status_code == 201, response.text
        body = response.json()
        assert body["name"] == "Ground handling"
        assert body["version"] == 1
        assert body["parent_framework_id"] is None
        assert body["is_active"] is True
        assert body["anecdote_count"] == 0
        assert body["is_live"] is False

    def test_definition_defaults_when_omitted(self, client: TestClient) -> None:
        """A new framework starts valid and empty, ready to fill in."""
        response = client.post("/api/frameworks", json={"name": "Blank"})

        assert response.status_code == 201
        definition = response.json()["definition"]
        assert definition["triads"] == []
        assert definition["capture_settings"]["anonymity_text"] == CANONICAL_ANONYMITY_TEXT

    def test_reports_respondent_facing_figures(self, client: TestClient) -> None:
        """The Studio shows these live while the operator edits."""
        response = client.post(
            "/api/frameworks",
            json={"name": "Two questions", "definition": {"triads": [TRIAD]}},
        )

        body = response.json()
        assert body["signifier_count"] == 1
        assert body["estimated_minutes"] > 0
        assert body["exceeds_screen_warning"] is False

    def test_rejects_an_empty_name(self, client: TestClient) -> None:
        assert client.post("/api/frameworks", json={"name": ""}).status_code == 422

    def test_rejects_an_invalid_definition(self, client: TestClient) -> None:
        broken = {"triads": [{**TRIAD, "corners": ["Only", "Two"]}]}
        response = client.post("/api/frameworks", json={"name": "Broken", "definition": broken})
        assert response.status_code == 422

    def test_rejects_an_unknown_field(self, client: TestClient) -> None:
        response = client.post(
            "/api/frameworks",
            json={"name": "Typo", "definition": {"prompt_txt": "wrong key"}},
        )
        assert response.status_code == 422


class TestFetch:
    def test_returns_the_framework(self, client: TestClient) -> None:
        created = client.post("/api/frameworks", json={"name": "Pilot"}).json()

        response = client.get(f"/api/frameworks/{created['id']}")

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_missing_framework_explains_itself(self, client: TestClient) -> None:
        """Constraint 7: plain English, with something to do about it."""
        response = client.get("/api/frameworks/4242")

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "framework_not_found"
        assert "4242" in error["message"]
        assert error["action"]


class TestList:
    def test_empty_at_the_start(self, client: TestClient) -> None:
        assert client.get("/api/frameworks").json() == []

    def test_returns_every_framework(self, client: TestClient) -> None:
        for name in ("First", "Second", "Third"):
            client.post("/api/frameworks", json={"name": name})

        body = client.get("/api/frameworks").json()

        assert len(body) == 3
        assert {row["name"] for row in body} == {"First", "Second", "Third"}

    def test_carries_the_counts_the_version_sidebar_needs(self, client: TestClient) -> None:
        """PRD §5.1: version history sidebar shows versions with story counts."""
        client.post("/api/frameworks", json={"name": "Pilot"})

        row = client.get("/api/frameworks").json()[0]

        assert "version" in row
        assert "anecdote_count" in row
        assert "parent_framework_id" in row
        assert "edit_log" in row
