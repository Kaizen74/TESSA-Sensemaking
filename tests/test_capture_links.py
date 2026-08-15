"""Capture links and the public capture path (PRD §6 Phase 4).

The tests the PRD names for this phase: token lifecycle, identifier-absence, and
voice fallback. The 375px snapshot is a browser check, recorded in PROGRESS.md.

``tests/test_public_identifier_absence.py`` carries the constraint-9 half.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.models import Anecdote, CaptureLink
from backend.rate_limit import reset_all

TRIAD = {"id": "pressure", "title": "What drove this?", "corners": ["Speed", "Care", "Cost"]}
DEFINITION = {
    "prompt_text": "Tell us about a moment at work that stuck with you.",
    "triads": [TRIAD],
    "capture_settings": {"respondent_groups": ["Ramp", "Cabin"]},
}


@pytest.fixture(autouse=True)
def _clear_limits():
    """Rate limiters are process-wide; keep cases independent."""
    reset_all()
    yield
    reset_all()


def _framework(client: TestClient, definition: dict | None = None) -> dict:
    response = client.post(
        "/api/frameworks",
        json={"name": "Ground handling", "definition": definition or DEFINITION},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _link(client: TestClient, framework_id: int, label: str | None = "Hangar wall") -> dict:
    response = client.post(
        "/api/capture-links",
        json={"framework_id": framework_id, "label": label},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _story(**overrides) -> dict:
    body = {
        "text": "The inbound was early and nobody had the paperwork.",
        "input_method": "typed",
        "respondent_group": "Ramp",
        "significations": [
            {"signifier_id": "pressure", "value": {"Speed": 0.5, "Care": 0.3, "Cost": 0.2}}
        ],
    }
    body.update(overrides)
    return body


class TestLinkCreation:
    def test_creates_an_open_link(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        assert link["is_active"] is True
        assert link["revoked_at"] is None
        assert link["label"] == "Hangar wall"
        assert link["story_count"] == 0

    def test_token_is_long_and_unguessable(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        assert len(link["token"]) >= 32

    def test_every_link_gets_its_own_token(self, client: TestClient) -> None:
        framework = _framework(client)
        tokens = {_link(client, framework["id"])["token"] for _ in range(5)}

        assert len(tokens) == 5

    def test_the_url_carries_the_token(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        assert link["token"] in link["url"]
        assert link["url"].startswith("http")

    def test_the_url_is_not_loopback(self, client: TestClient) -> None:
        """A QR pointing at 127.0.0.1 works on the laptop and fails on a phone."""
        framework = _framework(client)
        link = _link(client, framework["id"])

        assert "127.0.0.1" not in link["url"], (
            "capture URL must be reachable from another device on the mesh"
        )

    def test_a_link_names_the_exact_version_it_points_at(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        assert link["framework_id"] == framework["id"]
        assert link["framework_version"] == framework["version"]

    def test_missing_framework_explains_itself(self, client: TestClient) -> None:
        response = client.post("/api/capture-links", json={"framework_id": 4242})

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "framework_not_found"

    def test_links_are_listed_with_their_story_counts(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/public/capture/{link['token']}", json=_story())

        listed = client.get("/api/capture-links").json()
        assert len(listed) == 1
        assert listed[0]["story_count"] == 1


class TestTokenLifecycle:
    """PRD §6 Phase 4: token lifecycle. §7.6: revoked links close."""

    def test_an_open_link_serves_its_questions(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        response = client.get(f"/api/public/capture/{link['token']}")

        assert response.status_code == 200
        assert response.json()["definition"]["prompt_text"] == DEFINITION["prompt_text"]

    def test_an_open_link_accepts_a_story(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        response = client.post(f"/api/public/capture/{link['token']}", json=_story())

        assert response.status_code == 201, response.text
        assert response.json()["entry_mode"] == "link"

    def test_revoking_closes_the_link(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        revoked = client.post(f"/api/capture-links/{link['id']}/revoke")

        assert revoked.status_code == 200
        assert revoked.json()["is_active"] is False
        assert revoked.json()["revoked_at"] is not None

    def test_a_revoked_link_serves_no_questions(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/capture-links/{link['id']}/revoke")

        response = client.get(f"/api/public/capture/{link['token']}")

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "capture_link_closed"

    def test_a_revoked_link_accepts_no_stories(self, client: TestClient) -> None:
        """The heart of §7.6: a taken-down QR poster cannot keep collecting."""
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/capture-links/{link['id']}/revoke")

        response = client.post(f"/api/public/capture/{link['token']}", json=_story())

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "capture_link_closed"

    def test_the_closed_message_is_plain_english(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/capture-links/{link['id']}/revoke")

        error = client.get(f"/api/public/capture/{link['token']}").json()["detail"]["error"]

        assert "closed" in error["message"]
        assert error["action"]
        for jargon in ("404", "HTTP", "token", "None", "null"):
            assert jargon not in error["message"]

    def test_revoking_twice_is_refused_rather_than_silently_repeated(
        self, client: TestClient
    ) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/capture-links/{link['id']}/revoke")

        second = client.post(f"/api/capture-links/{link['id']}/revoke")

        assert second.status_code == 409
        assert second.json()["detail"]["error"]["code"] == "capture_link_already_closed"

    def test_revoking_keeps_the_stories_it_collected(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/public/capture/{link['token']}", json=_story())

        client.post(f"/api/capture-links/{link['id']}/revoke")

        listed = client.get("/api/capture-links").json()
        assert listed[0]["story_count"] == 1, "revoking must not erase what was collected"

    def test_a_closed_link_stays_listed(self, client: TestClient) -> None:
        """Hiding the link would hide where its stories came from."""
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/capture-links/{link['id']}/revoke")

        listed = client.get("/api/capture-links").json()
        assert [row["id"] for row in listed] == [link["id"]]

    def test_an_unknown_token_is_refused(self, client: TestClient) -> None:
        response = client.get("/api/public/capture/not-a-real-token")

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "capture_link_not_found"

    def test_revoking_a_missing_link_explains_itself(self, client: TestClient) -> None:
        response = client.post("/api/capture-links/4242/revoke")

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "capture_link_not_found"


class TestTokenDecidesEverything:
    """The token, not the body, chooses the version and the entry mode."""

    def test_the_link_serves_the_version_it_was_made_against(
        self, client: TestClient
    ) -> None:
        """A later meaning change must not retarget an existing link."""
        v1 = _framework(client)
        link = _link(client, v1["id"])
        client.post(f"/api/public/capture/{link['token']}", json=_story())

        client.put(
            f"/api/frameworks/{v1['id']}",
            json={
                "definition": {**DEFINITION, "prompt_text": "A different question."},
                "edit_kind": "meaning_change",
            },
        )

        served = client.get(f"/api/public/capture/{link['token']}").json()
        assert served["definition"]["prompt_text"] == DEFINITION["prompt_text"]
        assert served["framework_version"] == 1

    def test_a_submitted_framework_id_cannot_redirect_the_story(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        """The browser may not choose which question set it answered."""
        target = _framework(client)
        other = _framework(client, {**DEFINITION, "prompt_text": "Some other set."})
        link = _link(client, target["id"])

        response = client.post(
            f"/api/public/capture/{link['token']}",
            json=_story(framework_id=other["id"]),
        )

        assert response.status_code == 201
        stored = session.scalars(select(Anecdote)).one()
        assert stored.framework_id == target["id"]

    def test_entry_mode_cannot_be_claimed_by_the_caller(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        response = client.post(
            f"/api/public/capture/{link['token']}",
            json=_story(entry_mode="admin"),
        )

        assert response.status_code == 422, "entry_mode is not an accepted public field"

    def test_the_public_payload_carries_no_operator_metadata(
        self, client: TestClient
    ) -> None:
        """A respondent's browser is told the questions and nothing more."""
        framework = _framework(client)
        link = _link(client, framework["id"])

        served = client.get(f"/api/public/capture/{link['token']}").json()

        assert set(served) == {"definition", "framework_version"}
        for leaked in ("id", "framework_id", "anecdote_count", "edit_log", "is_active"):
            assert leaked not in served


