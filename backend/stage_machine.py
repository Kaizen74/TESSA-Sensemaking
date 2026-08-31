"""The ingestion stage machine and its gate (PRD §3, §4; constraints 1 and 12).

An import walks one path and cannot skip a step:

``uploaded → organised → mapping_confirmed → proposed → done``

with ``failed`` reachable from any working stage. The interesting edge is the
third one. Constraint 1 says Stage A output — including the column mapping —
requires human confirmation before Stage B may run, and constraint 12 says
tabular ingestion requires a *confirmed* mapping and displayed row
reconciliation. Those are not warnings printed next to a button; they are this
table. A job that has not reached ``mapping_confirmed`` cannot become
``proposed``, so there is no order of API calls that gets AI-proposed
significations into the queue without a person having said yes first.

The gate answers with 409 and a sentence the operator can act on, never a
silent no-op and never a redirect that quietly does the missing step for them.

Stages have handlers attached to them phase by phase — Phase 5 builds the walk
as far as ``mapping_confirmed``; Phase 6 attaches Stage B to the
``mapping_confirmed → proposed`` edge that is already refused here. The table
is complete now precisely so that edge is guarded before anything can drive it.
"""

from __future__ import annotations

from backend import errors
from backend.models import IMPORT_STAGES, ImportJob

STAGE_UPLOADED = "uploaded"
STAGE_ORGANISED = "organised"
STAGE_MAPPING_CONFIRMED = "mapping_confirmed"
STAGE_PROPOSED = "proposed"
STAGE_DONE = "done"
STAGE_FAILED = "failed"

#: Every move the machine permits. Anything not listed is refused — including
#: staying put, which would otherwise let Analyse be clicked twice and organise
#: the same file into two different sets of stories.
ALLOWED_TRANSITIONS: dict[str, tuple[str, ...]] = {
    STAGE_UPLOADED: (STAGE_ORGANISED, STAGE_FAILED),
    STAGE_ORGANISED: (STAGE_MAPPING_CONFIRMED, STAGE_FAILED),
    STAGE_MAPPING_CONFIRMED: (STAGE_PROPOSED, STAGE_FAILED),
    STAGE_PROPOSED: (STAGE_DONE, STAGE_FAILED),
    STAGE_DONE: (),
    STAGE_FAILED: (),
}

#: How each stage is described to the operator. No jargon, no stage names.
STAGE_LABELS: dict[str, str] = {
    STAGE_UPLOADED: "read, and waiting to be organised",
    STAGE_ORGANISED: "organised, and waiting for you to check it",
    STAGE_MAPPING_CONFIRMED: "checked by you, and ready for the next step",
    STAGE_PROPOSED: "marked up, and waiting in the validation queue",
    STAGE_DONE: "finished",
    STAGE_FAILED: "stopped, because something went wrong",
}

#: What the operator should do next from each stage.
STAGE_ACTIONS: dict[str, str] = {
    STAGE_UPLOADED: "Click Organise on this file first.",
    STAGE_ORGANISED: "Check what was found and confirm it before going on.",
    STAGE_MAPPING_CONFIRMED: "Carry on to the next step for this file.",
    STAGE_PROPOSED: "Open the validation queue to work through it.",
    STAGE_DONE: "This file is finished. Import another one if you have more.",
    STAGE_FAILED: "Start again with a fresh import of the file.",
}


def can_advance(current: str, target: str) -> bool:
    """Whether the machine permits ``current → target``."""
    return target in ALLOWED_TRANSITIONS.get(current, ())


def reachable(start: str, target: str) -> bool:
    """Whether ``target`` can be reached from ``start`` by any number of steps.

    Used by the tests to state the guarantee as a property of the table rather
    than of one endpoint: nothing reaches ``proposed`` without passing through
    ``mapping_confirmed``.
    """
    seen = {start}
    frontier = [start]
    while frontier:
        stage = frontier.pop()
        for nxt in ALLOWED_TRANSITIONS.get(stage, ()):
            if nxt == target:
                return True
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return False


def require_stage(job: ImportJob, expected: str) -> None:
    """Refuse, with 409 and an explanation, unless the job is at ``expected``.

    This is the stage gate. It is deliberately a plain refusal: doing the
    missing step automatically would be the app confirming Stage A output on the
    operator's behalf, which is the one thing constraint 1 forbids.
    """
    if job.stage == expected:
        return
    raise errors.conflict(
        "wrong_stage",
        f"'{job.filename}' is {STAGE_LABELS[job.stage]}, so that step cannot "
        "run yet.",
        STAGE_ACTIONS[job.stage],
    )


def advance(job: ImportJob, target: str) -> None:
    """Move the job on, or refuse the move with the same 409 the gate uses."""
    if target not in IMPORT_STAGES:  # pragma: no cover - a bug in a caller
        raise ValueError(f"unknown stage: {target}")
    if not can_advance(job.stage, target):
        raise errors.conflict(
            "wrong_stage",
            f"'{job.filename}' is {STAGE_LABELS[job.stage]}, so that step "
            "cannot run yet.",
            STAGE_ACTIONS[job.stage],
        )
    job.stage = target


def record_error(job: ImportJob, message: str) -> None:
    """Note why a step did not work, without moving the job.

    A failed AI call is worth retrying, and ``failed`` is a terminal stage — no
    transition leads out of it. Parking a job there because the network blinked
    would force the operator to upload the file again, so a recoverable problem
    leaves the stage where it was and only writes down what happened.
    """
    job.error_message = message
