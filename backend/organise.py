"""Stage A — Organise (PRD §4a, constraint 1).

Stage A looks at a normalised file and *proposes* how it breaks into stories.
It proposes and nothing more: its output is written onto the import job, shown
to the operator, and goes no further until a person confirms it. No anecdote is
created here, and no signification — those are Stage B and the validation queue.

There is one prompt per file class, because the two questions are genuinely
different:

* **narrative** — "where does one account end and the next begin?" The AI reads
  located blocks of prose and returns segments, each with the locator it came
  from and a confidence.
* **tabular** — "which column holds the story, and which sheets are not
  responses at all?" The AI reads headers and a few sample rows and returns a
  per-sheet mapping. It never reads the whole table and never extracts a single
  row: extraction is deterministic and happens *after* confirmation
  (:mod:`backend.extraction`), so what lands in the dataset is the file's own
  cells rather than a model's transcription of them.

Every proposal is checked against the file before the operator sees it. A sheet
or column name that is not in the document is a hallucination, and the import
stops with a plain-English message rather than offering the operator a mapping
onto a column that does not exist.
"""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from backend import ai_client
from backend.parsers import (
    FILE_CLASS_NARRATIVE,
    FILE_CLASS_TABULAR,
    NormalisedDocument,
    Sheet,
)

ROLE_STORIES = "stories"
ROLE_IGNORE = "ignore"

#: How many sample rows per sheet Stage A is shown. Enough to tell a story
#: column from a date column, few enough to keep the prompt small.
SAMPLE_ROWS = 5

#: A block at least this long is a story on its own in the eyes of the mock.
#: Shorter ones are proposed too, at a confidence under constraint 2's 0.70, so
#: the amber path is exercised by the fixtures rather than only by a unit test.
MOCK_CONFIDENT_CHARS = 120

#: Headers the mock reads as "this is the story". Real Stage A is not limited to
#: these; the mock is deliberately dumb and deterministic.
MOCK_STORY_HINTS = (
    "story",
    "narrative",
    "experience",
    "what happened",
    "incident",
    "account",
    "response",
    "answer",
    "comment",
    "description",
)
MOCK_GROUP_HINTS = ("group", "team", "role", "department", "unit", "site", "function")
MOCK_TITLE_HINTS = ("title", "headline", "summary", "subject")

#: A column whose cells average at least this many characters looks like prose
#: even when its header says nothing useful.
MOCK_PROSE_CHARS = 40

TITLE_CHARS = 80


class NarrativeSegment(BaseModel):
    """One proposed story from a prose file."""

    model_config = ConfigDict(extra="forbid")

    source_locator: str
    text: str
    title: str
    confidence: float = Field(ge=0.0, le=1.0)


class NarrativeOrganisation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segments: list[NarrativeSegment]


class SheetProposal(BaseModel):
    """A proposed role and column mapping for one sheet."""

    model_config = ConfigDict(extra="forbid")

    sheet: str
    role: Literal["stories", "ignore"]
    story_column: str | None = None
    respondent_group_column: str | None = None
    title_column: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    note: str = ""


class TabularOrganisation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sheets: list[SheetProposal]


class OrganiseResult(BaseModel):
    """Stage A's whole output, as stored on the job and shown for confirmation."""

    model_config = ConfigDict(extra="forbid")

    file_class: str
    segments: list[NarrativeSegment] = Field(default_factory=list)
    sheets: list[SheetProposal] = Field(default_factory=list)
    #: How many stories Stage A believes the file holds.
    segments_found: int
    #: True when anything in the proposal falls under constraint 2's threshold,
    #: so the screen can flag it amber without recomputing the rule.
    has_low_confidence: bool


NARRATIVE_SYSTEM = (
    "You are helping an analyst organise a file of collected stories. You are "
    "given the file as numbered blocks of text, each with a locator saying "
    "where it came from. Decide where one person's account ends and the next "
    "begins, and return the accounts you find.\n\n"
    "Rules you must not break:\n"
    "- Never invent, summarise, paraphrase, translate, or tidy any text. Each "
    "segment's text must be copied from the blocks you were given.\n"
    "- A segment may join consecutive blocks, but its source_locator must be "
    "the locator of the first block it starts in, exactly as given.\n"
    "- Skip headings, page furniture, and instructions to the reader.\n"
    "- title is a short label of at most 80 characters for recognising the "
    "account in a list.\n"
    "- confidence is your own 0 to 1 estimate that this really is one whole "
    "account by one person.\n\n"
    'Return {"segments": [{"source_locator": str, "text": str, "title": str, '
    '"confidence": number}]}.'
)

