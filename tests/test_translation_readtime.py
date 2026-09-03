"""Read-time translation, display-only (delta §6, constraint 15).

The second half of constraint 15, and the half where the first half could
quietly be broken. A translation is a machine's reading of somebody's words. The
moment it becomes the story — stored in ``anecdotes.text``, sent to Stage B,
counted in an aggregate — the app has started computing on a reading nobody
gave it, which is exactly what "a translated text is never signified by anyone"
forbids.

The central test is therefore an equivalence, and it is deliberately blunt:
**delete every cached translation and every figure the app draws is
byte-identical.** Patterns, landscape, explorer, clusters, quality, and all
three exports. If a cache row can change a number, it has stopped being a cache
and become the record.

Around that sit the other four promises: the translated text never reaches
``anecdotes``; no aggregation or Stage B path can even read the table; the UI
cannot render a translation without its label; and an offline failure leaves the
original readable, which is the text that mattered anyway.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend import ai_client
from backend import translate as translate_module
from backend.ai_client import AiError
from backend.models import Anecdote, Translation
from backend.translate import MOCK_PATH, TRANSLATE_SYSTEM, TranslationReply, translate_prompt
from tests.patterns_fixtures import GOLDEN_DEFINITION, build_golden_dataset
from tests.queue_fixtures import make_framework

MULTILINGUAL = {
    **GOLDEN_DEFINITION,
    "capture_settings": {
        **GOLDEN_DEFINITION["capture_settings"],
        "languages": ["en", "ms", "ta"],
    },
}

TAMIL_STORY = "எங்கள் கடைசி நேரத்தில் உதிரி பாகங்கள் வந்தன."


def capture(client: TestClient, framework_id: int, **extra) -> int:
    body = {
        "framework_id": framework_id,
        "text": TAMIL_STORY,
        "language_code": "ta",
        "significations": [],
        **extra,
    }
    response = client.post("/api/capture", json=body)
    assert response.status_code == 201, response.text
    return response.json()["anecdote_id"]


def translate(client: TestClient, anecdote_id: int, target: str = "en") -> dict:
    response = client.get(
        f"/api/stories/{anecdote_id}/translation", params={"target": target}
    )
    assert response.status_code == 200, response.text
    return response.json()


def serialise(payload) -> str:
    return json.dumps(payload, sort_keys=True, indent=2)


# --------------------------------------------------------------------------
# The cache-deletion equivalence guard (delta §6, the named one)
# --------------------------------------------------------------------------


def test_deleting_every_cached_row_changes_nothing_but_speed(
    client: TestClient, session: Session
) -> None:
    """The whole specification of this table, as a test.

    Twenty stories, every one of them translated and cached, then the cache
    wiped. Every figure the app draws must come back character for character
    identical — because a cache that can move a number is not a cache.
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
    exports = {
        "csv": f"/api/export/csv?framework_id={fid}",
        "brief": f"/api/export/brief?framework_id={fid}",
        "heard": f"/api/export/heard?framework_id={fid}",
    }

    # Cache a translation for every story. The golden set is English, so the
    # rows are made directly — the point is that rows exist, not how.
    for row in session.scalars(select(Anecdote)).all():
        session.add(
            Translation(
                anecdote_id=row.id,
                target_language_code="ta",
                translated_text="ஒரு மொழிபெயர்ப்பு.",
                model_used="test-model",
            )
        )
    session.commit()
    cached_count = len(session.scalars(select(Translation)).all())
    assert cached_count == 20, cached_count

    with_cache = {name: serialise(client.get(p).json()) for name, p in views.items()}
    with_cache.update({name: client.get(p).text for name, p in exports.items()})

    session.execute(delete(Translation))
    session.commit()
    assert session.scalars(select(Translation)).all() == []

    for name, path in views.items():
        assert serialise(client.get(path).json()) == with_cache[name], name
    for name, path in exports.items():
        assert client.get(path).text == with_cache[name], name


def test_the_story_browser_is_unmoved_by_the_cache_too(
    client: TestClient, session: Session
) -> None:
    """The browser reads stories; a translation is not one."""
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])

    before = serialise(client.get(f"/api/stories/{framework['id']}").json())
    translate(client, anecdote_id)
    after = serialise(client.get(f"/api/stories/{framework['id']}").json())

    assert after == before
    assert session.scalars(select(Translation)).all(), "nothing was cached at all"


# --------------------------------------------------------------------------
# The translation is never the story
# --------------------------------------------------------------------------


