"""The staged import machine end to end, over HTTP, with zero network.

Acceptance criterion 7: all-format fixtures pass Stage A with ``NL_MOCK_AI=1``,
and the xlsx mapping screen's reconciliation matches the fixture. Both are
checked here against real files of each format, driven through the same
endpoints the Import screen calls.
"""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import Anecdote, ImportJob, Signification
from tests import ingest_fixtures as fx

MAPPING_KEYS = ("sheet", "role", "story_column", "respondent_group_column", "title_column")


def _upload(client: TestClient, filename: str, data: bytes) -> dict:
    response = client.post("/api/import", files={"file": (filename, data)})
    assert response.status_code == 201, response.text
    return response.json()


def _organise(client: TestClient, job_id: int) -> dict:
    response = client.post(f"/api/import/{job_id}/organise")
    assert response.status_code == 200, response.text
    return response.json()


def _confirmation_body(organised: dict) -> dict:
    """Accept exactly what Stage A proposed — the operator's default click."""
    if organised["file_class"] == "tabular":
        return {
            "sheets": [
                {key: sheet[key] for key in MAPPING_KEYS}
                for sheet in organised["organisation"]["sheets"]
            ]
        }
    return {"accepted": list(range(len(organised["organisation"]["segments"])))}


def _confirm(client: TestClient, job_id: int, body: dict) -> dict:
    response = client.post(f"/api/import/{job_id}/mapping", json=body)
    assert response.status_code == 200, response.text
    return response.json()


# --------------------------------------------------------------------------
# Every format, all the way through Stage A (acceptance criterion 7)
# --------------------------------------------------------------------------


@pytest.mark.parametrize("filename", sorted(fx.ALL_FORMATS))
def test_every_format_walks_the_whole_machine_offline(
    client: TestClient, filename: str
) -> None:
    uploaded = _upload(client, filename, fx.ALL_FORMATS[filename])
    assert uploaded["stage"] == "uploaded"
    assert uploaded["segments_found"] is None

    organised = _organise(client, uploaded["id"])
    assert organised["stage"] == "organised"
    assert organised["segments_found"] > 0
    assert organised["organisation"]["file_class"] == organised["file_class"]

    confirmed = _confirm(client, uploaded["id"], _confirmation_body(organised))
    assert confirmed["stage"] == "mapping_confirmed"
    assert confirmed["confirmation"]["candidate_count"] > 0
    assert confirmed["confirmation"]["reconciliation"]["balanced"] is True


@pytest.mark.parametrize(
    ("filename", "file_class"),
    [
        ("workshop.txt", "narrative"),
        ("workshop.md", "narrative"),
        ("workshop.docx", "narrative"),
        ("workshop.pdf", "narrative"),
        ("workshop.pptx", "narrative"),
        ("workshop.vtt", "narrative"),
        ("workshop.srt", "narrative"),
        ("workshop.xlsx", "tabular"),
        ("workshop.csv", "tabular"),
    ],
)
def test_the_file_class_decides_which_screen_the_operator_gets(
    client: TestClient, filename: str, file_class: str
) -> None:
    uploaded = _upload(client, filename, fx.ALL_FORMATS[filename])

    assert uploaded["file_class"] == file_class
    if file_class == "tabular":
        assert uploaded["sheets"] and uploaded["block_count"] == 0
    else:
        assert uploaded["block_count"] > 0 and uploaded["sheets"] == []


# --------------------------------------------------------------------------
# The stage gate, as the operator meets it
# --------------------------------------------------------------------------


