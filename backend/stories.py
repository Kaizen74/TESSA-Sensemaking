"""The story browser's read model (PRD §1.6).

The landscape says where stories gather. This says which stories they are. It
is the other half of the same question, and the honest end of every pattern:
when a hill surprises you, the next move is to read what is under it.

Three rules it inherits rather than invents:

* **Only validated stories** (:mod:`backend.dataset`). The browser is a view of
  the data, and the data is what a person has approved. Anything still waiting
  belongs to the validation queue, which is a different screen with a different
  job.
* **The same scope as every other view** — one framework version unless mixing
  is asked for, and the same provenance filters as the patterns rail.
* **Nothing identifying, because there is nothing to identify with**
  (constraint 9). A story carries its own words, its group, and an hour. There
  is no name in the schema for this screen to leak.

Stars are stored as a reserved tag rather than as a new column: PRD §3 ends
with "no further schema in v1", and a tag row says exactly the same thing as a
boolean would.
"""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from backend import dataset, errors
from backend.models import Anecdote, Signification, Tag

#: The tag a star is stored as. Reserved, and refused as a typed tag, so a
#: starred story and a story tagged "starred" can never be confused.
STAR_TAG = "__starred__"

#: How many stories one page of the browser holds. A browser is for reading,
#: and a thousand rows at once is a scroll bar rather than a list.
PAGE_SIZE = 50

#: Tags are the analyst's own shorthand. Long enough to be a phrase, short
#: enough to stay a label.
MAX_TAG_CHARS = 60


class Story(BaseModel):
    """One story as the browser lists it."""

    model_config = ConfigDict(extra="forbid")

    anecdote_id: int
    framework_id: int
    framework_version: int
    #: What to show: the name its teller gave it, else the machine's (delta §3).
    title: str
    #: Present only when a respondent actually named it, so the screen can say
    #: whose words the title is rather than leaving a reader to guess.
    respondent_title: str | None
    text: str
    respondent_group: str | None
    created_at_hour: dt.datetime | None
    source_type: str
    entry_mode: str
    input_method: str
    source_file: str | None
    source_locator: str | None
    starred: bool
    tags: list[str] = Field(default_factory=list)
    #: How many questions this story answered — the browser's one figure.
    answered: int


class StoryPage(BaseModel):
    """A page of the browser, and everything the screen needs around it."""

    model_config = ConfigDict(extra="forbid")

    framework_id: int
    framework_name: str
    framework_version: int
    mixed: bool
    filters: dict[str, str] = Field(default_factory=dict)
    query: str = ""
    #: Stories matching the search and filters, before paging.
    matched: int = 0
    #: Stories in scope with no search applied — the denominator on screen.
    total: int = 0
    offset: int = 0
    page_size: int = PAGE_SIZE
    stories: list[Story] = Field(default_factory=list)
    #: Every tag in use in this scope, so the screen can offer them.
    known_tags: list[str] = Field(default_factory=list)


def selected_ids(ids: str | None) -> set[int] | None:
    """The story ids a caller asked for by name, or None for all of them.

    One parser for both readers of a selection — the CSV export's "export
    selected" and the landscape's region drill — so the two cannot drift into
    disagreeing about what a list of ids means, or into two different sentences
    for the same mistake.
    """
    if ids is None:
        return None
    chosen: set[int] = set()
    for part in ids.split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit():
            raise errors.bad_request(
                "unreadable_selection",
                "That download asked for stories by a name Narrative Lens does "
                "not recognise.",
                "Go back to the story list, tick the stories you want, and "
                "download again.",
            )
        chosen.add(int(part))
    return chosen


def display_title(anecdote: Anecdote) -> str:
    """The delta's display rule, in one place (delta §3).

    The name its teller gave it when there is one, else the machine's first
    words. Written once so a list, a drawer and a drill can never show three
    different titles for the same story.
    """
    return anecdote.respondent_title or anecdote.title_auto or ""


def marks_for(session: Session, anecdote_ids: list[int]) -> dict[int, tuple[bool, list[str]]]:
    """Star and tags per story, in one query rather than one per row."""
    if not anecdote_ids:
        return {}

    rows = session.execute(
        select(Tag.anecdote_id, Tag.tag_text).where(Tag.anecdote_id.in_(anecdote_ids))
    ).all()

    marks: dict[int, tuple[bool, list[str]]] = {}
    for anecdote_id, text in rows:
        starred, tags = marks.get(anecdote_id, (False, []))
        if text == STAR_TAG:
            starred = True
        else:
            tags.append(text)
        marks[anecdote_id] = (starred, tags)
    return {key: (starred, sorted(tags)) for key, (starred, tags) in marks.items()}


