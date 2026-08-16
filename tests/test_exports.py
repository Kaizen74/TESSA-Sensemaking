"""The CSV and the Pattern Brief.

The CSV is tested as a file a person will open in Excel and have to trust: every
provenance field present, every placement readable, and nothing in it that
constraint 9 promised would not exist. The brief is tested as prose: it has to
say findings rather than topics, and every number in it has to be one the reader
could recount by hand.
"""

from __future__ import annotations

import csv
import io

from fastapi.testclient import TestClient

from backend.exports import PROVENANCE_COLUMNS
from tests.patterns_fixtures import GOLDEN_DEFINITION, build_golden_dataset
from tests.queue_fixtures import make_framework, proposed_import


def _csv(client: TestClient, framework_id: int, **params) -> tuple[list[dict], list[str]]:
    response = client.get("/api/export/csv", params={"framework_id": framework_id, **params})
    assert response.status_code == 200, response.text
    reader = csv.DictReader(io.StringIO(response.text))
    return list(reader), list(reader.fieldnames or [])


def _brief(client: TestClient, framework_id: int, **params) -> str:
    response = client.get("/api/export/brief", params={"framework_id": framework_id, **params})
    assert response.status_code == 200, response.text
    return response.text


# --------------------------------------------------------------------------
# The CSV
# --------------------------------------------------------------------------


def test_every_record_carries_its_whole_provenance(client: TestClient) -> None:
    """Acceptance criterion 8, on the file the analyst actually gets."""
    framework = build_golden_dataset(client)

    rows, columns = _csv(client, framework["id"])

    for field in PROVENANCE_COLUMNS:
        assert field in columns
    assert len(rows) == 20
    first = rows[0]
    assert first["source_type"] == "capture"
    assert first["input_method"] in ("typed", "paper", "voice")
    assert first["entry_mode"] in ("admin", "kiosk")
    assert first["framework_version"] == "1"
    assert first["signified_by"] == "respondent"
    assert first["validated_at"]
    assert first["status"] == "validated"


def test_the_csv_carries_no_identifier_of_any_kind(client: TestClient) -> None:
    """Constraint 9 does not stop at the database edge."""
    framework = build_golden_dataset(client)

    response = client.get("/api/export/csv", params={"framework_id": framework["id"]})

    header = response.text.splitlines()[0].lower()
    for banned in ("ip", "user_agent", "useragent", "email", "name_", "fingerprint"):
        assert banned not in header.replace("framework_name", "").replace(
            "source_file", ""
        ), banned


def test_times_stay_hour_rounded_in_the_export(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    rows, _ = _csv(client, framework["id"])

    for row in rows:
        assert row["created_at_hour"].endswith(":00:00")


def test_a_column_per_answerable_value(client: TestClient) -> None:
    """Every placement is readable without decoding JSON in a spreadsheet."""
    framework = build_golden_dataset(client)

    rows, columns = _csv(client, framework["id"])

    for expected in ("t1:Speed", "t1:Care", "t1:Cost", "d1", "s1:Planning:x", "m1"):
        assert expected in columns
    first = rows[0]
    assert first["t1:Speed"] and first["d1"] and first["m1"]
    assert (
        round(sum(float(first[f"t1:{c}"]) for c in ("Speed", "Care", "Cost")), 6) == 1.0
    )


def test_a_skipped_question_exports_as_blank_not_zero(client: TestClient) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)
    client.post(
        "/api/capture",
        json={
            "framework_id": framework["id"],
            "text": "A story with nothing placed on it.",
            "significations": [],
        },
    )

    rows, _ = _csv(client, framework["id"])

    assert rows[0]["d1"] == ""
    assert rows[0]["t1:Speed"] == ""
    assert rows[0]["m1"] == ""


def test_the_export_matches_the_filters_on_screen(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    everything, _ = _csv(client, framework["id"])
    ops, _ = _csv(client, framework["id"], respondent_group="Ops")

    assert len(everything) == 20
    assert len(ops) == 7
    assert {row["respondent_group"] for row in ops} == {"Ops"}


def test_only_validated_stories_are_exported(client: TestClient) -> None:
    framework = make_framework(client)
    proposed_import(client, framework["id"])

    rows, _ = _csv(client, framework["id"])

    assert rows == []


def test_an_imported_story_exports_its_file_and_row(client: TestClient) -> None:
    framework = make_framework(client)
    proposed_import(client, framework["id"])
    item = client.get("/api/queue").json()["items"][0]
    client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "accept"})

    rows, _ = _csv(client, framework["id"])

    assert len(rows) == 1
    assert rows[0]["source_type"] == "import"
    assert rows[0]["input_method"] == "imported"
    assert rows[0]["source_file"] == "workshop.xlsx"
    assert rows[0]["source_locator"] == "Responses row 2"
    assert rows[0]["signified_by"] == "ai"
    assert rows[0]["lowest_ai_confidence"]


