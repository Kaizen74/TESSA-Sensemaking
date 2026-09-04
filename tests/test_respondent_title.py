"""The name a storyteller gives their own story (delta §6, items 2 and 5).

A machine title is a convenience: the first eighty characters of the text, so a
list of stories is readable. A name somebody chose for their own story is
something else — it is the shortest thing they said about what happened, and it
is testimony. This file holds the line between the two.

Four things are checked, in this order: it arrives from every way in; it is
preferred when it exists and absent when it does not; it never overwrites the
machine title; and the length is a limit rather than a suggestion.

The paper card is here too, because a field that exists on screen and not on the
page would make the two capture routes different questions.
"""

from __future__ import annotations

import csv
import io

import pytest
from fastapi.testclient import TestClient

from backend.capture_schema import MAX_RESPONDENT_TITLE_CHARS
from backend.paper_pack import STORY_NAME_PROMPT
from tests.queue_fixtures import FULL_DEFINITION, make_framework

NAME = "The morning the parts finally came"

STORY = (
    "We were three hours from the deadline when the parts finally arrived, and "
    "nobody had told the night shift they were coming."
)


def capture(client: TestClient, framework_id: int, **extra) -> dict:
    body = {"framework_id": framework_id, "text": STORY, "significations": [], **extra}
    response = client.post("/api/capture", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def stored(client: TestClient, framework_id: int) -> list[dict]:
    response = client.get(f"/api/stories/{framework_id}")
    assert response.status_code == 200, response.text
    return response.json()["stories"]


def link_for(client: TestClient, framework_id: int) -> str:
    created = client.post("/api/capture-links", json={"framework_id": framework_id})
    assert created.status_code == 201, created.text
    return created.json()["token"]


# --------------------------------------------------------------------------
# It arrives from every way in
# --------------------------------------------------------------------------


@pytest.mark.parametrize("entry_mode", ("admin", "kiosk"))
def test_the_name_round_trips_from_the_local_paths(
    client: TestClient, entry_mode: str
) -> None:
    """Admin capture and kiosk — the wizard on the operator's own machine."""
    framework = make_framework(client)

    capture(
        client, framework["id"], entry_mode=entry_mode, respondent_title=NAME
    )

    assert stored(client, framework["id"])[0]["respondent_title"] == NAME


def test_the_name_round_trips_from_paper_entry(client: TestClient) -> None:
    """The card's name line, typed in by whoever is entering the pile."""
    framework = make_framework(client)

    capture(client, framework["id"], input_method="paper", respondent_title=NAME)

    row = stored(client, framework["id"])[0]
    assert row["respondent_title"] == NAME
    assert row["input_method"] == "paper"


def test_the_name_round_trips_from_a_capture_link(client: TestClient) -> None:
    """The remote path, where the token decides everything the browser cannot."""
    framework = make_framework(client)
    token = link_for(client, framework["id"])

    submitted = client.post(
        f"/api/public/capture/{token}",
        json={"text": STORY, "significations": [], "respondent_title": NAME},
    )
    assert submitted.status_code == 201, submitted.text

    row = stored(client, framework["id"])[0]
    assert row["respondent_title"] == NAME
    assert row["entry_mode"] == "link"


# --------------------------------------------------------------------------
# Preferred when it exists, absent when it does not
# --------------------------------------------------------------------------


def test_the_displayed_title_is_the_storytellers_when_they_gave_one(
    client: TestClient,
) -> None:
    framework = make_framework(client)

    capture(client, framework["id"], respondent_title=NAME)

    assert stored(client, framework["id"])[0]["title"] == NAME


def test_the_display_falls_back_to_the_machine_title(client: TestClient) -> None:
    """No name given is the ordinary case, and it must read as a story anyway."""
    framework = make_framework(client)

    capture(client, framework["id"])

    row = stored(client, framework["id"])[0]
    assert row["respondent_title"] is None
    assert row["title"].startswith("We were three hours")


def test_an_empty_box_is_not_a_name(client: TestClient) -> None:
    """A skipped field submits as blank; blank is no name, not a name of "".

    Otherwise the display rule would prefer an empty string over the machine
    title and every skipped field would produce a story with no title at all.
    """
    framework = make_framework(client)

    capture(client, framework["id"], respondent_title="   ")

    row = stored(client, framework["id"])[0]
    assert row["respondent_title"] is None
    assert row["title"].startswith("We were three hours")


def test_a_named_story_is_findable_by_its_name(client: TestClient) -> None:
    """The one title a person chose is the one the search box must see."""
    framework = make_framework(client)
    capture(client, framework["id"], respondent_title=NAME)
    capture(client, framework["id"], text="A different shift entirely.")

    found = client.get(f"/api/stories/{framework['id']}", params={"q": "parts finally came"})

    assert found.status_code == 200, found.text
    assert found.json()["matched"] == 1


# --------------------------------------------------------------------------
# It never overwrites the machine title
# --------------------------------------------------------------------------


def test_the_machine_title_is_kept_beside_it_not_replaced(client: TestClient) -> None:
    """Both are retained (delta §3), and the CSV is where that is checkable."""
    framework = make_framework(client)
    capture(client, framework["id"], respondent_title=NAME)

    response = client.get("/api/export/csv", params={"framework_id": framework["id"]})
    row = next(iter(csv.DictReader(io.StringIO(response.text))))

    assert row["respondent_title"] == NAME
    assert row["title"].startswith("We were three hours")
    assert row["title"] != row["respondent_title"]


def test_the_csv_carries_both_columns_even_when_nobody_named_it(
    client: TestClient,
) -> None:
    framework = make_framework(client)
    capture(client, framework["id"])

    response = client.get("/api/export/csv", params={"framework_id": framework["id"]})
    reader = csv.DictReader(io.StringIO(response.text))
    row = next(iter(reader))

    assert "respondent_title" in (reader.fieldnames or [])
    assert row["respondent_title"] == ""
    assert row["title"]


# --------------------------------------------------------------------------
# The limit is a limit
# --------------------------------------------------------------------------


def test_a_name_at_the_limit_is_accepted(client: TestClient) -> None:
    framework = make_framework(client)

    capture(client, framework["id"], respondent_title="x" * MAX_RESPONDENT_TITLE_CHARS)

    title = stored(client, framework["id"])[0]["respondent_title"]
    assert len(title) == MAX_RESPONDENT_TITLE_CHARS


def test_a_name_over_the_limit_is_refused(client: TestClient) -> None:
    """The field must not quietly become a second story box."""
    framework = make_framework(client)

    response = client.post(
        "/api/capture",
        json={
            "framework_id": framework["id"],
            "text": STORY,
            "significations": [],
            "respondent_title": "x" * (MAX_RESPONDENT_TITLE_CHARS + 1),
        },
    )

    assert response.status_code == 422


def test_the_limit_holds_on_the_public_path_too(client: TestClient) -> None:
    """A respondent's browser gets no more latitude than the operator's."""
    framework = make_framework(client)
    token = link_for(client, framework["id"])

    response = client.post(
        f"/api/public/capture/{token}",
        json={
            "text": STORY,
            "significations": [],
            "respondent_title": "x" * (MAX_RESPONDENT_TITLE_CHARS + 1),
        },
    )

    assert response.status_code == 422


# --------------------------------------------------------------------------
# The paper card asks the same question
# --------------------------------------------------------------------------


def test_the_paper_story_card_carries_the_name_line(client: TestClient) -> None:
    framework = make_framework(client, FULL_DEFINITION)

    pack = client.get(f"/api/frameworks/{framework['id']}/paper-pack")

    assert pack.status_code == 200, pack.text
    assert STORY_NAME_PROMPT in pack.text


def test_the_name_line_is_on_the_story_card_and_not_a_sheet_of_its_own(
    client: TestClient,
) -> None:
    """Constraint 10 in print: the card is one page, and this does not add one."""
    framework = make_framework(client, FULL_DEFINITION)

    body = client.get(f"/api/frameworks/{framework['id']}/paper-pack").text
    card = body.split('data-sheet="story-card"')[1].split("</section>")[0]

    assert STORY_NAME_PROMPT in card
    assert body.count(STORY_NAME_PROMPT) == 1


def test_the_screen_and_the_card_ask_it_in_the_same_words() -> None:
    """One question, one wording, wherever somebody meets it.

    The frontend holds its own copy — it cannot import Python — so this is the
    assertion that keeps the two from drifting apart.
    """
    source = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parent.parent.joinpath("frontend/src/capture/Wizard.jsx")
        .read_text(encoding="utf-8")
    )

    assert f'"{STORY_NAME_PROMPT}"' in source
    assert f"MAX_RESPONDENT_TITLE_CHARS = {MAX_RESPONDENT_TITLE_CHARS}" in source
