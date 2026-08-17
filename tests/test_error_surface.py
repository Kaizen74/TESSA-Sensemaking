"""The plain-English error pass, held as a test (constraint 7, PRD §4).

Individual endpoints already prove their own refusals. This file is about the
*surface*: every sentence the app can put in front of the operator, all at once,
checked against the same rules — so a message added in a hurry six months from
now cannot quietly reintroduce "Internal Server Error" or a validator's field
dump.

Two halves, because the surface has two halves.

* **The written ones.** Every ``errors.not_found``/``bad_request``/``conflict``/
  ``upstream`` and every operator-facing exception the app raises, read out of
  the source with :mod:`ast` rather than by calling each one. A test that walks
  the code cannot miss a raise site the way a test per endpoint can.
* **The ones nobody wrote.** A mistyped address, a body the page malformed, a
  fault in the app itself. These are the paths that hand out framework wording
  by default, so each is exercised against a live app.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend import stage_machine
from backend.main import app

BACKEND = Path(__file__).resolve().parent.parent / "backend"

#: Functions and exception classes that carry the PRD §4 triple, in the order
#: (code, message, action).
TRIPLE_CALLS = {
    "not_found",
    "bad_request",
    "conflict",
    "upstream",
    "AiError",
    "ExtractionError",
    "OrganiseError",
    "ParseError",
    "ProposeError",
}

#: ``CaptureError(message, action)`` — the code is added by its router.
PAIR_CALLS = {"CaptureError"}

#: Words that mean something to a programmer and nothing to the operator this
#: app is written for. A message containing one of these has been written for
#: the wrong reader.
#:
#: Single words are matched as whole words rather than as substrings, so a rule
#: about "none" does not fire on "nonetheless". "validation" is deliberately
#: absent: the validation queue is a thing the operator uses by that name, and a
#: rule that bans the app's own vocabulary would push the writing further from
#: plain English rather than closer to it.
JARGON = (
    "http",
    "json",
    "sql",
    "sqlite",
    "python",
    "traceback",
    "stack",
    "exception",
    "null",
    "none",
    "nan",
    "boolean",
    "parameter",
    "argument",
    "payload",
    "schema",
    "database",
    "server error",
    "internal",
    "unhandled",
    "validator",
    "serialise",
    "deserialise",
    "timeout",
    "status code",
    "request body",
    "api",
    "uuid",
    "regex",
)


def _speaks_jargon(text: str) -> str | None:
    """The first jargon term in ``text``, or None. Whole words, not substrings."""
    lowered = text.lower()
    words = set(re.split(r"[^a-z]+", lowered))
    for term in JARGON:
        if " " in term:
            if term in lowered:
                return term
        elif term in words:
            return term
    return None


def _text(node: ast.AST) -> str | None:
    """The literal text of a string argument, with ``{}`` for what is filled in."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(
            str(part.value) if isinstance(part, ast.Constant) else "{}" for part in node.values
        )
    return None


