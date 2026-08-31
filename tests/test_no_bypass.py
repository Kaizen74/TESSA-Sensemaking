"""The no-bypass test (acceptance criterion 7, constraint 1).

> No AI-organised anecdote and no AI-proposed signification ever enters the
> dataset without explicit human validation, at any confidence level.

That is a claim about every path through the app, not about one endpoint, so it
is tested twice over.

**Behaviourally** — a file is driven the whole way through both AI stages and
then the dataset is swept. Nothing Stage B wrote is in it. Every other endpoint
is then tried against those pending stories, and none of them moves one.

**Structurally** — ``backend/dataset.py`` is the single definition of what
counts as data, and exactly two modules are allowed to write ``validated``:
capture, where no AI was involved at all, and the queue, where a person just
said yes. A future edit that starts writing it from a third place fails here,
which is the point: a promise that only holds while everyone remembers it is
not engineered, it is hoped for.
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import dataset
from backend.models import Anecdote, Signification
from tests.queue_fixtures import confirmed_import, make_framework, proposed_import

BACKEND = Path(__file__).resolve().parent.parent / "backend"

#: The only two modules that may move a story into the dataset. Capture is
#: first-hand testimony that no model touched; the queue is a person saying yes.
ALLOWED_VALIDATORS = {"routers/capture.py", "routers/queue.py"}


def _validated(session: Session) -> list[Anecdote]:
    return list(session.scalars(dataset.only_validated(select(Anecdote))).all())


# --------------------------------------------------------------------------
# Behaviour: the whole pipeline, then a sweep
# --------------------------------------------------------------------------


def test_both_ai_stages_leave_the_dataset_empty(
    client: TestClient, session: Session
) -> None:
    framework = make_framework(client)

    proposed_import(client, framework["id"])

    # Stories exist. None of them is data.
    assert session.query(Anecdote).count() == 3
    assert _validated(session) == []
    assert session.query(Signification).count() > 0
    assert session.query(Signification).filter(
        Signification.validated_at.isnot(None)
    ).count() == 0


def test_stage_a_alone_creates_no_story_at_all(
    client: TestClient, session: Session
) -> None:
    """Constraint 1's first half: AI-organised anecdotes wait for a person too."""
    confirmed_import(client)

    assert session.query(Anecdote).count() == 0


def test_confidence_never_changes_the_route(
    client: TestClient, session: Session
) -> None:
    """Constraint 2: at any confidence level, it queues.

    "At any confidence level" is the part of constraint 1 a well-meaning
    optimisation would break first — auto-accepting the 0.98s to save the
    operator time. So the fixture is checked to contain placements on both sides
    of the 0.70 line, and then every one of them is checked to be waiting.
    """
    framework = make_framework(client)
    proposed_import(client, framework["id"])

    items = client.get("/api/queue").json()["items"]
    placements = [
        placement for item in items for placement in item["significations"]
    ]

    assert any(placement["low_confidence"] for placement in placements)
    assert any(not placement["low_confidence"] for placement in placements)
    assert all(placement["validated_at"] is None for placement in placements)
    assert all(item["status"] == dataset.STATUS_PENDING for item in items)
    assert _validated(session) == []


def test_no_other_endpoint_can_move_a_story_into_the_dataset(
    client: TestClient, session: Session
) -> None:
    """Every door except the queue, tried against stories that are waiting."""
    framework = make_framework(client)
    job = proposed_import(client, framework["id"])
    job_id = job["id"]

    attempts = [
        client.post(f"/api/import/{job_id}/organise"),
        client.post(f"/api/import/{job_id}/mapping", json={"sheets": []}),
        client.post(f"/api/import/{job_id}/propose", json={"framework_id": framework["id"]}),
        client.get(f"/api/import/{job_id}"),
        client.get("/api/import"),
        client.get("/api/queue"),
        client.get(f"/api/frameworks/{framework['id']}"),
    ]

    # The three stage transitions are refused outright; the reads are harmless.
    assert [attempt.status_code for attempt in attempts] == [409, 409, 409, 200, 200, 200, 200]
    assert _validated(session) == []
    assert session.query(Anecdote).filter_by(status=dataset.STATUS_PENDING).count() == 3


