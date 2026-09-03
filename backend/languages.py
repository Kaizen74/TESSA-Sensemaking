"""The language a story was told in (delta §3, constraint 15).

Constraint 15 says the original language is the record. This module is what
makes that a fact about the data rather than an intention: a story carries the
language it was told in, and that tag travels with it into the browser, the
drill and the CSV. Phase F will add read-time translation on top; nothing here
translates anything, and nothing here may.

Two fields, and the second is the one that usually gets forgotten:

* ``language_code`` — a BCP-47 tag. "en", "ms", "ta", "zh-Hans".
* ``language_source`` — *how the app came to believe that*. A respondent who
  chose Tamil on the welcome screen and an operator who guessed while typing up
  a pile of paper are making claims of very different strength, and a dataset
  that recorded only the tag would flatten the two. An analyst deciding whether
  a language split means anything needs to know which they are looking at.

Absent is absent. A story with no language reads as unknown, never as English —
assuming the majority language of whoever built the app is exactly how a
multilingual dataset quietly becomes a monolingual one.

Names are held here rather than fetched, because constraint 4 permits no network
for this and a respondent picking their own language must see it written the way
they write it. The list is short and editable: it is a starting point for the
Studio, not a claim about which languages exist.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict

#: How the app came to believe a story's language (delta §3).
LANGUAGE_SOURCE_RESPONDENT = "respondent_selected"
LANGUAGE_SOURCE_ADMIN = "admin_entered"
LANGUAGE_SOURCE_UNKNOWN = "unknown"

LANGUAGE_SOURCES = (
    LANGUAGE_SOURCE_RESPONDENT,
    LANGUAGE_SOURCE_ADMIN,
    LANGUAGE_SOURCE_UNKNOWN,
)

#: What the screen says when nothing is recorded. Not "English".
UNKNOWN_LANGUAGE_LABEL = "Language not recorded"

#: A conservative BCP-47 shape: a two- or three-letter primary tag, then up to
#: three subtags of letters or digits. It admits "en", "ms", "zh-Hans",
#: "pt-BR"; it refuses free text, a sentence, or an injection attempt.
#:
#: Deliberately not a registry check. The IANA list changes, an offline app
#: cannot consult it, and refusing a real language because a local copy was out
#: of date would be worse than accepting a well-formed tag nobody uses.
BCP47 = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8}){0,3}$")

MAX_LANGUAGE_CODE_CHARS = 35


class Language(BaseModel):
    """One language a framework may offer, named twice."""

    model_config = ConfigDict(extra="forbid")

    code: str
    #: What an English-reading operator calls it, for the Studio and the CSV.
    english_name: str
    #: What its own speakers call it, for the respondent choosing it. A person
    #: scanning a welcome screen for their language is looking for their word,
    #: not ours.
    endonym: str


#: A starting list, weighted to the frontline workforces this app is built for.
#: The Studio offers these; a framework may configure any subset.
KNOWN_LANGUAGES: tuple[Language, ...] = (
    Language(code="en", english_name="English", endonym="English"),
    Language(code="ms", english_name="Malay", endonym="Bahasa Melayu"),
    Language(code="ta", english_name="Tamil", endonym="தமிழ்"),
    Language(code="zh-Hans", english_name="Chinese (Simplified)", endonym="简体中文"),
    Language(code="zh-Hant", english_name="Chinese (Traditional)", endonym="繁體中文"),
    Language(code="hi", english_name="Hindi", endonym="हिन्दी"),
    Language(code="bn", english_name="Bengali", endonym="বাংলা"),
    Language(code="my", english_name="Burmese", endonym="မြန်မာ"),
    Language(code="th", english_name="Thai", endonym="ไทย"),
    Language(code="tl", english_name="Tagalog", endonym="Tagalog"),
    Language(code="id", english_name="Indonesian", endonym="Bahasa Indonesia"),
    Language(code="vi", english_name="Vietnamese", endonym="Tiếng Việt"),
    Language(code="ne", english_name="Nepali", endonym="नेपाली"),
    Language(code="si", english_name="Sinhala", endonym="සිංහල"),
)

BY_CODE = {language.code: language for language in KNOWN_LANGUAGES}

#: What a framework offers when nobody has configured anything (delta §6:
#: "defaulting to English only so nothing changes for existing frameworks").
DEFAULT_LANGUAGE = "en"


def well_formed(code: str) -> bool:
    """Whether a tag is shaped like a language tag at all."""
    return bool(code) and len(code) <= MAX_LANGUAGE_CODE_CHARS and bool(BCP47.match(code))


def display_name(code: str | None) -> str:
    """What to show for a story's language.

    A code we know gets its English name. A well-formed code we do not know gets
    itself, because a tag is more use to a reader than nothing. Absent gets the
    unknown label — never "English".
    """
    if not code:
        return UNKNOWN_LANGUAGE_LABEL
    known = BY_CODE.get(code)
    return known.english_name if known else code


def offered(codes: list[str]) -> list[Language]:
    """The languages a framework offers, in the order it lists them.

    An unknown but well-formed code is offered under its own tag rather than
    dropped: an operator who typed a language this app has never heard of meant
    it, and a workforce that speaks it should still be able to choose it.
    """
    languages: list[Language] = []
    for code in codes:
        known = BY_CODE.get(code)
        languages.append(known or Language(code=code, english_name=code, endonym=code))
    return languages