TABULAR_SYSTEM = (
    "You are helping an analyst import a spreadsheet of collected stories. You "
    "are given each sheet's name, its column headers, and a few sample rows. "
    "For each sheet, say whether it holds people's stories or should be "
    "ignored, and which column is which.\n\n"
    "Rules you must not break:\n"
    "- Return exactly one entry per sheet you were given, using the sheet name "
    "exactly as given.\n"
    "- Every column name you return must be one of that sheet's headers, "
    "copied exactly. Use null when there is no such column.\n"
    '- role is "stories" when rows are people\'s accounts, "ignore" for '
    "lookup tables, notes, instructions, or summary sheets.\n"
    '- story_column is the column holding the account itself. A sheet with '
    'role "stories" must name one.\n'
    "- Do not copy any row data into your answer. The analyst's own software "
    "reads the rows once the mapping is confirmed.\n"
    "- confidence is your own 0 to 1 estimate that this mapping is right.\n"
    "- note is one short plain-English sentence saying why.\n\n"
    'Return {"sheets": [{"sheet": str, "role": "stories"|"ignore", '
    '"story_column": str|null, "respondent_group_column": str|null, '
    '"title_column": str|null, "confidence": number, "note": str}]}.'
)


class OrganiseError(Exception):
    """Stage A produced something that does not match the file."""

    def __init__(self, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action


def _short_title(text: str) -> str:
    flat = " ".join(text.split())
    if len(flat) <= TITLE_CHARS:
        return flat
    return flat[: TITLE_CHARS - 1].rsplit(" ", 1)[0] + "…"


def _narrative_prompt(document: NormalisedDocument) -> str:
    blocks = [{"locator": b.locator, "text": b.text} for b in document.blocks]
    return "Blocks:\n" + json.dumps(blocks, ensure_ascii=False, indent=1)


def _tabular_prompt(document: NormalisedDocument) -> str:
    sheets = [
        {
            "sheet": sheet.name,
            "headers": sheet.headers,
            "sample_rows": sheet.rows[:SAMPLE_ROWS],
            "total_rows": len(sheet.rows),
        }
        for sheet in document.sheets
    ]
    return "Sheets:\n" + json.dumps(sheets, ensure_ascii=False, indent=1)


def _mock_narrative(document: NormalisedDocument) -> dict[str, Any]:
    """One segment per block, confident about the long ones.

    Deterministic and derived from the file in front of it, so a fixture that
    changes changes the mock's answer too and a stale expectation fails.
    """
    return {
        "segments": [
            {
                "source_locator": block.locator,
                "text": block.text,
                "title": _short_title(block.text),
                "confidence": 0.92 if len(block.text) >= MOCK_CONFIDENT_CHARS else 0.55,
            }
            for block in document.blocks
        ]
    }


def _hinted_column(headers: list[str], hints: tuple[str, ...]) -> str | None:
    for header in headers:
        lowered = header.lower()
        if any(hint in lowered for hint in hints):
            return header
    return None


def _prose_column(sheet: Sheet) -> str | None:
    """The column whose cells read most like prose, if any of them do."""
    best: tuple[float, str] | None = None
    for index, header in enumerate(sheet.headers):
        cells = [row[index] for row in sheet.rows if row[index]]
        if not cells:
            continue
        mean = sum(len(cell) for cell in cells) / len(cells)
        if mean >= MOCK_PROSE_CHARS and (best is None or mean > best[0]):
            best = (mean, header)
    return None if best is None else best[1]


def _mock_tabular(document: NormalisedDocument) -> dict[str, Any]:
    """Header keywords first, then cell length, then give up and ignore."""
    sheets: list[dict[str, Any]] = []
    for sheet in document.sheets:
        by_hint = _hinted_column(sheet.headers, MOCK_STORY_HINTS)
        story = by_hint or _prose_column(sheet)
        if story is None:
            sheets.append(
                {
                    "sheet": sheet.name,
                    "role": ROLE_IGNORE,
                    "story_column": None,
                    "respondent_group_column": None,
                    "title_column": None,
                    "confidence": 0.9,
                    "note": "No column on this sheet reads like a person's account.",
                }
            )
            continue
        sheets.append(
            {
                "sheet": sheet.name,
                "role": ROLE_STORIES,
                "story_column": story,
                "respondent_group_column": _hinted_column(sheet.headers, MOCK_GROUP_HINTS),
                "title_column": _hinted_column(sheet.headers, MOCK_TITLE_HINTS),
                "confidence": 0.9 if by_hint else 0.6,
                "note": (
                    f"'{story}' is named like the account itself."
                    if by_hint
                    else f"'{story}' holds the longest text on this sheet."
                ),
            }
        )
    return {"sheets": sheets}


def _check_narrative(
    document: NormalisedDocument, organisation: NarrativeOrganisation
) -> None:
    known = {block.locator for block in document.blocks}
    unknown = sorted({s.source_locator for s in organisation.segments} - known)
    if unknown:
        raise OrganiseError(
            "organise_locator_unknown",
            "The AI pointed at parts of the file that are not in it "
            f"({unknown[0]}), so Narrative Lens stopped rather than guess.",
            "Click Organise again. If it keeps happening, import a smaller "
            "part of the file.",
        )


def _check_tabular(document: NormalisedDocument, organisation: TabularOrganisation) -> None:
    by_name = {sheet.name: sheet for sheet in document.sheets}
    proposed = [proposal.sheet for proposal in organisation.sheets]

    if sorted(proposed) != sorted(by_name) or len(set(proposed)) != len(proposed):
        raise OrganiseError(
            "organise_sheets_mismatch",
            "The AI did not answer for every sheet in the spreadsheet, so "
            "Narrative Lens stopped rather than guess.",
            "Click Organise again. If it keeps happening, save each sheet as "
            "its own file and import them one at a time.",
        )

    for proposal in organisation.sheets:
        headers = by_name[proposal.sheet].headers
        named = [
            proposal.story_column,
            proposal.respondent_group_column,
            proposal.title_column,
        ]
        for column in named:
            if column is not None and column not in headers:
                raise OrganiseError(
                    "organise_column_unknown",
                    f"The AI pointed at a column called '{column}' that is not "
                    f"on the sheet '{proposal.sheet}', so Narrative Lens "
                    "stopped rather than guess.",
                    "Click Organise again, then check the mapping before you "
                    "confirm it.",
                )
        if proposal.role == ROLE_STORIES and not proposal.story_column:
            raise OrganiseError(
                "organise_no_story_column",
                f"The AI said the sheet '{proposal.sheet}' holds stories but "
                "did not say which column they are in.",
                "Click Organise again, then set the column yourself on the "
                "mapping screen before you confirm it.",
            )


def organise(document: NormalisedDocument) -> OrganiseResult:
    """Run Stage A over a parsed file and return its proposal.

    Nothing is written to the dataset here — the caller stores this on the
    import job and shows it to the operator for confirmation (constraint 1).
    """
    if document.file_class == FILE_CLASS_NARRATIVE:
        narrative = ai_client.request_json(
            system=NARRATIVE_SYSTEM,
            prompt=_narrative_prompt(document),
            shape=NarrativeOrganisation,
            mock=lambda: _mock_narrative(document),
        )
        _check_narrative(document, narrative)
        return OrganiseResult(
            file_class=FILE_CLASS_NARRATIVE,
            segments=narrative.segments,
            segments_found=len(narrative.segments),
            has_low_confidence=any(
                segment.confidence < ai_client.LOW_CONFIDENCE
                for segment in narrative.segments
            ),
        )

    if document.file_class == FILE_CLASS_TABULAR:
        tabular = ai_client.request_json(
            system=TABULAR_SYSTEM,
            prompt=_tabular_prompt(document),
            shape=TabularOrganisation,
            mock=lambda: _mock_tabular(document),
        )
        _check_tabular(document, tabular)
        by_name = {sheet.name: sheet for sheet in document.sheets}
        found = sum(
            len(by_name[p.sheet].rows) for p in tabular.sheets if p.role == ROLE_STORIES
        )
        return OrganiseResult(
            file_class=FILE_CLASS_TABULAR,
            sheets=tabular.sheets,
            segments_found=found,
            has_low_confidence=any(
                proposal.confidence < ai_client.LOW_CONFIDENCE for proposal in tabular.sheets
            ),
        )

    raise OrganiseError(  # pragma: no cover - guarded by parsers.classify
        "organise_unknown_class",
        "Narrative Lens does not know how to organise that kind of file.",
        "Import a Word document, PDF, slide deck, transcript, spreadsheet, or CSV.",
    )