def test_the_translated_text_is_never_stored_in_anecdotes(
    client: TestClient, session: Session
) -> None:
    """``anecdotes.text`` is the record and stays exactly as it was told."""
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])

    reply = translate(client, anecdote_id)
    session.expire_all()
    row = session.get(Anecdote, anecdote_id)

    assert row.text == TAMIL_STORY
    assert row.text != reply["translated_text"]
    assert reply["translated_text"] not in json.dumps(
        {
            "text": row.text,
            "title_auto": row.title_auto,
            "respondent_title": row.respondent_title,
        }
    )


def test_the_language_of_record_does_not_change(
    client: TestClient, session: Session
) -> None:
    """Translating into English does not make the story an English story."""
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])

    translate(client, anecdote_id)
    session.expire_all()

    assert session.get(Anecdote, anecdote_id).language_code == "ta"


def test_no_signification_is_created_by_translating(
    client: TestClient, session: Session
) -> None:
    """"A translated text is never signified by anyone" (constraint 15)."""
    from backend.models import Signification

    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])
    before = len(session.scalars(select(Signification)).all())

    translate(client, anecdote_id)
    session.expire_all()

    assert len(session.scalars(select(Signification)).all()) == before


# --------------------------------------------------------------------------
# Nothing that computes can even read the table
# --------------------------------------------------------------------------


BACKEND = Path(__file__).resolve().parent.parent / "backend"

#: Every module that produces a figure, an export of record, or a Stage B input.
COMPUTING_MODULES = (
    "patterns.py",
    "landscape.py",
    "clusters.py",
    "quality.py",
    "exports.py",
    "dataset.py",
    "propose.py",
    "organise.py",
    "barycentric.py",
    "routers/patterns.py",
    "routers/landscape.py",
    "routers/quality.py",
    "routers/exports.py",
)


@pytest.mark.parametrize("name", COMPUTING_MODULES)
def test_no_computing_module_can_reach_the_cache(name: str) -> None:
    """Structural, not behavioural.

    The equivalence test above proves no cached row *did* change a figure on
    that fixture. This proves none *could*: there is no import of the table into
    any module that computes, exports of record, or feeds Stage B.
    """
    code = code_of(BACKEND / name)

    assert "Translation" not in code, f"backend/{name} reaches the Translation model"
    assert "translations" not in code, f"backend/{name} reaches the translations table"


def code_of(path: Path) -> str:
    """A module's code with its docstrings and comments taken out.

    These assertions are about what a module can *reach*, and prose describing
    a rule must not be mistaken for breaking it — otherwise a module could pass
    the test by not explaining itself.

    Only *docstrings* are removed, never every string. Blanking all string
    constants would also blind this to a literal like ``"translations"`` used as
    a column name, which is exactly the kind of reach it exists to catch —
    ``ast.unparse`` drops comments on its own.
    """
    import ast

    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(
            node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
        ):
            continue
        body = getattr(node, "body", [])
        first = body[0] if body else None
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            first.value.value = ""
    return ast.unparse(tree)


def test_the_translate_module_cannot_reach_a_signification() -> None:
    """And the traffic does not flow the other way either."""
    code = code_of(BACKEND / "translate.py")

    for banned in ("Signification", "propose", "aggregate", "PatternSet"):
        assert banned not in code, f"backend/translate.py reaches {banned}"


