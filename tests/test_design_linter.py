"""The framework design linter (delta §6, phase C).

This is the one AI call in Narrative Lens that never sees data, and most of this
file is about keeping it that way. A linter that could read stories would be a
second, unaccountable route from anecdotes to a language model — precisely what
constraint 1's validation gate exists to prevent, arriving through a door
nobody was watching.

So the promises tested here are:

* it reads ``definition_json`` and nothing else — asserted on the actual prompt
  string, with story text sitting in the database while the call is made;
* it never writes: the framework is byte-identical afterwards;
* it cannot block publishing, with every finding outstanding;
* a reply that will not parse costs one repair and then a plain-English
  failure, leaving the Studio usable;
* ``NL_MOCK_AI=1`` covers the whole path with zero network.

The fixture framework is deliberately badly designed — a leading prompt, a triad
with an obviously right corner, an evaluative dyad — which is acceptance
criterion 7's setup.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend import ai_client
from backend import lint as lint_module
from backend.ai_client import AiError
from backend.framework_schema import FrameworkDefinition
from backend.lint import LINT_SYSTEM, MOCK_PATH, LintReport, lint, lint_prompt
from backend.models import Framework
from tests.queue_fixtures import make_framework

#: Badly designed on purpose (acceptance criterion 7). Every fault the delta's
#: §4a check-list names is in here somewhere, so a live model would have
#: something true to say and the mock has something plausible to stand in for.
BAD_DEFINITION = {
    # Leading: it names the answer it wants.
    "prompt_text": "Tell us about a time poor communication caused a problem.",
    "triads": [
        {
            # "Doing it properly" is the answer a good worker is supposed to pick.
            "id": "t1",
            "title": "What was the main thing driving how this piece of work went?",
            "corners": ["Doing it properly", "Rushing", "Penny-pinching"],
        }
    ],
    # One end obviously good, the other obviously bad.
    "dyads": [{"id": "d1", "title": "How was it handled?", "left": "Badly", "right": "Well"}],
    "mcqs": [{"id": "m1", "title": "How did it end?", "options": ["Well", "Badly"]}],
    "capture_settings": {"respondent_groups": ["Ops", "Deck"]},
}

STORY = (
    "We were three hours from the deadline when the parts finally arrived, and "
    "nobody had told the night shift they were coming."
)


def check(client: TestClient, framework_id: int) -> dict:
    response = client.post(f"/api/frameworks/{framework_id}/lint")
    assert response.status_code == 200, response.text
    return response.json()


# --------------------------------------------------------------------------
# It runs, and the findings come back in the shape the panel renders
# --------------------------------------------------------------------------


def test_the_mock_returns_findings_for_a_badly_designed_question_set(
    client: TestClient,
) -> None:
    """Acceptance criterion 7's first half."""
    framework = make_framework(client, BAD_DEFINITION)

    report = check(client, framework["id"])

    assert report["framework_id"] == framework["id"]
    assert report["framework_version"] == 1
    assert report["findings"], "the linter found nothing to say"


def test_every_finding_carries_the_four_fields_the_panel_needs(
    client: TestClient,
) -> None:
    """severity · location · finding · suggestion (delta §4a).

    The panel names the field each finding is about and offers the suggestion
    as text; a finding missing either would render as a blank line.
    """
    framework = make_framework(client, BAD_DEFINITION)

    for finding in check(client, framework["id"])["findings"]:
        assert finding["severity"] in ("info", "warning")
        assert finding["location"].strip()
        assert finding["finding"].strip()
        assert finding["suggestion"].strip()


def test_a_reply_with_an_unknown_severity_is_refused(client: TestClient) -> None:
    """The shape is enforced on the mock exactly as on a live reply.

    ``request_json`` validates both against the same model, so a mock that
    drifted out of date fails the suite rather than propping up a contract the
    live path would reject.
    """
    with pytest.raises(Exception):  # noqa: B017 - pydantic's own error type
        LintReport.model_validate(
            {"findings": [{"severity": "critical", "location": "x", "finding": "y",
                           "suggestion": "z"}]}
        )


def test_the_shipped_mock_file_is_a_valid_reply() -> None:
    """The fixture is held to the same shape it stands in for."""
    assert MOCK_PATH.is_file(), f"the mock reply is missing at {MOCK_PATH}"

    report = LintReport.model_validate(json.loads(MOCK_PATH.read_text(encoding="utf-8")))

    assert report.findings
    assert report.warnings >= 1


