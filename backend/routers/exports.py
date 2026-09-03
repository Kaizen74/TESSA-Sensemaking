"""Export endpoints (PRD §4, §1.7).

Both exports read through the same scope as the patterns endpoint — same version
rule, same filters — so what downloads is exactly what was on screen. An export
that quietly covered a different set of stories than the charts above it would
be worse than no export at all.

``/heard`` is the odd one out. It is the summary that goes *back* to the people
who told the stories, so it drops the provenance and the verbatim text and
suppresses every slice under five (PRD §1.7, acceptance criterion 13). The other
two exports are for the analyst; that one is for the room.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import interpretations
from backend.db import get_session
from backend.exports import dataset_csv, pattern_brief, what_we_heard
from backend.framework_schema import FrameworkDefinition
from backend.models import Framework, utcnow
from backend.routers.patterns import (
    applied_filters,
    applied_signified_by,
    load_framework,
    load_rows,
    load_view,
    scoped_ids,
)
from backend.stories import selected_ids

router = APIRouter(prefix="/api/export", tags=["export"])


def _slug(text: str) -> str:
    """A filename a Windows operator can keep without renaming it."""
    kept = [character if character.isalnum() else "-" for character in text.lower()]
    return "".join(kept).strip("-").replace("--", "-") or "narrative-lens"


@router.get("/csv", response_class=PlainTextResponse)
def export_csv(
    session: Annotated[Session, Depends(get_session)],
    framework_id: Annotated[int, Query()],
    mixed: Annotated[bool, Query()] = False,
    respondent_group: Annotated[str | None, Query()] = None,
    input_method: Annotated[str | None, Query()] = None,
    entry_mode: Annotated[str | None, Query()] = None,
    source_type: Annotated[str | None, Query()] = None,
    language_code: Annotated[str | None, Query()] = None,
    signified_by: Annotated[str | None, Query()] = None,
    ids: Annotated[str | None, Query()] = None,
) -> PlainTextResponse:
    """The filtered dataset, one row per story, full provenance (constraint 3).

    ``ids`` narrows it to a chosen few — the story browser's "export selected"
    (PRD §1.7). It is the same code path and the same provenance columns, so a
    selection cannot quietly become a different kind of export.

    ``signified_by`` defaults with everything else to participant-signified
    placements only (constraint 14): a CSV taken without changing anything
    carries no reading anybody made on a storyteller's behalf.
    """
    framework = load_framework(session, framework_id)
    filters = applied_filters(
        respondent_group, input_method, entry_mode, source_type, language_code
    )
    anecdotes, placements = load_rows(
        session,
        framework,
        mixed=mixed,
        filters=filters,
        signified_by=applied_signified_by(signified_by),
    )

    chosen = selected_ids(ids)
    if chosen is not None:
        anecdotes = [row for row in anecdotes if row.id in chosen]
        keep = {row.id for row in anecdotes}
        placements = [row for row in placements if row.anecdote_id in keep]

    names = {
        row.id: (row.name, row.version)
        for row in session.scalars(
            select(Framework).where(Framework.id.in_(scoped_ids(session, framework, mixed)))
        ).all()
    }

    body = dataset_csv(
        FrameworkDefinition.model_validate(framework.definition_json),
        anecdotes,
        placements,
        names,
    )
    kind = "selected-stories" if chosen is not None else "stories"
    filename = f"{_slug(framework.name)}-v{framework.version}-{kind}.csv"
    return PlainTextResponse(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/brief", response_class=PlainTextResponse)
def export_brief(
    session: Annotated[Session, Depends(get_session)],
    framework_id: Annotated[int, Query()],
    mixed: Annotated[bool, Query()] = False,
    respondent_group: Annotated[str | None, Query()] = None,
    input_method: Annotated[str | None, Query()] = None,
    entry_mode: Annotated[str | None, Query()] = None,
    source_type: Annotated[str | None, Query()] = None,
    language_code: Annotated[str | None, Query()] = None,
    signified_by: Annotated[str | None, Query()] = None,
) -> PlainTextResponse:
    """The Pattern Brief: findings in markdown, generated from the figures."""
    framework = load_framework(session, framework_id)
    filters = applied_filters(
        respondent_group, input_method, entry_mode, source_type, language_code
    )
    patterns = load_view(
        session,
        framework,
        mixed=mixed,
        filters=filters,
        signified_by=applied_signified_by(signified_by),
    )

    # Constraint 16: reported alongside the pattern, never merged into it. The
    # brief gets them as a separate section; the figures above are untouched.
    rooms = [
        interpretations.to_out(row)
        for row in interpretations.for_framework(
            session, scoped_ids(session, framework, mixed)
        )
    ]

    filename = f"{_slug(framework.name)}-v{framework.version}-brief.md"
    return PlainTextResponse(
        content=pattern_brief(patterns, utcnow(), rooms),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/heard", response_class=PlainTextResponse)
def export_heard(
    session: Annotated[Session, Depends(get_session)],
    framework_id: Annotated[int, Query()],
    mixed: Annotated[bool, Query()] = False,
    respondent_group: Annotated[str | None, Query()] = None,
    input_method: Annotated[str | None, Query()] = None,
    entry_mode: Annotated[str | None, Query()] = None,
    source_type: Annotated[str | None, Query()] = None,
    language_code: Annotated[str | None, Query()] = None,
    signified_by: Annotated[str | None, Query()] = None,
) -> PlainTextResponse:
    """"What We Heard": the summary that goes back to the room.

    Same figures as the brief, with everything a respondent should not see taken
    out — no story text, no provenance, and no slice fewer than five people
    said. It takes the same filters as the other exports so the operator can
    hand one group back their own picture, but the suppression floor applies
    after the filter, which is exactly when it matters most.

    Of the three exports this is the one where the provenance default matters
    most: handing a room figures partly composed of somebody else's reading of
    their stories, without saying so, is the failure constraint 14 names.
    """
    framework = load_framework(session, framework_id)
    filters = applied_filters(
        respondent_group, input_method, entry_mode, source_type, language_code
    )
    patterns = load_view(
        session,
        framework,
        mixed=mixed,
        filters=filters,
        signified_by=applied_signified_by(signified_by),
    )

    filename = f"{_slug(framework.name)}-v{framework.version}-what-we-heard.md"
    return PlainTextResponse(
        content=what_we_heard(patterns, utcnow()),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
