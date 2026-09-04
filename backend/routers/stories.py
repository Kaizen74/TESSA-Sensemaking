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

from backend import ai_client, errors, stories, translate
from backend.ai_client import AiError
from backend.db import get_session
from backend.languages import DEFAULT_LANGUAGE, MAX_LANGUAGE_CODE_CHARS, well_formed
from backend.models import Anecdote, Framework
from backend.routers.patterns import applied_filters, load_framework, scoped_ids
from backend.translate import TranslationOut

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
    language_code: Annotated[str | None, Query()] = None,
) -> stories.StoryPage:
    """One page of stories: searched, filtered, newest first.

    ``ids`` asks for a named few rather than a search — how the landscape's
    region drill reads the stories under a hill. It narrows the same scope
    everything else does, so a drill can never surface a story the current
    version rule or the validated rule excludes.
    """
    framework = load_framework(session, framework_id)
    filters = applied_filters(
        respondent_group, input_method, entry_mode, source_type, language_code
    )
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
                language_code=row.language_code,
                language_source=row.language_source,
                language_name=stories.language_label(row.language_code),
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


@router.get("/{anecdote_id}/translation", response_model=TranslationOut)
def get_translation(
    anecdote_id: int,
    session: Annotated[Session, Depends(get_session)],
    target: Annotated[str, Query(max_length=MAX_LANGUAGE_CODE_CHARS)] = DEFAULT_LANGUAGE,
) -> TranslationOut:
    """One story, carried into another language for reading only (constraint 15).

    ``GET`` because it reads a story, but it may write to the cache on the way —
    which is a cache doing its job, not the endpoint changing anything. The
    story itself is never touched: ``anecdotes.text`` is the record, and no
    branch of this function writes to it.

    The response always carries ``is_translation`` and the original text, so a
    screen cannot render the translation without both. A failure is an ordinary
    state of the app (constraint 4): the story stays readable in the language it
    was told in, which is the one that matters.
    """
    anecdote = session.get(Anecdote, anecdote_id)
    if anecdote is None:
        raise errors.not_found(
            "story_not_found",
            f"There is no story numbered {anecdote_id}.",
            "Reload the list and pick a story from it.",
        )

    if not well_formed(target):
        raise errors.bad_request(
            "unknown_language",
            f"'{target}' is not a language Narrative Lens can translate into.",
            "Use the language buttons on the story rather than editing the "
            "address.",
        )

    if anecdote.language_code == target:
        raise errors.bad_request(
            "already_in_that_language",
            "That story was already told in this language.",
            "Read it as it is — it is the original, which is always the better "
            "text.",
        )

    hit = translate.cached(session, anecdote.id, target)
    if hit is not None:
        return translate.to_out(anecdote, hit, from_cache=True)

    try:
        text = translate.translate(anecdote.text, target)
    except AiError as exc:
        raise errors.upstream(exc.code, exc.message, exc.action) from exc

    row = translate.store(session, anecdote.id, target, text, ai_client.MODEL)
    return translate.to_out(anecdote, row, from_cache=False)


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
        language_code=anecdote.language_code,
        language_source=anecdote.language_source,
        language_name=stories.language_label(anecdote.language_code),
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
