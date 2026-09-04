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

#: The same twenty stories under the delta's new default (delta §6, baseline
#: block). Generated once, byte-identical thereafter, and never a substitute for
#: the file above — the pair is the evidence that the default changed the view
#: and nothing else.
PARTICIPANT_GOLDEN = (
    Path(__file__).resolve().parent / "golden" / "patterns_20_anecdotes_participant.json"
)

#: Fields the meaningfulness delta added to the response envelope (delta §4).
#:
#: The pre-delta golden pins the *aggregate*: every count, share, point, bin and
#: sort order. It cannot also pin fields that did not exist when it was written,
#: and the delta forbids regenerating it. So these two are lifted out before the
#: comparison, and pinned instead by the participant golden below — which is new,
#: and therefore free to hold them — and by
#: ``tests/test_signification_provenance.py``, which is about them.
DELTA_ENVELOPE_FIELDS = ("signified_by_applied", "counts_by_signified_by")


def serialise(payload: dict) -> str:
    """The one way this project writes a golden file.

    Sorted keys and a fixed indent, so the file's byte order comes from the data
    rather than from whatever order a dict happened to be built in.
    """
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def without_delta_envelope(payload: dict) -> dict:
    """The aggregate as it was before the delta, so the old golden still fits."""
    return {key: value for key, value in payload.items() if key not in DELTA_ENVELOPE_FIELDS}


def produce(client: TestClient) -> str:
    """The pre-delta view: every placement, whoever made it.

    ``signified_by=all`` is now explicit. Before the delta this endpoint had no
    such parameter and returned exactly this population; passing it keeps the
    golden measuring the same twenty stories' worth of placements rather than
    silently following the new default (delta §6, baseline block).
    """
    framework = build_golden_dataset(client)
    response = client.get(f"/api/patterns/{framework['id']}", params={"signified_by": "all"})
    assert response.status_code == 200, response.text
    return serialise(without_delta_envelope(response.json()))


def produce_participant(client: TestClient) -> str:
    """The new default view, envelope and all."""
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


# --------------------------------------------------------------------------
# The participant golden (delta §6, baseline block)
# --------------------------------------------------------------------------


def test_the_participant_golden_file_exists() -> None:
    assert PARTICIPANT_GOLDEN.is_file(), (
        "the participant golden is missing; generate it once with "
        "`python -m tests.regenerate_golden participant`"
    )


def test_the_default_view_is_byte_identical_to_its_own_golden(client: TestClient) -> None:
    """The new default, pinned the same way the old view has always been."""
    produced = produce_participant(client)

    assert produced == PARTICIPANT_GOLDEN.read_text(encoding="utf-8")


def test_the_two_goldens_agree_on_every_figure(client: TestClient) -> None:
    """The delta changed which placements are counted, not how they are counted.

    On this fixture every story was told and signified by the same person, so
    "participant" and "all" cover the same placements — and every figure in the
    two files must therefore be identical. What differs is only the envelope
    saying which view it is. If these two ever diverge on a count, the filter has
    started dropping placements it should keep.
    """
    stored = json.loads(GOLDEN.read_text(encoding="utf-8"))
    participant = json.loads(PARTICIPANT_GOLDEN.read_text(encoding="utf-8"))

    assert without_delta_envelope(participant) == stored
    assert participant["signified_by_applied"] == "participant"
    assert participant["counts_by_signified_by"] == {
        "participant": STORY_COUNT * 5,
        "ai_validated": 0,
    }