def test_a_corrected_story_says_both_hands_touched_it(client: TestClient) -> None:
    """The case the provenance column exists for."""
    framework = make_framework(client)
    proposed_import(client, framework["id"])
    item = client.get("/api/queue").json()["items"][0]
    original = {p["signifier_id"]: p["value"] for p in item["significations"]}
    client.put(
        f"/api/queue/{item['anecdote_id']}",
        json={
            "action": "correct",
            "significations": [
                {"signifier_id": "t1", "value": {"Speed": 0.2, "Care": 0.5, "Cost": 0.3}},
                {"signifier_id": "d1", "value": original["d1"]},
            ],
        },
    )

    rows, _ = _csv(client, framework["id"])

    assert rows[0]["signified_by"] == "ai|analyst"


def test_a_mixed_export_says_which_wording_each_story_answered(
    client: TestClient,
) -> None:
    framework = build_golden_dataset(client)
    changed = dict(GOLDEN_DEFINITION)
    changed["prompt_text"] = "Tell us about something that went differently."
    second = client.put(
        f"/api/frameworks/{framework['id']}",
        json={"definition": changed, "edit_kind": "meaning_change"},
    ).json()
    client.post(
        "/api/capture",
        json={
            "framework_id": second["id"],
            "text": "A story told against the new wording.",
            "significations": [],
        },
    )

    rows, _ = _csv(client, second["id"], mixed=True)

    versions = {row["framework_version"] for row in rows}
    assert versions == {"1", "2"}
    assert len(rows) == 21


def test_the_download_is_named_after_the_question_set(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    response = client.get("/api/export/csv", params={"framework_id": framework["id"]})

    assert "hangar-v1-stories.csv" in response.headers["content-disposition"]
    assert response.headers["content-type"].startswith("text/csv")


# --------------------------------------------------------------------------
# The Pattern Brief
# --------------------------------------------------------------------------


def test_the_headline_is_a_finding_not_a_topic(client: TestClient) -> None:
    """Constraint 13f, the whole point of the brief."""
    framework = build_golden_dataset(client)

    brief = _brief(client, framework["id"])

    headline = brief.splitlines()[0]
    assert headline.startswith("# ")
    # A finding says what was found. A topic names the question and stops.
    assert any(
        word in headline for word in ("pull towards", "lean towards", "Most stories", "told most")
    ), headline
    for topic in ("Triad", "results", "breakdown", "Signifier", "Chart"):
        assert topic not in headline


def test_the_brief_states_the_figures_it_was_built_from(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    brief = _brief(client, framework["id"])

    assert "20 stories" in brief
    assert "Hangar — version 1" in brief
    assert "## What the figures say" in brief
    assert brief.count("- On *") >= 3


def test_the_brief_records_the_filters_it_was_taken_under(client: TestClient) -> None:
    """A brief that did not say what it excluded would be misleading."""
    framework = build_golden_dataset(client)

    brief = _brief(client, framework["id"], respondent_group="Ops")

    assert "**Filtered to:** respondent group = Ops" in brief


def test_a_mixed_brief_warns_that_it_mixes_versions(client: TestClient) -> None:
    framework = build_golden_dataset(client)
    changed = dict(GOLDEN_DEFINITION)
    changed["prompt_text"] = "Something else entirely."
    second = client.put(
        f"/api/frameworks/{framework['id']}",
        json={"definition": changed, "edit_kind": "meaning_change"},
    ).json()

    brief = _brief(client, second["id"], mixed=True)

    assert "mixes framework versions" in brief
    assert "version 1 (20)" in brief


def test_the_brief_carries_the_closure_caveat(client: TestClient) -> None:
    """Constraint 12: exploratory and abductive, never causal."""
    framework = build_golden_dataset(client)

    brief = _brief(client, framework["id"])

    assert "closure-constrained" in brief
    assert "not evidence of what caused what" in brief
    assert "Nothing here was written or interpreted by AI" in brief


def test_a_thin_view_says_so_rather_than_inventing_a_finding(
    client: TestClient,
) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)
    client.post(
        "/api/capture",
        json={
            "framework_id": framework["id"],
            "text": "The only story so far.",
            "significations": [{"signifier_id": "d1", "value": {"value": 0.9}}],
        },
    )

    brief = _brief(client, framework["id"])

    assert "too few to read a pattern from" in brief.splitlines()[0]


def test_an_empty_view_is_honest_about_being_empty(client: TestClient) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)

    brief = _brief(client, framework["id"])

    assert brief.splitlines()[0] == "# No stories match these filters yet"


def test_the_brief_downloads_as_markdown(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    response = client.get("/api/export/brief", params={"framework_id": framework["id"]})

    assert "hangar-v1-brief.md" in response.headers["content-disposition"]
    assert response.headers["content-type"].startswith("text/markdown")


def test_ties_read_as_english(client: TestClient) -> None:
    """Three-way ties are common in small sets and must not read like code."""
    framework = build_golden_dataset(client)

    brief = _brief(client, framework["id"])

    assert " and and " not in brief
    assert "** and **" not in brief or ", " in brief
