"""The data-quality endpoint (delta §4, §5).

One reading, computed entirely locally. Constraint 11 is the whole story here:
this endpoint counts, and nothing on this path can reach a language model —
:mod:`backend.quality` imports no AI client, and neither does this router.

Scope comes from the patterns router rather than being decided again: the same
version rule, the same ``only_validated``, the same filters and the same
provenance choice. A quality panel that measured a different set of stories than
the charts above it would be worse than no panel, because it would look like it
agreed with them.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend import quality
from backend.db import get_session
from backend.framework_schema import FrameworkDefinition
from backend.models import Signification
from backend.quality import QualityReport
from backend.routers.patterns import (
    applied_filters,
    applied_signified_by,
    load_framework,
    signified_by_clause,
    signified_by_counts,
    story_scope,
)

router = APIRouter(prefix="/api/quality", tags=["quality"])


def answered_by_signifier(
    session: Session,
    in_scope,
    signified_by: str,
) -> dict[str, int]:
    """How many stories placed a marker on each signifier, in one query.

    Counting distinct stories rather than rows: the stones signifier stores one
    row per chip, and a story that placed three chips answered the question
    once, not three times. Skips are the complement of this, so getting it wrong
    here would misreport both signals at once.
    """
    rows = session.execute(
        signified_by_clause(
            select(
                Signification.signifier_id,
                func.count(func.distinct(Signification.anecdote_id)),
            ).join(in_scope, in_scope.c.id == Signification.anecdote_id),
            signified_by,
        ).group_by(Signification.signifier_id)
    ).all()
    return {signifier_id: int(count) for signifier_id, count in rows}


def triad_values(
    session: Session,
    in_scope,
    signified_by: str,
    triad_ids: list[str],
) -> dict[str, list[dict]]:
    """Every triad placement in scope, grouped by signifier, in one query.

    One query for all of the triads rather than one each: a framework may carry
    ten, and the endpoint has the same 200ms budget as every other read (delta
    §4). Only the two columns the arithmetic needs are read, for the reason
    :func:`backend.routers.patterns.load_answers` gives.
    """
    if not triad_ids:
        return {}

    rows = session.execute(
        signified_by_clause(
            select(Signification.signifier_id, Signification.value_json)
            .join(in_scope, in_scope.c.id == Signification.anecdote_id)
            .where(Signification.signifier_id.in_(triad_ids)),
            signified_by,
        ).order_by(Signification.id)
    ).all()

    grouped: dict[str, list[dict]] = {triad_id: [] for triad_id in triad_ids}
    for signifier_id, value in rows:
        grouped[signifier_id].append(value)
    return grouped


@router.get("/{framework_id}", response_model=QualityReport)
def get_quality(
    framework_id: int,
    session: Annotated[Session, Depends(get_session)],
    mixed: Annotated[bool, Query()] = False,
    respondent_group: Annotated[str | None, Query()] = None,
    input_method: Annotated[str | None, Query()] = None,
    entry_mode: Annotated[str | None, Query()] = None,
    source_type: Annotated[str | None, Query()] = None,
    language_code: Annotated[str | None, Query()] = None,
    signified_by: Annotated[str | None, Query()] = None,
) -> QualityReport:
    """Centre-parking and skip rate per signifier, for the stories in scope.

    Two proportions and the counts behind them. What they mean is left to the
    reader — a high centre-parking share on one triangle is a question worth
    looking at again, and this endpoint will not say more than that
    (constraint 11).
    """
    framework = load_framework(session, framework_id)
    filters = applied_filters(
        respondent_group, input_method, entry_mode, source_type, language_code
    )
    provenance = applied_signified_by(signified_by)
    definition = FrameworkDefinition.model_validate(framework.definition_json)

    scope = story_scope(session, framework, mixed=mixed, filters=filters).subquery()
    total = session.scalar(select(func.count()).select_from(scope)) or 0

    return quality.report(
        definition,
        framework_id=framework.id,
        framework_name=framework.name,
        framework_version=framework.version,
        mixed=mixed,
        filters=filters,
        signified_by=provenance,
        counts_by_signified_by=signified_by_counts(
            session, framework, mixed=mixed, filters=filters
        ),
        total=int(total),
        answered_by_signifier=answered_by_signifier(session, scope, provenance),
        triad_values=triad_values(
            session, scope, provenance, [triad.id for triad in definition.triads]
        ),
    )
