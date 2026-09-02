"""The story browser (PRD §1.6, §5.4).

Two endpoints. One lists the stories in the current scope, searched and
filtered; the other records what the analyst has marked on one of them. Reading
goes through the same scope rule as every other view, so the browser and the
landscape are always looking at the same set of stories.

Exporting a selection is not a third endpoint: ``/api/export/csv`` takes the
ids, so a selected export and a whole-dataset export are one code path and one
provenance guarantee (constraint 3).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend import errors, stories
from backend.db import get_session
from backend.models import Anecdote, Framework
from backend.routers.patterns import applied_filters, load_framework, scoped_ids

router = APIRouter(prefix="/api/stories", tags=["stories"])


class MarksIn(BaseModel):
    """What the analyst has marked on one story."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    starred: bool | None = None
    tags: list[str] | None = Field(default=None, max_length=20)


@router.get("/{framework_id}", response_model=stories.StoryPage)
def browse_stories(
    framework_id: int,
    session: Annotated[Session, Depends(get_session)],
    q: Annotated[str, Query(max_length=200)] = "",
    tag: Annotated[str | None, Query(max_length=stories.MAX_TAG_CHARS)] = None,
    starred: Annotated[bool, Query()] = False,
    ids: Annotated[str | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    mixed: Annotated[bool, Query()] = False,
    respondent_group: Annotated[str | None, Query()] = None,
    input_method: Annotated[str | None, Query()] = None,
    entry_mode: Annotated[str | None, Query()] = None,
    source_type: Annotated[str | None, Query()] = None,
) -> stories.StoryPage:
    """One page of stories: searched, filtered, newest first.

    ``ids`` asks for a named few rather than a search — how the landscape's
    region drill reads the stories under a hill. It narrows the same scope
    everything else does, so a drill can never surface a story the current
    version rule or the validated rule excludes.
    """
    framework = load_framework(session, framework_id)
    filters = applied_filters(respondent_group, input_method, entry_mode, source_type)
    scope = scoped_ids(session, framework, mixed)
    chosen = stories.selected_ids(ids)

    matching = stories.stories_in_scope(
        session, scope, filters=filters, query=q, tag=tag, starred_only=starred, ids=chosen
    )
    everything = stories.stories_in_scope(
        session, scope, filters={}, query="", tag=None, starred_only=False
    )

    matched = session.scalar(select(func.count()).select_from(matching.subquery())) or 0
    total = session.scalar(select(func.count()).select_from(everything.subquery())) or 0

    rows = list(
        session.scalars(
            matching.order_by(Anecdote.id.desc()).offset(offset).limit(stories.PAGE_SIZE)
        ).all()
    )
    anecdote_ids = [row.id for row in rows]
    marks = stories.marks_for(session, anecdote_ids)
    answered = stories.answer_counts(session, anecdote_ids)
    versions = {
        row.id: row.version
        for row in session.scalars(select(Framework).where(Framework.id.in_(scope))).all()
    }

    return stories.StoryPage(
        framework_id=framework.id,
        framework_name=framework.name,
        framework_version=framework.version,
        mixed=mixed,
        filters=filters,
        query=q,
        matched=int(matched),
        total=int(total),
        offset=offset,
        stories=[
            stories.Story(
                anecdote_id=row.id,
                framework_id=row.framework_id,
                framework_version=versions.get(row.framework_id, framework.version),
                title=stories.display_title(row),
                respondent_title=row.respondent_title,
                text=row.text,
                respondent_group=row.respondent_group,
                created_at_hour=row.created_at_hour,
                source_type=row.source_type,
                entry_mode=row.entry_mode,
                input_method=row.input_method,
                source_file=row.source_file,
                source_locator=row.source_locator,
                starred=marks.get(row.id, (False, []))[0],
                tags=marks.get(row.id, (False, []))[1],
                answered=answered.get(row.id, 0),
            )
            for row in rows
        ],
        known_tags=stories.known_tags(session, scope),
    )


@router.put("/{anecdote_id}/marks", response_model=stories.Story)
def set_marks(
    anecdote_id: int,
    body: MarksIn,
    session: Annotated[Session, Depends(get_session)],
) -> stories.Story:
    """Star a story, or replace its tags. The analyst's own shorthand."""
    anecdote = session.get(Anecdote, anecdote_id)
    if anecdote is None:
        raise errors.not_found(
            "story_not_found",
            f"There is no story numbered {anecdote_id}.",
            "Reload the list and pick a story from it.",
        )

    for text in body.tags or []:
        if text.strip() == stories.STAR_TAG:
            raise errors.bad_request(
                "reserved_tag",
                "That word is how a starred story is kept, so it cannot be a tag.",
                "Use the star for starring, and pick another word for the tag.",
            )
        if len(text) > stories.MAX_TAG_CHARS:
            raise errors.bad_request(
                "tag_too_long",
                f"A tag can be up to {stories.MAX_TAG_CHARS} characters.",
                "Shorten it, or split it into two tags.",
            )

    starred, tags = stories.set_marks(
        session, anecdote, starred=body.starred, tags=body.tags
    )
    framework = session.get(Framework, anecdote.framework_id)
    answered = stories.answer_counts(session, [anecdote.id])

    return stories.Story(
        anecdote_id=anecdote.id,
        framework_id=anecdote.framework_id,
        framework_version=framework.version if framework else 0,
        title=stories.display_title(anecdote),
        respondent_title=anecdote.respondent_title,
        text=anecdote.text,
        respondent_group=anecdote.respondent_group,
        created_at_hour=anecdote.created_at_hour,
        source_type=anecdote.source_type,
        entry_mode=anecdote.entry_mode,
        input_method=anecdote.input_method,
        source_file=anecdote.source_file,
        source_locator=anecdote.source_locator,
        starred=starred,
        tags=tags,
        answered=answered.get(anecdote.id, 0),
    )
