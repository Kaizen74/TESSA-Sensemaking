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
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from backend import dataset, errors
from backend.dataset import AnswerRow, StoryRow
from backend.db import get_session
from backend.framework_schema import FrameworkDefinition
from backend.models import Anecdote, Framework, Signification
from backend.patterns import (
    FILTERABLE,
    SIGNIFIED_BY_AI_VALIDATED,
    SIGNIFIED_BY_CHOICES,
    SIGNIFIED_BY_DEFAULT,
    SIGNIFIED_BY_PARTICIPANT,
    SIGNIFIED_BY_STORED,
    PatternSet,
    SignifiedByCounts,
    VersionCount,
    aggregate,
)
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


def applied_signified_by(value: str | None) -> str:
    """The provenance choice in force, refusing anything that is not one.

    Absent means the default, which constraint 14 fixes at participant-signified
    only. A view that quietly fell back to "everything" when it did not
    understand a parameter would be the exact failure the constraint exists to
    prevent, so an unknown value is refused rather than ignored.
    """
    if value is None:
        return SIGNIFIED_BY_DEFAULT
    if value not in SIGNIFIED_BY_CHOICES:
        raise errors.bad_request(
            "unknown_signified_by",
            f"'{value}' is not a way of choosing whose interpretation to show.",
            "Use the control on the page rather than editing the address.",
        )
    return value


def signified_by_clause(statement: Select, choice: str) -> Select:
    """Narrow a signification query to the chosen provenance (constraint 14).

    The one place the choice becomes SQL. Every read that draws a figure goes
    through here, which is what makes "no view may silently mix the two" a
    property of the code rather than a promise about it.
    """
    stored = SIGNIFIED_BY_STORED.get(choice)
    if stored is None:  # "all" — both, and the caller has to say so on screen.
        return statement
    return statement.where(Signification.signified_by.in_(stored))


def story_scope(
    session: Session,
    framework: Framework,
    *,
    mixed: bool,
    filters: dict[str, str],
) -> Select:
    """The ids of the stories in scope: right version, validated, filtered.

    One definition, so the counts, the answers and the rows can never disagree
    about which stories a view is about.
    """
    ids = scoped_ids(session, framework, mixed)
    statement = dataset.only_validated(select(Anecdote.id)).where(
        Anecdote.framework_id.in_(ids)
    )
    for field, value in filters.items():
        statement = statement.where(getattr(Anecdote, field) == value)
    return statement


def signified_by_counts(
    session: Session,
    framework: Framework,
    *,
    mixed: bool,
    filters: dict[str, str],
) -> SignifiedByCounts:
    """How many placements each provenance holds, whatever choice is in force.

    Both halves, always, so a screen can name what it is not showing as well as
    what it is (constraint 14). Deliberately unfiltered by the choice: these are
    the numbers that make the choice legible.
    """
    in_scope = story_scope(session, framework, mixed=mixed, filters=filters).subquery()
    rows = session.execute(
        select(Signification.signified_by, func.count(Signification.id))
        .join(in_scope, in_scope.c.id == Signification.anecdote_id)
        .group_by(Signification.signified_by)
    ).all()

    counts = SignifiedByCounts()
    for stored, count in rows:
        if stored in SIGNIFIED_BY_STORED[SIGNIFIED_BY_PARTICIPANT]:
            counts.participant += count
        elif stored in SIGNIFIED_BY_STORED[SIGNIFIED_BY_AI_VALIDATED]:
            counts.ai_validated += count
    return counts


def load_rows(
    session: Session,
    framework: Framework,
    *,
    mixed: bool,
    filters: dict[str, str],
    signified_by: str = SIGNIFIED_BY_DEFAULT,
) -> tuple[list[StoryRow], list[AnswerRow]]:
    """The validated stories in scope, and their placements.

    The one place a pattern view decides which stories it is about. The exports
    read through it too, so a downloaded CSV is exactly the rows the charts on
    screen were drawn from — including the version scope and every filter.

    Rows rather than mapped objects (:data:`backend.dataset.StoryRow`). Every
    reader here only ever asks a story for its columns, and at five thousand
    stories the entities SQLAlchemy built so they could be written to — which
    nothing on this path does — cost more than all the arithmetic together.

    ``signified_by`` narrows the *placements*, never the stories. A story whose
    markers were all placed by an analyst still exists and was still told by
    somebody; what the default view withholds is their reading of it, not them.
    """
    ids = scoped_ids(session, framework, mixed)

    statement = dataset.only_validated(select(*dataset.STORY_COLUMNS)).where(
        Anecdote.framework_id.in_(ids)
    )
    for field, value in filters.items():
        statement = statement.where(getattr(Anecdote, field) == value)

    anecdotes = list(session.execute(statement.order_by(Anecdote.id)).all())
    answers = signified_by_clause(
        select(
            Signification.id,
            Signification.anecdote_id,
            Signification.signifier_id,
            Signification.signifier_type,
            Signification.value_json,
            Signification.ai_confidence,
            Signification.signified_by,
            Signification.validated_at,
        ).where(Signification.anecdote_id.in_([a.id for a in anecdotes])),
        signified_by,
    )
    placements = (
        list(session.execute(answers.order_by(Signification.id)).all()) if anecdotes else []
    )
    return anecdotes, placements