def _messages() -> list[tuple[str, int, str, str]]:
    """Every written error triple in the backend: (file, line, message, action).

    Non-literal arguments — ``exc.message`` passed on from a lower layer — are
    skipped here, because the layer that wrote them is itself scanned.
    """
    found: list[tuple[str, int, str, str]] = []
    for path in sorted(BACKEND.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name in TRIPLE_CALLS and len(node.args) == 3:
                message, action = _text(node.args[1]), _text(node.args[2])
            elif name in PAIR_CALLS and len(node.args) == 2:
                message, action = _text(node.args[0]), _text(node.args[1])
            elif name == "AppError" and len(node.args) == 4:
                message, action = _text(node.args[2]), _text(node.args[3])
            else:
                continue
            if message is None or action is None:
                continue
            found.append((str(path.relative_to(BACKEND.parent)), node.lineno, message, action))
    return found


WRITTEN = _messages()


def test_the_scan_actually_found_the_error_surface() -> None:
    """A guard on the guard: a scan that silently finds nothing proves nothing."""
    files = {entry[0] for entry in WRITTEN}

    assert len(WRITTEN) > 60
    assert "backend/parsers.py" in files
    assert "backend/routers/imports.py" in files
    assert "backend/capture_schema.py" in files


@pytest.mark.parametrize("source, line, message, action", WRITTEN)
def test_every_message_is_a_sentence_for_a_person(
    source: str, line: int, message: str, action: str
) -> None:
    where = f"{source}:{line}"

    assert message.strip(), f"{where}: empty message"
    assert message[0].isupper() or message[0] in "'“{", f"{where}: {message!r}"
    assert message.rstrip().endswith((".", "?")), f"{where}: {message!r}"
    assert len(message.split()) >= 4, f"{where}: too terse to be a sentence — {message!r}"


@pytest.mark.parametrize("source, line, message, action", WRITTEN)
def test_every_message_says_what_to_do_next(
    source: str, line: int, message: str, action: str
) -> None:
    """Constraint 7: an error the operator cannot act on is a dead end."""
    where = f"{source}:{line}"

    assert action.strip(), f"{where}: no action"
    assert action != message, f"{where}: the action just repeats the message"
    assert action.rstrip().endswith("."), f"{where}: {action!r}"
    assert len(action.split()) >= 3, f"{where}: {action!r}"


@pytest.mark.parametrize("source, line, message, action", WRITTEN)
def test_no_message_speaks_to_a_programmer(
    source: str, line: int, message: str, action: str
) -> None:
    spoken = _speaks_jargon(f"{message} {action}")

    assert spoken is None, f"{source}:{line}: '{spoken}' in {message!r} / {action!r}"


def test_the_stage_gate_actions_are_written_the_same_way() -> None:
    """Its actions come from a table, so the scan cannot see them at the raise."""
    for stage, action in stage_machine.STAGE_ACTIONS.items():
        assert action.rstrip().endswith("."), stage
        assert action[0].isupper(), stage
        assert len(action.split()) >= 3, stage
        assert _speaks_jargon(action) is None, f"{stage}: '{_speaks_jargon(action)}'"


# --------------------------------------------------------------------------
# The errors nobody wrote: the paths that answer by default
# --------------------------------------------------------------------------


def _error(response) -> dict:
    """The PRD §4 envelope, asserted to be exactly that shape on the way out."""
    body = response.json()
    assert set(body) == {"error"}, body
    assert set(body["error"]) == {"code", "message", "action"}, body
    return body["error"]


def test_a_mistyped_address_is_answered_in_english(client: TestClient) -> None:
    response = client.get("/api/frameworks-list")

    assert response.status_code == 404
    error = _error(response)
    assert error["message"] == "Narrative Lens does not have that address."
    assert error["action"]


def test_the_wrong_kind_of_request_is_answered_in_english(client: TestClient) -> None:
    response = client.delete("/api/health")

    assert response.status_code == 405
    error = _error(response)
    assert "does not do" in error["message"]
    assert "http" not in error["message"].lower()


def test_a_malformed_request_never_shows_a_field_dump(client: TestClient) -> None:
    """The default here is a list of validator objects. The operator gets a
    sentence, and the part that was wrong is named in ordinary words."""
    response = client.post("/api/frameworks", json={"name": "", "definition": {}})

    assert response.status_code == 422
    error = _error(response)
    assert error["code"] == "request_not_understood"
    assert "Narrative Lens could not make sense" in error["message"]
    for leak in ("type=", "loc", "ctx", "value_error", "[", "{'"):
        assert leak not in error["message"], leak


def test_a_fault_in_the_app_itself_is_still_a_sentence(monkeypatch) -> None:
    """The one message that must never say "Internal Server Error"."""
    from backend.routers import patterns as patterns_router

    def explode(*args, **kwargs):
        raise RuntimeError("a bug nobody has found yet")

    monkeypatch.setattr(patterns_router, "load_framework", explode)

    # raise_server_exceptions=False: this asks the app what it would send a
    # browser, rather than re-raising the fault into the test.
    with TestClient(app, raise_server_exceptions=False) as unguarded:
        response = unguarded.get("/api/patterns/1")

    assert response.status_code == 500
    error = _error(response)
    assert "Narrative Lens hit a problem" in error["message"]
    assert "a bug nobody has found yet" not in response.text
    for leak in ("Traceback", "RuntimeError", "Internal Server Error"):
        assert leak not in response.text, leak


def test_the_app_speaks_one_error_shape_everywhere(client: TestClient) -> None:
    """PRD §4 says the shape is the same everywhere, so it is checked that way:
    one written refusal, one framework refusal, one malformed request."""
    responses = [
        client.get("/api/frameworks/9999"),
        client.get("/api/nothing-here"),
        client.post("/api/capture", json={"framework_id": "not a number"}),
    ]

    for response in responses:
        assert response.status_code >= 400
        error = _error(response)
        assert error["code"] and error["message"] and error["action"]
