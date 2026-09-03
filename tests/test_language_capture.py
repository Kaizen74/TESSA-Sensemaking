"""The original language is the record (delta §6, constraint 15).

Constraint 15 has two halves and this phase builds the first: a story carries
the language it was told in, and that tag travels with it. Phase F adds
read-time translation on top, and its guard — that deleting every cached
translation changes nothing — only means something if this half is right first.

Four promises are tested here:

* the language round-trips from every capture path;
* **absent reads as unknown, never as English** — assuming the majority language
  of whoever built the app is exactly how a multilingual dataset quietly becomes
  a monolingual one;
* Stage B receives the original text and nothing else, so nothing is ever
  signified in translation;
* a story's ``language_code`` changes no figure anywhere. It filters, and that
  is all it does.

The last one is the load-bearing test. A language tag that leaked into an
aggregate would mean the app had started computing on a property of the telling
rather than of the told, which is the failure constraint 15 exists to name.
"""

from __future__ import annotations

import csv
import io
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.languages import (
    BY_CODE,
    DEFAULT_LANGUAGE,
    KNOWN_LANGUAGES,
    LANGUAGE_SOURCE_RESPONDENT,
    LANGUAGE_SOURCE_UNKNOWN,
    UNKNOWN_LANGUAGE_LABEL,
    display_name,
    well_formed,
)
from backend.models import Anecdote
from tests.patterns_fixtures import GOLDEN_DEFINITION, build_golden_dataset
from tests.queue_fixtures import make_framework, proposed_import

#: A question set published in four languages, which is the case this phase is
#: for. The signifiers are the golden set's, so nothing about the maths changes.
MULTILINGUAL = {
    **GOLDEN_DEFINITION,
    "capture_settings": {
        **GOLDEN_DEFINITION["capture_settings"],
        "languages": ["en", "ms", "ta", "zh-Hans"],
    },
}

TAMIL_STORY = "எங்கள் கடைசி நேரத்தில் உதிரி பாகங்கள் வந்தன."
MALAY_STORY = "Alat ganti itu tiba tiga jam sebelum tarikh akhir."


