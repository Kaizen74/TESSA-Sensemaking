"""The patterns endpoint (PRD §4, §1.5).

One job, and one guard.

The job is to hand the supporting charts a filtered, aggregated view of the
data. All of the arithmetic lives in :mod:`backend.patterns` and none of it
anywhere near a language model (constraint 11).

The guard is about framework versions. A meaning change creates version n+1 and
leaves the old stories bound to the wording they actually answered, so pooling
two versions means pooling answers to two different questions. The app will do
it — an analyst may well want to — but never quietly: one version by default,
and ``mixed=true`` to span the lineage, which then returns the per-version counts
the version chip needs (PRD §4, §5.4).

Only validated stories are read (:mod:`backend.dataset`). That is where the
no-bypass promise stops being about writing and starts being about what the
operator sees.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend import dataset, errors
from backend.db import get_session
from backend.framework_schema import FrameworkDefinition
from backend.models import Anecdote, Framework, Signification
from backend.patterns import FILTERABLE, PatternSet, VersionCount, aggregate
from backend.routers.frameworks import lineage_ids

router = APIRouter(prefix="/api/patterns", tags=["patterns"])


def load_framework(session: Session, framework_id: int) -> Framework:
    framework = session.get(Framework, framework_id)
    if framework is None:
        raise errors.not_found(
            "framework_not_found",
            f"There is no question set numbered {framework_id}.",
            "Go back to the Studio and pick a question set from the list.",
        )
    return framework


def applied_filters(
    respondent_group: str | None,
    input_method: str | None,
    entry_mode: str | None,
    source_type: str | None,
) -> dict[str, str]:
    """The filters actually in force, as plain field/value pairs."""
    chosen = {
        "respondent_group": respondent_group,
        "input_method": input_method,
        "entry_mode": entry_mode,
        "source_type": source_type,
    }
    return {field: value for field, value in chosen.items() if value}


def scoped_ids(session: Session, framework: Framework, mixed: bool) -> list[int]:
    """Which framework versions this view covers."""
    return lineage_ids(session, framework) if mixed else [framework.id]


def version_counts(session: Session, framework_ids: list[int]) -> list[VersionCount]:
    """Per-version story counts, for the version chip."""
    rows = session.execute(
        dataset.only_validated(
            select(Framework.id, Framework.version, func.count(Anecdote.id))
            .join(Anecdote, Anecdote.framework_id == Framework.id)
            .where(Framework.id.in_(framework_ids))
        ).group_by(Framework.id, Framework.version)
    ).all()
    return [
        VersionCount(framework_id=fid, version=version, count=count)
        for fid, version, count in sorted(rows, key=lambda row: (row[1], row[0]))
    ]


def load_rows(
    session: Session,
    framework: Framework,
    *,
    mixed: bool,
    filters: dict[str, str],
) -> tuple[list[Anecdote], list[Signification]]:
    """The validated stories in scope, and their placements.

    The one place a pattern view decides which stories it is about. The exports
    read through it too, so a downloaded CSV is exactly the rows the charts on
    screen were drawn from — including the version scope and every filter.
    """
    ids = scoped_ids(session, framework, mixed)

    statement = dataset.only_validated(select(Anecdote)).where(
        Anecdote.framework_id.in_(ids)
    )
    for field, value in filters.items():
        statement = statement.where(getattr(Anecdote, field) == value)

    anecdotes = list(session.scalars(statement.order_by(Anecdote.id)).all())
    placements = (
        list(
            session.scalars(
                select(Signification)
                .where(Signification.anecdote_id.in_([a.id for a in anecdotes]))
                .order_by(Signification.id)
            ).all()
        )
        if anecdotes
        else []
    )
    return anecdotes, placements


def load_view(
    session: Session,
    framework: Framework,
    *,
    mixed: bool,
    filters: dict[str, str],
) -> PatternSet:
    """Read the stories in scope and compute every supporting chart."""
    ids = scoped_ids(session, framework, mixed)
    anecdotes, placements = load_rows(session, framework, mixed=mixed, filters=filters)

    return aggregate(
        FrameworkDefinition.model_validate(framework.definition_json),
        anecdotes,
        placements,
        framework_id=framework.id,
        framework_name=framework.name,
        framework_version=framework.version,
        mixed=mixed,
        versions=version_counts(session, ids) if mixed else [],
        filters=filters,
    )


@router.get("/{framework_id}", response_model=PatternSet)
def get_patterns(
    framework_id: int,
    session: Annotated[Session, Depends(get_session)],
    mixed: Annotated[bool, Query()] = False,
    respondent_group: Annotated[str | None, Query()] = None,
    input_method: Annotated[str | None, Query()] = None,
    entry_mode: Annotated[str | None, Query()] = None,
    source_type: Annotated[str | None, Query()] = None,
) -> PatternSet:
    """Every supporting chart for one framework version, or for its lineage.

    Without ``mixed`` this is strictly one version's stories: an answer given to
    version 1's wording never appears under version 2, because it was never an
    answer to version 2's question.
    """
    framework = load_framework(session, framework_id)
    filters = applied_filters(respondent_group, input_method, entry_mode, source_type)

    unknown = set(filters) - set(FILTERABLE)
    if unknown:  # pragma: no cover - the signature admits only these four
        raise errors.bad_request(
            "unknown_filter",
            "That is not something stories can be filtered by.",
            "Use the filters on the page rather than editing the address.",
        )

    return load_view(session, framework, mixed=mixed, filters=filters)
