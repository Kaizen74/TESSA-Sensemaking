"""The live path to api.anthropic.com — the one Phase 7 switches on.

Everything before this phase ran on mocks, which proves the app is testable but
proves nothing about the call it will actually make. So these tests stand a fake
``anthropic`` module in front of :func:`backend.ai_client._live_text` and check
the request that comes out of it: the model PRD §4a pins, temperature 0, the
system prompt, and the message list including the repair turn.

They also check the other half of constraint 4 — that being unable to reach the
service is an ordinary state of the app rather than a broken one. Analyse fails
in a sentence; capture, patterns and exports carry on working offline.

No network is opened here either. The fake is injected into ``sys.modules``, so
the suite still runs with nothing but a Python interpreter.
"""

from __future__ import annotations

import sys
import types
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend import ai_client
from backend.ai_client import AiError
from tests import ingest_fixtures as fx
from tests.patterns_fixtures import GOLDEN_DEFINITION
from tests.queue_fixtures import confirmed_import, make_framework


class _Block:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _Response:
    def __init__(self, blocks: list[Any]) -> None:
        self.content = blocks


class _FakeMessages:
    def __init__(self, owner: _FakeAnthropic) -> None:
        self._owner = owner

    def create(self, **kwargs: Any) -> _Response:
        self._owner.calls.append(kwargs)
        if self._owner.raises:
            raise self._owner.raises
        reply = self._owner.replies[min(len(self._owner.calls) - 1, len(self._owner.replies) - 1)]
        return _Response([_Block(reply)])


class _FakeAnthropic:
    """Stands in for ``anthropic.Anthropic`` and records what it was asked."""

    instances: list[_FakeAnthropic] = []

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key
        self.calls: list[dict[str, Any]] = []
        self.replies: list[str] = ['{"answer": "yes"}']
        self.raises: Exception | None = None
        self.messages = _FakeMessages(self)
        _FakeAnthropic.instances.append(self)


class APIConnectionError(Exception):
    pass


class RateLimitError(Exception):
    pass


class APIStatusError(Exception):
    pass