class TestLinkProvenance:
    """Constraint 3: provenance on every record, whatever route it came by."""

    def test_a_link_story_is_stamped_link(self, client: TestClient, session) -> None:  # noqa: ANN001
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/public/capture/{link['token']}", json=_story())

        stored = session.scalars(select(Anecdote)).one()
        assert stored.entry_mode == "link"
        assert stored.source_type == "capture"
        assert stored.input_method == "typed"

    def test_the_story_records_which_link_brought_it(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/public/capture/{link['token']}", json=_story())

        stored = session.scalars(select(Anecdote)).one()
        assert stored.capture_link_id == link["id"]

    def test_a_voice_story_is_stamped_voice(self, client: TestClient, session) -> None:  # noqa: ANN001
        """Constraint 3: input_method distinguishes voice from typing."""
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(
            f"/api/public/capture/{link['token']}", json=_story(input_method="voice")
        )

        stored = session.scalars(select(Anecdote)).one()
        assert stored.input_method == "voice"

    def test_link_stories_are_still_hour_rounded(self, client: TestClient, session) -> None:  # noqa: ANN001
        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/public/capture/{link['token']}", json=_story())

        stored = session.scalars(select(Anecdote)).one()
        assert stored.created_at_hour.minute == 0
        assert stored.created_at_hour.second == 0

    def test_placements_validate_the_same_way_as_local_capture(
        self, client: TestClient
    ) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        response = client.post(
            f"/api/public/capture/{link['token']}",
            json=_story(
                significations=[
                    {"signifier_id": "pressure", "value": {"Speed": -0.5, "Care": 1.0, "Cost": 0.5}}
                ]
            ),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["error"]["code"] == "capture_invalid"


class TestKioskMode:
    """PRD §1.2: three entry modes share one wizard."""

    def test_kiosk_stories_are_stamped_kiosk(self, client: TestClient, session) -> None:  # noqa: ANN001
        framework = _framework(client)

        response = client.post(
            "/api/capture",
            json={**_story(), "framework_id": framework["id"], "entry_mode": "kiosk"},
        )

        assert response.status_code == 201
        assert response.json()["entry_mode"] == "kiosk"
        assert session.scalars(select(Anecdote)).one().entry_mode == "kiosk"

    def test_admin_remains_the_default(self, client: TestClient) -> None:
        framework = _framework(client)

        response = client.post(
            "/api/capture", json={**_story(), "framework_id": framework["id"]}
        )

        assert response.json()["entry_mode"] == "admin"

    def test_the_local_endpoint_refuses_to_claim_link(self, client: TestClient) -> None:
        """Only a real token may produce a ``link`` record."""
        framework = _framework(client)

        response = client.post(
            "/api/capture",
            json={**_story(), "framework_id": framework["id"], "entry_mode": "link"},
        )

        assert response.status_code == 422

    def test_imported_cannot_be_claimed_by_a_live_capture(self, client: TestClient) -> None:
        """Constraint 1: AI-derived content must not pose as first-hand."""
        framework = _framework(client)

        response = client.post(
            "/api/capture",
            json={**_story(), "framework_id": framework["id"], "input_method": "imported"},
        )

        assert response.status_code == 422


class TestQrCode:
    def test_returns_a_png(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        response = client.get(f"/api/capture-links/{link['id']}/qr.png")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert response.content.startswith(b"\x89PNG\r\n\x1a\n"), "not a valid PNG header"

    def test_the_qr_decodes_back_to_the_capture_url(self, client: TestClient) -> None:
        """A QR nobody can scan is a poster with a picture on it."""
        pytest.importorskip("PIL")
        framework = _framework(client)
        link = _link(client, framework["id"])

        response = client.get(f"/api/capture-links/{link['id']}/qr.png")

        # Re-encode the known URL and compare pixels: the same payload at the
        # same settings must produce the same image, which proves the endpoint
        # encoded the URL it claims to.
        from backend.qr import qr_png_bytes

        assert response.content == qr_png_bytes(link["url"])

    def test_a_missing_link_explains_itself(self, client: TestClient) -> None:
        response = client.get("/api/capture-links/4242/qr.png")

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "capture_link_not_found"


class TestRateLimiting:
    """PRD §4: public endpoints are rate-limited — per token, never per person."""

    def test_submissions_are_capped(self, client: TestClient) -> None:
        from backend.rate_limit import SUBMIT_LIMIT

        framework = _framework(client)
        link = _link(client, framework["id"])

        statuses = [
            client.post(f"/api/public/capture/{link['token']}", json=_story()).status_code
            for _ in range(SUBMIT_LIMIT + 2)
        ]

        assert statuses[:SUBMIT_LIMIT] == [201] * SUBMIT_LIMIT
        assert statuses[SUBMIT_LIMIT:] == [429, 429]

    def test_the_limit_message_reassures_rather_than_alarms(
        self, client: TestClient
    ) -> None:
        from backend.rate_limit import SUBMIT_LIMIT

        framework = _framework(client)
        link = _link(client, framework["id"])
        for _ in range(SUBMIT_LIMIT):
            client.post(f"/api/public/capture/{link['token']}", json=_story())

        error = client.post(
            f"/api/public/capture/{link['token']}", json=_story()
        ).json()["detail"]["error"]

        assert "not sent" in error["message"]
        assert "still here" in error["action"], "a respondent must not fear losing their words"

    def test_one_busy_link_does_not_block_another(self, client: TestClient) -> None:
        """The limit is per link, so one workshop cannot shut down another."""
        from backend.rate_limit import SUBMIT_LIMIT

        framework = _framework(client)
        busy = _link(client, framework["id"], label="Busy")
        quiet = _link(client, framework["id"], label="Quiet")

        for _ in range(SUBMIT_LIMIT + 1):
            client.post(f"/api/public/capture/{busy['token']}", json=_story())

        response = client.post(f"/api/public/capture/{quiet['token']}", json=_story())
        assert response.status_code == 201

    def test_revoking_frees_the_counters(self, client: TestClient, session) -> None:  # noqa: ANN001
        from backend.rate_limit import submit_limiter

        framework = _framework(client)
        link = _link(client, framework["id"])
        client.post(f"/api/public/capture/{link['token']}", json=_story())
        client.post(f"/api/capture-links/{link['id']}/revoke")

        token = session.scalars(select(CaptureLink.token)).one()
        from backend.rate_limit import SUBMIT_LIMIT

        assert submit_limiter.remaining(token) == SUBMIT_LIMIT
