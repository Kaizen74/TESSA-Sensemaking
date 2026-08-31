"""Confirmation, deterministic extraction, and the reconciliation (constraint 12).

This is the step where Stage A's proposal becomes something the app will act on,
and it is the step a human has to press. Two things happen, in this order:

1. **The operator's confirmation is checked against the file itself** — not
   against what Stage A said. Sheet names, column names, and segment numbers all
   have to exist. A mapping that survives this is true of the file regardless of
   what the AI proposed or how confident it was.
2. **Extraction runs with no AI at all.** For a spreadsheet the candidate
   stories are the file's own cells, read by :mod:`backend.parsers`; the model
   never transcribed them and cannot have altered them. For prose the candidates
   are the segments the operator accepted, whose text Stage A copied from the
   parsed blocks.

Then the arithmetic. Constraint 12 requires *exact row reconciliation*, shown.
Every row in the file lands in exactly one line of the tally — extracted, blank,
or on a sheet the operator chose to ignore — and the lines add up to the file's
own row count. If they ever did not, that would mean rows had gone missing
between the file and the dataset, so a tally that does not balance stops the
import instead of being displayed.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.organise import (
    ROLE_IGNORE,
    ROLE_STORIES,
    NarrativeSegment,
    _short_title,
)
from backend.parsers import (
    FILE_CLASS_NARRATIVE,
    FILE_CLASS_TABULAR,
    NormalisedDocument,
)


class ExtractionError(Exception):
    """A confirmation that does not fit the file, phrased for the operator."""

    def __init__(self, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action


class SheetMapping(BaseModel):
    """The operator's confirmed mapping for one sheet."""

    model_config = ConfigDict(extra="forbid")

    sheet: str
    role: Literal["stories", "ignore"]
    story_column: str | None = None
    respondent_group_column: str | None = None
    title_column: str | None = None


class Candidate(BaseModel):
    """One story the file appears to contain, still outside the dataset.

    A candidate is not an anecdote. It sits on the import job until Stage B has
    proposed significations for it and the operator has validated them — the
    second half of constraint 1, built in Phase 6.
    """

    model_config = ConfigDict(extra="forbid")

    text: str
    title: str
    source_locator: str
    respondent_group: str | None = None
    #: Stage A's confidence for prose. ``None`` for spreadsheet rows, which no
    #: model read — an empty confidence column is honest, a fabricated 1.0 is
    #: not.
    confidence: float | None = None


class ReconciliationLine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    count: int


