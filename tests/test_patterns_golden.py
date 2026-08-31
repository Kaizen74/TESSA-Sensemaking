"""The pattern golden — byte-identical from Phase 7 onward (PRD §6).

Twenty stories with placements fixed by arithmetic go through the real capture
endpoint, and the whole aggregate is compared against a stored file character
for character.

This is a blunt instrument on purpose. Constraint 11 says patterns are computed,
never composed, and the way that promise fails in practice is not a dramatic
rewrite — it is a rounding change, a re-sort, a bin boundary moved by one, a
field quietly added. None of those would fail a test that only checked a few
numbers. A byte comparison fails all of them, and the diff says exactly what
moved.

Regenerating the golden is a deliberate act: run

    python -m tests.regenerate_golden

and the change shows up in review as a diff of the file, which is the point.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from tests.patterns_fixtures import STORY_COUNT, build_golden_dataset

GOLDEN = Path(__file__).resolve().parent / "golden" / "patterns_20_anecdotes.json"


def serialise(payload: dict) -> str:
    """The one way this project writes a golden file.

    Sorted keys and a fixed indent, so the file's byte order comes from the data
    rather than from whatever order a dict happened to be built in.
    """
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def produce(client: TestClient) -> str:
    framework = build_golden_dataset(client)
    response = client.get(f"/api/patterns/{framework['id']}")
    assert response.status_code == 200, response.text
    return serialise(response.json())


def test_the_golden_file_exists() -> None:
    """A missing golden would make every other test here silently vacuous."""
    assert GOLDEN.is_file(), (
        "the pattern golden is missing; regenerate it with "
        "`python -m tests.regenerate_golden`"
    )


def test_the_aggregate_is_byte_identical_to_the_golden(client: TestClient) -> None:
    produced = produce(client)

    assert produced == GOLDEN.read_text(encoding="utf-8")


def test_the_aggregate_is_the_same_twice_running(client: TestClient) -> None:
    """Determinism, checked against itself rather than against the file.

    If aggregation ever picked up an unstable sort or a set iteration order,
    this fails even on a machine whose golden was regenerated to match it.
    """
    framework = build_golden_dataset(client)

    first = client.get(f"/api/patterns/{framework['id']}").json()
    second = client.get(f"/api/patterns/{framework['id']}").json()

    assert serialise(first) == serialise(second)


def test_the_golden_covers_every_signifier_kind() -> None:
    """A golden that missed a kind would pin three quarters of the maths."""
    stored = json.loads(GOLDEN.read_text(encoding="utf-8"))

    assert len(stored["triads"]) == 2
    assert len(stored["dyads"]) == 1
    assert stored["stones"] is not None
    assert len(stored["mcqs"]) == 1
    assert len(stored["demographics"]) == 4
    assert stored["total"] == STORY_COUNT


def test_the_golden_holds_real_placements() -> None:
    """Twenty stories, every one of them answered on every question."""
    stored = json.loads(GOLDEN.read_text(encoding="utf-8"))

    assert stored["triads"][0]["answered"] == STORY_COUNT
    assert stored["dyads"][0]["answered"] == STORY_COUNT
    assert stored["stones"]["answered"] == STORY_COUNT
    assert len(stored["stones"]["points"]) == STORY_COUNT * 3
    assert sum(bar["count"] for bar in stored["mcqs"][0]["bars"]) == STORY_COUNT
