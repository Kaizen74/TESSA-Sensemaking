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

from backend.db import get_session
from backend.exports import dataset_csv, pattern_brief, what_we_heard
from backend.framework_schema import FrameworkDefinition
from backend.models import Framework, utcnow
from backend.routers.patterns import (
    applied_filters,
    load_framework,
    load_rows,
    load_view,
    scoped_ids,
)

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
) -> PlainTextResponse:
    """The filtered dataset, one row per story, full provenance (constraint 3)."""
    framework = load_framework(session, framework_id)
    filters = applied_filters(respondent_group, input_method, entry_mode, source_type)
    anecdotes, placements = load_rows(session, framework, mixed=mixed, filters=filters)

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
    filename = f"{_slug(framework.name)}-v{framework.version}-stories.csv"
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
) -> PlainTextResponse:
    """The Pattern Brief: findings in markdown, generated from the figures."""
    framework = load_framework(session, framework_id)
    filters = applied_filters(respondent_group, input_method, entry_mode, source_type)
    patterns = load_view(session, framework, mixed=mixed, filters=filters)

    filename = f"{_slug(framework.name)}-v{framework.version}-brief.md"
    return PlainTextResponse(
        content=pattern_brief(patterns, utcnow()),
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
) -> PlainTextResponse:
    """"What We Heard": the summary that goes back to the room.

    Same figures as the brief, with everything a respondent should not see taken
    out — no story text, no provenance, and no slice fewer than five people
    said. It takes the same filters as the other exports so the operator can
    hand one group back their own picture, but the suppression floor applies
    after the filter, which is exactly when it matters most.
    """
    framework = load_framework(session, framework_id)
    filters = applied_filters(respondent_group, input_method, entry_mode, source_type)
    patterns = load_view(session, framework, mixed=mixed, filters=filters)

    filename = f"{_slug(framework.name)}-v{framework.version}-what-we-heard.md"
    return PlainTextResponse(
        content=what_we_heard(patterns, utcnow()),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