def test_stage_b_is_not_given_a_translation(
    client: TestClient, session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A cached translation exists; the prompt still carries the original.

    The order matters: the story is translated *first*, so there is something
    for Stage B to have picked up had the paths been connected.
    """
    from tests.queue_fixtures import confirmed_import

    framework = make_framework(client, MULTILINGUAL)
    # A story that exists, in Tamil, with an English translation already cached.
    # Stage B then runs over an imported file while that cache sits in the
    # database — which is the shape the risk actually takes.
    anecdote_id = capture(client, framework["id"])
    translated = translate(client, anecdote_id)["translated_text"]
    assert session.scalars(select(Translation)).all(), "nothing was cached"

    job = confirmed_import(client)

    seen: list[list[dict[str, str]]] = []

    def capture_call(system: str, messages: list[dict[str, str]]) -> str:
        seen.append(messages)
        return json.dumps(
            {
                "stories": [
                    {"index": i, "placements": []}
                    for i in range(job["confirmation"]["candidate_count"])
                ]
            }
        )

    monkeypatch.setattr(ai_client, "_live_text", capture_call)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.setenv(ai_client.API_KEY_ENV_VAR, "test-key")

    proposed = client.post(
        f"/api/import/{job['id']}/propose", json={"framework_id": framework["id"]}
    )
    assert proposed.status_code == 200, proposed.text

    everything = json.dumps(seen, ensure_ascii=False)
    assert everything, "Stage B was never called"
    assert translated not in everything, "Stage B was given a translation"
    # Nor the translated story's own text, which is not part of this import.
    assert TAMIL_STORY not in everything


# --------------------------------------------------------------------------
# The response cannot be shown unlabelled
# --------------------------------------------------------------------------


def test_the_reply_always_carries_the_flag_and_the_original(
    client: TestClient,
) -> None:
    """Delta §4a: the UI cannot display a translation unlabelled.

    Made structural by the response shape — a screen holding this object holds
    the original and the flag whether it wanted them or not.
    """
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])

    reply = translate(client, anecdote_id)

    assert reply["is_translation"] is True
    assert reply["original_text"] == TAMIL_STORY
    assert reply["original_language_code"] == "ta"
    assert reply["original_language_name"] == "Tamil"
    assert reply["target_language_name"] == "English"
    assert reply["model_used"]


def test_the_second_reading_comes_from_the_cache(client: TestClient) -> None:
    """The cache's entire purpose: not paying twice to read the same story."""
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])

    first = translate(client, anecdote_id)
    second = translate(client, anecdote_id)

    assert first["from_cache"] is False
    assert second["from_cache"] is True
    assert second["translated_text"] == first["translated_text"]


def test_one_row_per_story_per_language(client: TestClient, session: Session) -> None:
    """Replaced, not accumulated — which is what makes it a cache and not a log."""
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])

    translate(client, anecdote_id)
    translate(client, anecdote_id)
    translate(client, anecdote_id, target="ms")

    rows = session.scalars(select(Translation)).all()
    assert len(rows) == 2
    assert {row.target_language_code for row in rows} == {"en", "ms"}


# --------------------------------------------------------------------------
# The UI keeps the label with the text
# --------------------------------------------------------------------------


BROWSER_JSX = (
    Path(__file__).resolve().parent.parent
    / "frontend"
    / "src"
    / "patterns"
    / "StoryBrowser.jsx"
)


def translation_component() -> str:
    source = BROWSER_JSX.read_text(encoding="utf-8")
    return source.split("function StoryTranslation")[1].split("\nfunction ")[0]


def test_the_label_and_the_text_are_the_same_block() -> None:
    """Delta §6: "assert the label is in the same component and not
    conditionally hidden".

    They are returned by one branch, in one element, with the label first. There
    is no arrangement of state in which the translated text renders and the
    label does not.
    """
    component = translation_component()
    body = component.split('className="nl-translate__body"')[1]
    shown = body.split("nl-translate__text")[0]

    assert "nl-translate__label" in shown, "the label is not above the text"
    # One guard opens the block, and it guards both.
    assert component.count("{shown && (") == 1


def test_the_label_is_not_behind_a_toggle_of_its_own() -> None:
    """A label with its own state could be turned off; this one has none."""
    component = translation_component()

    for switchable in ("showLabel", "labelVisible", "hideLabel", "withLabel"):
        assert switchable not in component


def test_the_label_says_what_it_is_and_where_the_original_is() -> None:
    component = translation_component()

    assert "Translated by" in component
    assert "the original is above" in component
    assert "what was actually said" in component


def test_the_original_stays_primary() -> None:
    """The story's own text is rendered before the toggle, always."""
    source = BROWSER_JSX.read_text(encoding="utf-8")

    assert source.index("nl-story__text") < source.index("<StoryTranslation")


def test_the_translation_is_quieter_than_the_original() -> None:
    """Secondary weight (delta §5), read off the stylesheet."""
    css = (
        Path(__file__).resolve().parent.parent
        / "frontend"
        / "src"
        / "patterns"
        / "patterns.css"
    ).read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    block = css.split(".nl-translate__text {")[1].split("}")[0]

    assert "--nl-text-sm" in block
    assert "--nl-grey" in block


def test_a_story_already_in_the_reading_language_offers_no_toggle() -> None:
    """Nothing to carry across, so nothing to offer."""
    component = translation_component()

    assert 'story.language_code === "en"' in component
    assert "return null" in component


# --------------------------------------------------------------------------
# Failure leaves the original readable (constraint 4)
# --------------------------------------------------------------------------


