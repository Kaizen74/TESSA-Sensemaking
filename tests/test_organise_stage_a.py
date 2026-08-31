"""Stage A: what it proposes, and what it is not allowed to get away with.

Stage A is the only place a language model's answer shapes an import, so its
answer is checked against the file before the operator ever sees it. A locator,
sheet, or column the file does not have is not a small inaccuracy — it is a
mapping onto something that does not exist, and it stops the import.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend import ai_client
from backend import organise as stage_a
from backend.ai_client import AiError
from backend.models import ImportJob
from backend.organise import OrganiseError, organise
from backend.parsers import parse
from tests import ingest_fixtures as fx


def _reply(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    """Make Stage A's next answer whatever the test says it is."""

    def fake(*, system: str, prompt: str, shape: type, mock: object) -> Any:
        return shape.model_validate(payload)

    monkeypatch.setattr(stage_a.ai_client, "request_json", fake)


# --------------------------------------------------------------------------
# What the mock proposes
# --------------------------------------------------------------------------


def test_the_mock_reads_a_named_story_column() -> None:
    document = parse("workshop.xlsx", fx.xlsx_bytes())

    result = organise(document)

    responses, lookup = result.sheets
    assert (responses.sheet, responses.role, responses.story_column) == (
        "Responses",
        "stories",
        "Story",
    )
    assert responses.respondent_group_column == "Team"
    assert (lookup.sheet, lookup.role) == ("Team codes", "ignore")


def test_a_sheet_with_nothing_story_like_is_proposed_as_ignore() -> None:
    """A lookup table is not a set of responses, and saying so is the answer."""
    document = parse("workshop.xlsx", fx.xlsx_bytes())

    result = organise(document)

    lookup = result.sheets[1]
    assert lookup.role == "ignore"
    assert lookup.story_column is None
    assert lookup.note


def test_a_prose_column_is_found_even_when_its_header_says_nothing(
    tmp_path,
) -> None:
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Q4"
    sheet.append(["Ref", "Field 2"])
    sheet.append(["R-1", fx.STORY_ONE])
    sheet.append(["R-2", fx.STORY_TWO])
    path = tmp_path / "anon.xlsx"
    workbook.save(path)

    result = organise(parse("anon.xlsx", path.read_bytes()))

    proposal = result.sheets[0]
    assert proposal.story_column == "Field 2"
    # Guessed from cell length rather than read from the header, so it is
    # offered with less confidence — and the operator confirms it either way.
    assert proposal.confidence < ai_client.LOW_CONFIDENCE + 0.01
    assert "longest text" in proposal.note


def test_prose_segments_carry_the_locator_they_came_from() -> None:
    document = parse("workshop.pptx", fx.pptx_bytes())

    result = organise(document)

    assert [segment.source_locator for segment in result.segments] == [
        "slide 1",
        "slide 1 notes",
    ]


def test_segments_found_counts_what_stage_a_believes_it_found() -> None:
    result = organise(parse("workshop.vtt", fx.vtt_bytes()))

    assert result.segments_found == len(result.segments) == 2


# --------------------------------------------------------------------------
# What Stage A is not allowed to get away with
# --------------------------------------------------------------------------


def test_a_locator_that_is_not_in_the_file_stops_the_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = parse("workshop.txt", fx.txt_bytes())
    _reply(
        monkeypatch,
        {
            "segments": [
                {
                    "source_locator": "paragraph 99",
                    "text": "Something nobody said.",
                    "title": "Invented",
                    "confidence": 0.99,
                }
            ]
        },
    )

    with pytest.raises(OrganiseError) as caught:
        organise(document)

    assert caught.value.code == "organise_locator_unknown"
    assert "paragraph 99" in caught.value.message


