"""The one AI client, and the four promises constraint 6 makes about it."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

from backend import ai_client
from backend.ai_client import AiError


class Shape(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    confidence: float


@pytest.fixture
def live(monkeypatch: pytest.MonkeyPatch) -> None:
    """Turn mock mode off for the tests that are about the live path."""
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")


def test_the_suite_runs_in_mock_mode_by_default() -> None:
    """Constraint 6: NL_MOCK_AI=1 runs everything with zero network."""
    assert ai_client.mock_enabled()


def test_mock_mode_never_touches_the_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def explode(*args: object, **kwargs: object) -> str:
        raise AssertionError("mock mode made a live call")

    monkeypatch.setattr(ai_client, "_live_text", explode)

    result = ai_client.request_json(
        system="s",
        prompt="p",
        shape=Shape,
        mock=lambda: {"answer": "yes", "confidence": 0.9},
    )

    assert result.answer == "yes"


def test_a_mock_that_has_drifted_out_of_shape_fails_loudly() -> None:
    """A mock is validated against the same shape as a live reply.

    Otherwise a mock could keep a broken contract looking healthy for a whole
    phase, and the failure would surface on the operator's first live click.
    """
    with pytest.raises(AiError) as caught:
        ai_client.request_json(
            system="s", prompt="p", shape=Shape, mock=lambda: {"answer": "yes"}
        )

    assert caught.value.code == "ai_mock_invalid"


def test_api_key_is_the_only_module_that_names_the_service() -> None:
    """Constraint 4: api.anthropic.com is reachable from exactly one file.

    A structural test rather than a behavioural one — the promise is about the
    import graph, so a future edit that starts calling the service from a second
    module has to fail here rather than pass unnoticed.
    """
    backend = Path(__file__).resolve().parent.parent / "backend"
    offenders = [
        path.relative_to(backend).as_posix()
        for path in backend.rglob("*.py")
        if "anthropic" in path.read_text(encoding="utf-8").lower()
    ]

    assert offenders == ["ai_client.py"]


def test_a_clean_reply_is_parsed_once(live: None, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[dict[str, str]]] = []

    def reply(system: str, messages: list[dict[str, str]]) -> str:
        calls.append(list(messages))
        return '{"answer": "yes", "confidence": 0.8}'

    monkeypatch.setattr(ai_client, "_live_text", reply)

    result = ai_client.request_json(system="s", prompt="p", shape=Shape, mock=dict)

    assert result.confidence == 0.8
    assert len(calls) == 1


def test_a_fenced_reply_costs_nothing(live: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """A correct object in a markdown fence is the one wrapper worth unwrapping."""
    monkeypatch.setattr(
        ai_client,
        "_live_text",
        lambda system, messages: '```json\n{"answer": "yes", "confidence": 0.5}\n```',
    )

    assert ai_client.request_json(system="s", prompt="p", shape=Shape, mock=dict).answer == "yes"


def test_a_broken_reply_gets_exactly_one_repair_retry(
    live: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    replies = ["Sure! Here you go: not json at all", '{"answer": "yes", "confidence": 0.1}']
    seen: list[list[dict[str, str]]] = []

    def reply(system: str, messages: list[dict[str, str]]) -> str:
        seen.append(list(messages))
        return replies[len(seen) - 1]

    monkeypatch.setattr(ai_client, "_live_text", reply)

    result = ai_client.request_json(system="s", prompt="p", shape=Shape, mock=dict)

    assert result.answer == "yes"
    assert len(seen) == 2
    # The retry hands the model its own reply and names the problem, rather than
    # asking the same question again and hoping.
    assert seen[1][1]["content"] == replies[0]
    assert "could not be read as JSON" in seen[1][2]["content"]


def test_a_reply_of_the_wrong_shape_also_goes_to_repair(
    live: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Valid JSON of the wrong shape is just as unusable as invalid JSON."""
    replies = ['{"answer": "yes"}', '{"answer": "yes", "confidence": 0.4}']
    count = {"n": 0}

    def reply(system: str, messages: list[dict[str, str]]) -> str:
        count["n"] += 1
        return replies[count["n"] - 1]

    monkeypatch.setattr(ai_client, "_live_text", reply)

    assert ai_client.request_json(system="s", prompt="p", shape=Shape, mock=dict).confidence == 0.4
    assert count["n"] == 2


def test_two_broken_replies_fail_gracefully_in_plain_english(
    live: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    count = {"n": 0}

    def reply(system: str, messages: list[dict[str, str]]) -> str:
        count["n"] += 1
        return "still not json"

    monkeypatch.setattr(ai_client, "_live_text", reply)

    with pytest.raises(AiError) as caught:
        ai_client.request_json(system="s", prompt="p", shape=Shape, mock=dict)

    # One repair retry, and only one.
    assert count["n"] == 2
    assert caught.value.code == "ai_unreadable_reply"
    for word in ("JSON", "API", "schema", "parse"):
        assert word not in caught.value.message
    assert caught.value.action


def test_a_missing_key_is_an_offer_of_the_offline_path(
    live: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ai_client.API_KEY_ENV_VAR, raising=False)

    with pytest.raises(AiError) as caught:
        ai_client._live_text("s", [{"role": "user", "content": "p"}])

    assert caught.value.code == "ai_key_missing"
    assert "Capture" in caught.value.action


def test_the_model_and_temperature_are_the_ones_the_prd_pins() -> None:
    """PRD §4a. Temperature 0 is what makes two runs of a file comparable."""
    assert ai_client.MODEL == "claude-sonnet-4-6"
    assert ai_client.TEMPERATURE == 0


def test_the_amber_threshold_is_constraint_twos() -> None:
    assert ai_client.LOW_CONFIDENCE == 0.70
