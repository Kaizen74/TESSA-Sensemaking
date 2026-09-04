"""Collective interpretation as an artefact, not data (delta §6, constraint 16).

The temptation this file exists to defend against is a specific one. A room
concludes "most of these are about being asked to choose between speed and
safety", and it would be so easy to store that as a marker, a weight, or a
cluster label — and then the landscape would show what the room *said* rather
than what the storytellers *placed*, and within a week nobody could tell the
two apart.

So the central test here is an equivalence: the landscape's entire output,
serialised, is byte-identical before and after an interpretation is recorded.
That is the constraint-16 guard the delta names, and it is on the regression
list from this phase onward.

Everything else follows from it. Recording captures the signifier and the
filters that were on screen; an interpretation appears in no signification
query; the brief quotes it verbatim and attributes it to the room; and the
projector view hides the controls and can be left with a key.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.interpretations import (
    MAX_INTERPRETATION_CHARS,
    MAX_SESSION_LABEL_CHARS,
)
from backend.models import Interpretation, Signification
from tests.patterns_fixtures import GOLDEN_DEFINITION, build_golden_dataset

ROOM_SAID = (
    "Most of these are about being asked to choose between doing it fast and "
    "doing it safely, and being blamed either way."
)


def record(client: TestClient, framework_id: int, **overrides) -> dict:
    body = {
        "framework_id": framework_id,
        "interpretation_text": ROOM_SAID,
        "view_kind": "landscape",
        "signifier_id": "t1",
        "filter_state": {"respondent_group": "Ops"},
        "session_label": "Ops night shift, 12 March",
        "participant_count": 9,
    }
    body.update(overrides)
    response = client.post("/api/interpretations", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def listed(client: TestClient, framework_id: int, **params) -> list[dict]:
    response = client.get(
        "/api/interpretations", params={"framework_id": framework_id, **params}
    )
    assert response.status_code == 200, response.text
    return response.json()


def landscape(client: TestClient, framework_id: int, triad_id: str = "t1", **params) -> dict:
    response = client.get(f"/api/landscape/{framework_id}/{triad_id}", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def serialise(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, indent=2)


# --------------------------------------------------------------------------
# The constraint-16 guard
# --------------------------------------------------------------------------


def test_the_landscape_is_byte_identical_before_and_after_recording(
    client: TestClient,
) -> None:
    """The named guard of delta §6, and the whole point of this phase.

    Not "the peaks are close" and not "the count is the same" — the entire
    response, serialised, character for character. If an interpretation ever
    finds a route into the terrain, this fails and says exactly what moved.
    """
    framework = build_golden_dataset(client)

    before = serialise(landscape(client, framework["id"]))
    record(client, framework["id"])
    after = serialise(landscape(client, framework["id"]))

    assert after == before


def test_recording_many_changes_nothing_either(client: TestClient) -> None:
    """One interpretation might round away. Ten cannot."""
    framework = build_golden_dataset(client)
    before = serialise(landscape(client, framework["id"]))

    for index in range(10):
        record(client, framework["id"], interpretation_text=f"Reading {index}.")

    assert serialise(landscape(client, framework["id"])) == before


def test_every_other_view_is_unmoved_too(client: TestClient) -> None:
    """The landscape is the named guard; it is not the only surface that matters.

    Patterns, the explorer, the clusters and the quality signals all aggregate
    significations, and an interpretation must be invisible to every one of
    them.
    """
    framework = build_golden_dataset(client)
    fid = framework["id"]
    views = {
        "patterns": f"/api/patterns/{fid}",
        "explorer": f"/api/explorer/{fid}",
        "clusters": f"/api/clusters/{fid}",
        "quality": f"/api/quality/{fid}",
    }
    before = {name: serialise(client.get(path).json()) for name, path in views.items()}

    record(client, fid)

    for name, path in views.items():
        assert serialise(client.get(path).json()) == before[name], name


def test_an_interpretation_is_in_no_signification_query(
    client: TestClient, session: Session
) -> None:
    """Read off the database, not off an endpoint.

    An endpoint could be filtering one out while the row sat in the table
    pretending to be a placement. It does not: an interpretation is a different
    table with no anecdote link, and the count of significations is untouched.
    """
    framework = build_golden_dataset(client)
    before = session.scalar(select(Signification).order_by(Signification.id.desc()))
    count_before = len(session.scalars(select(Signification)).all())

    record(client, framework["id"])
    session.expire_all()

    assert len(session.scalars(select(Signification)).all()) == count_before
    after = session.scalar(select(Signification).order_by(Signification.id.desc()))
    assert after.id == before.id


def test_the_stored_row_carries_no_route_to_a_story(
    client: TestClient, session: Session
) -> None:
    """Structural: there is no column through which it could reach one."""
    framework = build_golden_dataset(client)
    record(client, framework["id"])

    row = session.scalar(select(Interpretation))

    assert not hasattr(row, "anecdote_id")
    assert not hasattr(row, "signification_id")
    assert row.framework_id == framework["id"]


# --------------------------------------------------------------------------
# Recording captures what was on screen
# --------------------------------------------------------------------------


def test_recording_captures_the_signifier_and_the_filter_state(
    client: TestClient,
) -> None:
    """Delta §5: captured automatically, not typed by the facilitator."""
    framework = build_golden_dataset(client)

    stored = record(client, framework["id"])

    assert stored["signifier_id"] == "t1"
    assert stored["filter_state"] == {"respondent_group": "Ops"}
    assert stored["view_kind"] == "landscape"
    assert stored["recorded_at"]


def test_the_room_and_its_size_are_kept_when_given(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    stored = record(client, framework["id"])

    assert stored["session_label"] == "Ops night shift, 12 March"
    assert stored["participant_count"] == 9


def test_the_optional_fields_are_genuinely_optional(client: TestClient) -> None:
    """A room in a hurry types the sentence and nothing else."""
    framework = build_golden_dataset(client)

    stored = record(
        client,
        framework["id"],
        session_label=None,
        participant_count=None,
        signifier_id=None,
        filter_state={},
    )

    assert stored["session_label"] is None
    assert stored["participant_count"] is None
    assert stored["signifier_id"] is None
    assert stored["filter_state"] == {}


def test_the_words_are_stored_exactly_as_typed(client: TestClient) -> None:
    """Verbatim. Never summarised, never re-worded, never coded."""
    framework = build_golden_dataset(client)
    awkward = 'They said: "it\'s the same story every time" — and nobody disagreed.'

    stored = record(client, framework["id"], interpretation_text=awkward)

    assert stored["interpretation_text"] == awkward
    assert listed(client, framework["id"])[0]["interpretation_text"] == awkward


def test_they_come_back_newest_first(client: TestClient) -> None:
    framework = build_golden_dataset(client)
    for index in range(3):
        record(client, framework["id"], interpretation_text=f"Reading {index}.")

    rows = listed(client, framework["id"])

    assert [row["interpretation_text"] for row in rows] == [
        "Reading 2.",
        "Reading 1.",
        "Reading 0.",
    ]


# --------------------------------------------------------------------------
# Scope: a conclusion belongs to the wording it was made about
# --------------------------------------------------------------------------


def test_a_conclusion_stays_with_the_version_it_was_made_about(
    client: TestClient,
) -> None:
    """A room reading version 1 was reading a different question from version 2."""
    framework = build_golden_dataset(client)
    record(client, framework["id"])

    changed = dict(GOLDEN_DEFINITION)
    changed["prompt_text"] = "Tell us about something that went differently."
    second = client.put(
        f"/api/frameworks/{framework['id']}",
        json={"definition": changed, "edit_kind": "meaning_change"},
    ).json()

    assert listed(client, second["id"]) == []
    assert len(listed(client, second["id"], mixed=True)) == 1


def test_an_unknown_question_set_says_so_in_plain_english(client: TestClient) -> None:
    response = client.get("/api/interpretations", params={"framework_id": 9999})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "framework_not_found"


def test_recording_against_an_unknown_question_set_is_refused(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/interpretations",
        json={"framework_id": 9999, "interpretation_text": ROOM_SAID},
    )

    assert response.status_code == 404
    assert response.json()["error"]["action"]


def test_a_signifier_this_question_set_does_not_have_is_refused(
    client: TestClient,
) -> None:
    """Otherwise a conclusion could point at a question that never existed."""
    framework = build_golden_dataset(client)

    response = client.post(
        "/api/interpretations",
        json={
            "framework_id": framework["id"],
            "interpretation_text": ROOM_SAID,
            "signifier_id": "nope",
        },
    )

    assert response.status_code == 400
    body = response.json()["error"]
    assert body["code"] == "unknown_signifier"
    assert body["action"]


def test_a_view_kind_the_app_does_not_draw_is_refused(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    response = client.post(
        "/api/interpretations",
        json={
            "framework_id": framework["id"],
            "interpretation_text": ROOM_SAID,
            "view_kind": "hologram",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unknown_view_kind"


def test_an_empty_conclusion_is_refused(client: TestClient) -> None:
    """Recording nothing would put a blank quotation under the landscape."""
    framework = build_golden_dataset(client)

    response = client.post(
        "/api/interpretations",
        json={"framework_id": framework["id"], "interpretation_text": "   "},
    )

    assert response.status_code == 422


def test_the_length_limits_hold(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    too_long = client.post(
        "/api/interpretations",
        json={
            "framework_id": framework["id"],
            "interpretation_text": "x" * (MAX_INTERPRETATION_CHARS + 1),
        },
    )
    assert too_long.status_code == 422

    long_label = client.post(
        "/api/interpretations",
        json={
            "framework_id": framework["id"],
            "interpretation_text": ROOM_SAID,
            "session_label": "x" * (MAX_SESSION_LABEL_CHARS + 1),
        },
    )
    assert long_label.status_code == 422


# --------------------------------------------------------------------------
# The Pattern Brief quotes it, and says whose words it is
# --------------------------------------------------------------------------


def brief(client: TestClient, framework_id: int, **params) -> str:
    response = client.get(
        "/api/export/brief", params={"framework_id": framework_id, **params}
    )
    assert response.status_code == 200, response.text
    return response.text


def test_the_brief_quotes_the_room_verbatim(client: TestClient) -> None:
    framework = build_golden_dataset(client)
    record(client, framework["id"])

    text = brief(client, framework["id"])

    assert ROOM_SAID in text
    assert "What the room made of it" in text


def test_the_brief_attributes_it_to_the_room_not_the_analyst(
    client: TestClient,
) -> None:
    """Delta §6 names this. A reader must not take it for a computed finding."""
    framework = build_golden_dataset(client)
    record(client, framework["id"])

    text = brief(client, framework["id"])
    section = text.split("What the room made of it")[1]

    assert "their words, not the analyst's" in section
    assert "form no part of it" in section
    assert "Ops night shift, 12 March" in section


def test_the_brief_keeps_the_figures_and_the_words_apart(
    client: TestClient,
) -> None:
    """Two headings, and the conclusion under neither one by accident.

    "What the figures say" is arithmetic; "What the room made of it" is
    judgement. A reader has to be able to tell which is which at a glance.
    """
    framework = build_golden_dataset(client)
    record(client, framework["id"])

    text = brief(client, framework["id"])
    figures = text.split("## What the figures say")[1].split("##")[0]

    assert ROOM_SAID not in figures


def test_a_brief_without_interpretations_is_unchanged(client: TestClient) -> None:
    """Nothing appears for a framework nobody has interpreted."""
    framework = build_golden_dataset(client)

    text = brief(client, framework["id"])

    assert "What the room made of it" not in text


def test_the_brief_is_otherwise_byte_identical(client: TestClient) -> None:
    """The section is added; nothing else in the document moves.

    Compared with the section cut out, so a stray change anywhere else in the
    brief shows up here rather than being masked by the new content.
    """
    framework = build_golden_dataset(client)
    before = brief(client, framework["id"])

    record(client, framework["id"])
    after = brief(client, framework["id"])
    without = (
        after.split("## What the room made of it")[0]
        + "## How to read this"
        + after.split("## How to read this")[1]
    )

    # The generated-at stamp is a date, so both were prepared the same day.
    assert without == before


def test_what_we_heard_does_not_carry_the_rooms_conclusions(
    client: TestClient,
) -> None:
    """The respondents' copy stays what it was.

    A conclusion drawn by nine people in a workshop is not something to hand
    back to everyone who told a story as though it were their own finding.
    """
    framework = build_golden_dataset(client)
    record(client, framework["id"])

    response = client.get(
        "/api/export/heard", params={"framework_id": framework["id"]}
    )

    assert ROOM_SAID not in response.text


def test_the_csv_does_not_gain_a_column_for_them(client: TestClient) -> None:
    """The dataset export is stories. An interpretation is not a story."""
    framework = build_golden_dataset(client)
    record(client, framework["id"])

    response = client.get("/api/export/csv", params={"framework_id": framework["id"]})

    assert ROOM_SAID not in response.text
    assert "interpretation" not in response.text.splitlines()[0].lower()


# --------------------------------------------------------------------------
# The projector view (delta §5)
# --------------------------------------------------------------------------


SESSION_JSX = (
    Path(__file__).resolve().parent.parent
    / "frontend"
    / "src"
    / "patterns"
    / "SessionMode.jsx"
)


def session_source() -> str:
    return SESSION_JSX.read_text(encoding="utf-8")


def test_the_projector_view_hides_the_controls() -> None:
    """Delta §5: "the landscape at full screen with controls hidden".

    Checked by absence: the filter rail, the sub-navigation and the export links
    are all things this component must not contain.
    """
    source = session_source()

    for control in ("nl-rail", "nl-patterns__views", "exportCsvUrl", "SUB_VIEWS"):
        assert control not in source, f"session mode still carries {control}"


def test_the_projector_view_is_keyboard_escapable() -> None:
    """Delta §6 names this. A view you cannot leave strands the facilitator."""
    source = session_source()

    assert 'event.key === "Escape"' in source
    assert "onClose()" in source
    # And the way out is written on the button, not left to be discovered.
    assert "Esc" in source


def test_the_projector_view_says_recording_changes_nothing() -> None:
    """The question a facilitator will silently be asking, answered on screen."""
    source = session_source()

    assert "does not change the landscape" in source
    assert "The landscape above is unchanged" in source


def test_the_session_view_captures_rather_than_asks_for_the_filters() -> None:
    """The filters come from the screen, not from a field somebody fills in."""
    source = session_source()

    assert "filter_state: filters" in source
    assert "signifier_id: triadId" in source


def test_the_room_list_quotes_and_never_counts() -> None:
    """Constraint 16 in the list: quoted, attributed, and not turned into a figure."""
    patterns = (
        Path(__file__).resolve().parent.parent
        / "frontend"
        / "src"
        / "patterns"
        / "Patterns.jsx"
    ).read_text(encoding="utf-8")
    rooms = patterns.split("function RoomsList")[1].split("\nfunction ")[0]

    assert "<blockquote" in rooms
    assert "forming no part of them" in rooms
    for arithmetic in ("reduce(", "average", "count +", "score"):
        assert arithmetic not in rooms, f"the room list computes something ({arithmetic})"


@pytest.mark.parametrize("field", ["session_label", "recorded_at", "filter_state"])
def test_the_list_shows_the_context_a_reader_needs(field: str) -> None:
    """A sentence about "this landscape" is worthless without the landscape."""
    patterns = (
        Path(__file__).resolve().parent.parent
        / "frontend"
        / "src"
        / "patterns"
        / "Patterns.jsx"
    ).read_text(encoding="utf-8")
    rooms = patterns.split("function RoomsList")[1].split("\nfunction ")[0]

    assert field in rooms
