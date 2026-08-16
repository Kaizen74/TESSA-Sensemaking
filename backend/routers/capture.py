"""Capture endpoints (PRD §4).

Phase 3 covers local capture: the admin wizard and paper batch entry, both
``entry_mode=admin``. Remote links and kiosk arrive in Phase 4 and will reuse
this same submission path — one wizard, three entry modes (PRD §1.2).

Provenance (constraint 3) is stamped here and nowhere else, so every stored
record carries the same fields regardless of how it arrived.
"""

from __future__ import annotations

import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend import errors
from backend.capture_schema import (
    SIGNIFIED_BY_RESPONDENT,
    SOURCE_TYPE_CAPTURE,
    CaptureError,
    CaptureSubmission,
    LocalCaptureSubmission,
    validate_significations,
)
from backend.dataset import STATUS_VALIDATED
from backend.db import get_session
from backend.framework_schema import FrameworkDefinition
from backend.models import Anecdote, Framework, Signification, hour_rounded_now, utcnow

router = APIRouter(prefix="/api/capture", tags=["capture"])

#: How much of the story to keep as a title. Enough to recognise a story in a
#: list, short enough not to become a second copy of it.
TITLE_CHARS = 80


class CaptureResult(BaseModel):
    """What the wizard needs after a submission, including the reflection."""

    anecdote_id: int
    framework_id: int
    framework_version: int
    status: str
    input_method: str
    entry_mode: str
    created_at_hour: dt.datetime
    signification_count: int
    #: The signifier the reflection screen shows back (PRD §9 assumption 7).
    reflection_signifier_id: str | None
    thankyou_text: str


def _auto_title(text: str) -> str:
    """First words of the story, for recognising it in a list."""
    flat = " ".join(text.split())
    if len(flat) <= TITLE_CHARS:
        return flat
    return flat[: TITLE_CHARS - 1].rsplit(" ", 1)[0] + "…"


def store_capture(
    session: Session,
    framework: Framework,
    body: CaptureSubmission,
    entry_mode: str,
    capture_link_id: int | None = None,
) -> CaptureResult:
    """Store one story and its placements, whatever route it arrived by.

    The three entry modes of PRD §1.2 — admin, link, kiosk — share one wizard,
    so they share one way of being written down. Provenance (constraint 3) is
    stamped here and nowhere else, which is what makes every record comparable
    regardless of how it was collected.

    The story is bound to the exact framework version answered, so a later
    meaning change cannot retro-fit new wording onto it.

    Status is ``validated``: nothing here passed through AI. Constraint 1 gates
    AI-organised anecdotes and AI-proposed significations, and this is neither —
    the respondent wrote the story and placed the markers themselves. Sending
    first-hand testimony to a validation queue would ask the operator to approve
    something no machine ever touched, and would stop a story reaching the live
    picture the respondent was promised.
    """
    definition = FrameworkDefinition.model_validate(framework.definition_json)

    try:
        cleaned = validate_significations(definition, body.significations)
    except CaptureError as exc:
        raise errors.bad_request("capture_invalid", str(exc), exc.action) from exc

    groups = definition.capture_settings.respondent_groups
    if body.respondent_group and groups and body.respondent_group not in groups:
        raise errors.bad_request(
            "unknown_respondent_group",
            f"'{body.respondent_group}' is not one of the groups on this question set.",
            "Reload the page so you have the current groups, then try again.",
        )

    signified_at = utcnow()

    anecdote = Anecdote(
        framework_id=framework.id,
        text=body.text,
        title_auto=_auto_title(body.text),
        source_type=SOURCE_TYPE_CAPTURE,
        entry_mode=entry_mode,
        capture_link_id=capture_link_id,
        input_method=body.input_method,
        source_file=None,
        source_locator=None,
        import_job_id=None,
        respondent_group=body.respondent_group,
        # Constraint 9: hour-rounded, written only by this helper.
        created_at_hour=hour_rounded_now(),
        status=STATUS_VALIDATED,
    )
    session.add(anecdote)
    session.flush()

    for signifier_id, signifier_type, value in cleaned:
        session.add(
            Signification(
                anecdote_id=anecdote.id,
                signifier_id=signifier_id,
                signifier_type=signifier_type,
                value_json=value,
                # No AI touched this, so there is no confidence to record.
                ai_confidence=None,
                signified_by=SIGNIFIED_BY_RESPONDENT,
                validated_at=signified_at,
            )
        )

    session.commit()

    return CaptureResult(
        anecdote_id=anecdote.id,
        framework_id=framework.id,
        framework_version=framework.version,
        status=anecdote.status,
        input_method=anecdote.input_method,
        entry_mode=anecdote.entry_mode,
        created_at_hour=anecdote.created_at_hour,
        signification_count=len(cleaned),
        reflection_signifier_id=cleaned[0][0] if cleaned else None,
        thankyou_text=definition.capture_settings.thankyou_text,
    )


@router.post("", response_model=CaptureResult, status_code=201)
def create_capture(
    body: LocalCaptureSubmission,
    session: Annotated[Session, Depends(get_session)],
) -> CaptureResult:
    """Local capture: the admin wizard, paper batch entry, and kiosk.

    All three run on the operator's own machine, so ``entry_mode`` may be stated
    by the caller. The remote path cannot do that — there the server derives the
    entry mode from the token, because a respondent's browser must never get to
    say how its story was collected.
    """
    framework = session.get(Framework, body.framework_id)
    if framework is None:
        raise errors.not_found(
            "framework_not_found",
            f"There is no question set numbered {body.framework_id}.",
            "Reload the page. If it keeps happening, ask whoever set this up.",
        )

    return store_capture(session, framework, body, entry_mode=body.entry_mode)
