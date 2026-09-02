"""Framework endpoints (PRD §4).

``PUT`` carries the edit-semantics guardrail: free while a framework has no
stories, and once stories exist it must declare ``edit_kind``. See
``backend/edit_semantics.py`` for the rules and ``tests/test_edit_semantics.py``
for the state machine those rules must satisfy.
"""

from __future__ import annotations

import datetime as dt
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend import errors
from backend.ai_client import AiError
from backend.db import get_session
from backend.edit_semantics import (
    build_edit_log_entries,
    is_structural_change,
    label_renames,
    rename_in_value,
)
from backend.framework_schema import FrameworkDefinition, default_definition
from backend.lint import LintFinding, lint
from backend.models import Anecdote, Framework, Signification, utcnow
from backend.paper_pack import render_paper_pack

router = APIRouter(prefix="/api/frameworks", tags=["frameworks"])

NameStr = Annotated[str, Field(min_length=1, max_length=200)]


class FrameworkCreate(BaseModel):
    """Body for creating a framework. Version 1 of a fresh lineage."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: NameStr
    definition: FrameworkDefinition = Field(default_factory=default_definition)


class FrameworkUpdate(BaseModel):
    """Body for editing a framework.

    ``edit_kind`` is required once the framework has stories; sending it on a
    framework with no stories is harmless and ignored.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: NameStr | None = None
    definition: FrameworkDefinition
    edit_kind: Literal["wording_fix", "meaning_change"] | None = None


class FrameworkOut(BaseModel):
    """A framework as the Studio reads it."""

    id: int
    name: str
    version: int
    definition: FrameworkDefinition
    edit_log: list[dict]
    parent_framework_id: int | None
    created_at: dt.datetime
    is_active: bool
    #: How many stories are bound to this exact version.
    anecdote_count: int
    #: True once stories exist — the point where the guardrail switches on.
    is_live: bool
    #: Respondent-facing figures the Studio shows while editing.
    signifier_count: int
    estimated_minutes: float
    exceeds_screen_warning: bool


def _anecdote_count(session: Session, framework_id: int) -> int:
    return (
        session.scalar(
            select(func.count())
            .select_from(Anecdote)
            .where(Anecdote.framework_id == framework_id)
        )
        or 0
    )


def _to_out(session: Session, framework: Framework) -> FrameworkOut:
    definition = FrameworkDefinition.model_validate(framework.definition_json)
    count = _anecdote_count(session, framework.id)
    return FrameworkOut(
        id=framework.id,
        name=framework.name,
        version=framework.version,
        definition=definition,
        edit_log=list(framework.edit_log_json or []),
        parent_framework_id=framework.parent_framework_id,
        created_at=framework.created_at,
        is_active=framework.is_active,
        anecdote_count=count,
        is_live=count > 0,
        signifier_count=definition.signifier_count,
        estimated_minutes=definition.estimated_minutes(),
        exceeds_screen_warning=definition.exceeds_screen_warning,
    )


def _get_or_404(session: Session, framework_id: int) -> Framework:
    framework = session.get(Framework, framework_id)
    if framework is None:
        raise errors.not_found(
            "framework_not_found",
            f"There is no question set numbered {framework_id}.",
            "Go back to the Studio and pick a question set from the list.",
        )
    return framework


def lineage_ids(session: Session, framework: Framework) -> list[int]:
    """Every framework id in the same version chain, oldest first.

    Walks up to the root, then collects every descendant. Small by construction —
    a lineage is one framework's edit history.
    """
    root = framework
    seen_up: set[int] = set()
    while root.parent_framework_id is not None and root.parent_framework_id not in seen_up:
        seen_up.add(root.id)
        parent = session.get(Framework, root.parent_framework_id)
        if parent is None:
            break
        root = parent

    collected: list[Framework] = []
    frontier = [root]
    while frontier:
        current = frontier.pop()
        collected.append(current)
        children = session.scalars(
            select(Framework).where(Framework.parent_framework_id == current.id)
        ).all()
        frontier.extend(children)

    return [f.id for f in sorted(collected, key=lambda f: (f.version, f.id))]


def _next_version(session: Session, framework: Framework) -> int:
    """One past the highest version anywhere in this lineage."""
    ids = lineage_ids(session, framework)
    highest = session.scalar(select(func.max(Framework.version)).where(Framework.id.in_(ids)))
    return int(highest or framework.version) + 1


@router.get("", response_model=list[FrameworkOut])
def list_frameworks(session: Annotated[Session, Depends(get_session)]) -> list[FrameworkOut]:
    """Every framework, newest first. The Studio groups these into lineages."""
    frameworks = session.scalars(
        select(Framework).order_by(Framework.created_at.desc(), Framework.id.desc())
    ).all()
    return [_to_out(session, framework) for framework in frameworks]


@router.post("", response_model=FrameworkOut, status_code=201)
def create_framework(
    body: FrameworkCreate,
    session: Annotated[Session, Depends(get_session)],
) -> FrameworkOut:
    """Create version 1 of a new framework."""
    framework = Framework(
        name=body.name,
        version=1,
        definition_json=body.definition.model_dump(mode="json"),
        edit_log_json=[],
        parent_framework_id=None,
        is_active=True,
    )
    session.add(framework)
    session.commit()
    return _to_out(session, framework)


