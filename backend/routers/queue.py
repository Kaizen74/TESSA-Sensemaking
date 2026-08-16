"""The validation queue (PRD §4, §5.3) — where a person says yes.

This is the door constraint 1 is about. Stage B writes its suggestions onto
anecdotes whose status is ``pending_validation``, and nothing else in the app
moves one of those to ``validated``. Three decisions are on offer, and all three
are the operator's:

* **Accept** — the AI read it right. The placements stand as proposed and are
  stamped ``validated_at``. ``signified_by`` stays ``ai``, because the honest
  record is that a model placed the marker and a person agreed with it.
* **Correct** — the operator moves the markers. Each placement they changed is
  restamped ``analyst`` and loses its model confidence; the ones they left alone
  keep both. Provenance then says, per placement, who actually decided it.
* **Reject** — not a usable story. It stays on disk so the import stays
  auditable, and it is never data.

Confidence changes nothing about the route (constraint 2). A placement at 0.31
and one at 0.98 arrive on the same list and wait for the same person.

Once a file's last pending story has been decided, its import job moves to
``done`` — the end of the stage machine, reached only by working through this
queue.
"""

from __future__ import annotations

import datetime as dt
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend import dataset, errors, stage_machine
from backend.ai_client import LOW_CONFIDENCE
from backend.capture_schema import (
    CaptureError,
    SubmittedSignification,
    validate_significations,
)
from backend.dataset import STATUS_PENDING, STATUS_REJECTED, STATUS_VALIDATED
from backend.db import get_session
from backend.framework_schema import FrameworkDefinition
from backend.models import Anecdote, Framework, ImportJob, Signification, utcnow
from backend.propose import SIGNIFIED_BY_AI, SIGNIFIED_BY_ANALYST

router = APIRouter(prefix="/api/queue", tags=["queue"])

#: How many stories one page of the queue carries. The operator works through
#: them one at a time; this is only about not sending the whole import at once.
DEFAULT_LIMIT = 50
MAX_LIMIT = 200


class QueueSignification(BaseModel):
    """One placement as the queue screen shows it."""

    model_config = ConfigDict(extra="forbid")

    signifier_id: str
    signifier_type: str
    value: dict
    ai_confidence: float | None
    signified_by: str
    validated_at: dt.datetime | None
    #: Constraint 2 — amber below 0.70, same list, same queue.
    low_confidence: bool


class QueueItem(BaseModel):
    """One story waiting on a person, with its full provenance (constraint 3)."""

    model_config = ConfigDict(extra="forbid")

    anecdote_id: int
    framework_id: int
    framework_name: str
    framework_version: int
    text: str
    title_auto: str | None
    status: str
    source_type: str
    entry_mode: str
    input_method: str
    source_file: str | None
    source_locator: str | None
    import_job_id: int | None
    respondent_group: str | None
    created_at_hour: dt.datetime
    significations: list[QueueSignification]
    has_low_confidence: bool


class QueueCounts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pending: int
    validated: int
    rejected: int


class QueueView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    counts: QueueCounts
    items: list[QueueItem]


class QueueDecision(BaseModel):
    """What the operator decided about one story.

    ``significations`` belongs to ``correct`` and nowhere else: accepting means
    accepting what is already stored, and a payload alongside it would be an
    invitation to change the data while claiming not to have.
    """

    model_config = ConfigDict(extra="forbid")

    action: Literal["accept", "correct", "reject"]
    significations: list[SubmittedSignification] | None = None


def _low(confidence: float | None) -> bool:
    return confidence is not None and confidence < LOW_CONFIDENCE


def _view(
    session: Session, anecdote: Anecdote, framework: Framework
) -> QueueItem:
    placements = session.scalars(
        select(Signification)
        .where(Signification.anecdote_id == anecdote.id)
        .order_by(Signification.id)
    ).all()

    significations = [
        QueueSignification(
            signifier_id=placement.signifier_id,
            signifier_type=placement.signifier_type,
            value=placement.value_json,
            ai_confidence=placement.ai_confidence,
            signified_by=placement.signified_by,
            validated_at=placement.validated_at,
            low_confidence=_low(placement.ai_confidence),
        )
        for placement in placements
    ]

    return QueueItem(
        anecdote_id=anecdote.id,
        framework_id=framework.id,
        framework_name=framework.name,
        framework_version=framework.version,
        text=anecdote.text,
        title_auto=anecdote.title_auto,
        status=anecdote.status,
        source_type=anecdote.source_type,
        entry_mode=anecdote.entry_mode,
        input_method=anecdote.input_method,
        source_file=anecdote.source_file,
        source_locator=anecdote.source_locator,
        import_job_id=anecdote.import_job_id,
        respondent_group=anecdote.respondent_group,
        created_at_hour=anecdote.created_at_hour,
        significations=significations,
        has_low_confidence=any(entry.low_confidence for entry in significations),
    )