def test_being_offline_leaves_the_story_exactly_where_it_was(
    client: TestClient, session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])

    def unreachable(system: str, messages: list[dict[str, str]]) -> str:
        raise AiError(
            "ai_unreachable",
            "Narrative Lens could not reach the AI service.",
            "Check the internet connection and try again.",
        )

    monkeypatch.setattr(ai_client, "_live_text", unreachable)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.setenv(ai_client.API_KEY_ENV_VAR, "test-key")

    failed = client.get(f"/api/stories/{anecdote_id}/translation")

    assert failed.status_code == 502
    body = failed.json()["error"]
    assert body["code"] == "ai_unreachable"
    assert body["action"]

    # Nothing half-written, and the story still reads.
    session.expire_all()
    assert session.scalars(select(Translation)).all() == []
    assert session.get(Anecdote, anecdote_id).text == TAMIL_STORY

    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "1")
    listed = client.get(f"/api/stories/{framework['id']}").json()["stories"]
    assert listed[0]["text"] == TAMIL_STORY


def test_a_missing_key_is_a_sentence_not_a_stack_trace(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.delenv(ai_client.API_KEY_ENV_VAR, raising=False)

    response = client.get(f"/api/stories/{anecdote_id}/translation")

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "ai_key_missing"


def test_a_reply_that_will_not_parse_costs_one_repair_then_a_sentence(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])
    calls: list[str] = []

    def never_json(system: str, messages: list[dict[str, str]]) -> str:
        calls.append("call")
        return "Here is a translation for you."

    monkeypatch.setattr(ai_client, "_live_text", never_json)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.setenv(ai_client.API_KEY_ENV_VAR, "test-key")

    response = client.get(f"/api/stories/{anecdote_id}/translation")

    assert len(calls) == 2, f"{len(calls)} calls; expected one try and one repair"
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "ai_unreadable_reply"


def test_the_whole_path_runs_with_zero_network(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Constraint 6: ``NL_MOCK_AI=1`` never goes near the network."""
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])

    def explode(system: str, messages: list[dict[str, str]]) -> str:
        raise AssertionError("the translator reached the network in mock mode")

    monkeypatch.setattr(ai_client, "_live_text", explode)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "1")
    monkeypatch.delenv(ai_client.API_KEY_ENV_VAR, raising=False)

    assert translate(client, anecdote_id)["translated_text"]


# --------------------------------------------------------------------------
# What the model is asked, and what it is not
# --------------------------------------------------------------------------


def test_the_prompt_carries_the_story_and_the_target_and_nothing_else() -> None:
    """No title, no placements, no group, no provenance. A translator needs words."""
    prompt = json.loads(translate_prompt(TAMIL_STORY, "en"))

    assert set(prompt) == {"target_language", "text"}
    assert prompt["text"] == TAMIL_STORY
    assert prompt["target_language"] == "English"


def test_the_system_prompt_forbids_improving_the_story() -> None:
    """Translate, not summarise. The register is part of what was said."""
    lowered = TRANSLATE_SYSTEM.lower()

    assert "do not summarise" in lowered
    assert "keep the register" in lowered
    assert "say nothing about the story" in lowered


def test_the_shipped_mock_file_is_a_valid_reply() -> None:
    assert MOCK_PATH.is_file(), f"the mock reply is missing at {MOCK_PATH}"

    reply = TranslationReply.model_validate(
        json.loads(MOCK_PATH.read_text(encoding="utf-8"))
    )

    assert reply.translated_text.strip()


def test_the_translate_module_reads_its_mock_from_the_backend() -> None:
    """Shipped with the app, like the linter's — constraint 6 is an app mode."""
    assert MOCK_PATH.is_relative_to(BACKEND)
    assert translate_module.MOCK_PATH.name == "mock_translation_response.json"


def test_a_story_cannot_be_translated_into_its_own_language(
    client: TestClient,
) -> None:
    """The original is always the better text; offering it back is a nonsense."""
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])

    response = client.get(
        f"/api/stories/{anecdote_id}/translation", params={"target": "ta"}
    )

    assert response.status_code == 400
    body = response.json()["error"]
    assert body["code"] == "already_in_that_language"
    assert body["action"]


def test_a_target_that_is_not_a_language_is_refused(client: TestClient) -> None:
    framework = make_framework(client, MULTILINGUAL)
    anecdote_id = capture(client, framework["id"])

    response = client.get(
        f"/api/stories/{anecdote_id}/translation", params={"target": "not a language"}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unknown_language"


def test_a_story_that_does_not_exist_says_so_in_plain_english(
    client: TestClient,
) -> None:
    response = client.get("/api/stories/9999/translation")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "story_not_found"
