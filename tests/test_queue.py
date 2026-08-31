"""The validation queue over HTTP — accept, correct, reject.

Everything here is about one question: who decided this, and does the record say
so honestly? Accepting keeps the AI's name on a placement because the AI made
it; correcting moves the name to the analyst, but only on the placements they
actually moved.
"""

from __future__ import annotations

import time

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import Anecdote, ImportJob, Signification
from tests import ingest_fixtures as fx
from tests.queue_fixtures import make_framework, proposed_import


def _queue(client: TestClient, **params) -> dict:
    response = client.get("/api/queue", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def _setup(client: TestClient) -> tuple[dict, dict]:
    framework = make_framework(client)
    job = proposed_import(client, framework["id"])
    return framework, job


# --------------------------------------------------------------------------
# What arrives in the queue
# --------------------------------------------------------------------------


def test_marking_up_a_file_fills_the_queue(client: TestClient) -> None:
    _, job = _setup(client)

    assert job["stage"] == "proposed"
    assert job["queue"] == {"pending": 3, "validated": 0, "rejected": 0}
    assert _queue(client)["counts"]["pending"] == 3


def test_every_queued_story_carries_its_whole_provenance(client: TestClient) -> None:
    """Constraint 3, on the screen the operator actually reads."""
    framework, _ = _setup(client)

    item = _queue(client)["items"][0]

    assert item["source_type"] == "import"
    assert item["entry_mode"] == "admin"
    assert item["input_method"] == "imported"
    assert item["source_file"] == "workshop.xlsx"
    assert item["source_locator"] == "Responses row 2"
    assert item["respondent_group"] == "Ops"
    assert item["framework_id"] == framework["id"]
    assert item["framework_version"] == 1
    assert item["import_job_id"] is not None


def test_queued_times_are_still_hour_rounded(client: TestClient) -> None:
    """Constraint 9 does not stop applying because the story came from a file."""
    _setup(client)

    item = _queue(client)["items"][0]

    assert item["created_at_hour"].endswith("T00:00:00") or item[
        "created_at_hour"
    ].endswith(":00:00")


def test_a_queued_placement_says_the_ai_made_it_and_nobody_has_agreed(
    client: TestClient,
) -> None:
    _setup(client)

    item = _queue(client)["items"][0]

    assert item["significations"]
    for placement in item["significations"]:
        assert placement["signified_by"] == "ai"
        assert placement["validated_at"] is None
        assert placement["ai_confidence"] is not None


def test_the_queue_is_oldest_first(client: TestClient) -> None:
    _setup(client)

    ids = [item["anecdote_id"] for item in _queue(client)["items"]]

    assert ids == sorted(ids)


def test_the_queue_can_be_narrowed_to_one_file(client: TestClient) -> None:
    framework = make_framework(client)
    first = proposed_import(client, framework["id"])
    proposed_import(client, framework["id"], filename="workshop.csv")

    assert _queue(client)["counts"]["pending"] == 5
    narrowed = _queue(client, job_id=first["id"])
    assert narrowed["counts"]["pending"] == 3
    assert {item["import_job_id"] for item in narrowed["items"]} == {first["id"]}


def test_low_confidence_is_flagged_on_the_item_and_the_placement(
    client: TestClient,
) -> None:
    """Constraint 2 — a colour, not a different queue."""
    _setup(client)

    items = _queue(client)["items"]

    flagged = [item for item in items if item["has_low_confidence"]]
    assert flagged, "the fixture should produce at least one thin placement"
    for item in flagged:
        assert any(placement["low_confidence"] for placement in item["significations"])
    # Everything is on the same list regardless.
    assert len(items) == 3


def test_a_directly_captured_story_never_reaches_the_queue(client: TestClient) -> None:
    """Nothing AI touched it, so there is nothing for the operator to approve."""
    framework = make_framework(client)
    created = client.post(
        "/api/capture",
        json={
            "framework_id": framework["id"],
            "text": "We stayed late and the job went out on time.",
            "significations": [{"signifier_id": "d1", "value": {"value": 0.8}}],
        },
    )
    assert created.status_code == 201

    assert _queue(client)["items"] == []
    assert _queue(client)["counts"]["validated"] == 1


# --------------------------------------------------------------------------
# Accept
# --------------------------------------------------------------------------


def test_accepting_keeps_the_placements_and_stamps_them(client: TestClient) -> None:
    _setup(client)
    item = _queue(client)["items"][0]
    before = {p["signifier_id"]: p["value"] for p in item["significations"]}

    response = client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "accept"})

    assert response.status_code == 200, response.text
    decided = response.json()
    assert decided["status"] == "validated"
    for placement in decided["significations"]:
        assert placement["value"] == before[placement["signifier_id"]]
        assert placement["validated_at"] is not None
        # The AI placed it and a person agreed. Saying the person placed it
        # would be a nicer story and a false one.
        assert placement["signified_by"] == "ai"
        assert placement["ai_confidence"] is not None