@router.get("/{framework_id}", response_model=FrameworkOut)
def get_framework(
    framework_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> FrameworkOut:
    return _to_out(session, _get_or_404(session, framework_id))


@router.get("/{framework_id}/paper-pack", response_class=HTMLResponse)
def get_paper_pack(
    framework_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> HTMLResponse:
    """The print-ready paper pack for this exact framework version (PRD §1.2).

    Returns a self-contained HTML page. The operator prints it, or uses the
    browser's Save-as-PDF — no PDF library, per PRD §9 assumption 11.
    """
    framework = _get_or_404(session, framework_id)
    definition = FrameworkDefinition.model_validate(framework.definition_json)
    html = render_paper_pack(definition, framework.name, framework.version)
    return HTMLResponse(content=html)


class LintOut(BaseModel):
    """A design critique of one framework version, and nothing about its data."""

    model_config = ConfigDict(extra="forbid")

    framework_id: int
    framework_version: int
    findings: list[LintFinding] = Field(default_factory=list)


@router.post("/{framework_id}/lint", response_model=LintOut)
def lint_framework(
    framework_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> LintOut:
    """Ask the model what a respondent might trip over (delta §4a).

    The only AI call in the app that never sees data. It reads this version's
    ``definition_json`` and returns advice about the wording; it writes nothing,
    and it cannot stop the operator publishing. ``POST`` because it costs money
    and takes a moment — it happens when somebody clicks, never on a page load.

    A failure is an ordinary state of the app (constraint 4): the Studio says
    what happened in a sentence and stays usable, because nothing here was
    half-written. There is no state to leave behind.
    """
    framework = _get_or_404(session, framework_id)
    definition = FrameworkDefinition.model_validate(framework.definition_json)

    try:
        report = lint(definition)
    except AiError as exc:
        raise errors.upstream(exc.code, exc.message, exc.action) from exc

    return LintOut(
        framework_id=framework.id,
        framework_version=framework.version,
        findings=report.findings,
    )


@router.put("/{framework_id}", response_model=FrameworkOut)
def update_framework(
    framework_id: int,
    body: FrameworkUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> FrameworkOut:
    """Edit a framework, honouring the wording-fix / meaning-change guardrail.

    * No stories yet → the edit applies in place, whatever ``edit_kind`` says.
    * Stories exist and no ``edit_kind`` → 409, explained in plain English.
    * ``wording_fix`` → patch in place and append to the edit log.
    * ``meaning_change`` → create version n+1 and leave old stories where they are.
    """
    framework = _get_or_404(session, framework_id)
    old_definition = FrameworkDefinition.model_validate(framework.definition_json)
    new_definition = body.definition
    story_count = _anecdote_count(session, framework.id)

    if story_count == 0:
        framework.definition_json = new_definition.model_dump(mode="json")
        if body.name is not None:
            framework.name = body.name
        session.commit()
        return _to_out(session, framework)

    if body.edit_kind is None:
        raise errors.conflict(
            "edit_kind_required",
            (
                f"This question set already has {story_count} "
                f"{'story' if story_count == 1 else 'stories'}, so changing its "
                "words needs a decision from you first."
            ),
            (
                "Choose 'Fix wording' if you are correcting a typo or making the "
                "same question clearer, or 'Change meaning' if you are asking "
                "something different. A wording fix is recorded in the edit log; "
                "a meaning change starts a new version so existing stories stay "
                "attached to the words people actually saw."
            ),
        )

    if body.edit_kind == "wording_fix":
        return _apply_wording_fix(session, framework, old_definition, new_definition, body.name)

    return _apply_meaning_change(session, framework, new_definition, body.name)


def _apply_wording_fix(
    session: Session,
    framework: Framework,
    old_definition: FrameworkDefinition,
    new_definition: FrameworkDefinition,
    new_name: str | None,
) -> FrameworkOut:
    """Patch in place and append to the edit log."""
    if is_structural_change(old_definition, new_definition):
        raise errors.conflict(
            "structural_change_needs_new_version",
            (
                "That edit does more than change wording — it adds, removes or "
                "reshapes a question, and stories have already been answered "
                "against the old shape."
            ),
            (
                "Choose 'Change meaning' instead. That starts a new version, so "
                "the stories you already have stay attached to the questions "
                "they were actually asked."
            ),
        )

    entries = build_edit_log_entries(old_definition, new_definition, utcnow())

    # A renamed corner, chip or option is a wording fix — and answers are stored
    # under those very words, so the answers have to come with it. Without this,
    # renaming a triad corner leaves every stored placement keyed by a word the
    # framework no longer has: the Patterns tab fails outright on a triad, and
    # an MCQ or a stone quietly stops counting. Positional, which is sound
    # because the structural check above has already refused any reshaping.
    renames = label_renames(old_definition, new_definition)
    if renames:
        stored = session.scalars(
            select(Signification)
            .join(Anecdote, Signification.anecdote_id == Anecdote.id)
            .where(
                Anecdote.framework_id == framework.id,
                Signification.signifier_id.in_(renames),
            )
        ).all()
        for placement in stored:
            placement.value_json = rename_in_value(
                placement.value_json, renames[placement.signifier_id]
            )

    framework.definition_json = new_definition.model_dump(mode="json")
    # Reassign rather than append: SQLAlchemy only notices a new object on a
    # JSON column, not an in-place mutation of the existing list.
    framework.edit_log_json = list(framework.edit_log_json or []) + entries
    if new_name is not None:
        framework.name = new_name

    session.commit()
    return _to_out(session, framework)


def _apply_meaning_change(
    session: Session,
    framework: Framework,
    new_definition: FrameworkDefinition,
    new_name: str | None,
) -> FrameworkOut:
    """Create version n+1, leaving the old version and its stories untouched."""
    child = Framework(
        name=new_name if new_name is not None else framework.name,
        version=_next_version(session, framework),
        definition_json=new_definition.model_dump(mode="json"),
        # A new version starts a fresh log; the parent keeps its own history.
        edit_log_json=[],
        parent_framework_id=framework.id,
        is_active=True,
    )
    session.add(child)
    session.commit()
    return _to_out(session, child)