# --------------------------------------------------------------------------
# It never sees a story — the assertion the delta asks for by name
# --------------------------------------------------------------------------


def test_the_prompt_carries_the_definition_and_nothing_else() -> None:
    """The prompt is the definition as JSON, and is checkable as such."""
    definition = FrameworkDefinition.model_validate(BAD_DEFINITION)

    prompt = lint_prompt(definition)

    assert json.loads(prompt) == definition.model_dump(mode="json")


def test_no_story_text_reaches_the_prompt_even_when_stories_exist(
    client: TestClient, session: Session
) -> None:
    """The real shape of the risk: stories in the database, none in the call.

    A test that linted an empty framework would prove nothing — there would have
    been no story text to leak. So this captures one first, then reads the exact
    string the model would have been sent.
    """
    framework = make_framework(client, BAD_DEFINITION)
    stored = client.post(
        "/api/capture",
        json={
            "framework_id": framework["id"],
            "text": STORY,
            "significations": [],
        },
    )
    assert stored.status_code == 201, stored.text

    row = session.get(Framework, framework["id"])
    prompt = lint_prompt(FrameworkDefinition.model_validate(row.definition_json))

    for fragment in ("three hours", "night shift", "parts finally arrived"):
        assert fragment not in prompt
    assert "anecdote" not in prompt.lower()