def test_accepting_removes_it_from_the_queue(client: TestClient) -> None:
    _setup(client)
    item = _queue(client)["items"][0]

    client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "accept"})

    after = _queue(client)
    assert after["counts"] == {"pending": 2, "validated": 1, "rejected": 0}
    assert item["anecdote_id"] not in [row["anecdote_id"] for row in after["items"]]


def test_accepting_does_not_take_placements(client: TestClient) -> None:
    _setup(client)
    item = _queue(client)["items"][0]

    response = client.put(
        f"/api/queue/{item['anecdote_id']}",
        json={"action": "accept", "significations": []},
    )

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "unexpected_placements"
    assert "Correct" in error["action"]


# --------------------------------------------------------------------------
# Correct
# --------------------------------------------------------------------------


def test_correcting_restamps_only_what_the_operator_moved(client: TestClient) -> None:
    _setup(client)
    item = _queue(client)["items"][0]
    original = {p["signifier_id"]: p["value"] for p in item["significations"]}

    response = client.put(
        f"/api/queue/{item['anecdote_id']}",
        json={
            "action": "correct",
            "significations": [
                {"signifier_id": "t1", "value": {"Speed": 0.2, "Care": 0.5, "Cost": 0.3}},
                {"signifier_id": "d1", "value": original["d1"]},
            ],
        },
    )

    assert response.status_code == 200, response.text
    decided = response.json()
    by_id = {p["signifier_id"]: p for p in decided["significations"]}

    assert decided["status"] == "validated"
    assert by_id["t1"]["signified_by"] == "analyst"
    assert by_id["t1"]["ai_confidence"] is None
    assert by_id["t1"]["value"] == {"Speed": 0.2, "Care": 0.5, "Cost": 0.3}
    # Left exactly as proposed, so it still says the AI proposed it.
    assert by_id["d1"]["signified_by"] == "ai"
    assert by_id["d1"]["ai_confidence"] is not None
    assert all(p["validated_at"] is not None for p in decided["significations"])


def test_correcting_can_drop_a_placement_altogether(client: TestClient) -> None:
    """The AI read something into a story that is not there — so remove it."""
    _setup(client)
    item = _queue(client)["items"][0]
    assert len(item["significations"]) == 5

    response = client.put(
        f"/api/queue/{item['anecdote_id']}",
        json={
            "action": "correct",
            "significations": [{"signifier_id": "d1", "value": {"value": 0.5}}],
        },
    )

    assert response.status_code == 200
    assert len(response.json()["significations"]) == 1


def test_correcting_can_empty_a_story_of_placements(client: TestClient) -> None:
    _setup(client)
    item = _queue(client)["items"][0]

    response = client.put(
        f"/api/queue/{item['anecdote_id']}", json={"action": "correct", "significations": []}
    )

    assert response.status_code == 200
    assert response.json()["significations"] == []
    assert response.json()["status"] == "validated"


def test_a_correction_is_checked_against_the_framework(client: TestClient) -> None:
    """The operator is held to the same shapes as the AI and the respondent."""
    _setup(client)
    item = _queue(client)["items"][0]

    response = client.put(
        f"/api/queue/{item['anecdote_id']}",
        json={
            "action": "correct",
            "significations": [{"signifier_id": "m1", "value": {"selected": ["Superb"]}}],
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "capture_invalid"


def test_correcting_needs_the_placements(client: TestClient) -> None:
    _setup(client)
    item = _queue(client)["items"][0]

    response = client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "correct"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "missing_placements"


# --------------------------------------------------------------------------
# Reject
# --------------------------------------------------------------------------


def test_rejecting_keeps_the_story_but_never_validates_it(
    client: TestClient, session: Session
) -> None:
    _setup(client)
    item = _queue(client)["items"][0]

    response = client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "reject"})

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    # Still on disk, so the import stays auditable.
    stored = session.get(Anecdote, item["anecdote_id"])
    assert stored is not None and stored.status == "rejected"
    placements = session.query(Signification).filter_by(anecdote_id=item["anecdote_id"]).all()
    assert placements and all(placement.validated_at is None for placement in placements)