def counts(session: Session, job_id: int | None = None) -> QueueCounts:
    """How many stories sit in each condition, optionally for one file."""
    statement = select(Anecdote.status, func.count(Anecdote.id)).group_by(Anecdote.status)
    if job_id is not None:
        statement = statement.where(Anecdote.import_job_id == job_id)
    tally = dict(session.execute(statement).all())
    return QueueCounts(
        pending=tally.get(STATUS_PENDING, 0),
        validated=tally.get(STATUS_VALIDATED, 0),
        rejected=tally.get(STATUS_REJECTED, 0),
    )


@router.get("", response_model=QueueView)
def read_queue(
    session: Annotated[Session, Depends(get_session)],
    job_id: Annotated[int | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
) -> QueueView:
    """The stories still waiting on a person, oldest first.

    Oldest first because a queue that reordered itself would lose the operator's
    place every time they answered one.
    """
    statement = dataset.only_pending(select(Anecdote)).order_by(Anecdote.id)
    if job_id is not None:
        statement = statement.where(Anecdote.import_job_id == job_id)

    anecdotes = session.scalars(statement.limit(limit)).all()
    frameworks = {
        framework.id: framework
        for framework in session.scalars(
            select(Framework).where(
                Framework.id.in_({anecdote.framework_id for anecdote in anecdotes})
            )
        ).all()
    }

    return QueueView(
        counts=counts(session, job_id),
        items=[
            _view(session, anecdote, frameworks[anecdote.framework_id])
            for anecdote in anecdotes
        ],
    )


def _finish_job_if_empty(session: Session, job_id: int | None) -> None:
    """Move a file to ``done`` once nothing of it is waiting any more."""
    if job_id is None:
        return
    job = session.get(ImportJob, job_id)
    if job is None or job.stage != stage_machine.STAGE_PROPOSED:
        return
    remaining = session.scalar(
        select(func.count(Anecdote.id)).where(
            Anecdote.import_job_id == job_id, Anecdote.status == STATUS_PENDING
        )
    )
    if not remaining:
        stage_machine.advance(job, stage_machine.STAGE_DONE)


@router.put("/{anecdote_id}", response_model=QueueItem)
def decide(
    anecdote_id: int,
    body: QueueDecision,
    session: Annotated[Session, Depends(get_session)],
) -> QueueItem:
    """Accept, correct, or reject one story. The only way into the dataset."""
    anecdote = session.get(Anecdote, anecdote_id)
    if anecdote is None:
        raise errors.not_found(
            "story_not_found",
            f"There is no story numbered {anecdote_id}.",
            "Reload the queue and pick one from the list.",
        )

    if anecdote.status != STATUS_PENDING:
        raise errors.conflict(
            "already_decided",
            "That story has already been dealt with, so it cannot be decided "
            "again.",
            "Reload the queue to see what is still waiting.",
        )

    framework = session.get(Framework, anecdote.framework_id)
    if framework is None:  # pragma: no cover - a foreign key guarantees it
        raise errors.not_found(
            "framework_not_found",
            "The question set this story was marked up against is missing.",
            "Reload the page. If it keeps happening, ask whoever set this up.",
        )

    if body.action == "reject":
        if body.significations is not None:
            raise errors.bad_request(
                "unexpected_placements",
                "Rejecting a story does not take any placements.",
                "Reload the queue and try again.",
            )
        anecdote.status = STATUS_REJECTED
        _finish_job_if_empty(session, anecdote.import_job_id)
        session.commit()
        return _view(session, anecdote, framework)

    decided_at = utcnow()
    stored = session.scalars(
        select(Signification)
        .where(Signification.anecdote_id == anecdote.id)
        .order_by(Signification.id)
    ).all()

    if body.action == "accept":
        if body.significations is not None:
            raise errors.bad_request(
                "unexpected_placements",
                "Accepting means keeping the placements as they are, so no new "
                "ones are needed.",
                "Use Correct if you want to move the markers yourself.",
            )
        for placement in stored:
            placement.validated_at = decided_at
    else:
        if body.significations is None:
            raise errors.bad_request(
                "missing_placements",
                "Correcting a story needs the placements you want kept.",
                "Move the markers you disagree with, then save again.",
            )

        definition = FrameworkDefinition.model_validate(framework.definition_json)
        try:
            cleaned = validate_significations(definition, body.significations)
        except CaptureError as exc:
            raise errors.bad_request("capture_invalid", str(exc), exc.action) from exc

        was = {placement.signifier_id: placement for placement in stored}
        for placement in stored:
            session.delete(placement)

        for signifier_id, signifier_type, value in cleaned:
            previous = was.get(signifier_id)
            # Untouched means untouched: a placement the operator left exactly
            # as proposed keeps saying the AI made it, and keeps its confidence.
            unchanged = previous is not None and previous.value_json == value
            session.add(
                Signification(
                    anecdote_id=anecdote.id,
                    signifier_id=signifier_id,
                    signifier_type=signifier_type,
                    value_json=value,
                    ai_confidence=previous.ai_confidence if unchanged else None,
                    signified_by=SIGNIFIED_BY_AI if unchanged else SIGNIFIED_BY_ANALYST,
                    validated_at=decided_at,
                )
            )

    anecdote.status = STATUS_VALIDATED
    _finish_job_if_empty(session, anecdote.import_job_id)
    session.commit()
    return _view(session, anecdote, framework)
