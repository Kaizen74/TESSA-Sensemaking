"""The one AI client (constraint 6).

Every call Narrative Lens makes to a language model goes through this module and
nowhere else. That is what makes the app testable with zero network and what
makes constraint 4's promise checkable: ``api.anthropic.com`` is reachable from
exactly one file, and only from a function the operator triggered by clicking
Analyse.

Four rules live here, all from constraint 6:

* **One client.** Both ingestion stages call :func:`request_json`.
* **Mocks for both stages.** Every entry point takes the mock alongside the
  prompt, so the mock cannot drift away from the call it stands in for. Stage A
  is built in Phase 5; Stage B joins it in Phase 6.
* **``NL_MOCK_AI=1`` runs everything with zero network.** In mock mode the
  ``anthropic`` package is never imported, so a missing key, a missing wheel,
  and a missing network are all equally harmless.
* **Strict JSON with one repair-retry, then a graceful plain-English failure.**
  A reply that will not parse is handed back to the model once, with the problem
  named. If the second reply is also unusable the operator gets a sentence they
  can act on, never a stack trace.

Nothing in here decides *anything* about the data. Stage A proposes how a file
breaks into stories; a human confirms it before a single row moves (constraint
1). Patterns never come near this module at all (constraint 11).
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

#: PRD §4a pins the model and the temperature. Temperature 0 is what makes two
#: runs of the same file comparable.
MODEL = "claude-sonnet-4-6"
TEMPERATURE = 0
MAX_TOKENS = 8000

MOCK_ENV_VAR = "NL_MOCK_AI"
API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"

#: Constraint 2 — below this a proposal is flagged amber. Routing is identical:
#: everything queues for a human either way.
LOW_CONFIDENCE = 0.70

#: Sent with every request. The strictness is deliberate: a preamble, an
#: apology, or a fenced explanation all cost a repair round-trip.
JSON_SYSTEM_SUFFIX = (
    "Reply with a single JSON object and nothing else. No preamble, no "
    "explanation, no markdown fence. If you are unsure about a value, still "
    "return the object and lower the confidence figure."
)

REPAIR_INSTRUCTION = (
    "That reply could not be read as JSON matching the requested shape. The "
    "problem was: {problem}\n\nSend the same content again as a single valid "
    "JSON object, with nothing before or after it."
)

Payload = TypeVar("Payload", bound=BaseModel)


class AiError(Exception):
    """An AI call that failed in a way the operator needs told about.

    Carries the PRD §4 error triple so the router can hand it straight to the
    operator without inventing wording at the call site.
    """

    def __init__(self, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action


def mock_enabled() -> bool:
    """Whether this process runs with mocks instead of the network.

    Read on every call rather than cached at import, so a test can switch modes
    without reloading the module.
    """
    return os.environ.get(MOCK_ENV_VAR, "") == "1"


def _fenced_json(raw: str) -> str:
    """Return *raw* with one surrounding markdown fence removed, if present.

    Strict JSON means the reply must *be* an object, and the system prompt says
    so. This trims the single failure that costs a whole extra round-trip for no
    information — a correct object wrapped in ```json — and nothing else. A
    reply with prose around it still fails and still goes to the repair retry.
    """
    text = raw.strip()
    if not text.startswith("```"):
        return text
    body = text[3:]
    if body.lower().startswith("json"):
        body = body[4:]
    closing = body.rfind("```")
    return (body[:closing] if closing != -1 else body).strip()


def _parse(raw: str, shape: type[Payload]) -> Payload:
    """Parse one reply strictly, or raise the reason it could not be parsed."""
    return shape.model_validate(json.loads(_fenced_json(raw)))


def _live_text(system: str, messages: list[dict[str, str]]) -> str:
    """One live call to api.anthropic.com. The only network in the app.

    Imported inside the function so that mock mode never loads the package at
    all — constraint 6's "zero network" is then a property of the import graph,
    not a promise about runtime behaviour.
    """
    import anthropic

    key = os.environ.get(API_KEY_ENV_VAR, "").strip()
    if not key:
        raise AiError(
            "ai_key_missing",
            "Narrative Lens has no key for the AI service, so it cannot read "
            "this file for you.",
            "Everything else still works offline. Add the key during setup, or "
            "type the stories in by hand under Capture.",
        )

    client = anthropic.Anthropic(api_key=key)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system,
            messages=messages,  # type: ignore[arg-type]
        )
    except anthropic.APIConnectionError as exc:
        raise AiError(
            "ai_unreachable",
            "Narrative Lens could not reach the AI service.",
            "Check the internet connection and try Analyse again. Capture, "
            "validation, patterns and printing all work without it.",
        ) from exc
    except anthropic.RateLimitError as exc:
        raise AiError(
            "ai_busy",
            "The AI service is busy and asked Narrative Lens to wait.",
            "Wait a minute and click Analyse again.",
        ) from exc
    except anthropic.APIStatusError as exc:
        raise AiError(
            "ai_refused",
            "The AI service turned down that request.",
            "Try Analyse again. If it keeps happening, the file may be too "
            "large — split it and import the parts.",
        ) from exc

    return "".join(block.text for block in response.content if block.type == "text")


def request_json(
    *,
    system: str,
    prompt: str,
    shape: type[Payload],
    mock: Callable[[], dict[str, Any]],
) -> Payload:
    """Ask for one JSON object of the given shape, or fail in plain English.

    In mock mode the mock is validated against the very same shape as a live
    reply, so a mock that has drifted out of date fails the suite instead of
    quietly propping up a broken contract.
    """
    if mock_enabled():
        try:
            return shape.model_validate(mock())
        except ValidationError as exc:  # pragma: no cover - a bug in a mock
            raise AiError(
                "ai_mock_invalid",
                "The built-in practice data does not match what Narrative Lens "
                "expects.",
                "This is a fault in the app itself. Report it to whoever set "
                "this up.",
            ) from exc

    full_system = f"{system}\n\n{JSON_SYSTEM_SUFFIX}"
    messages: list[dict[str, str]] = [{"role": "user", "content": prompt}]

    raw = _live_text(full_system, messages)
    try:
        return _parse(raw, shape)
    except (json.JSONDecodeError, ValidationError) as first:
        # One repair retry, and only one. A model that has misunderstood the
        # shape twice will not understand it on the third ask, and the operator
        # is waiting.
        messages.append({"role": "assistant", "content": raw})
        messages.append(
            {"role": "user", "content": REPAIR_INSTRUCTION.format(problem=first)}
        )
        repaired = _live_text(full_system, messages)
        try:
            return _parse(repaired, shape)
        except (json.JSONDecodeError, ValidationError) as second:
            raise AiError(
                "ai_unreadable_reply",
                "The AI service sent back something Narrative Lens could not "
                "read, twice.",
                "Click Analyse again. If it keeps happening, import a smaller "
                "part of the file, or type the stories in under Capture.",
            ) from second
