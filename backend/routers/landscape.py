"""Landscape, Explorer and cluster endpoints (PRD §4).

All three read through the same scope as the patterns endpoint — same version
rule, same filters — so the landscape, the supporting charts and the exports are
always looking at the same stories. A landscape that quietly covered a different
set than the bars beneath it would be the worst kind of bug: invisible, and
wrong in a way that changes what the operator concludes.

``/landscape`` serves the 3D surface and its 2D contour twin from one response,
because they must be the same landscape (constraint 13b). Splitting by a filter
returns several panels sharing one density scale, so two terrains side by side
can honestly be compared by height.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend import errors
from backend import landscape as landscape_maths
from backend.clusters import ClusterSet, ExplorerSet, cluster, explorer
from backend.db import get_session
from backend.framework_schema import FrameworkDefinition
from backend.landscape import Landscape
from backend.patterns import (
    FILTERABLE,
    SIGNIFIED_BY_DEFAULT,
    SignifiedByCounts,
    TriadChart,
    triad_from_answers,
)
from backend.routers.patterns import (
    applied_filters,
    applied_signified_by,
    distinct_values,
    load_answers,
    load_framework,
    load_rows,
    scoped_ids,
    signified_by_counts,
    version_counts,
)

router = APIRouter(prefix="/api", tags=["landscape"])

#: How many panels a split may produce before the screen is unreadable.
MAX_PANELS = 4


class LandscapeSet(BaseModel):
    """One triad's landscape, or several panels of it side by side."""

    model_config = ConfigDict(extra="forbid")

    framework_id: int
    framework_name: str
    framework_version: int
    triad_id: str
    total: int
    mixed: bool
    versions: list = Field(default_factory=list)
    filters: dict[str, str] = Field(default_factory=dict)
    #: The field the panels are split by, when there is one.
    split_by: str | None = None
    panels: list[Landscape] = Field(default_factory=list)
    #: Every triad on this framework, so the picker needs no second request.
    available_triads: list[dict] = Field(default_factory=list)
    #: Whose interpretation this terrain is, and what the other choice holds
    #: (constraint 14). The landscape is the view the app is built around, so
    #: it is the one that most needs to say whose reading it is drawing.
    signified_by_applied: str = SIGNIFIED_BY_DEFAULT
    counts_by_signified_by: SignifiedByCounts = Field(default_factory=SignifiedByCounts)


def _triad_chart(
    session: Session,
    framework,
    *,
    mixed: bool,
    filters: dict[str, str],
    triad_id: str,
    signified_by: str = SIGNIFIED_BY_DEFAULT,
) -> tuple[TriadChart, int, FrameworkDefinition]:
    """The one triad's points, through the same code the supporting charts use.

    One triangle's answers rather than the whole aggregate, and read as two
    columns rather than as an object per story: building every bar and histogram
    on the framework alongside the terrain, out of fully hydrated rows, was the
    difference between meeting and missing PRD §4's 200ms at five thousand
    stories.
    """
    definition = FrameworkDefinition.model_validate(framework.definition_json)
    answers, total = load_answers(
        session,
        framework,
        mixed=mixed,
        filters=filters,
        signifier_id=triad_id,
        signified_by=signified_by,
    )
    chart = triad_from_answers(definition, answers, triad_id, total)
    if chart is None:
        known = ", ".join(entry.id for entry in definition.triads) or "none"
        raise errors.not_found(
            "triad_not_found",
            f"This question set has no triangle called '{triad_id}'.",
            f"Pick one of these instead: {known}.",
        )
    return chart, total, definition


