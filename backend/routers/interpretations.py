"""The collective-interpretation endpoints (delta §4, §5).

Two operations: record what a room concluded, and list what rooms have
concluded before. Both are ordinary local reads and writes — no AI is reachable
from this module, and no aggregate is either.

Constraint 16 is why this router is so short. An interpretation is stored
alongside a pattern and never merged into one, so there is nothing to compute
here: no scoring, no coding, no rollup. The words go in, and the words come
back.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend import errors, interpretations
from backend.db import get_session
from backend.framework_schema import FrameworkDefinition
from backend.interpretations import InterpretationIn, InterpretationOut
from backend.routers.frameworks import lineage_ids
from backend.routers.patterns import load_framework

router = APIRouter(prefix="/api/interpretations", tags=["interpretations"])


@router.get("", response_model=list[InterpretationOut])
def list_interpretations(
    session: Annotated[Session, Depends(get_session)],
    framework_id: Annotated[int, Query()],
    mixed: Annotated[bool, Query()] = False,
) -> list[InterpretationOut]:
    """What rooms have concluded about this question set, newest first.

    ``mixed`` spans the version lineage, the same choice every other view
    offers. Without it this is strictly one version's conclusions, because a
    room reading version 1's wording was reading a different question.
    """
    framework = load_framework(session, framework_id)
    scope = lineage_ids(session, framework) if mixed else [framework.id]

    return [
        interpretations.to_out(row)
        for row in interpretations.for_framework(session, scope)
    ]


@router.post("", response_model=InterpretationOut, status_code=201)
def create_interpretation(
    body: InterpretationIn,
    session: Annotated[Session, Depends(get_session)],
) -> InterpretationOut:
    """Record what the room concluded, in the room's own words.

    Stored verbatim. The app has no opinion about it, does not code it, and will
    not let it near a landscape — there is no column on this table through which
    it could reach one (constraint 16).
    """
    framework = load_framework(session, body.framework_id)

    if not interpretations.valid_view_kind(body.view_kind):
        raise errors.bad_request(
            "unknown_view_kind",
            f"'{body.view_kind}' is not one of the pictures this app draws.",
            "Record the interpretation from the session view rather than by "
            "editing the address.",
        )

    definition = FrameworkDefinition.model_validate(framework.definition_json)
    known = {signifier.id for _, signifier in definition.signifiers_in_order()}
    if body.signifier_id and body.signifier_id not in known:
        raise errors.bad_request(
            "unknown_signifier",
            f"This question set has no question called '{body.signifier_id}'.",
            "Reload the Patterns tab so you have the current questions, then "
            "record it again.",
        )

    return interpretations.to_out(interpretations.record(session, body))