def capture(client: TestClient, framework_id: int, **extra) -> dict:
    body = {
        "framework_id": framework_id,
        "text": "A shift where the plan and the work did not line up.",
        "significations": [],
        **extra,
    }
    response = client.post("/api/capture", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def stories(client: TestClient, framework_id: int, **params) -> list[dict]:
    response = client.get(f"/api/stories/{framework_id}", params=params)
    assert response.status_code == 200, response.text
    return response.json()["stories"]


def csv_rows(client: TestClient, framework_id: int, **params) -> list[dict]:
    response = client.get(
        "/api/export/csv", params={"framework_id": framework_id, **params}
    )
    assert response.status_code == 200, response.text
    return list(csv.DictReader(io.StringIO(response.text)))


# --------------------------------------------------------------------------
# The tag itself
# --------------------------------------------------------------------------


def test_a_well_formed_tag_is_accepted_and_free_text_is_not() -> None:
    """Shape, not a registry. An offline app cannot consult IANA."""
    for good in ("en", "ms", "ta", "zh-Hans", "pt-BR", "yue"):
        assert well_formed(good), good
    for bad in ("", "e", "not a language", "en;DROP", "x" * 40, "en_US"):
        assert not well_formed(bad), bad


def test_every_shipped_language_is_named_in_its_own_script() -> None:
    """A respondent scanning for their language looks for their word, not ours."""
    for language in KNOWN_LANGUAGES:
        assert language.code and language.english_name and language.endonym
        assert well_formed(language.code)

    assert BY_CODE["ta"].endonym == "தமிழ்"
    assert BY_CODE["zh-Hans"].endonym == "简体中文"


def test_an_unrecorded_language_reads_as_unknown_not_as_english() -> None:
    """The named guarantee of delta §6, at the one place it is decided."""
    assert display_name(None) == UNKNOWN_LANGUAGE_LABEL
    assert display_name("") == UNKNOWN_LANGUAGE_LABEL
    assert display_name(DEFAULT_LANGUAGE) != UNKNOWN_LANGUAGE_LABEL
    assert display_name("en") == "English"


def test_a_tag_the_app_does_not_know_shows_itself() -> None:
    """More use to a reader than nothing, and better than a wrong guess."""
    assert display_name("yue") == "yue"


# --------------------------------------------------------------------------
# It round-trips from every capture path
# --------------------------------------------------------------------------


@pytest.mark.parametrize("entry_mode", ("admin", "kiosk"))
def test_the_language_round_trips_from_the_local_paths(
    client: TestClient, entry_mode: str
) -> None:
    framework = make_framework(client, MULTILINGUAL)

    capture(client, framework["id"], entry_mode=entry_mode, language_code="ta")

    row = stories(client, framework["id"])[0]
    assert row["language_code"] == "ta"
    assert row["language_name"] == "Tamil"
    assert row["language_source"] == LANGUAGE_SOURCE_RESPONDENT


def test_the_language_round_trips_from_paper_entry(client: TestClient) -> None:
    framework = make_framework(client, MULTILINGUAL)

    capture(client, framework["id"], input_method="paper", language_code="ms")

    row = stories(client, framework["id"])[0]
    assert row["language_code"] == "ms"
    assert row["input_method"] == "paper"


def test_the_language_round_trips_from_a_capture_link(client: TestClient) -> None:
    framework = make_framework(client, MULTILINGUAL)
    token = client.post(
        "/api/capture-links", json={"framework_id": framework["id"]}
    ).json()["token"]

    submitted = client.post(
        f"/api/public/capture/{token}",
        json={"text": TAMIL_STORY, "significations": [], "language_code": "ta"},
    )
    assert submitted.status_code == 201, submitted.text

    row = stories(client, framework["id"])[0]
    assert row["language_code"] == "ta"
    assert row["entry_mode"] == "link"


def test_the_story_is_stored_in_its_own_script(client: TestClient) -> None:
    """The text is the record. Not transliterated, not normalised, not folded."""
    framework = make_framework(client, MULTILINGUAL)

    capture(client, framework["id"], text=TAMIL_STORY, language_code="ta")

    assert stories(client, framework["id"])[0]["text"] == TAMIL_STORY


# --------------------------------------------------------------------------
# Absent is absent
# --------------------------------------------------------------------------


def test_a_story_with_no_language_reads_as_unknown(client: TestClient) -> None:
    framework = make_framework(client, MULTILINGUAL)

    capture(client, framework["id"])

    row = stories(client, framework["id"])[0]
    assert row["language_code"] is None
    assert row["language_name"] == UNKNOWN_LANGUAGE_LABEL
    assert row["language_source"] == LANGUAGE_SOURCE_UNKNOWN


def test_an_imported_story_does_not_acquire_a_language(client: TestClient) -> None:
    """Nobody asked the person who wrote it, so the app does not guess."""
    framework = make_framework(client)
    proposed_import(client, framework["id"])
    items = client.get("/api/queue").json()["items"]
    client.put(f"/api/queue/{items[0]['anecdote_id']}", json={"action": "accept"})

    row = stories(client, framework["id"])[0]
    assert row["language_code"] is None
    assert row["language_name"] == UNKNOWN_LANGUAGE_LABEL


def test_a_single_language_question_set_needs_no_choice(client: TestClient) -> None:
    """English alone by default, so nothing changes for an existing framework."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    definition = client.get(f"/api/frameworks/{framework['id']}").json()["definition"]

    assert definition["capture_settings"]["languages"] == []

    capture(client, framework["id"])
    assert stories(client, framework["id"])[0]["language_code"] is None


def test_a_language_the_question_set_does_not_offer_is_refused(
    client: TestClient,
) -> None:
    """A browser cannot make a claim about the story nobody made."""
    framework = make_framework(client, MULTILINGUAL)

    response = client.post(
        "/api/capture",
        json={"framework_id": framework["id"], "text": "x", "significations": [],
              "language_code": "fr"},
    )

    assert response.status_code == 400
    body = response.json()["error"]
    assert body["code"] == "unknown_language"
    assert body["action"]


def test_a_framework_cannot_be_published_in_a_non_language(client: TestClient) -> None:
    broken = {**GOLDEN_DEFINITION, "capture_settings": {"languages": ["Bahasa Melayu"]}}

    response = client.post(
        "/api/frameworks", json={"name": "Broken", "definition": broken}
    )

    assert response.status_code == 422


def test_a_language_cannot_be_listed_twice(client: TestClient) -> None:
    broken = {**GOLDEN_DEFINITION, "capture_settings": {"languages": ["en", "EN"]}}

    response = client.post(
        "/api/frameworks", json={"name": "Broken", "definition": broken}
    )

    assert response.status_code == 422


# --------------------------------------------------------------------------
# Stage B receives the original text only (constraint 15)
# --------------------------------------------------------------------------


def test_stage_b_is_given_the_story_as_told_and_no_language_hint(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nothing is ever signified in translation, so nothing translated is sent.

    Intercepts the one function that talks to the network and reads what it was
    actually handed: the story text, and no translation of it.
    """
    from backend import ai_client
    from tests.queue_fixtures import confirmed_import

    framework = make_framework(client)
    # Stage A runs on the mock as usual — it is not what this test is about, and
    # intercepting it would only mean writing a second fake reply. The fake goes
    # in immediately before Stage B, which is the call that sees story text.
    job = confirmed_import(client)

    seen: list[list[dict[str, str]]] = []
    expected = job["confirmation"]["candidate_count"]

    def capture_call(system: str, messages: list[dict[str, str]]) -> str:
        seen.append(messages)
        # A well-formed reply with no placements. Stage B rightly refuses a
        # reply that skips a story, and a 502 here would prove nothing about
        # what was sent — which is the only thing this test is asking.
        return json.dumps(
            {"stories": [{"index": i, "placements": []} for i in range(expected)]}
        )

    monkeypatch.setattr(ai_client, "_live_text", capture_call)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.setenv(ai_client.API_KEY_ENV_VAR, "test-key")

    proposed = client.post(
        f"/api/import/{job['id']}/propose", json={"framework_id": framework["id"]}
    )
    assert proposed.status_code == 200, proposed.text

    everything = json.dumps(seen)
    assert everything, "Stage B was never called"
    # The prompt talks about stories and questions; it must not talk about
    # translating them, or carry a language instruction.
    for banned in ("translat", "in English", "language_code"):
        assert banned not in everything, f"Stage B was sent {banned}"


def test_the_stage_b_prompt_module_cannot_reach_a_translation() -> None:
    """Structural: there is no route from the propose path to a translation."""
    from pathlib import Path

    source = (
        Path(__file__).resolve().parent.parent / "backend" / "propose.py"
    ).read_text(encoding="utf-8")

    for banned in ("translat", "language_code"):
        assert banned not in source, f"backend/propose.py mentions {banned}"


# --------------------------------------------------------------------------
# The language changes no figure — the load-bearing guard
# --------------------------------------------------------------------------


def serialise(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, indent=2)


def test_a_language_tag_changes_no_figure_anywhere(
    client: TestClient, session: Session
) -> None:
    """Constraint 15: never used to compute anything.

    The same twenty stories, once with no language and once with every one of
    them tagged. Every figure the app draws must be identical — the tag is a
    fact about the telling, and the arithmetic is about what was told.
    """
    framework = build_golden_dataset(client)
    fid = framework["id"]
    views = {
        "patterns": f"/api/patterns/{fid}",
        "landscape": f"/api/landscape/{fid}/t1",
        "explorer": f"/api/explorer/{fid}",
        "clusters": f"/api/clusters/{fid}",
        "quality": f"/api/quality/{fid}",
    }
    before = {name: serialise(client.get(path).json()) for name, path in views.items()}

    # Tag every story, directly, so no capture-path difference can explain it.
    for index, row in enumerate(session.scalars(select_anecdotes()).all()):
        row.language_code = ("ta", "ms", "zh-Hans")[index % 3]
        row.language_source = LANGUAGE_SOURCE_RESPONDENT
    session.commit()

    for name, path in views.items():
        assert serialise(client.get(path).json()) == before[name], name


def select_anecdotes():
    from sqlalchemy import select

    return select(Anecdote)


def test_the_supporting_charts_gained_no_fifth_breakdown(client: TestClient) -> None:
    """Language filters; it is not a demographic chart.

    Adding it to the breakdowns would move ``patterns_20_anecdotes.json``, and
    §7 acceptance 13 requires every pre-delta golden to stay byte-identical. The
    filter rail offers language from the question set's published list instead.
    """
    framework = build_golden_dataset(client)

    view = client.get(f"/api/patterns/{framework['id']}").json()

    assert len(view["demographics"]) == 4
    assert "language_code" not in [chart["id"] for chart in view["demographics"]]


# --------------------------------------------------------------------------
# It filters, and that is what it is for
# --------------------------------------------------------------------------


def test_filtering_by_language_narrows_the_view(client: TestClient) -> None:
    framework = make_framework(client, MULTILINGUAL)
    capture(client, framework["id"], text=TAMIL_STORY, language_code="ta")
    capture(client, framework["id"], text=MALAY_STORY, language_code="ms")
    capture(client, framework["id"], language_code="ms")

    tamil = client.get(
        f"/api/patterns/{framework['id']}", params={"language_code": "ta"}
    ).json()
    malay = client.get(
        f"/api/patterns/{framework['id']}", params={"language_code": "ms"}
    ).json()

    assert tamil["total"] == 1
    assert malay["total"] == 2
    assert tamil["filters"] == {"language_code": "ta"}


@pytest.mark.parametrize(
    "path", ["/api/patterns/{id}", "/api/quality/{id}", "/api/stories/{id}"]
)
def test_every_filtered_view_takes_the_language(client: TestClient, path: str) -> None:
    """One filter, applied the same way everywhere (delta §6: added to FILTERABLE)."""
    framework = make_framework(client, MULTILINGUAL)
    capture(client, framework["id"], language_code="ta")
    capture(client, framework["id"], language_code="ms")

    response = client.get(
        path.format(id=framework["id"]), params={"language_code": "ta"}
    )

    assert response.status_code == 200, response.text
    assert response.json()["filters"] == {"language_code": "ta"}


def test_the_landscape_can_be_split_by_language(client: TestClient) -> None:
    """It is in FILTERABLE, so it is a split like any other story field."""
    framework = make_framework(client, MULTILINGUAL)
    for code in ("ta", "ta", "ms"):
        capture(
            client,
            framework["id"],
            language_code=code,
            significations=[
                {"signifier_id": "t1", "value": {"Speed": 0.5, "Care": 0.3, "Cost": 0.2}}
            ],
        )

    response = client.get(
        f"/api/landscape/{framework['id']}/t1", params={"split_by": "language_code"}
    )

    assert response.status_code == 200, response.text
    panels = response.json()["panels"]
    assert {panel["panel"] for panel in panels} == {"ms", "ta"}


def test_the_csv_carries_the_language_and_how_it_was_known(
    client: TestClient,
) -> None:
    framework = make_framework(client, MULTILINGUAL)
    capture(client, framework["id"], language_code="ta")
    capture(client, framework["id"])

    rows = csv_rows(client, framework["id"])
    by_language = {row["language_code"]: row for row in rows}

    assert set(by_language) == {"ta", ""}
    assert by_language["ta"]["language_source"] == LANGUAGE_SOURCE_RESPONDENT
    assert by_language[""]["language_source"] == LANGUAGE_SOURCE_UNKNOWN


def test_the_csv_export_honours_the_language_filter(client: TestClient) -> None:
    framework = make_framework(client, MULTILINGUAL)
    capture(client, framework["id"], language_code="ta")
    capture(client, framework["id"], language_code="ms")

    rows = csv_rows(client, framework["id"], language_code="ta")

    assert len(rows) == 1
    assert rows[0]["language_code"] == "ta"


def test_the_studio_can_read_the_languages_it_may_offer(client: TestClient) -> None:
    response = client.get("/api/frameworks/languages")

    assert response.status_code == 200, response.text
    offered = response.json()
    assert {entry["code"] for entry in offered} >= {"en", "ms", "ta", "zh-Hans"}
    assert all(entry["endonym"] for entry in offered)