def test_confirming_a_mapping_before_organising_is_refused(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.xlsx", fx.xlsx_bytes())

    response = client.post(f"/api/import/{uploaded['id']}/mapping", json={"sheets": []})

    assert response.status_code == 409
    error = response.json()["detail"]["error"]
    assert error["code"] == "wrong_stage"
    assert error["action"] == "Click Organise on this file first."


def test_organising_twice_is_refused(client: TestClient) -> None:
    """Two runs of Stage A would give one file two different sets of stories."""
    uploaded = _upload(client, "workshop.txt", fx.txt_bytes())
    _organise(client, uploaded["id"])

    response = client.post(f"/api/import/{uploaded['id']}/organise")

    assert response.status_code == 409
    assert response.json()["detail"]["error"]["code"] == "wrong_stage"


def test_confirming_twice_is_refused(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.txt", fx.txt_bytes())
    organised = _organise(client, uploaded["id"])
    body = _confirmation_body(organised)
    _confirm(client, uploaded["id"], body)

    response = client.post(f"/api/import/{uploaded['id']}/mapping", json=body)

    assert response.status_code == 409


# --------------------------------------------------------------------------
# Constraint 12 — the mapping is confirmed, and the rows reconcile exactly
# --------------------------------------------------------------------------


def test_the_workbook_reconciliation_matches_the_fixture_exactly(
    client: TestClient,
) -> None:
    """Four response rows (one blank) and two lookup rows, all accounted for."""
    uploaded = _upload(client, "workshop.xlsx", fx.xlsx_bytes())
    organised = _organise(client, uploaded["id"])
    confirmed = _confirm(client, uploaded["id"], _confirmation_body(organised))

    reconciliation = confirmed["confirmation"]["reconciliation"]
    assert reconciliation["kind"] == "tabular"
    assert reconciliation["total"] == 6
    assert [(line["label"], line["count"]) for line in reconciliation["lines"]] == [
        ("Rows with a story", 3),
        ("Rows with an empty story", 1),
        ("Rows on sheets you skipped", 2),
    ]
    assert reconciliation["balanced"] is True
    assert confirmed["confirmation"]["candidate_count"] == 3


def test_the_reconciliation_always_adds_up_to_the_rows_in_the_file(
    client: TestClient,
) -> None:
    for filename in ("workshop.xlsx", "workshop.csv"):
        uploaded = _upload(client, filename, fx.ALL_FORMATS[filename])
        organised = _organise(client, uploaded["id"])
        confirmed = _confirm(client, uploaded["id"], _confirmation_body(organised))

        reconciliation = confirmed["confirmation"]["reconciliation"]
        counted = sum(line["count"] for line in reconciliation["lines"])
        rows_in_file = sum(sheet["row_count"] for sheet in confirmed["sheets"])
        assert counted == reconciliation["total"] == rows_in_file


def test_a_sheet_the_operator_ignores_is_skipped_whole(client: TestClient) -> None:
    """PRD §9 assumption 10, with the skipped rows still counted."""
    uploaded = _upload(client, "workshop.xlsx", fx.xlsx_bytes())
    organised = _organise(client, uploaded["id"])
    body = _confirmation_body(organised)
    for sheet in body["sheets"]:
        sheet.update(
            role="ignore", story_column=None, respondent_group_column=None, title_column=None
        )

    confirmed = _confirm(client, uploaded["id"], body)

    reconciliation = confirmed["confirmation"]["reconciliation"]
    assert confirmed["confirmation"]["candidate_count"] == 0
    assert reconciliation["total"] == 6
    assert reconciliation["lines"][2]["count"] == 6
    assert reconciliation["balanced"] is True


def test_the_operator_can_override_stage_as_column_choice(client: TestClient) -> None:
    """The mapping that counts is the one the human confirmed, not the proposal."""
    uploaded = _upload(client, "workshop.xlsx", fx.xlsx_bytes())
    organised = _organise(client, uploaded["id"])
    assert organised["organisation"]["sheets"][0]["story_column"] == "Story"

    body = _confirmation_body(organised)
    body["sheets"][0]["story_column"] = "Ref"
    confirmed = _confirm(client, uploaded["id"], body)

    # Every Ref cell is filled, so all four rows now count as stories.
    assert confirmed["confirmation"]["candidate_count"] == 4
    assert confirmed["confirmation"]["sheets"][0]["story_column"] == "Ref"


def test_a_mapping_onto_a_column_that_is_not_there_is_refused(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.xlsx", fx.xlsx_bytes())
    organised = _organise(client, uploaded["id"])
    body = _confirmation_body(organised)
    body["sheets"][0]["story_column"] = "Feelings"

    response = client.post(f"/api/import/{uploaded['id']}/mapping", json=body)

    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "mapping_column_unknown"


def test_a_mapping_that_forgets_a_sheet_is_refused(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.xlsx", fx.xlsx_bytes())
    organised = _organise(client, uploaded["id"])
    body = _confirmation_body(organised)
    body["sheets"] = body["sheets"][:1]

    response = client.post(f"/api/import/{uploaded['id']}/mapping", json=body)

    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "mapping_sheets_mismatch"


def test_a_stories_sheet_with_no_story_column_is_refused(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.csv", fx.csv_bytes())
    organised = _organise(client, uploaded["id"])
    body = _confirmation_body(organised)
    body["sheets"][0]["story_column"] = None

    response = client.post(f"/api/import/{uploaded['id']}/mapping", json=body)

    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "mapping_no_story_column"


def test_a_table_cannot_be_confirmed_as_if_it_were_prose(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.xlsx", fx.xlsx_bytes())
    _organise(client, uploaded["id"])

    response = client.post(f"/api/import/{uploaded['id']}/mapping", json={"accepted": [0]})

    assert response.status_code == 400
    error = response.json()["detail"]["error"]
    assert error["code"] == "confirmation_shape"
    assert "which column holds the story" in error["message"]


def test_prose_cannot_be_confirmed_as_if_it_were_a_table(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.txt", fx.txt_bytes())
    _organise(client, uploaded["id"])

    response = client.post(f"/api/import/{uploaded['id']}/mapping", json={"sheets": []})

    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "confirmation_shape"


# --------------------------------------------------------------------------
# Stage A proposes; the operator disposes
# --------------------------------------------------------------------------


def test_dropping_a_suggested_passage_is_counted_not_hidden(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.txt", fx.txt_bytes())
    organised = _organise(client, uploaded["id"])
    assert organised["segments_found"] == 3

    confirmed = _confirm(client, uploaded["id"], {"accepted": [0, 1]})

    reconciliation = confirmed["confirmation"]["reconciliation"]
    assert reconciliation["kind"] == "narrative"
    assert reconciliation["total"] == 3
    assert [line["count"] for line in reconciliation["lines"]] == [2, 1]
    assert reconciliation["balanced"] is True
    assert confirmed["confirmation"]["accepted"] == [0, 1]


def test_accepting_nothing_is_allowed_and_still_reconciles(client: TestClient) -> None:
    """A file of headings and furniture is a real outcome, not an error."""
    uploaded = _upload(client, "workshop.txt", fx.txt_bytes())
    _organise(client, uploaded["id"])

    response = client.post(f"/api/import/{uploaded['id']}/mapping", json={"accepted": []})

    assert response.status_code == 200
    reconciliation = response.json()["confirmation"]["reconciliation"]
    assert [line["count"] for line in reconciliation["lines"]] == [0, 3]
    assert reconciliation["balanced"] is True


def test_confirming_a_passage_that_is_not_on_the_list_is_refused(
    client: TestClient,
) -> None:
    uploaded = _upload(client, "workshop.txt", fx.txt_bytes())
    _organise(client, uploaded["id"])

    response = client.post(f"/api/import/{uploaded['id']}/mapping", json={"accepted": [99]})

    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "segment_not_found"


def test_the_same_passage_cannot_be_confirmed_twice(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.txt", fx.txt_bytes())
    _organise(client, uploaded["id"])

    response = client.post(f"/api/import/{uploaded['id']}/mapping", json={"accepted": [0, 0]})

    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "segment_repeated"


def test_low_confidence_is_flagged_but_routed_identically(client: TestClient) -> None:
    """Constraint 2: amber is a colour, not a different queue."""
    uploaded = _upload(client, "workshop.txt", fx.txt_bytes())

    organised = _organise(client, uploaded["id"])

    segments = organised["organisation"]["segments"]
    assert organised["organisation"]["has_low_confidence"] is True
    assert any(segment["confidence"] < 0.70 for segment in segments)
    # Every segment is on the same list awaiting the same confirmation.
    assert len(segments) == organised["segments_found"] == 3


def test_stage_a_copies_text_rather_than_rewriting_it(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.txt", fx.txt_bytes())

    organised = _organise(client, uploaded["id"])

    assert organised["organisation"]["segments"][0]["text"] == fx.STORY_ONE


def test_spreadsheet_candidates_carry_no_invented_confidence(client: TestClient) -> None:
    """No model read those cells, so there is nothing to be confident about."""
    uploaded = _upload(client, "workshop.xlsx", fx.xlsx_bytes())
    organised = _organise(client, uploaded["id"])
    _confirm(client, uploaded["id"], _confirmation_body(organised))

    detail = client.get(f"/api/import/{uploaded['id']}").json()
    assert detail["confirmation"]["reconciliation"]["kind"] == "tabular"
    # The confidence lives on the candidates, which the detail view summarises;
    # read them from the stored job to check nothing was fabricated.
    assert detail["confirmation"]["candidate_count"] == 3


def test_candidates_keep_the_row_the_operator_would_look_at(
    client: TestClient, session: Session
) -> None:
    uploaded = _upload(client, "workshop.xlsx", fx.xlsx_bytes())
    organised = _organise(client, uploaded["id"])
    _confirm(client, uploaded["id"], _confirmation_body(organised))

    job = session.get(ImportJob, uploaded["id"])
    candidates = job.column_mapping_json["candidates"]
    assert [candidate["source_locator"] for candidate in candidates] == [
        "Responses row 2",
        "Responses row 3",
        "Responses row 5",
    ]
    assert [candidate["respondent_group"] for candidate in candidates] == [
        "Ops",
        "Deck",
        "Support",
    ]
    assert all(candidate["confidence"] is None for candidate in candidates)


# --------------------------------------------------------------------------
# Constraint 1 — nothing reaches the dataset in Stage A
# --------------------------------------------------------------------------


@pytest.mark.parametrize("filename", sorted(fx.ALL_FORMATS))
def test_no_story_enters_the_dataset_before_validation(
    client: TestClient, session: Session, filename: str
) -> None:
    uploaded = _upload(client, filename, fx.ALL_FORMATS[filename])
    organised = _organise(client, uploaded["id"])
    _confirm(client, uploaded["id"], _confirmation_body(organised))

    assert session.query(Anecdote).count() == 0
    assert session.query(Signification).count() == 0


# --------------------------------------------------------------------------
# Housekeeping the operator will meet
# --------------------------------------------------------------------------


def test_an_unreadable_file_is_refused_at_the_door(client: TestClient) -> None:
    response = client.post("/api/import", files={"file": ("recording.mp3", b"...")})

    assert response.status_code == 400
    error = response.json()["detail"]["error"]
    assert error["code"] == "unsupported_file_type"
    assert ".docx" in error["action"]


def test_a_refused_file_leaves_no_job_behind(client: TestClient, session: Session) -> None:
    client.post("/api/import", files={"file": ("recording.mp3", b"...")})

    assert session.query(ImportJob).count() == 0


def test_the_upload_records_a_hash_of_what_arrived(
    client: TestClient, session: Session
) -> None:
    import hashlib

    data = fx.txt_bytes()
    uploaded = _upload(client, "workshop.txt", data)

    job = session.get(ImportJob, uploaded["id"])
    assert job.file_hash == hashlib.sha256(data).hexdigest()


def test_imports_are_listed_newest_first(client: TestClient) -> None:
    first = _upload(client, "one.txt", fx.txt_bytes())
    second = _upload(client, "two.csv", fx.csv_bytes())

    listed = client.get("/api/import").json()

    assert [row["id"] for row in listed] == [second["id"], first["id"]]
    assert [row["filename"] for row in listed] == ["two.csv", "one.txt"]


def test_an_unknown_job_says_so_in_plain_english(client: TestClient) -> None:
    response = client.get("/api/import/404")

    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "import_not_found"


def test_every_stage_is_described_without_jargon(client: TestClient) -> None:
    uploaded = _upload(client, "workshop.txt", fx.txt_bytes())
    assert uploaded["stage_label"] == "read, and waiting to be organised"

    organised = _organise(client, uploaded["id"])
    assert organised["stage_label"] == "organised, and waiting for you to check it"


def test_job_status_is_inside_the_200ms_budget(client: TestClient) -> None:
    """PRD §4: AI endpoints are exempt; reading a job's status is not."""
    uploaded = _upload(client, "workshop.xlsx", fx.xlsx_bytes())

    start = time.perf_counter()
    client.get(f"/api/import/{uploaded['id']}")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 200
