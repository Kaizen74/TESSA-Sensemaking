"""Every format PRD §1.3 promises, read from a real file of that format."""

from __future__ import annotations

import pytest

from backend import parsers
from tests import ingest_fixtures as fx


def test_every_promised_extension_is_classified() -> None:
    """PRD §1.3 lists nine extensions. All nine are readable, nothing else is."""
    assert set(parsers.FILE_TYPES) == {
        ".docx",
        ".txt",
        ".md",
        ".pdf",
        ".pptx",
        ".xlsx",
        ".csv",
        ".vtt",
        ".srt",
    }


@pytest.mark.parametrize("filename", sorted(fx.ALL_FORMATS))
def test_every_format_parses_to_something_usable(filename: str) -> None:
    document = parsers.parse(filename, fx.ALL_FORMATS[filename])

    assert document.file_class in (parsers.FILE_CLASS_NARRATIVE, parsers.FILE_CLASS_TABULAR)
    if document.file_class == parsers.FILE_CLASS_NARRATIVE:
        assert document.blocks and not document.sheets
        assert all(block.locator and block.text for block in document.blocks)
    else:
        assert document.sheets and not document.blocks
        assert all(sheet.headers for sheet in document.sheets)


def test_plain_text_splits_on_blank_lines() -> None:
    document = parsers.parse("workshop.txt", fx.txt_bytes())

    assert [block.locator for block in document.blocks] == [
        "paragraph 1",
        "paragraph 2",
        "paragraph 3",
    ]
    assert document.blocks[0].text == fx.STORY_ONE


def test_docx_keeps_document_order_and_numbers_every_paragraph() -> None:
    """The empty paragraph between the two stories is skipped, not renumbered.

    Locators point at the file, so paragraph 3 has to still be paragraph 3 when
    the operator opens the document to check it.
    """
    document = parsers.parse("workshop.docx", fx.docx_bytes())

    assert [block.locator for block in document.blocks] == ["paragraph 1", "paragraph 3"]


def test_pdf_locators_name_the_page_and_the_paragraph() -> None:
    document = parsers.parse("workshop.pdf", fx.pdf_bytes())

    assert [block.locator for block in document.blocks] == [
        "page 1, paragraph 1",
        "page 1, paragraph 2",
    ]
    assert "three hours from the deadline" in document.blocks[0].text


def test_deck_reads_slide_text_and_notes_and_nothing_else() -> None:
    """PRD §9 assumption 9: decks are text-only."""
    document = parsers.parse("workshop.pptx", fx.pptx_bytes())

    assert [block.locator for block in document.blocks] == ["slide 1", "slide 1 notes"]
    assert "What we heard" in document.blocks[0].text
    assert document.blocks[1].text == fx.STORY_TWO


@pytest.mark.parametrize(
    ("filename", "builder"),
    [("workshop.vtt", fx.vtt_bytes), ("workshop.srt", fx.srt_bytes)],
)
def test_captions_become_one_block_per_cue_with_its_timings(filename, builder) -> None:
    document = parsers.parse(filename, builder())

    assert len(document.blocks) == 2
    assert document.blocks[0].locator.startswith("cue 1 (00:00:01")
    assert "-->" not in document.blocks[0].text
    assert document.blocks[0].text == fx.STORY_ONE


def test_workbook_keeps_every_sheet_separately() -> None:
    """Assumption 10: a mixed-role workbook is mapped sheet by sheet."""
    document = parsers.parse("workshop.xlsx", fx.xlsx_bytes())

    names = [sheet.name for sheet in document.sheets]
    assert names == ["Responses", "Team codes"]
    responses = document.sheets[0]
    assert responses.headers == ["Ref", "Team", "Story", "Logged"]
    assert len(responses.rows) == 4
    # The empty story cell survives as an empty string rather than vanishing:
    # the reconciliation has to be able to count it.
    assert responses.rows[2][2] == ""


def test_workbook_rows_are_numbered_as_the_spreadsheet_numbers_them() -> None:
    document = parsers.parse("workshop.xlsx", fx.xlsx_bytes())

    # Headers are row 1, so the first data row is row 2 — the number the
    # operator sees when they open the file to check a story.
    assert document.sheets[0].first_row_number == 2


def test_csv_is_one_sheet_named_after_the_file() -> None:
    document = parsers.parse("workshop.csv", fx.csv_bytes())

    assert [sheet.name for sheet in document.sheets] == ["workshop"]
    assert document.sheets[0].headers == ["Team", "Story"]
    assert len(document.sheets[0].rows) == 3


def test_semicolon_separated_csv_still_reads() -> None:
    data = b"Team;Story\nOps;It went fine in the end\n"

    document = parsers.parse("export.csv", data)

    assert document.sheets[0].headers == ["Team", "Story"]


def test_windows_encoded_text_does_not_crash() -> None:
    data = "Café shift handover went badly".encode("cp1252")

    document = parsers.parse("notes.txt", data)

    assert "Caf" in document.blocks[0].text


def test_unknown_extension_is_refused_in_plain_english() -> None:
    with pytest.raises(parsers.ParseError) as caught:
        parsers.parse("recording.mp3", b"...")

    assert caught.value.code == "unsupported_file_type"
    assert ".docx" in caught.value.action
    assert "mp3" in caught.value.message


def test_a_file_with_no_text_is_refused_rather_than_imported_empty() -> None:
    with pytest.raises(parsers.ParseError) as caught:
        parsers.parse("blank.txt", b"   \n\n  \n")

    assert caught.value.code == "file_empty"
    assert caught.value.action


def test_a_huge_file_is_refused_before_it_is_read() -> None:
    with pytest.raises(parsers.ParseError) as caught:
        parsers.parse("huge.txt", b"x" * (parsers.MAX_UPLOAD_BYTES + 1))

    assert caught.value.code == "file_too_large"


def test_a_corrupt_office_file_says_what_to_do_about_it() -> None:
    with pytest.raises(parsers.ParseError) as caught:
        parsers.parse("broken.docx", b"this is not a zip archive")

    assert caught.value.code == "docx_unreadable"
    assert "re-save" in caught.value.action


def test_every_file_type_has_a_class() -> None:
    """The reverse map the API uses for jobs whose extension is long gone."""
    assert set(parsers.FILE_CLASSES) == {
        file_type for file_type, _ in parsers.FILE_TYPES.values()
    }
