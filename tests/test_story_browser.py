"""The story browser (PRD §1.6, §5.4).

The last item of §1's scope, and the one PRD §6 never gave a phase. It is the
end of the reading path: the landscape says where stories gather, the browser
says which stories they are, and "export selected" carries a chosen few out with
their provenance intact.

What is tested here is mostly what it must *not* do — read anything a person has
not validated, leak an identifier it does not have, or let a selection quietly
become a different export.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.stories import PAGE_SIZE, STAR_TAG
from tests.patterns_fixtures import GOLDEN_DEFINITION, build_golden_dataset
from tests.queue_fixtures import make_framework, proposed_import


def _browse(client: TestClient, framework_id: int, **params) -> dict:
    response = client.get(f"/api/stories/{framework_id}", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def _mark(client: TestClient, anecdote_id: int, **body) -> dict:
    response = client.put(f"/api/stories/{anecdote_id}/marks", json=body)
    assert response.status_code == 200, response.text
    return response.json()


# --------------------------------------------------------------------------
# Listing and searching
# --------------------------------------------------------------------------


def test_the_browser_lists_the_stories_in_scope(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    page = _browse(client, framework["id"])

    assert page["total"] == 20
    assert page["matched"] == 20
    assert len(page["stories"]) == 20
    assert page["stories"][0]["text"]


def test_search_narrows_to_every_word(client: TestClient) -> None:
    """Two words means both, not either — the useful reading of a search box."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    for text in (
        "The compressor failed on the night shift and nobody had the key.",
        "The compressor was fine; the paperwork was the problem.",
        "A quiet week on the day shift.",
    ):
        client.post(
            "/api/capture",
            json={"framework_id": framework["id"], "text": text, "significations": []},
        )

    assert _browse(client, framework["id"], q="compressor")["matched"] == 2
    assert _browse(client, framework["id"], q="compressor shift")["matched"] == 1
    assert _browse(client, framework["id"], q="COMPRESSOR")["matched"] == 2
    assert _browse(client, framework["id"], q="submarine")["matched"] == 0


def test_the_search_reports_both_numbers(client: TestClient) -> None:
    """"3 of 20" — a reader who sees only the 3 does not know what they are in."""
    framework = build_golden_dataset(client)

    page = _browse(client, framework["id"], q="Story 07")

    assert page["matched"] == 1
    assert page["total"] == 20
    assert page["query"] == "Story 07"


def test_a_filter_narrows_the_browser_the_same_way_it_narrows_the_charts(
    client: TestClient,
) -> None:
    framework = build_golden_dataset(client)

    page = _browse(client, framework["id"], respondent_group="Ops")

    assert page["matched"] == 7
    assert {story["respondent_group"] for story in page["stories"]} == {"Ops"}


def test_long_lists_are_paged(client: TestClient) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)
    for index in range(PAGE_SIZE + 5):
        client.post(
            "/api/capture",
            json={
                "framework_id": framework["id"],
                "text": f"Story number {index}, about a shift that did not go to plan.",
                "significations": [],
            },
        )

    first = _browse(client, framework["id"])
    second = _browse(client, framework["id"], offset=PAGE_SIZE)

    assert first["matched"] == PAGE_SIZE + 5
    assert len(first["stories"]) == PAGE_SIZE
    assert len(second["stories"]) == 5
    ids = {s["anecdote_id"] for s in first["stories"]} & {
        s["anecdote_id"] for s in second["stories"]
    }
    assert ids == set(), "a story appeared on two pages"