@router.get("/landscape/{framework_id}/{triad_id}", response_model=LandscapeSet)
def get_landscape(
    framework_id: int,
    triad_id: str,
    session: Annotated[Session, Depends(get_session)],
    mixed: Annotated[bool, Query()] = False,
    split_by: Annotated[str | None, Query()] = None,
    respondent_group: Annotated[str | None, Query()] = None,
    input_method: Annotated[str | None, Query()] = None,
    entry_mode: Annotated[str | None, Query()] = None,
    source_type: Annotated[str | None, Query()] = None,
    signified_by: Annotated[str | None, Query()] = None,
) -> LandscapeSet:
    """The terrain for one triangle: surface and contour twin, from one grid.

    Drawn from participant-signified placements unless asked otherwise
    (constraint 14). A hill made of readings somebody else supplied is a
    different claim about a workforce than a hill made of their own.
    """
    framework = load_framework(session, framework_id)
    filters = applied_filters(respondent_group, input_method, entry_mode, source_type)
    provenance = applied_signified_by(signified_by)

    if split_by is not None and split_by not in FILTERABLE:
        raise errors.bad_request(
            "unknown_split",
            "Stories cannot be split by that.",
            "Use the split control on the page rather than editing the address.",
        )

    chart, total, definition = _triad_chart(
        session,
        framework,
        mixed=mixed,
        filters=filters,
        triad_id=triad_id,
        signified_by=provenance,
    )

    if split_by is None:
        panels = [landscape_maths.compute(chart)]
    else:
        panels = _split_panels(
            session,
            framework,
            mixed=mixed,
            filters=filters,
            triad_id=triad_id,
            split_by=split_by,
            signified_by=provenance,
        )

    return LandscapeSet(
        framework_id=framework.id,
        framework_name=framework.name,
        framework_version=framework.version,
        triad_id=triad_id,
        total=total,
        mixed=mixed,
        versions=version_counts(session, scoped_ids(session, framework, mixed))
        if mixed
        else [],
        filters=filters,
        split_by=split_by,
        panels=panels,
        signified_by_applied=provenance,
        counts_by_signified_by=signified_by_counts(
            session, framework, mixed=mixed, filters=filters
        ),
        available_triads=[
            {"id": triad.id, "title": triad.title, "corners": list(triad.corners)}
            for triad in definition.triads
        ],
    )


def _split_panels(
    session: Session,
    framework,
    *,
    mixed: bool,
    filters: dict[str, str],
    triad_id: str,
    split_by: str,
    signified_by: str = SIGNIFIED_BY_DEFAULT,
) -> list[Landscape]:
    """One landscape per value of the split field, on a shared density scale."""
    values = distinct_values(session, framework, mixed=mixed, filters=filters, field=split_by)

    panels: list[Landscape] = []
    for value in values[:MAX_PANELS]:
        chart, _, _ = _triad_chart(
            session,
            framework,
            mixed=mixed,
            filters={**filters, split_by: value},
            triad_id=triad_id,
            signified_by=signified_by,
        )
        panels.append(landscape_maths.compute(chart, panel=value))

    return landscape_maths.share_scale(panels)


@router.get("/explorer/{framework_id}", response_model=ExplorerSet)
def get_explorer(
    framework_id: int,
    session: Annotated[Session, Depends(get_session)],
    mixed: Annotated[bool, Query()] = False,
    respondent_group: Annotated[str | None, Query()] = None,
    input_method: Annotated[str | None, Query()] = None,
    entry_mode: Annotated[str | None, Query()] = None,
    source_type: Annotated[str | None, Query()] = None,
    signified_by: Annotated[str | None, Query()] = None,
) -> ExplorerSet:
    """Every numeric answer, so any three can be plotted against each other.

    Same provenance default as the landscape it sits under (constraint 14): a
    point in the Explorer is the same placement, seen from another angle.
    """
    framework = load_framework(session, framework_id)
    filters = applied_filters(respondent_group, input_method, entry_mode, source_type)
    anecdotes, placements = load_rows(
        session,
        framework,
        mixed=mixed,
        filters=filters,
        signified_by=applied_signified_by(signified_by),
    )

    return explorer(
        FrameworkDefinition.model_validate(framework.definition_json),
        anecdotes,
        placements,
        framework_id=framework.id,
        framework_version=framework.version,
    )


@router.get("/clusters/{framework_id}", response_model=ClusterSet)
def get_clusters(
    framework_id: int,
    session: Annotated[Session, Depends(get_session)],
    k: Annotated[int, Query(ge=2, le=6)] = 3,
    mixed: Annotated[bool, Query()] = False,
    respondent_group: Annotated[str | None, Query()] = None,
    input_method: Annotated[str | None, Query()] = None,
    entry_mode: Annotated[str | None, Query()] = None,
    source_type: Annotated[str | None, Query()] = None,
    signified_by: Annotated[str | None, Query()] = None,
) -> ClusterSet:
    """k-means over the Explorer's dimensions. Deterministic, and descriptive only.

    Clusters what the Explorer plots, so the provenance choice reaches them by
    reaching it — there is no second path to the data for them to disagree over.
    """
    return cluster(
        get_explorer(
            framework_id,
            session,
            mixed=mixed,
            respondent_group=respondent_group,
            input_method=input_method,
            entry_mode=entry_mode,
            source_type=source_type,
            signified_by=signified_by,
        ),
        k=k,
    )