def load_answers(
    session: Session,
    framework: Framework,
    *,
    mixed: bool,
    filters: dict[str, str],
    signifier_id: str,
    signified_by: str = SIGNIFIED_BY_DEFAULT,
) -> tuple[list[tuple[int, dict]], int]:
    """One question's answers, and how many stories are in scope for them.

    Same scope as :func:`load_rows` — same version rule, same filters, the same
    ``only_validated``, the same provenance choice — but it reads two columns
    instead of building an object for every story and every placement in the
    framework. The landscape needs one triangle: at five thousand stories,
    hydrating the other four questions' answers to draw it was most of the time
    the endpoint spent (PRD §4's 200ms at 5,000 anecdotes).
    """
    in_scope = story_scope(session, framework, mixed=mixed, filters=filters).subquery()

    total = session.scalar(select(func.count()).select_from(in_scope)) or 0
    rows = session.execute(
        signified_by_clause(
            select(Signification.anecdote_id, Signification.value_json)
            .join(in_scope, in_scope.c.id == Signification.anecdote_id)
            .where(Signification.signifier_id == signifier_id),
            signified_by,
        ).order_by(Signification.id)
    ).all()
    return [(anecdote_id, value) for anecdote_id, value in rows], int(total)


def distinct_values(
    session: Session,
    framework: Framework,
    *,
    mixed: bool,
    filters: dict[str, str],
    field: str,
) -> list[str]:
    """The values a field actually takes in scope — what a split can split by.

    A ``SELECT DISTINCT`` rather than reading every story to look at one column
    of it, for the same reason :func:`load_answers` exists.
    """
    ids = scoped_ids(session, framework, mixed)
    statement = dataset.only_validated(select(getattr(Anecdote, field))).where(
        Anecdote.framework_id.in_(ids)
    )
    for name, value in filters.items():
        statement = statement.where(getattr(Anecdote, name) == value)

    found = session.scalars(statement.distinct()).all()
    return sorted(value for value in found if value)


def load_view(
    session: Session,
    framework: Framework,
    *,
    mixed: bool,
    filters: dict[str, str],
    signified_by: str = SIGNIFIED_BY_DEFAULT,
) -> PatternSet:
    """Read the stories in scope and compute every supporting chart."""
    ids = scoped_ids(session, framework, mixed)
    anecdotes, placements = load_rows(
        session, framework, mixed=mixed, filters=filters, signified_by=signified_by
    )

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
        signified_by=signified_by,
        counts_by_signified_by=signified_by_counts(
            session, framework, mixed=mixed, filters=filters
        ),
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
    signified_by: Annotated[str | None, Query()] = None,
) -> PatternSet:
    """Every supporting chart for one framework version, or for its lineage.

    Without ``mixed`` this is strictly one version's stories: an answer given to
    version 1's wording never appears under version 2, because it was never an
    answer to version 2's question.

    Without ``signified_by`` this is strictly what the storytellers said
    themselves (constraint 14). A reading somebody else made on their behalf is
    a different kind of thing, and pooling the two without saying so would make
    the app's central claim untrue in the one place it is checkable.
    """
    framework = load_framework(session, framework_id)
    filters = applied_filters(respondent_group, input_method, entry_mode, source_type)
    provenance = applied_signified_by(signified_by)

    unknown = set(filters) - set(FILTERABLE)
    if unknown:  # pragma: no cover - the signature admits only these four
        raise errors.bad_request(
            "unknown_filter",
            "That is not something stories can be filtered by.",
            "Use the filters on the page rather than editing the address.",
        )

    return load_view(
        session, framework, mixed=mixed, filters=filters, signified_by=provenance
    )