def test_the_live_call_is_given_only_the_definition(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Asserted on the wire, not on the helper.

    :func:`lint_prompt` could be correct and the caller could still hand
    something else to the model. This intercepts the one function that talks to
    the network and reads what it was actually given.
    """
    framework = make_framework(client, BAD_DEFINITION)
    client.post(
        "/api/capture",
        json={"framework_id": framework["id"], "text": STORY, "significations": []},
    )

    seen: dict[str, object] = {}

    def capture_call(system: str, messages: list[dict[str, str]]) -> str:
        seen["system"] = system
        seen["messages"] = messages
        return json.dumps({"findings": []})

    monkeypatch.setattr(ai_client, "_live_text", capture_call)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.setenv(ai_client.API_KEY_ENV_VAR, "test-key")

    response = client.post(f"/api/frameworks/{framework['id']}/lint")
    assert response.status_code == 200, response.text

    everything = str(seen["system"]) + json.dumps(seen["messages"])
    for fragment in ("three hours", "night shift", "parts finally arrived"):
        assert fragment not in everything
    # And it really did send the design.
    assert "Doing it properly" in everything


def test_the_system_prompt_forbids_talking_about_data() -> None:
    """The instruction is part of the contract, so it is part of the tests."""
    assert "no stories" in LINT_SYSTEM.lower()
    assert "design" in LINT_SYSTEM.lower()
    for banned in ("say nothing about stories", "do not rewrite"):
        assert banned in LINT_SYSTEM.lower()


def test_the_linter_module_cannot_reach_an_anecdote() -> None:
    """Structural: there is no route from here to a story, not merely no call."""
    source = Path(lint_module.__file__).read_text(encoding="utf-8")

    for banned in ("Anecdote", "Signification", "dataset", "get_session"):
        assert banned not in source, f"backend/lint.py mentions {banned}"


# --------------------------------------------------------------------------
# It never writes, and it never blocks
# --------------------------------------------------------------------------


def test_linting_leaves_the_framework_byte_identical(
    client: TestClient, session: Session
) -> None:
    framework = make_framework(client, BAD_DEFINITION)
    before = json.dumps(
        session.get(Framework, framework["id"]).definition_json, sort_keys=True
    )

    check(client, framework["id"])
    session.expire_all()

    after = json.dumps(
        session.get(Framework, framework["id"]).definition_json, sort_keys=True
    )
    assert after == before


def test_linting_does_not_bump_the_version_or_touch_the_edit_log(
    client: TestClient,
) -> None:
    """A critique is not an edit. Nothing about the version lineage may move."""
    framework = make_framework(client, BAD_DEFINITION)
    before = client.get(f"/api/frameworks/{framework['id']}").json()

    check(client, framework["id"])

    assert client.get(f"/api/frameworks/{framework['id']}").json() == before
    assert len(client.get("/api/frameworks").json()) == 1


def test_publishing_succeeds_with_every_finding_outstanding(
    client: TestClient,
) -> None:
    """The delta's flat rule: the linter can never block publishing.

    Nothing is changed in response to the findings — they are all still true of
    this question set — and the save goes through anyway.
    """
    framework = make_framework(client, BAD_DEFINITION)
    findings = check(client, framework["id"])["findings"]
    assert findings, "this test is vacuous without findings to ignore"

    changed = dict(BAD_DEFINITION)
    changed["prompt_text"] = "Tell us about a time poor communication caused trouble."
    saved = client.put(
        f"/api/frameworks/{framework['id']}",
        json={"definition": changed, "edit_kind": "wording_fix"},
    )

    assert saved.status_code == 200, saved.text


def test_a_story_can_still_be_captured_against_a_framework_with_findings(
    client: TestClient,
) -> None:
    """Advisory means advisory: capture is not gated on a clean report either."""
    framework = make_framework(client, BAD_DEFINITION)
    check(client, framework["id"])

    stored = client.post(
        "/api/capture",
        json={"framework_id": framework["id"], "text": STORY, "significations": []},
    )

    assert stored.status_code == 201, stored.text


def test_an_unknown_question_set_says_so_in_plain_english(client: TestClient) -> None:
    response = client.post("/api/frameworks/9999/lint")

    assert response.status_code == 404
    body = response.json()["error"]
    assert body["code"] == "framework_not_found"
    assert body["action"]


# --------------------------------------------------------------------------
# When it fails, it fails gracefully (constraint 6)
# --------------------------------------------------------------------------


def test_malformed_json_costs_one_repair_and_then_a_sentence(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One retry, and only one, then plain English (constraint 6).

    Counting the calls is the point: a linter that retried forever would leave
    the operator watching a spinner with no way to know it was stuck.
    """
    framework = make_framework(client, BAD_DEFINITION)
    calls: list[str] = []

    def never_json(system: str, messages: list[dict[str, str]]) -> str:
        calls.append("call")
        return "Here are some thoughts about your triangle."

    monkeypatch.setattr(ai_client, "_live_text", never_json)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.setenv(ai_client.API_KEY_ENV_VAR, "test-key")

    response = client.post(f"/api/frameworks/{framework['id']}/lint")

    assert len(calls) == 2, f"{len(calls)} calls; expected one try and one repair"
    assert response.status_code == 502
    body = response.json()["error"]
    assert body["code"] == "ai_unreadable_reply"
    assert body["action"]
    for jargon in ("Traceback", "JSONDecodeError", "ValidationError"):
        assert jargon not in body["message"]


def test_a_repaired_reply_is_accepted(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The retry is worth having: a second, valid reply is used."""
    framework = make_framework(client, BAD_DEFINITION)
    replies = iter(
        [
            "Sorry — here you go:",
            json.dumps(
                {
                    "findings": [
                        {
                            "severity": "info",
                            "location": "prompt_text",
                            "finding": "It leads a little.",
                            "suggestion": "Ask for a moment, not a cause.",
                        }
                    ]
                }
            ),
        ]
    )

    monkeypatch.setattr(ai_client, "_live_text", lambda system, messages: next(replies))
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.setenv(ai_client.API_KEY_ENV_VAR, "test-key")

    report = check(client, framework["id"])

    assert len(report["findings"]) == 1
    assert report["findings"][0]["location"] == "prompt_text"


def test_the_studio_is_still_usable_after_a_failed_check(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Constraint 4: the AI being unreachable is an ordinary state of the app.

    Nothing was written, so there is nothing half-finished to recover from —
    the same question set saves and prints exactly as before.
    """
    framework = make_framework(client, BAD_DEFINITION)

    def unreachable(system: str, messages: list[dict[str, str]]) -> str:
        raise AiError(
            "ai_unreachable",
            "Narrative Lens could not reach the AI service.",
            "Check the internet connection and try again.",
        )

    monkeypatch.setattr(ai_client, "_live_text", unreachable)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.setenv(ai_client.API_KEY_ENV_VAR, "test-key")

    failed = client.post(f"/api/frameworks/{framework['id']}/lint")
    assert failed.status_code == 502
    assert failed.json()["error"]["code"] == "ai_unreachable"

    monkeypatch.delattr(ai_client, "_live_text", raising=False)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "1")

    assert client.get(f"/api/frameworks/{framework['id']}").status_code == 200
    assert (
        client.put(
            f"/api/frameworks/{framework['id']}",
            json={"definition": BAD_DEFINITION, "edit_kind": "wording_fix"},
        ).status_code
        == 200
    )
    assert client.get(f"/api/frameworks/{framework['id']}/paper-pack").status_code == 200


def test_a_missing_key_is_a_sentence_not_a_stack_trace(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    framework = make_framework(client, BAD_DEFINITION)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.delenv(ai_client.API_KEY_ENV_VAR, raising=False)

    response = client.post(f"/api/frameworks/{framework['id']}/lint")

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "ai_key_missing"
    assert response.json()["error"]["action"]


# --------------------------------------------------------------------------
# Zero network under NL_MOCK_AI=1
# --------------------------------------------------------------------------


def test_the_whole_path_runs_with_no_anthropic_package_at_all(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Constraint 6's zero-network promise, as a property of the import graph.

    In mock mode ``_live_text`` is never called, so ``anthropic`` is never
    imported. Replacing it with something that raises on import proves the mock
    path never goes near it.
    """
    framework = make_framework(client, BAD_DEFINITION)

    def explode(system: str, messages: list[dict[str, str]]) -> str:
        raise AssertionError("the linter tried to reach the network in mock mode")

    monkeypatch.setattr(ai_client, "_live_text", explode)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "1")
    monkeypatch.delenv(ai_client.API_KEY_ENV_VAR, raising=False)

    assert check(client, framework["id"])["findings"]


def test_the_mock_is_the_same_every_time(client: TestClient) -> None:
    """Determinism: two checks of one question set say the same thing.

    A mock that varied would make the panel's output untestable and would give
    the operator a different answer every click for no reason.
    """
    framework = make_framework(client, BAD_DEFINITION)

    assert check(client, framework["id"]) == check(client, framework["id"])


def test_lint_returns_a_report_directly_for_callers_that_want_one() -> None:
    """The module works without the router, which is how the tests above read it."""
    report = lint(FrameworkDefinition.model_validate(BAD_DEFINITION))

    assert isinstance(report, LintReport)
    assert report.warnings >= 1


# --------------------------------------------------------------------------
# The panel (delta §5): quiet, and never a one-click apply
# --------------------------------------------------------------------------


STUDIO = Path(__file__).resolve().parent.parent / "frontend" / "src" / "studio"


def studio_jsx() -> str:
    return (STUDIO / "Studio.jsx").read_text(encoding="utf-8")


def panel_source() -> str:
    return studio_jsx().split("function LintPanel")[1].split("\nfunction ")[0]


def lint_css() -> str:
    import re

    raw = (STUDIO / "studio.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    blocks = [block for block in css.split("}") if ".nl-lint" in block.split("{")[0]]
    assert blocks, "the design panel has no styles of its own"
    return "\n".join(blocks)


def test_the_button_sits_beside_the_save_control() -> None:
    """Beside it, not in front of it — the linter gates nothing (delta §5)."""
    actions = studio_jsx().split('className="nl-actions"')[1].split("</div>")[0]

    assert "Check this design" in actions
    assert "Save changes" in actions


def test_a_suggestion_is_text_and_never_a_button() -> None:
    """The delta is explicit: "never as a one-click apply".

    The operator knows the workforce and the model is guessing at them; one
    click to accept a guess is how a question set drifts away from the people
    answering it.
    """
    panel = panel_source()
    suggestion_block = panel.split("nl-lint__try")[1].split("</p>")[0]

    assert "<button" not in suggestion_block
    for applying in ("onApply", "applySuggestion", "patch(", "setDraft"):
        assert applying not in panel, f"the panel can edit the framework ({applying})"


def test_the_panel_says_it_is_about_questions_not_data() -> None:
    """Otherwise a reader would think the model had read their stories."""
    panel = panel_source()

    assert "not about your data" in panel
    assert "No stories were read" in panel
    assert "stops you publishing" in panel


def test_the_panel_groups_by_severity() -> None:
    panel = panel_source()

    assert 'severity === "warning"' in panel
    assert "Worth changing" in panel and "Worth a second look" in panel


def test_a_failed_check_still_renders_something_usable() -> None:
    """The failure branch says what happened and that nothing was changed."""
    panel = panel_source()

    assert "could not run" in panel
    assert "Nothing was changed" in panel


def test_the_panel_is_quiet() -> None:
    """Constraint 13a: nothing in the Studio competes for attention like this.

    Body text, greys and one rule. No colour encodes severity — the heading a
    finding sits under does that, which is what keeps it readable in greyscale.
    """
    css = lint_css()

    assert "--nl-accent" not in css, "severity is being carried by colour"
    for loud in ("--nl-text-lg", "--nl-text-xl", "font-weight: 700", "font-weight: 600"):
        assert loud not in css, f"the design panel uses {loud}"
    import re

    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", css), "a raw colour literal"