def answer_counts(session: Session, anecdote_ids: list[int]) -> dict[int, int]:
    """How many questions each story answered."""
    if not anecdote_ids:
        return {}
    rows = session.execute(
        select(Signification.anecdote_id, func.count(Signification.id))
        .where(Signification.anecdote_id.in_(anecdote_ids))
        .group_by(Signification.anecdote_id)
    ).all()
    return dict(rows)  # type: ignore[arg-type]


def search_clause(query: str):
    """The full-text rule: every word must appear, in the story or either title.

    Deliberately plain ``LIKE``. A search index would be another table, and PRD
    §3 ends the schema at six; at the scale this app is for, the difference is
    not something an operator could feel.

    ``%`` and ``_`` are escaped rather than passed through. They are ordinary
    characters in a story about a 50% overrun or a file called shift_notes, and
    a search box that quietly treats them as wildcards returns matches the
    operator cannot account for.
    """
    clauses = []
    for word in query.split():
        escaped = word.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        clauses.append(
            func.lower(Anecdote.text).like(pattern, escape="\\")
            | func.lower(func.coalesce(Anecdote.title_auto, "")).like(pattern, escape="\\")
            # A story its teller named is findable by that name. Searching only
            # the machine's title would make the one title a person chose the
            # one title the search box could not see.
            | func.lower(func.coalesce(Anecdote.respondent_title, "")).like(
                pattern, escape="\\"
            )
        )
    return clauses


def stories_in_scope(
    session: Session,
    framework_ids: list[int],
    *,
    filters: dict[str, str],
    query: str,
    tag: str | None,
    starred_only: bool,
    ids: set[int] | None = None,
):
    """The select every count and page in this module is built from.

    ``ids`` narrows it to a named few — how the landscape's region drill reads
    the stories under a hill. It is a filter on the same scope as everything
    else, not a way around it: a story the version rule or the validated rule
    excludes stays excluded however it was asked for.
    """
    statement = dataset.only_validated(select(Anecdote)).where(
        Anecdote.framework_id.in_(framework_ids)
    )
    if ids is not None:
        statement = statement.where(Anecdote.id.in_(sorted(ids)))
    for field, value in filters.items():
        statement = statement.where(getattr(Anecdote, field) == value)
    for clause in search_clause(query):
        statement = statement.where(clause)

    wanted = [STAR_TAG] if starred_only else []
    if tag:
        wanted.append(tag)
    for text in wanted:
        marked = select(Tag.anecdote_id).where(Tag.tag_text == text)
        statement = statement.where(Anecdote.id.in_(marked))

    return statement


def known_tags(session: Session, framework_ids: list[int]) -> list[str]:
    """Every tag the analyst has used in this scope, alphabetically."""
    rows = session.scalars(
        select(Tag.tag_text)
        .join(Anecdote, Anecdote.id == Tag.anecdote_id)
        .where(Anecdote.framework_id.in_(framework_ids))
        .distinct()
    ).all()
    return sorted(text for text in rows if text != STAR_TAG)


def set_marks(
    session: Session,
    anecdote: Anecdote,
    *,
    starred: bool | None,
    tags: list[str] | None,
) -> tuple[bool, list[str]]:
    """Set a story's star and tags, and return what it now carries.

    Both are replacements rather than additions: the screen sends what the story
    should have, which is what the operator sees in front of them.
    """
    existing = session.scalars(select(Tag).where(Tag.anecdote_id == anecdote.id)).all()
    was_starred = any(row.tag_text == STAR_TAG for row in existing)
    kept = sorted({row.tag_text for row in existing if row.tag_text != STAR_TAG})

    if tags is not None:
        cleaned = sorted({text.strip() for text in tags if text.strip()})
        session.execute(
            delete(Tag).where(Tag.anecdote_id == anecdote.id, Tag.tag_text != STAR_TAG)
        )
        for text in cleaned:
            session.add(Tag(anecdote_id=anecdote.id, tag_text=text))
        kept = cleaned

    if starred is not None and starred != was_starred:
        if starred:
            session.add(Tag(anecdote_id=anecdote.id, tag_text=STAR_TAG))
        else:
            session.execute(
                delete(Tag).where(Tag.anecdote_id == anecdote.id, Tag.tag_text == STAR_TAG)
            )
        was_starred = starred

    session.commit()
    return was_starred, kept