@pytest.fixture
def fake_anthropic(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    """Install a fake ``anthropic`` package and turn mock mode off."""
    module = types.ModuleType("anthropic")
    module.Anthropic = _FakeAnthropic  # type: ignore[attr-defined]
    module.APIConnectionError = APIConnectionError  # type: ignore[attr-defined]
    module.RateLimitError = RateLimitError  # type: ignore[attr-defined]
    module.APIStatusError = APIStatusError  # type: ignore[attr-defined]

    _FakeAnthropic.instances.clear()
    monkeypatch.setitem(sys.modules, "anthropic", module)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.setenv(ai_client.API_KEY_ENV_VAR, "test-key-not-a-real-one")
    return module


def _calls() -> list[dict[str, Any]]:
    """Every request made, across every client.

    ``_live_text`` builds a fresh ``Anthropic`` per call — deliberately, so no
    connection outlives the click that opened it — so the record of what was
    asked has to be gathered across instances rather than read off the last one.
    """
    return [call for instance in _FakeAnthropic.instances for call in instance.calls]


def _last() -> _FakeAnthropic:
    assert _FakeAnthropic.instances, "no client was constructed"
    return _FakeAnthropic.instances[-1]


def _replies(monkeypatch: pytest.MonkeyPatch, replies: list[str]) -> None:
    """Answer each successive request with the next reply in the list."""
    sent: list[str] = []

    def create(self: _FakeMessages, **kwargs: Any) -> _Response:
        self._owner.calls.append(kwargs)
        reply = replies[min(len(sent), len(replies) - 1)]
        sent.append(reply)
        return _Response([_Block(reply)])

    monkeypatch.setattr(_FakeMessages, "create", create)


# --------------------------------------------------------------------------
# The request the app actually makes
# --------------------------------------------------------------------------


def test_the_call_uses_the_model_and_temperature_the_prd_pins(
    fake_anthropic: types.ModuleType,
) -> None:
    ai_client._live_text("a system prompt", [{"role": "user", "content": "hello"}])

    sent = _calls()[0]
    assert sent["model"] == "claude-sonnet-4-6"
    assert sent["temperature"] == 0
    assert sent["max_tokens"] == ai_client.MAX_TOKENS
    assert sent["system"] == "a system prompt"
    assert sent["messages"] == [{"role": "user", "content": "hello"}]


def test_the_key_comes_from_the_environment_and_nowhere_else(
    fake_anthropic: types.ModuleType,
) -> None:
    ai_client._live_text("s", [{"role": "user", "content": "p"}])

    assert _last().api_key == "test-key-not-a-real-one"


def test_only_the_text_blocks_of_a_reply_are_read(
    fake_anthropic: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A reply may carry blocks that are not text; they are not the answer."""

    class _Other:
        type = "thinking"
        text = "should be ignored"

    def create(self: _FakeMessages, **kwargs: Any) -> _Response:
        return _Response([_Other(), _Block('{"a":'), _Block(" 1}")])

    monkeypatch.setattr(_FakeMessages, "create", create)

    assert ai_client._live_text("s", [{"role": "user", "content": "p"}]) == '{"a": 1}'


def test_the_json_instruction_is_appended_to_every_system_prompt(
    fake_anthropic: types.ModuleType,
) -> None:
    """Strict JSON is asked for on every call, not only where it is convenient."""
    from pydantic import BaseModel

    class Shape(BaseModel):
        answer: str

    ai_client.request_json(system="Do a thing.", prompt="p", shape=Shape, mock=dict)

    system = _calls()[0]["system"]
    assert system.startswith("Do a thing.")
    assert ai_client.JSON_SYSTEM_SUFFIX in system


# --------------------------------------------------------------------------
# The repair path, end to end through a real stage
# --------------------------------------------------------------------------


def test_stage_a_repairs_one_bad_reply_and_carries_on(
    fake_anthropic: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PRD §6 Phase 7: the repair path, exercised through Stage A itself."""
    import json

    from backend.organise import organise
    from backend.parsers import parse

    document = parse("workshop.txt", fx.txt_bytes())
    good = json.dumps(
        {
            "segments": [
                {
                    "source_locator": block.locator,
                    "text": block.text,
                    "title": "A story",
                    "confidence": 0.8,
                }
                for block in document.blocks
            ]
        }
    )
    _replies(monkeypatch, ["Certainly! Here is the answer:", good])

    result = organise(document)

    assert result.segments_found == len(document.blocks)
    calls = _calls()
    assert len(calls) == 2
    # The repair turn hands the model its own reply back and names the problem.
    assert calls[1]["messages"][1]["role"] == "assistant"
    assert "could not be read as JSON" in calls[1]["messages"][2]["content"]


def test_two_bad_replies_give_up_in_plain_english(
    fake_anthropic: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pydantic import BaseModel

    class Shape(BaseModel):
        answer: str

    _replies(monkeypatch, ["not json, sorry"])

    with pytest.raises(AiError) as caught:
        ai_client.request_json(system="s", prompt="p", shape=Shape, mock=dict)

    assert caught.value.code == "ai_unreadable_reply"
    # One repair retry, and only one.
    assert len(_calls()) == 2


@pytest.mark.parametrize(
    ("failure", "code"),
    [
        (APIConnectionError("no route"), "ai_unreachable"),
        (RateLimitError("slow down"), "ai_busy"),
        (APIStatusError("bad request"), "ai_refused"),
    ],
)
def test_every_service_failure_becomes_a_sentence(
    fake_anthropic: types.ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    failure: Exception,
    code: str,
) -> None:
    def create(self: _FakeMessages, **kwargs: Any) -> _Response:
        raise failure

    monkeypatch.setattr(_FakeMessages, "create", create)

    with pytest.raises(AiError) as caught:
        ai_client._live_text("s", [{"role": "user", "content": "p"}])

    assert caught.value.code == code
    assert caught.value.action
    for jargon in ("Traceback", "Exception", "HTTP", "None"):
        assert jargon not in caught.value.message


# --------------------------------------------------------------------------
# Offline degradation (constraint 4, acceptance criterion 12)
# --------------------------------------------------------------------------


def test_analyse_fails_in_a_sentence_when_there_is_no_key(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.delenv(ai_client.API_KEY_ENV_VAR, raising=False)
    uploaded = client.post(
        "/api/import", files={"file": ("workshop.txt", fx.txt_bytes())}
    ).json()

    response = client.post(f"/api/import/{uploaded['id']}/organise")

    assert response.status_code == 502
    error = response.json()["detail"]["error"]
    assert error["code"] == "ai_key_missing"
    assert "Capture" in error["action"]


def test_everything_that_is_not_analyse_still_works_offline(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Acceptance criterion 12: offline is a working state, not a broken one."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.delenv(ai_client.API_KEY_ENV_VAR, raising=False)

    captured = client.post(
        "/api/capture",
        json={
            "framework_id": framework["id"],
            "text": "Typed on the operator's own laptop with no internet at all.",
            "significations": [{"signifier_id": "d1", "value": {"value": 0.6}}],
        },
    )
    patterns = client.get(f"/api/patterns/{framework['id']}")
    csv_export = client.get("/api/export/csv", params={"framework_id": framework["id"]})
    brief = client.get("/api/export/brief", params={"framework_id": framework["id"]})
    pack = client.get(f"/api/frameworks/{framework['id']}/paper-pack")

    assert captured.status_code == 201
    assert patterns.status_code == 200 and patterns.json()["total"] == 1
    assert csv_export.status_code == 200
    assert brief.status_code == 200
    assert pack.status_code == 200


def test_a_file_waiting_to_be_analysed_survives_the_outage(
    client: TestClient, session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The operator loses the click, not the file."""
    from backend.models import ImportJob

    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.delenv(ai_client.API_KEY_ENV_VAR, raising=False)
    uploaded = client.post(
        "/api/import", files={"file": ("workshop.txt", fx.txt_bytes())}
    ).json()

    client.post(f"/api/import/{uploaded['id']}/organise")

    job = session.get(ImportJob, uploaded["id"])
    assert job.stage == "uploaded"
    assert job.error_message


def test_stage_b_also_degrades_gracefully(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    framework = make_framework(client)
    job = confirmed_import(client)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.delenv(ai_client.API_KEY_ENV_VAR, raising=False)

    response = client.post(
        f"/api/import/{job['id']}/propose", json={"framework_id": framework["id"]}
    )

    assert response.status_code == 502
    assert response.json()["detail"]["error"]["code"] == "ai_key_missing"