def test_a_sheet_left_out_of_the_answer_stops_the_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = parse("workshop.xlsx", fx.xlsx_bytes())
    _reply(
        monkeypatch,
        {
            "sheets": [
                {
                    "sheet": "Responses",
                    "role": "stories",
                    "story_column": "Story",
                    "respondent_group_column": None,
                    "title_column": None,
                    "confidence": 0.9,
                    "note": "",
                }
            ]
        },
    )

    with pytest.raises(OrganiseError) as caught:
        organise(document)

    assert caught.value.code == "organise_sheets_mismatch"


def test_a_column_the_sheet_does_not_have_stops_the_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = parse("workshop.csv", fx.csv_bytes())
    _reply(
        monkeypatch,
        {
            "sheets": [
                {
                    "sheet": "workshop",
                    "role": "stories",
                    "story_column": "Narrative",
                    "respondent_group_column": None,
                    "title_column": None,
                    "confidence": 0.95,
                    "note": "",
                }
            ]
        },
    )

    with pytest.raises(OrganiseError) as caught:
        organise(document)

    assert caught.value.code == "organise_column_unknown"
    assert "Narrative" in caught.value.message


def test_a_stories_sheet_with_no_column_named_stops_the_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = parse("workshop.csv", fx.csv_bytes())
    _reply(
        monkeypatch,
        {
            "sheets": [
                {
                    "sheet": "workshop",
                    "role": "stories",
                    "story_column": None,
                    "respondent_group_column": None,
                    "title_column": None,
                    "confidence": 0.95,
                    "note": "",
                }
            ]
        },
    )

    with pytest.raises(OrganiseError) as caught:
        organise(document)

    assert caught.value.code == "organise_no_story_column"


# --------------------------------------------------------------------------
# When the AI is not there at all
# --------------------------------------------------------------------------


def test_an_unreachable_service_leaves_the_file_where_it_was(
    client: TestClient, session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Constraint 4 and 7: offline is a normal state, not a broken one.

    The file stays at ``uploaded``, so Organise can simply be clicked again once
    the connection is back. Parking it in ``failed`` would be terminal and would
    make the operator upload the file a second time.
    """
    uploaded = client.post(
        "/api/import", files={"file": ("workshop.txt", fx.txt_bytes())}
    ).json()

    def unreachable(**kwargs: object) -> Any:
        raise AiError(
            "ai_unreachable",
            "Narrative Lens could not reach the AI service.",
            "Check the internet connection and try Analyse again.",
        )

    monkeypatch.setattr(stage_a.ai_client, "request_json", unreachable)

    response = client.post(f"/api/import/{uploaded['id']}/organise")

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "ai_unreachable"

    job = session.get(ImportJob, uploaded["id"])
    assert job.stage == "uploaded"
    assert job.error_message == "Narrative Lens could not reach the AI service."


def test_the_file_can_be_organised_again_once_the_service_is_back(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    uploaded = client.post(
        "/api/import", files={"file": ("workshop.txt", fx.txt_bytes())}
    ).json()

    def unreachable(**kwargs: object) -> Any:
        raise AiError("ai_unreachable", "No connection.", "Try again.")

    monkeypatch.setattr(stage_a.ai_client, "request_json", unreachable)
    client.post(f"/api/import/{uploaded['id']}/organise")
    monkeypatch.undo()

    retry = client.post(f"/api/import/{uploaded['id']}/organise")

    assert retry.status_code == 200
    assert retry.json()["stage"] == "organised"
    assert retry.json()["error_message"] is None


def test_a_hallucinated_answer_is_reported_as_the_services_fault(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    uploaded = client.post(
        "/api/import", files={"file": ("workshop.txt", fx.txt_bytes())}
    ).json()
    _reply(
        monkeypatch,
        {
            "segments": [
                {
                    "source_locator": "paragraph 99",
                    "text": "Nobody said this.",
                    "title": "Invented",
                    "confidence": 1.0,
                }
            ]
        },
    )

    response = client.post(f"/api/import/{uploaded['id']}/organise")

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "organise_locator_unknown"
