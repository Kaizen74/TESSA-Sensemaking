"""Local capture (PRD §6 Phase 3).

The tests the PRD names for this phase: wizard round-trip, paper provenance, and
p95 under 200ms on submit. Draft-survives-reload lives in
``tests/test_capture_draft.py`` because it is browser-side behaviour.
"""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.models import Anecdote, Signification

TRIAD = {"id": "pressure", "title": "What drove this?", "corners": ["Speed", "Care", "Cost"]}
DYAD = {"id": "clarity", "title": "How clear was it?", "left": "Murky", "right": "Clear"}
STONES = {
    "id": "forces",
    "title": "Place the forces",
    "x_axis": {"low": "Rare", "high": "Constant"},
    "y_axis": {"low": "Minor", "high": "Major"},
    "chips": ["Time", "Kit"],
}
MCQ = {"id": "team", "title": "Which team?", "options": ["Ramp", "Cabin", "Cargo"]}

DEFINITION = {
    "prompt_text": "Tell us about a moment at work that stuck with you.",
    "triads": [TRIAD],
    "dyads": [DYAD],
    "stones": STONES,
    "mcqs": [MCQ],
    "capture_settings": {"respondent_groups": ["Ramp", "Cabin"]},
}

FULL_PLACEMENTS = [
    {"signifier_id": "pressure", "value": {"Speed": 0.5, "Care": 0.3, "Cost": 0.2}},
    {"signifier_id": "clarity", "value": {"value": 0.75}},
    {
        "signifier_id": "forces",
        "value": {"placements": [{"label": "Time", "x": 0.8, "y": 0.9}]},
    },
    {"signifier_id": "team", "value": {"selected": ["Ramp"]}},
]