def test_rejecting_does_not_take_placements(client: TestClient) -> None:
    _setup(client)
    item = _queue(client)["items"][0]

    response = client.put(
        f"/api/queue/{item['anecdote_id']}",
        json={"action": "reject", "significations": []},
    )

    assert response.status_code == 400


# --------------------------------------------------------------------------
# Deciding twice, and other things that go wrong
# --------------------------------------------------------------------------


def test_a_story_cannot_be_decided_twice(client: TestClient) -> None:
    _setup(client)
    item = _queue(client)["items"][0]
    client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "accept"})

    again = client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "reject"})

    assert again.status_code == 409
    error = again.json()["error"]
    assert error["code"] == "already_decided"
    assert "already been dealt with" in error["message"]


def test_a_directly_captured_story_cannot_be_re_decided(client: TestClient) -> None:
    """It is already validated, so the queue has nothing to say about it."""
    framework = make_framework(client)
    created = client.post(
        "/api/capture",
        json={"framework_id": framework["id"], "text": "A short account.", "significations": []},
    ).json()

    response = client.put(
        f"/api/queue/{created['anecdote_id']}", json={"action": "reject"}
    )

    assert response.status_code == 409


def test_an_unknown_story_says_so_in_plain_english(client: TestClient) -> None:
    response = client.put("/api/queue/404", json={"action": "accept"})

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "story_not_found"
    assert "Reload the queue" in error["action"]


def test_an_unknown_action_is_refused(client: TestClient) -> None:
    _setup(client)
    item = _queue(client)["items"][0]

    response = client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "approve"})

    assert response.status_code == 422


# --------------------------------------------------------------------------
# Emptying the queue finishes the file
# --------------------------------------------------------------------------


def test_the_file_is_finished_only_when_its_queue_empties(
    client: TestClient, session: Session
) -> None:
    _, job = _setup(client)
    items = _queue(client)["items"]

    client.put(f"/api/queue/{items[0]['anecdote_id']}", json={"action": "accept"})
    assert session.get(ImportJob, job["id"]).stage == "proposed"

    client.put(f"/api/queue/{items[1]['anecdote_id']}", json={"action": "reject"})
    assert session.get(ImportJob, job["id"]).stage == "proposed"

    client.put(f"/api/queue/{items[2]['anecdote_id']}", json={"action": "accept"})

    finished = client.get(f"/api/import/{job['id']}").json()
    assert finished["stage"] == "done"
    assert finished["queue"] == {"pending": 0, "validated": 2, "rejected": 1}
    assert finished["stage_label"] == "finished"


def test_a_finished_file_goes_no_further(client: TestClient) -> None:
    _, job = _setup(client)
    for item in _queue(client)["items"]:
        client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "accept"})

    again = client.post(f"/api/import/{job['id']}/propose", json={"framework_id": 1})

    assert again.status_code == 409
    assert again.json()["error"]["code"] == "wrong_stage"


def test_one_file_finishing_does_not_finish_another(client: TestClient) -> None:
    framework = make_framework(client)
    first = proposed_import(client, framework["id"])
    second = proposed_import(client, framework["id"], filename="workshop.csv")

    for item in _queue(client, job_id=first["id"])["items"]:
        client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "accept"})

    assert client.get(f"/api/import/{first['id']}").json()["stage"] == "done"
    assert client.get(f"/api/import/{second['id']}").json()["stage"] == "proposed"


# --------------------------------------------------------------------------
# Budgets
# --------------------------------------------------------------------------


def test_reading_the_queue_is_inside_the_200ms_budget(client: TestClient) -> None:
    """PRD §4: AI endpoints are exempt; the queue is not."""
    _setup(client)

    start = time.perf_counter()
    client.get("/api/queue")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 200


def test_deciding_is_inside_the_200ms_budget(client: TestClient) -> None:
    _setup(client)
    item = _queue(client)["items"][0]

    start = time.perf_counter()
    client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "accept"})
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 200


def test_prose_imports_reach_the_queue_too(client: TestClient) -> None:
    """Every file class ends in the same place, whatever shape it started in."""
    framework = make_framework(client)

    proposed_import(client, framework["id"], filename="workshop.txt", data=fx.txt_bytes())

    items = _queue(client)["items"]
    assert len(items) == 3
    assert {item["source_locator"] for item in items} == {
        "paragraph 1",
        "paragraph 2",
        "paragraph 3",
    }
