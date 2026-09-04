"""Read-time translation, display-only (delta §4a, constraint 15).

The second half of constraint 15, and the half where it would be easiest to
break the first. Translation here is a reading aid and nothing else:

* **Never stored as the story.** ``anecdotes.text`` is untouched, always. What
  is cached lives in its own table and is keyed by the story rather than being
  part of it.
* **Never sent to Stage B.** Nothing is ever signified in translation, so
  nothing translated goes anywhere near the propose path — there is no import
  from this module into it, and none from it into this one.
* **Never used to compute anything.** No aggregate, no KDE, no export-of-record
  reads the cache. ``tests/test_translation_readtime.py`` proves that the
  bluntest way there is: delete every cached row and every figure the app draws
  is byte-identical.
* **Never displayed unlabelled.** The response carries ``is_translation: true``
  and the original alongside, so a screen physically cannot render the
  translation without having the original in hand and the flag set.

The cache exists for one reason: reading the same story twice should not cost
two API calls. Delete it and the app is correct, only slower. That sentence is
the whole specification of this table, and it is a test rather than a comment.
"""

from __future__ import annotations

import datetime as dt
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import ai_client
from backend.languages import display_name
from backend.models import Anecdote, Translation, utcnow

#: The practice reply, shipped with the app for the same reason the linter's is
#: (see ``backend/lint.py``): ``NL_MOCK_AI=1`` is a backend mode, and a mock the
#: app could only find beside the test tree would make "zero network" untrue of
#: a real install.
MOCK_PATH = Path(__file__).resolve().parent / "fixtures" / "mock_translation_response.json"

TRANSLATE_SYSTEM = (
    "You translate one short workplace story into a target language.\n\n"
    "Rules you must not break:\n"
    "- Translate. Do not summarise, shorten, explain, tidy or improve.\n"
    "- Keep the register the person used. If they were blunt, be blunt; if they "
    "swore, the meaning of that stays.\n"
    "- Keep names, places and job titles as they are.\n"
    "- If a phrase has no good equivalent, translate it as closely as you can "
    "and leave it at that. Do not add a note, a gloss or a bracket.\n"
    "- Say nothing about the story. You are not reading it, you are carrying "
    "it across.\n\n"
    'Return {"translated_text": str}.'
)


class TranslationReply(BaseModel):
    """What the model is asked for: the translation, and nothing else."""

    model_config = ConfigDict(extra="forbid")

    translated_text: str = Field(min_length=1, max_length=40_000)


class TranslationOut(BaseModel):
    """A translation as every screen receives it.

    ``original_text`` and ``is_translation`` are not optional and are not
    conveniences. They are here so that a component *cannot* render the
    translation without also holding the original and knowing that what it has
    is a translation — the UI's half of constraint 15 is made structural by the
    shape of this response.
    """

    model_config = ConfigDict(extra="forbid")

    anecdote_id: int
    #: Always true. A constant in the response rather than something a caller
    #: has to infer: a screen that forgot to check it would still have to go out
    #: of its way to display this text unlabelled.
    is_translation: bool = True
    target_language_code: str
    target_language_name: str
    translated_text: str
    #: The story as it was told. Always sent, so the original can stay primary.
    original_text: str
    original_language_code: str | None
    original_language_name: str
    model_used: str
    translated_at: dt.datetime
    #: Whether this came from the cache rather than from a fresh call. Useful to
    #: an operator watching what a session costs; used by nothing else.
    from_cache: bool = False


@lru_cache(maxsize=1)
def _mock_reply() -> dict[str, Any]:
    """The practice reply, read once from the file that holds it."""
    return json.loads(MOCK_PATH.read_text(encoding="utf-8"))


def translate_prompt(text: str, target: str) -> str:
    """What the model is given: the story as told, and where to carry it to.

    The original text and nothing else about the story — no title, no
    placements, no group, no provenance. A translator needs the words.
    """
    return json.dumps(
        {"target_language": display_name(target), "text": text},
        indent=2,
        ensure_ascii=False,
    )


def cached(session: Session, anecdote_id: int, target: str) -> Translation | None:
    """The cached translation, if this story has been read in this language."""
    return session.scalar(
        select(Translation).where(
            Translation.anecdote_id == anecdote_id,
            Translation.target_language_code == target,
        )
    )


def store(
    session: Session, anecdote_id: int, target: str, text: str, model_used: str
) -> Translation:
    """Cache one translation, replacing any earlier one for the same pair.

    Replaced rather than accumulated: the unique constraint says one row per
    story per language, and a second reading of the same story in the same
    language is the same answer, not a new fact.
    """
    row = cached(session, anecdote_id, target)
    if row is None:
        row = Translation(
            anecdote_id=anecdote_id,
            target_language_code=target,
            translated_text=text,
            model_used=model_used,
        )
        session.add(row)
    else:
        row.translated_text = text
        row.model_used = model_used
        row.translated_at = utcnow()
    session.commit()
    session.refresh(row)
    return row


def to_out(anecdote: Anecdote, row: Translation, *, from_cache: bool) -> TranslationOut:
    """One cached row, with the original it must never be shown without."""
    return TranslationOut(
        anecdote_id=anecdote.id,
        target_language_code=row.target_language_code,
        target_language_name=display_name(row.target_language_code),
        translated_text=row.translated_text,
        original_text=anecdote.text,
        original_language_code=anecdote.language_code,
        original_language_name=display_name(anecdote.language_code),
        model_used=row.model_used,
        translated_at=row.translated_at,
        from_cache=from_cache,
    )


def translate(text: str, target: str) -> str:
    """Ask for one translation. Raises :class:`~backend.ai_client.AiError`.

    Deliberately takes and returns a bare string: this function knows about a
    piece of text and a language, and nothing about stories, the database or
    the cache. That is what keeps the translation path unable to touch anything
    it should not.
    """
    reply = ai_client.request_json(
        system=TRANSLATE_SYSTEM,
        prompt=translate_prompt(text, target),
        shape=TranslationReply,
        mock=_mock_reply,
    )
    return reply.translated_text
