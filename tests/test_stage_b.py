"""Stage B — what it proposes, and what it is not allowed to get away with.

Stage B is where a model's judgement first touches the shape of the data, so it
is held to the framework by the same validator a respondent's own submission
goes through. A model cannot name a corner that does not exist, put a dyad off
the end of its line, or pick an option that is not on the list — not because it
is asked nicely not to, but because the proposal is checked before it is stored.
"""

from __future__ import annotations

from typing import Any

import pytest

from backend import ai_client
from backend import propose as stage_b
from backend.framework_schema import FrameworkDefinition
from backend.propose import CHUNK_SIZE, ProposeError, chunks, describe_signifiers, propose
from tests.queue_fixtures import FULL_DEFINITION

STORIES = [
    "The parts arrived three hours before the deadline and nobody had told the "
    "night shift they were coming.",
    "The checklist assumed you had both hands free, which on a wet deck you "
    "never do.",
]


@pytest.fixture
def definition() -> FrameworkDefinition:
    return FrameworkDefinition.model_validate(FULL_DEFINITION)


def _reply(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    def fake(*, system: str, prompt: str, shape: type, mock: object) -> Any:
        return shape.model_validate(payload)

    monkeypatch.setattr(stage_b.ai_client, "request_json", fake)


# --------------------------------------------------------------------------
# Chunking (PRD §4a)
# --------------------------------------------------------------------------


def test_stage_b_is_chunked_at_twenty() -> None:
    assert CHUNK_SIZE == 20


def test_a_long_file_is_split_into_calls_of_twenty() -> None:
    stories = [f"story {n}" for n in range(45)]

    batches = chunks(stories)

    assert [len(batch) for batch in batches] == [20, 20, 5]
    assert [story for batch in batches for story in batch] == stories


def test_a_short_file_is_one_call() -> None:
    assert chunks(["one", "two"]) == [["one", "two"]]


def test_every_story_in_a_multi_chunk_file_keeps_its_own_index(
    definition: FrameworkDefinition,
) -> None:
    """The index is how a proposal finds its story, so it must survive chunking."""
    stories = [f"Something happened on day {n}, and it mattered." for n in range(25)]

    proposals = propose(definition, stories)

    assert [proposal.index for proposal in proposals] == list(range(25))


# --------------------------------------------------------------------------
# What the mock proposes
# --------------------------------------------------------------------------


def test_every_signifier_kind_gets_a_placement(definition: FrameworkDefinition) -> None:
    proposals = propose(definition, STORIES[:1])

    kinds = {placement.signifier_type for placement in proposals[0].placements}
    assert kinds == {"triad", "dyad", "stones", "mcq"}
    # Two triads, a dyad, the stones canvas, and one MCQ.
    assert len(proposals[0].placements) == 5


def test_the_mock_is_deterministic(definition: FrameworkDefinition) -> None:
    """The same file marked up twice proposes the same thing.

    ``hash()`` is salted per process; a digest is not. Without this a golden
    baseline could not exist at all.
    """
    first = propose(definition, STORIES)
    second = propose(definition, STORIES)

    assert first == second


def test_different_stories_are_placed_differently(
    definition: FrameworkDefinition,
) -> None:
    proposals = propose(definition, STORIES)

    first = next(p for p in proposals[0].placements if p.signifier_id == "t1")
    second = next(p for p in proposals[1].placements if p.signifier_id == "t1")
    assert first.value != second.value


def test_triad_weights_sum_to_one(definition: FrameworkDefinition) -> None:
    proposals = propose(definition, STORIES)

    for proposal in proposals:
        for placement in proposal.placements:
            if placement.signifier_type == "triad":
                assert sum(placement.value.values()) == pytest.approx(1.0, abs=1e-5)


def test_stones_place_every_chip_inside_the_square(
    definition: FrameworkDefinition,
) -> None:
    proposals = propose(definition, STORIES[:1])

    stones = next(p for p in proposals[0].placements if p.signifier_type == "stones")
    labels = [placement["label"] for placement in stones.value["placements"]]
    assert labels == ["Planning", "Doing", "Fixing"]
    for placement in stones.value["placements"]:
        assert 0.0 <= placement["x"] <= 1.0
        assert 0.0 <= placement["y"] <= 1.0


def test_an_mcq_picks_one_of_the_real_options(definition: FrameworkDefinition) -> None:
    proposals = propose(definition, STORIES[:1])

    mcq = next(p for p in proposals[0].placements if p.signifier_type == "mcq")
    assert mcq.value["selected"][0] in ("Well", "Badly", "Unresolved")
    assert len(mcq.value["selected"]) == 1


def test_confidence_lands_on_both_sides_of_the_amber_line(
    definition: FrameworkDefinition,
) -> None:
    """Constraint 2's threshold has to be exercised by real fixtures."""
    stories = [f"On day {n} something happened that changed how we work." for n in range(12)]

    proposals = propose(definition, stories)

    scores = [p.confidence for proposal in proposals for p in proposal.placements]
    assert any(score < ai_client.LOW_CONFIDENCE for score in scores)
    assert any(score >= ai_client.LOW_CONFIDENCE for score in scores)
    assert all(0.0 <= score <= 1.0 for score in scores)


def test_a_story_with_any_thin_placement_is_flagged(
    definition: FrameworkDefinition,
) -> None:
    stories = [f"Day {n}." for n in range(20)]

    proposals = propose(definition, stories)

    flagged = [proposal for proposal in proposals if proposal.has_low_confidence]
    assert flagged
    for proposal in flagged:
        assert any(p.confidence < ai_client.LOW_CONFIDENCE for p in proposal.placements)


# --------------------------------------------------------------------------
# The prompt tells the model exactly what it may say
# --------------------------------------------------------------------------


def test_the_prompt_spells_out_every_label(definition: FrameworkDefinition) -> None:
    """The only thing between the model and an invented corner is this list."""
    described = describe_signifiers(definition)

    by_id = {entry["signifier_id"]: entry for entry in described}
    assert set(by_id) == {"t1", "t2", "d1", "s1", "m1"}
    assert by_id["t1"]["corners"] == ["Speed", "Care", "Cost"]
    assert by_id["d1"]["left"] == "Alone" and by_id["d1"]["right"] == "Backed"
    assert by_id["s1"]["chips"] == ["Planning", "Doing", "Fixing"]
    assert by_id["m1"]["options"] == ["Well", "Badly", "Unresolved"]
    assert all(entry["value_shape"] for entry in described)


def test_the_prompt_forbids_guessing() -> None:
    assert "A missing answer is better" in stage_b.PROPOSE_SYSTEM
    assert "Never invent" in stage_b.PROPOSE_SYSTEM


# --------------------------------------------------------------------------
# What Stage B is not allowed to get away with
# --------------------------------------------------------------------------


def test_an_invented_corner_stops_the_markup(
    definition: FrameworkDefinition, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reply(
        monkeypatch,
        {
            "stories": [
                {
                    "index": 0,
                    "placements": [
                        {
                            "signifier_id": "t1",
                            "value": {"Speed": 0.3, "Care": 0.3, "Urgency": 0.4},
                            "confidence": 0.95,
                        }
                    ],
                }
            ]
        },
    )

    with pytest.raises(ProposeError) as caught:
        propose(definition, STORIES[:1])

    assert caught.value.code == "propose_invalid_placement"


def test_an_unknown_signifier_stops_the_markup(
    definition: FrameworkDefinition, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reply(
        monkeypatch,
        {
            "stories": [
                {
                    "index": 0,
                    "placements": [
                        {"signifier_id": "t9", "value": {"value": 0.5}, "confidence": 0.9}
                    ],
                }
            ]
        },
    )

    with pytest.raises(ProposeError) as caught:
        propose(definition, STORIES[:1])

    assert caught.value.code == "propose_invalid_placement"


def test_an_option_that_is_not_on_the_list_stops_the_markup(
    definition: FrameworkDefinition, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reply(
        monkeypatch,
        {
            "stories": [
                {
                    "index": 0,
                    "placements": [
                        {
                            "signifier_id": "m1",
                            "value": {"selected": ["Mixed"]},
                            "confidence": 0.9,
                        }
                    ],
                }
            ]
        },
    )

    with pytest.raises(ProposeError) as caught:
        propose(definition, STORIES[:1])

    assert caught.value.code == "propose_invalid_placement"


def test_a_missing_story_stops_the_markup(
    definition: FrameworkDefinition, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reply(monkeypatch, {"stories": [{"index": 0, "placements": []}]})

    with pytest.raises(ProposeError) as caught:
        propose(definition, STORIES)

    assert caught.value.code == "propose_stories_mismatch"
    assert "every story" in caught.value.message


def test_leaving_a_question_unanswered_is_allowed(
    definition: FrameworkDefinition, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A silence is better than an invention, and the prompt says so."""
    _reply(
        monkeypatch,
        {
            "stories": [
                {
                    "index": 0,
                    "placements": [
                        {"signifier_id": "d1", "value": {"value": 0.4}, "confidence": 0.5}
                    ],
                }
            ]
        },
    )

    proposals = propose(definition, STORIES[:1])

    assert [placement.signifier_id for placement in proposals[0].placements] == ["d1"]


def test_a_framework_with_no_signifiers_proposes_nothing() -> None:
    """A question set that asks nothing gets no placements, not an error."""
    bare = FrameworkDefinition.model_validate({"prompt_text": "Tell us a story."})

    proposals = propose(bare, STORIES)

    assert [proposal.placements for proposal in proposals] == [[], []]
