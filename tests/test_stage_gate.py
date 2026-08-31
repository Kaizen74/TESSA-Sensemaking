"""The stage machine and its 409 gate (constraints 1 and 12).

Two levels are tested. The table itself, because that is where the guarantee
lives — Stage B cannot be reached without passing through human confirmation,
whatever endpoints exist now or later. And the gate as the API applies it, so
the operator gets 409 and a sentence rather than a silent no-op.
"""

from __future__ import annotations

import pytest

from backend import errors, stage_machine
from backend.models import IMPORT_STAGES, ImportJob


def _job(stage: str) -> ImportJob:
    return ImportJob(
        filename="workshop.xlsx",
        file_type="xlsx",
        file_hash="0" * 64,
        stage=stage,
    )


def test_the_table_covers_every_stage_the_schema_allows() -> None:
    """A stage with no row would be a dead end nothing could describe."""
    assert set(stage_machine.ALLOWED_TRANSITIONS) == set(IMPORT_STAGES)
    assert set(stage_machine.STAGE_LABELS) == set(IMPORT_STAGES)
    assert set(stage_machine.STAGE_ACTIONS) == set(IMPORT_STAGES)


def test_the_happy_path_is_the_only_way_forward() -> None:
    assert stage_machine.ALLOWED_TRANSITIONS[stage_machine.STAGE_UPLOADED] == (
        stage_machine.STAGE_ORGANISED,
        stage_machine.STAGE_FAILED,
    )
    assert stage_machine.ALLOWED_TRANSITIONS[stage_machine.STAGE_ORGANISED] == (
        stage_machine.STAGE_MAPPING_CONFIRMED,
        stage_machine.STAGE_FAILED,
    )
    assert stage_machine.ALLOWED_TRANSITIONS[stage_machine.STAGE_MAPPING_CONFIRMED] == (
        stage_machine.STAGE_PROPOSED,
        stage_machine.STAGE_FAILED,
    )


def test_stage_b_cannot_be_reached_without_human_confirmation() -> None:
    """Constraint 1, stated as a property of the table rather than of a route.

    With ``mapping_confirmed`` removed from the graph, ``proposed`` becomes
    unreachable from every earlier stage. That is the guarantee: no ordering of
    calls — now, or when Phase 6 attaches Stage B to this edge — gets an
    AI-proposed signification into the queue without a person having said yes.
    """
    without_confirmation = {
        stage: tuple(
            target for target in targets if target != stage_machine.STAGE_MAPPING_CONFIRMED
        )
        for stage, targets in stage_machine.ALLOWED_TRANSITIONS.items()
    }
    original = stage_machine.ALLOWED_TRANSITIONS
    try:
        stage_machine.ALLOWED_TRANSITIONS = without_confirmation  # type: ignore[misc]
        for start in (
            stage_machine.STAGE_UPLOADED,
            stage_machine.STAGE_ORGANISED,
        ):
            assert not stage_machine.reachable(start, stage_machine.STAGE_PROPOSED)
    finally:
        stage_machine.ALLOWED_TRANSITIONS = original  # type: ignore[misc]

    # And with it back in place, the path exists — the test above is about the
    # confirmation step specifically, not about the graph being disconnected.
    assert stage_machine.reachable(
        stage_machine.STAGE_UPLOADED, stage_machine.STAGE_PROPOSED
    )


def test_a_finished_or_failed_job_goes_nowhere() -> None:
    assert stage_machine.ALLOWED_TRANSITIONS[stage_machine.STAGE_DONE] == ()
    assert stage_machine.ALLOWED_TRANSITIONS[stage_machine.STAGE_FAILED] == ()


def test_a_stage_cannot_repeat_itself() -> None:
    """Organising twice would organise one file into two different sets."""
    for stage, targets in stage_machine.ALLOWED_TRANSITIONS.items():
        assert stage not in targets


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("uploaded", "mapping_confirmed"),
        ("uploaded", "proposed"),
        ("uploaded", "done"),
        ("organised", "proposed"),
        ("organised", "done"),
        ("mapping_confirmed", "done"),
        ("organised", "uploaded"),
        ("proposed", "organised"),
    ],
)
def test_every_skip_and_every_step_backwards_is_refused(current: str, target: str) -> None:
    assert not stage_machine.can_advance(current, target)

    with pytest.raises(errors.AppError) as caught:
        stage_machine.advance(_job(current), target)

    assert caught.value.status_code == 409


def test_the_gate_says_where_the_file_has_got_to_and_what_to_do() -> None:
    """Constraint 7: a refusal the operator can act on, with no jargon in it."""
    job = _job(stage_machine.STAGE_UPLOADED)

    with pytest.raises(errors.AppError) as caught:
        stage_machine.require_stage(job, stage_machine.STAGE_ORGANISED)

    detail = caught.value.detail["error"]
    assert caught.value.status_code == 409
    assert detail["code"] == "wrong_stage"
    assert "workshop.xlsx" in detail["message"]
    assert detail["action"] == "Click Organise on this file first."
    for jargon in ("409", "stage", "uploaded", "mapping_confirmed"):
        assert jargon not in detail["message"]


def test_the_gate_lets_the_right_stage_through() -> None:
    stage_machine.require_stage(_job(stage_machine.STAGE_ORGANISED), "organised")


def test_advancing_along_the_path_moves_the_job() -> None:
    job = _job(stage_machine.STAGE_UPLOADED)

    stage_machine.advance(job, stage_machine.STAGE_ORGANISED)

    assert job.stage == stage_machine.STAGE_ORGANISED


def test_a_recoverable_error_is_written_down_but_does_not_park_the_job() -> None:
    """``failed`` is terminal, so a blinking network must not land there."""
    job = _job(stage_machine.STAGE_UPLOADED)

    stage_machine.record_error(job, "Narrative Lens could not reach the AI service.")

    assert job.stage == stage_machine.STAGE_UPLOADED
    assert job.error_message