def test_the_browser_never_shows_a_story_nobody_validated(client: TestClient) -> None:
    """Constraint 1, on the reading side. The queue is where pending lives."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    proposed_import(client, framework["id"])

    page = _browse(client, framework["id"])

    assert page["total"] == 0
    assert page["stories"] == []
    # And the stories genuinely exist — they are waiting, not missing.
    assert client.get("/api/queue").json()["counts"]["pending"] > 0


def test_the_browser_carries_provenance_and_no_identifier(client: TestClient) -> None:
    """Constraint 3 shown, constraint 9 absent — the same as every other view."""
    framework = build_golden_dataset(client)

    story = _browse(client, framework["id"])["stories"][0]

    assert story["input_method"] in {"typed", "paper", "voice", "imported"}
    assert story["entry_mode"] in {"admin", "link", "kiosk"}
    assert story["created_at_hour"].endswith("00:00")
    for leak in ("ip", "user_agent", "email", "name", "fingerprint"):
        assert leak not in story, leak


# --------------------------------------------------------------------------
# Tagging and starring
# --------------------------------------------------------------------------


def test_a_story_can_be_starred_and_unstarred(client: TestClient) -> None:
    framework = build_golden_dataset(client)
    story = _browse(client, framework["id"])["stories"][0]

    assert _mark(client, story["anecdote_id"], starred=True)["starred"] is True
    assert _mark(client, story["anecdote_id"], starred=False)["starred"] is False


def test_tags_are_replaced_by_what_the_screen_sends(client: TestClient) -> None:
    framework = build_golden_dataset(client)
    story = _browse(client, framework["id"])["stories"][0]

    _mark(client, story["anecdote_id"], tags=["handover", "night shift"])
    assert _mark(client, story["anecdote_id"], tags=["handover"])["tags"] == ["handover"]


def test_starring_and_tagging_do_not_disturb_each_other(client: TestClient) -> None:
    """They share a table, so this is the join worth testing."""
    framework = build_golden_dataset(client)
    story = _browse(client, framework["id"])["stories"][0]

    _mark(client, story["anecdote_id"], starred=True)
    after = _mark(client, story["anecdote_id"], tags=["handover"])

    assert after["starred"] is True
    assert after["tags"] == ["handover"]

    unstarred = _mark(client, story["anecdote_id"], starred=False)
    assert unstarred["tags"] == ["handover"]


def test_the_reserved_star_word_cannot_be_typed_as_a_tag(client: TestClient) -> None:
    framework = build_golden_dataset(client)
    story = _browse(client, framework["id"])["stories"][0]

    response = client.put(
        f"/api/stories/{story['anecdote_id']}/marks", json={"tags": [STAR_TAG]}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "reserved_tag"


def test_the_browser_can_be_narrowed_to_stars_and_tags(client: TestClient) -> None:
    framework = build_golden_dataset(client)
    listed = _browse(client, framework["id"])["stories"]
    _mark(client, listed[0]["anecdote_id"], starred=True, tags=["handover"])
    _mark(client, listed[1]["anecdote_id"], tags=["handover"])

    assert _browse(client, framework["id"], starred=True)["matched"] == 1
    assert _browse(client, framework["id"], tag="handover")["matched"] == 2
    assert _browse(client, framework["id"], tag="handover", starred=True)["matched"] == 1
    assert _browse(client, framework["id"])["known_tags"] == ["handover"]


def test_the_star_is_never_listed_as_a_tag(client: TestClient) -> None:
    """It is stored as one, which is exactly why this is worth asserting."""
    framework = build_golden_dataset(client)
    story = _browse(client, framework["id"])["stories"][0]

    marked = _mark(client, story["anecdote_id"], starred=True)

    assert marked["tags"] == []
    assert STAR_TAG not in _browse(client, framework["id"])["known_tags"]


def test_marking_a_story_that_is_not_there_says_so_plainly(client: TestClient) -> None:
    response = client.put("/api/stories/9999/marks", json={"starred": True})

    assert response.status_code == 404
    error = response.json()["error"]
    assert "no story numbered 9999" in error["message"]
    assert error["action"]


# --------------------------------------------------------------------------
# Export selected (PRD §1.7)
# --------------------------------------------------------------------------


def test_a_selection_exports_only_those_stories(client: TestClient) -> None:
    framework = build_golden_dataset(client)
    listed = _browse(client, framework["id"])["stories"]
    chosen = [listed[0]["anecdote_id"], listed[3]["anecdote_id"]]

    response = client.get(
        "/api/export/csv",
        params={"framework_id": framework["id"], "ids": ",".join(str(i) for i in chosen)},
    )

    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    assert len(lines) == 3, "header plus the two chosen stories"
    assert "selected-stories.csv" in response.headers["content-disposition"]


def test_a_selected_export_carries_the_same_provenance(client: TestClient) -> None:
    """One code path, so a selection cannot become a thinner kind of export."""
    framework = build_golden_dataset(client)
    story = _browse(client, framework["id"])["stories"][0]

    whole = client.get("/api/export/csv", params={"framework_id": framework["id"]})
    selected = client.get(
        "/api/export/csv",
        params={"framework_id": framework["id"], "ids": str(story["anecdote_id"])},
    )

    assert selected.text.splitlines()[0] == whole.text.splitlines()[0]


def test_an_unreadable_selection_is_refused_in_plain_english(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    response = client.get(
        "/api/export/csv", params={"framework_id": framework["id"], "ids": "one,two"}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unreadable_selection"


def test_a_wildcard_in_the_search_box_is_just_a_character(client: TestClient) -> None:
    """"50%" is a thing people write in stories, not a pattern to match with."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    for text in (
        "We came in at a 50% overrun and nobody flagged it.",
        "The shift_notes file was the only record anyone kept.",
        "A quiet week with nothing unusual in it.",
    ):
        client.post(
            "/api/capture",
            json={"framework_id": framework["id"], "text": text, "significations": []},
        )

    assert _browse(client, framework["id"], q="50%")["matched"] == 1
    assert _browse(client, framework["id"], q="shift_notes")["matched"] == 1
    # And the wildcards do not quietly match everything.
    assert _browse(client, framework["id"], q="%")["matched"] == 1
    assert _browse(client, framework["id"], q="_")["matched"] == 1