def _framework(client: TestClient, definition: dict | None = None) -> dict:
    response = client.post(
        "/api/frameworks",
        json={"name": "Ground handling", "definition": definition or DEFINITION},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _submit(client: TestClient, framework_id: int, **overrides) -> dict:
    body = {
        "framework_id": framework_id,
        "text": "The inbound was early and nobody had the paperwork.",
        "input_method": "typed",
        "respondent_group": "Ramp",
        "significations": FULL_PLACEMENTS,
    }
    body.update(overrides)
    return client.post("/api/capture", json=body)


class TestWizardRoundTrip:
    """A story goes in through the wizard and comes back out intact."""

    def test_submission_is_accepted(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(client, framework["id"])

        assert response.status_code == 201, response.text
        body = response.json()
        assert body["anecdote_id"] > 0
        assert body["signification_count"] == 4

    def test_story_text_is_stored_exactly(self, client: TestClient, session) -> None:  # noqa: ANN001
        framework = _framework(client)
        text = "The inbound was early and nobody had the paperwork."
        _submit(client, framework["id"], text=text)

        stored = session.scalars(select(Anecdote)).one()
        assert stored.text == text

    def test_every_placement_round_trips(self, client: TestClient, session) -> None:  # noqa: ANN001
        framework = _framework(client)
        _submit(client, framework["id"])

        stored = {
            row.signifier_id: (row.signifier_type, row.value_json)
            for row in session.scalars(select(Signification)).all()
        }

        assert stored["pressure"][0] == "triad"
        assert stored["pressure"][1] == {"Speed": 0.5, "Care": 0.3, "Cost": 0.2}
        assert stored["clarity"] == ("dyad", {"value": 0.75})
        assert stored["forces"][0] == "stones"
        assert stored["forces"][1]["placements"] == [{"label": "Time", "x": 0.8, "y": 0.9}]
        assert stored["team"] == ("mcq", {"selected": ["Ramp"]})

    def test_triad_weights_still_sum_to_one_after_the_round_trip(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        framework = _framework(client)
        _submit(client, framework["id"])

        row = session.scalars(
            select(Signification).where(Signification.signifier_id == "pressure")
        ).one()
        assert sum(row.value_json.values()) == pytest.approx(1.0, abs=1e-6)

    def test_the_story_binds_to_the_exact_version_answered(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        framework = _framework(client)
        _submit(client, framework["id"])

        stored = session.scalars(select(Anecdote)).one()
        assert stored.framework_id == framework["id"]

    def test_reflection_names_a_signifier_to_show_back(self, client: TestClient) -> None:
        """PRD §9 assumption 7: reflection shows one signifier."""
        framework = _framework(client)
        body = _submit(client, framework["id"]).json()

        assert body["reflection_signifier_id"] == "pressure"

    def test_thankyou_text_comes_from_the_version_answered(self, client: TestClient) -> None:
        framework = _framework(
            client,
            {**DEFINITION, "capture_settings": {"thankyou_text": "Thanks — that helps."}},
        )
        body = _submit(client, framework["id"], respondent_group=None).json()

        assert body["thankyou_text"] == "Thanks — that helps."

    def test_a_story_with_no_placements_is_still_a_story(self, client: TestClient) -> None:
        """Skipping every question is allowed; the story is the point."""
        framework = _framework(client)
        response = _submit(client, framework["id"], significations=[])

        assert response.status_code == 201
        assert response.json()["signification_count"] == 0
        assert response.json()["reflection_signifier_id"] is None


class TestProvenance:
    """Constraint 3: provenance on every record."""

    def test_typed_capture_carries_full_provenance(self, client: TestClient, session) -> None:  # noqa: ANN001
        framework = _framework(client)
        _submit(client, framework["id"])

        stored = session.scalars(select(Anecdote)).one()
        assert stored.source_type == "capture"
        assert stored.entry_mode == "admin"
        assert stored.input_method == "typed"
        assert stored.respondent_group == "Ramp"
        assert stored.import_job_id is None
        assert stored.capture_link_id is None

    def test_paper_entry_is_stamped_as_paper(self, client: TestClient, session) -> None:  # noqa: ANN001
        """PRD §6 Phase 3: batch entry writes paper provenance."""
        framework = _framework(client)
        _submit(client, framework["id"], input_method="paper")

        stored = session.scalars(select(Anecdote)).one()
        assert stored.input_method == "paper"
        assert stored.entry_mode == "admin"

    def test_significations_record_who_interpreted(self, client: TestClient, session) -> None:  # noqa: ANN001
        framework = _framework(client)
        _submit(client, framework["id"])

        for row in session.scalars(select(Signification)).all():
            assert row.signified_by == "respondent"
            assert row.ai_confidence is None, "no AI touched a directly-captured placement"
            assert row.validated_at is not None

    def test_a_title_is_derived_for_the_story_browser(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        framework = _framework(client)
        _submit(client, framework["id"])

        stored = session.scalars(select(Anecdote)).one()
        assert stored.title_auto
        assert stored.title_auto.startswith("The inbound was early")

    def test_a_long_story_gets_a_short_title(self, client: TestClient, session) -> None:  # noqa: ANN001
        framework = _framework(client)
        _submit(client, framework["id"], text="word " * 400)

        stored = session.scalars(select(Anecdote)).one()
        assert len(stored.title_auto) <= 81


class TestAnonymityAtCapture:
    """Constraint 9, at the moment a story is actually written."""

    def test_stored_time_is_rounded_to_the_hour(self, client: TestClient, session) -> None:  # noqa: ANN001
        framework = _framework(client)
        _submit(client, framework["id"])

        stored = session.scalars(select(Anecdote)).one()
        assert stored.created_at_hour.minute == 0
        assert stored.created_at_hour.second == 0
        assert stored.created_at_hour.microsecond == 0

    def test_the_endpoint_refuses_identifying_extras(self, client: TestClient) -> None:
        """Nothing may smuggle an identifier in alongside the story."""
        framework = _framework(client)
        for smuggled in ("email", "name", "ip", "user_agent", "device_id"):
            response = client.post(
                "/api/capture",
                json={
                    "framework_id": framework["id"],
                    "text": "A story.",
                    smuggled: "something identifying",
                },
            )
            assert response.status_code == 422, f"'{smuggled}' was not rejected"


class TestCaptureIsNotAiOutput:
    """Constraint 1 gates AI output; first-hand testimony is not AI output."""

    def test_a_captured_story_is_validated_at_source(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        framework = _framework(client)
        _submit(client, framework["id"])

        stored = session.scalars(select(Anecdote)).one()
        assert stored.status == "validated"

    def test_captured_placements_carry_no_ai_confidence(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        framework = _framework(client)
        _submit(client, framework["id"])

        rows = session.scalars(select(Signification)).all()
        assert rows
        assert all(row.ai_confidence is None for row in rows)


class TestPlacementValidation:
    def test_unknown_signifier_is_refused(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[{"signifier_id": "nonexistent", "value": {"value": 0.5}}],
        )

        assert response.status_code == 400
        assert response.json()["detail"]["error"]["code"] == "capture_invalid"

    def test_triad_missing_a_corner_is_refused(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[
                {"signifier_id": "pressure", "value": {"Speed": 0.5, "Care": 0.5}}
            ],
        )

        assert response.status_code == 400
        assert "missing a corner" in response.json()["detail"]["error"]["message"]

    def test_triad_that_does_not_sum_to_one_is_normalised(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        """A slightly-off placement is repaired, not thrown away."""
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[
                {"signifier_id": "pressure", "value": {"Speed": 2.0, "Care": 1.0, "Cost": 1.0}}
            ],
        )

        assert response.status_code == 201
        row = session.scalars(select(Signification)).one()
        assert sum(row.value_json.values()) == pytest.approx(1.0, abs=1e-6)
        assert row.value_json["Speed"] == pytest.approx(0.5, abs=1e-6)

    def test_negative_triad_weight_is_refused(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[
                {"signifier_id": "pressure", "value": {"Speed": -0.2, "Care": 0.6, "Cost": 0.6}}
            ],
        )

        assert response.status_code == 400
        assert "outside the triangle" in response.json()["detail"]["error"]["message"]

    def test_dyad_out_of_range_is_refused(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[{"signifier_id": "clarity", "value": {"value": 1.4}}],
        )

        assert response.status_code == 400
        assert "off the end of the line" in response.json()["detail"]["error"]["message"]

    def test_stones_outside_the_square_is_refused(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[
                {
                    "signifier_id": "forces",
                    "value": {"placements": [{"label": "Time", "x": 1.3, "y": 0.5}]},
                }
            ],
        )

        assert response.status_code == 400
        assert "outside the square" in response.json()["detail"]["error"]["message"]

    def test_stones_unknown_chip_is_refused(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[
                {
                    "signifier_id": "forces",
                    "value": {"placements": [{"label": "Ghost", "x": 0.5, "y": 0.5}]},
                }
            ],
        )

        assert response.status_code == 400

    def test_mcq_unknown_option_is_refused(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[{"signifier_id": "team", "value": {"selected": ["Flight deck"]}}],
        )

        assert response.status_code == 400

    def test_single_choice_mcq_refuses_two_answers(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[{"signifier_id": "team", "value": {"selected": ["Ramp", "Cabin"]}}],
        )

        assert response.status_code == 400
        assert "takes one answer" in response.json()["detail"]["error"]["message"]

    def test_multi_choice_mcq_accepts_two_answers(self, client: TestClient) -> None:
        framework = _framework(
            client,
            {**DEFINITION, "mcqs": [{**MCQ, "multi": True}]},
        )
        response = _submit(
            client,
            framework["id"],
            significations=[{"signifier_id": "team", "value": {"selected": ["Ramp", "Cabin"]}}],
        )

        assert response.status_code == 201

    def test_answering_the_same_question_twice_is_refused(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[
                {"signifier_id": "clarity", "value": {"value": 0.2}},
                {"signifier_id": "clarity", "value": {"value": 0.8}},
            ],
        )

        assert response.status_code == 400
        assert "answered twice" in response.json()["detail"]["error"]["message"]

    def test_an_empty_story_is_refused(self, client: TestClient) -> None:
        framework = _framework(client)
        assert _submit(client, framework["id"], text="").status_code == 422

    def test_unknown_respondent_group_is_refused(self, client: TestClient) -> None:
        framework = _framework(client)
        response = _submit(client, framework["id"], respondent_group="Flight deck")

        assert response.status_code == 400
        assert response.json()["detail"]["error"]["code"] == "unknown_respondent_group"

    def test_missing_framework_explains_itself(self, client: TestClient) -> None:
        response = _submit(client, 4242)

        assert response.status_code == 404
        error = response.json()["detail"]["error"]
        assert error["code"] == "framework_not_found"
        assert error["action"]

    def test_every_refusal_is_plain_english(self, client: TestClient) -> None:
        """Constraint 7: a respondent must be able to act on the message."""
        framework = _framework(client)
        response = _submit(
            client,
            framework["id"],
            significations=[{"signifier_id": "clarity", "value": {"value": 9.0}}],
        )
        error = response.json()["detail"]["error"]

        assert error["message"].endswith(".")
        assert error["action"]
        for jargon in ("400", "HTTP", "None", "null", "Traceback", "pydantic"):
            assert jargon not in error["message"]


class TestVersionBinding:
    def test_answers_stay_with_the_version_they_answered(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        """A meaning change after capture must not move existing stories."""
        v1 = _framework(client)
        _submit(client, v1["id"])

        v2 = client.put(
            f"/api/frameworks/{v1['id']}",
            json={
                "definition": {**DEFINITION, "prompt_text": "A different question."},
                "edit_kind": "meaning_change",
            },
        ).json()

        stored = session.scalars(select(Anecdote)).one()
        assert stored.framework_id == v1["id"]
        assert stored.framework_id != v2["id"]

    def test_a_placement_for_a_removed_question_is_refused(self, client: TestClient) -> None:
        """Answering v1's question against v2 must not silently succeed."""
        v1 = _framework(client)
        v2 = client.put(
            f"/api/frameworks/{v1['id']}",
            json={"definition": {**DEFINITION, "dyads": []}},
        ).json()

        response = _submit(
            client,
            v2["id"],
            significations=[{"signifier_id": "clarity", "value": {"value": 0.5}}],
        )
        assert response.status_code == 400


class TestSubmitPerformance:
    """PRD §6 Phase 3: p95 < 200ms on submit."""

    def test_p95_submit_is_under_200ms(self, client: TestClient) -> None:
        framework = _framework(client)

        timings = []
        for _ in range(40):
            start = time.perf_counter()
            response = _submit(client, framework["id"])
            timings.append((time.perf_counter() - start) * 1000)
            assert response.status_code == 201

        timings.sort()
        p95 = timings[int(len(timings) * 0.95) - 1]
        assert p95 < 200, f"p95 was {p95:.1f}ms over {len(timings)} submissions"