def test_capture_cannot_launder_a_pending_story(
    client: TestClient, session: Session
) -> None:
    """A new capture is a new story, never a promotion of a waiting one."""
    framework = make_framework(client)
    proposed_import(client, framework["id"])

    client.post(
        "/api/capture",
        json={
            "framework_id": framework["id"],
            "text": "A different story altogether.",
            "significations": [],
        },
    )

    validated = _validated(session)
    assert len(validated) == 1
    assert validated[0].source_type == "capture"
    assert validated[0].import_job_id is None


def test_a_rejected_story_is_never_data(client: TestClient, session: Session) -> None:
    framework = make_framework(client)
    proposed_import(client, framework["id"])
    items = client.get("/api/queue").json()["items"]

    for item in items:
        client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "reject"})

    assert _validated(session) == []
    assert session.query(Anecdote).count() == 3


def test_the_queue_is_the_way_in(client: TestClient, session: Session) -> None:
    """And it does work — otherwise the tests above prove only that it is broken."""
    framework = make_framework(client)
    proposed_import(client, framework["id"])
    items = client.get("/api/queue").json()["items"]

    client.put(f"/api/queue/{items[0]['anecdote_id']}", json={"action": "accept"})

    validated = _validated(session)
    assert [anecdote.id for anecdote in validated] == [items[0]["anecdote_id"]]
    placements = session.query(Signification).filter_by(anecdote_id=validated[0].id).all()
    assert placements and all(placement.validated_at is not None for placement in placements)


def test_correcting_is_also_a_human_yes(client: TestClient, session: Session) -> None:
    framework = make_framework(client)
    proposed_import(client, framework["id"])
    item = client.get("/api/queue").json()["items"][0]

    client.put(
        f"/api/queue/{item['anecdote_id']}",
        json={
            "action": "correct",
            "significations": [{"signifier_id": "d1", "value": {"value": 0.5}}],
        },
    )

    assert [anecdote.id for anecdote in _validated(session)] == [item["anecdote_id"]]


# --------------------------------------------------------------------------
# Structure: the promise as a property of the code
# --------------------------------------------------------------------------


def _backend_modules() -> list[Path]:
    return [
        path
        for path in sorted(BACKEND.rglob("*.py"))
        # Migrations declare the vocabulary; they never move a story.
        if "alembic" not in path.parts
    ]


def test_only_two_modules_write_validated() -> None:
    writers = set()
    for path in _backend_modules():
        source = path.read_text(encoding="utf-8")
        if re.search(r"status\s*=\s*STATUS_VALIDATED", source):
            writers.add(path.relative_to(BACKEND).as_posix())

    assert writers == ALLOWED_VALIDATORS


def test_nobody_writes_the_status_as_a_bare_string() -> None:
    """One symbol, so the test above cannot be sidestepped by a literal."""
    offenders = [
        path.relative_to(BACKEND).as_posix()
        for path in _backend_modules()
        if re.search(r"status\s*=\s*[\"']validated[\"']", path.read_text(encoding="utf-8"))
    ]

    assert offenders == []


def test_the_definition_of_data_lives_in_one_place() -> None:
    """Anything that reads the dataset goes through ``only_validated``."""
    source = (BACKEND / "dataset.py").read_text(encoding="utf-8")

    assert dataset.STATUS_VALIDATED == "validated"
    assert "def only_validated" in source
    # The filter is stated once, in the function, and nowhere else.
    assert source.count("Anecdote.status == STATUS_VALIDATED") == 1


def test_the_three_statuses_are_the_schema_s_own() -> None:
    from backend.models import ANECDOTE_STATUSES

    assert set(ANECDOTE_STATUSES) == {
        dataset.STATUS_PENDING,
        dataset.STATUS_VALIDATED,
        dataset.STATUS_REJECTED,
    }
