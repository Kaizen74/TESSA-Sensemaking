"""Collective interpretation: what a room concluded, kept as an artefact.

Constraint 16 in one module. A room reads its own landscape and says what it
thinks; that sentence is recorded next to the pattern, in the room's own words,
and it never becomes part of the pattern.

The distinction matters because the alternative is so tempting. A workshop
concludes "most of these are about being asked to choose between speed and
safety", and it would be easy to store that as a marker, or a weight, or a
cluster label — and then the landscape would show what the room *said* rather
than what the storytellers *placed*. The two would be indistinguishable within a
week. So an interpretation carries no coordinate, joins to no anecdote, and has
no path into the KDE: :class:`backend.models.Interpretation` has no column that
could carry one.

What it does carry is the context needed to read it later — the framework
version, the signifier on screen, the filters in force, the time. A sentence
about "this landscape" is worthless six months on unless you can put the
landscape back.

Nothing here is AI-adjacent. The room writes the words; the app stores them
verbatim and never summarises, rewrites or codes them (constraint 11's spirit,
and delta §9 assumption 5: a room's conclusion resists a schema, and forcing one
would be the same error as machine-coding a story).
"""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import INTERPRETATION_VIEW_KINDS, Interpretation

#: How long a room's conclusion may be. Generous — this is a paragraph somebody
#: typed while ten people watched, not a form field.
MAX_INTERPRETATION_CHARS = 4000

#: What a session may call itself. Long enough for "Ops night shift, 12 March".
MAX_SESSION_LABEL_CHARS = 200

#: A sane ceiling on a room. Recorded because a workshop's size changes how much
#: weight a reader gives its conclusion.
MAX_PARTICIPANTS = 10_000


class InterpretationIn(BaseModel):
    """One conclusion, as the session view sends it.

    ``filter_state`` and ``signifier_id`` are sent by the screen rather than
    typed by anybody: what was on display is a fact about the moment, and asking
    a facilitator to write it down again is asking them to get it wrong.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    framework_id: int
    interpretation_text: str = Field(min_length=1, max_length=MAX_INTERPRETATION_CHARS)
    view_kind: str = "landscape"
    signifier_id: str | None = Field(default=None, max_length=100)
    filter_state: dict[str, str] = Field(default_factory=dict)
    session_label: str | None = Field(default=None, max_length=MAX_SESSION_LABEL_CHARS)
    participant_count: int | None = Field(default=None, ge=0, le=MAX_PARTICIPANTS)


class InterpretationOut(BaseModel):
    """One conclusion as every screen and the brief read it back."""

    model_config = ConfigDict(extra="forbid")

    id: int
    framework_id: int
    #: Verbatim. Never trimmed to a summary, never re-worded.
    interpretation_text: str
    view_kind: str
    signifier_id: str | None
    filter_state: dict[str, str] = Field(default_factory=dict)
    session_label: str | None
    participant_count: int | None
    recorded_at: dt.datetime


def to_out(row: Interpretation) -> InterpretationOut:
    return InterpretationOut(
        id=row.id,
        framework_id=row.framework_id,
        interpretation_text=row.interpretation_text,
        view_kind=row.view_kind,
        signifier_id=row.signifier_id,
        filter_state=dict(row.filter_state_json or {}),
        session_label=row.session_label,
        participant_count=row.participant_count,
        recorded_at=row.recorded_at,
    )


def valid_view_kind(value: str) -> bool:
    return value in INTERPRETATION_VIEW_KINDS


def record(session: Session, body: InterpretationIn) -> Interpretation:
    """Store one conclusion exactly as the room gave it.

    The text goes in unchanged. Everything else is context the screen supplied,
    stored beside it rather than mixed into it.
    """
    row = Interpretation(
        framework_id=body.framework_id,
        signifier_id=body.signifier_id,
        filter_state_json=dict(body.filter_state),
        view_kind=body.view_kind,
        session_label=body.session_label or None,
        interpretation_text=body.interpretation_text,
        participant_count=body.participant_count,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def for_framework(session: Session, framework_ids: list[int]) -> list[Interpretation]:
    """Every conclusion recorded against these framework versions, newest first.

    Takes ids rather than a framework so the caller decides whether to span a
    lineage — the same choice ``mixed`` makes everywhere else. A conclusion about
    version 1's wording is not automatically about version 2's.
    """
    if not framework_ids:
        return []
    return list(
        session.scalars(
            select(Interpretation)
            .where(Interpretation.framework_id.in_(framework_ids))
            .order_by(Interpretation.recorded_at.desc(), Interpretation.id.desc())
        ).all()
    )