class SheetTally(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sheet: str
    role: str
    rows: int
    stories: int
    blank: int


class Reconciliation(BaseModel):
    """The arithmetic the Mapping screen shows, and that has to add up."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["narrative", "tabular"]
    total_label: str
    total: int
    lines: list[ReconciliationLine]
    balanced: bool
    sheets: list[SheetTally] = Field(default_factory=list)


class ConfirmedExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_class: str
    reconciliation: Reconciliation
    candidates: list[Candidate]
    sheets: list[SheetMapping] = Field(default_factory=list)
    accepted: list[int] = Field(default_factory=list)


def _balance(total: int, lines: list[ReconciliationLine]) -> bool:
    return total == sum(line.count for line in lines)


def _tally_must_balance(reconciliation: Reconciliation) -> None:
    if reconciliation.balanced:
        return
    raise ExtractionError(  # pragma: no cover - a bug in this module
        "reconciliation_unbalanced",
        "Narrative Lens could not account for every row in that file, so it "
        "stopped rather than import part of it.",
        "This is a fault in the app itself. Report it to whoever set this up.",
    )


def confirm_narrative(
    document: NormalisedDocument,
    proposed: list[NarrativeSegment],
    accepted: list[int],
) -> ConfirmedExtraction:
    """Keep the segments the operator ticked, and count what happened to the rest."""
    seen: set[int] = set()
    for index in accepted:
        if index < 0 or index >= len(proposed):
            raise ExtractionError(
                "segment_not_found",
                "Some of the stories you confirmed are no longer in this file's "
                "list, so nothing was imported.",
                "Reload the page to get the current list, then confirm again.",
            )
        if index in seen:
            raise ExtractionError(
                "segment_repeated",
                "The same story was confirmed twice, so nothing was imported.",
                "Reload the page, then confirm again.",
            )
        seen.add(index)

    kept = [proposed[index] for index in sorted(seen)]
    lines = [
        ReconciliationLine(label="Stories you kept", count=len(kept)),
        ReconciliationLine(label="Suggestions you dropped", count=len(proposed) - len(kept)),
    ]
    reconciliation = Reconciliation(
        kind="narrative",
        total_label="Passages the AI suggested",
        total=len(proposed),
        lines=lines,
        balanced=_balance(len(proposed), lines),
    )
    _tally_must_balance(reconciliation)

    return ConfirmedExtraction(
        file_class=document.file_class,
        reconciliation=reconciliation,
        candidates=[
            Candidate(
                text=segment.text,
                title=segment.title,
                source_locator=segment.source_locator,
                confidence=segment.confidence,
            )
            for segment in kept
        ],
        accepted=sorted(seen),
    )


def confirm_tabular(
    document: NormalisedDocument, mappings: list[SheetMapping]
) -> ConfirmedExtraction:
    """Check the mapping against the workbook, then read the rows deterministically."""
    by_name = {sheet.name: sheet for sheet in document.sheets}
    named = [mapping.sheet for mapping in mappings]

    if sorted(named) != sorted(by_name) or len(set(named)) != len(named):
        raise ExtractionError(
            "mapping_sheets_mismatch",
            "The mapping you confirmed does not cover every sheet in the "
            "spreadsheet exactly once, so nothing was imported.",
            "Reload the page and set a choice for each sheet, then confirm again.",
        )

    for mapping in mappings:
        headers = by_name[mapping.sheet].headers
        for column in (
            mapping.story_column,
            mapping.respondent_group_column,
            mapping.title_column,
        ):
            if column is not None and column not in headers:
                raise ExtractionError(
                    "mapping_column_unknown",
                    f"The sheet '{mapping.sheet}' has no column called "
                    f"'{column}', so nothing was imported.",
                    "Reload the page to get this file's real columns, then "
                    "confirm again.",
                )
        if mapping.role == ROLE_STORIES and not mapping.story_column:
            raise ExtractionError(
                "mapping_no_story_column",
                f"You marked '{mapping.sheet}' as holding stories but did not "
                "say which column they are in, so nothing was imported.",
                "Choose the column holding the story, or set that sheet to "
                "'ignore', then confirm again.",
            )

    candidates: list[Candidate] = []
    tallies: list[SheetTally] = []
    blank_total = 0
    ignored_total = 0

    for mapping in mappings:
        sheet = by_name[mapping.sheet]
        if mapping.role == ROLE_IGNORE:
            ignored_total += len(sheet.rows)
            tallies.append(
                SheetTally(
                    sheet=sheet.name,
                    role=ROLE_IGNORE,
                    rows=len(sheet.rows),
                    stories=0,
                    blank=0,
                )
            )
            continue

        assert mapping.story_column is not None  # checked above
        story_at = sheet.headers.index(mapping.story_column)
        group_at = (
            sheet.headers.index(mapping.respondent_group_column)
            if mapping.respondent_group_column
            else None
        )
        title_at = (
            sheet.headers.index(mapping.title_column) if mapping.title_column else None
        )

        blank_here = 0
        stories_here = 0
        for offset, row in enumerate(sheet.rows):
            number = sheet.first_row_number + offset
            text = row[story_at].strip()
            if not text:
                blank_here += 1
                continue
            title = row[title_at].strip() if title_at is not None else ""
            group = row[group_at].strip() if group_at is not None else ""
            candidates.append(
                Candidate(
                    text=text,
                    title=title or _short_title(text),
                    source_locator=f"{sheet.name} row {number}",
                    respondent_group=group or None,
                    confidence=None,
                )
            )
            stories_here += 1

        blank_total += blank_here
        tallies.append(
            SheetTally(
                sheet=sheet.name,
                role=ROLE_STORIES,
                rows=len(sheet.rows),
                stories=stories_here,
                blank=blank_here,
            )
        )

    lines = [
        ReconciliationLine(label="Rows with a story", count=len(candidates)),
        ReconciliationLine(label="Rows with an empty story", count=blank_total),
        ReconciliationLine(label="Rows on sheets you skipped", count=ignored_total),
    ]
    reconciliation = Reconciliation(
        kind="tabular",
        total_label="Rows in the file",
        total=document.row_count,
        lines=lines,
        balanced=_balance(document.row_count, lines),
        sheets=tallies,
    )
    _tally_must_balance(reconciliation)

    return ConfirmedExtraction(
        file_class=document.file_class,
        reconciliation=reconciliation,
        candidates=candidates,
        sheets=mappings,
    )


def confirm(
    document: NormalisedDocument,
    proposed_segments: list[NarrativeSegment],
    accepted: list[int] | None,
    mappings: list[SheetMapping] | None,
) -> ConfirmedExtraction:
    """Dispatch on the file class, refusing a confirmation of the wrong shape."""
    if document.file_class == FILE_CLASS_NARRATIVE:
        if accepted is None:
            raise ExtractionError(
                "confirmation_shape",
                "That file holds written accounts, not a table, so there is no "
                "column mapping to confirm.",
                "Tick the passages that are whole stories, then confirm.",
            )
        return confirm_narrative(document, proposed_segments, accepted)

    if document.file_class == FILE_CLASS_TABULAR:
        if mappings is None:
            raise ExtractionError(
                "confirmation_shape",
                "That file is a table, so Narrative Lens needs to know which "
                "column holds the story before it can import anything.",
                "Set the column for each sheet on the mapping screen, then "
                "confirm.",
            )
        return confirm_tabular(document, mappings)

    raise ExtractionError(  # pragma: no cover - guarded by parsers.classify
        "confirmation_shape",
        "Narrative Lens does not know how to import that kind of file.",
        "Import a Word document, PDF, slide deck, transcript, spreadsheet, or CSV.",
    )
