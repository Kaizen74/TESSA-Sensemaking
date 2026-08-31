"""Constraint 9 on the remote path (PRD §6 Phase 4: identifier-absence test).

Phase 1's ``tests/test_schema_absence.py`` proves the *schema* has nowhere to
put a respondent identifier. That was enough while every story was typed on the
operator's own laptop. From Phase 4 a story arrives from a stranger's phone
across a network, carrying headers that identify it — so this module proves the
other half: that the request path never reads, stores, or echoes any of them.

The anonymity statement on the respondent's screen says "we do not record your
name, your email, your device, or your network address — none of these exist
anywhere in this app". These tests are what make that sentence true of the code
rather than merely printed on it.
"""

from __future__ import annotations

import inspect

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from backend.models import Anecdote, Signification
from backend.rate_limit import reset_all
from backend.routers import public

TRIAD = {"id": "pressure", "title": "What drove this?", "corners": ["Speed", "Care", "Cost"]}
DEFINITION = {"prompt_text": "Tell us a story.", "triads": [TRIAD]}

#: Headers a real phone sends that would identify it. Every request below
#: carries the lot, so any accidental capture has something to catch.
IDENTIFYING_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) TESTUA",
    "X-Forwarded-For": "203.0.113.77",
    "X-Real-IP": "203.0.113.77",
    "Forwarded": "for=203.0.113.77;proto=https",
    "Referer": "https://example.invalid/where-they-came-from",
    "Cookie": "session=abc123; who=someone",
    "X-Device-Id": "device-abcdef-123456",
    "From": "someone@example.invalid",
}

#: Fragments that must not appear anywhere in the stored data or the response.
IDENTIFYING_FRAGMENTS = (
    "203.0.113.77",
    "TESTUA",
    "iPhone",
    "Mozilla",
    "abc123",
    "device-abcdef-123456",
    "someone@example.invalid",
    "example.invalid",
)


@pytest.fixture(autouse=True)
def _clear_limits():
    reset_all()
    yield
    reset_all()


def _framework(client: TestClient) -> dict:
    return client.post(
        "/api/frameworks", json={"name": "Remote", "definition": DEFINITION}
    ).json()


def _link(client: TestClient, framework_id: int) -> dict:
    return client.post(
        "/api/capture-links", json={"framework_id": framework_id}
    ).json()


def _submit(client: TestClient, token: str) -> object:
    return client.post(
        f"/api/public/capture/{token}",
        headers=IDENTIFYING_HEADERS,
        json={
            "text": "A story told from a phone.",
            "input_method": "voice",
            "significations": [
                {"signifier_id": "pressure", "value": {"Speed": 0.5, "Care": 0.3, "Cost": 0.2}}
            ],
        },
    )


class TestNothingIdentifyingIsStored:
    def test_a_remote_story_stores_no_header_data(self, client: TestClient, session) -> None:  # noqa: ANN001
        framework = _framework(client)
        link = _link(client, framework["id"])

        assert _submit(client, link["token"]).status_code == 201

        stored = session.scalars(select(Anecdote)).one()
        blob = " ".join(
            str(value) for value in stored.__dict__.values() if value is not None
        )
        for fragment in IDENTIFYING_FRAGMENTS:
            assert fragment not in blob, f"'{fragment}' reached the anecdote row"

    def test_significations_carry_nothing_identifying_either(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        framework = _framework(client)
        link = _link(client, framework["id"])
        _submit(client, link["token"])

        for row in session.scalars(select(Signification)).all():
            blob = f"{row.value_json} {row.signified_by}"
            for fragment in IDENTIFYING_FRAGMENTS:
                assert fragment not in blob

    def test_nothing_identifying_is_anywhere_in_the_database(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        """Sweep every column of every table, not just the ones we expect."""
        framework = _framework(client)
        link = _link(client, framework["id"])
        _submit(client, link["token"])
        session.commit()

        tables = [
            row[0]
            for row in session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
        ]

        for table in tables:
            rows = session.execute(text(f"SELECT * FROM {table}")).fetchall()  # noqa: S608
            blob = " ".join(str(cell) for row in rows for cell in row if cell is not None)
            for fragment in IDENTIFYING_FRAGMENTS:
                assert fragment not in blob, f"'{fragment}' found in table '{table}'"

    def test_the_response_echoes_nothing_identifying(self, client: TestClient) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        response = _submit(client, link["token"])

        body = response.text
        for fragment in IDENTIFYING_FRAGMENTS:
            assert fragment not in body

    def test_the_questions_response_echoes_nothing_identifying(
        self, client: TestClient
    ) -> None:
        framework = _framework(client)
        link = _link(client, framework["id"])

        response = client.get(
            f"/api/public/capture/{link['token']}", headers=IDENTIFYING_HEADERS
        )

        for fragment in IDENTIFYING_FRAGMENTS:
            assert fragment not in response.text


class TestThePathCannotReachForAnIdentifier:
    """Structural guards: not "it doesn't today", but "it has no way to"."""

    def test_no_public_handler_accepts_a_request_object(self) -> None:
        """Taking a ``Request`` would put every header within arm's reach."""
        for name, function in vars(public).items():
            if not callable(function) or not hasattr(function, "__annotations__"):
                continue
            if getattr(function, "__module__", None) != public.__name__:
                continue
            annotations = inspect.get_annotations(function, eval_str=False)
            for parameter, annotation in annotations.items():
                rendered = str(annotation)
                assert "Request" not in rendered, (
                    f"{name}() takes {parameter}: {rendered} — a public handler "
                    "must not be able to see request headers (constraint 9)"
                )

    def test_the_public_module_never_mentions_header_access(self) -> None:
        """A grep-level guard against a future edit reaching for client data."""
        source = inspect.getsource(public)
        for forbidden in (
            ".headers",
            ".client.host",
            "request.client",
            "x-forwarded-for",
            "X-Forwarded-For",
            "user_agent",
            "User-Agent",
            "remote_addr",
        ):
            assert forbidden not in source, (
                f"backend/routers/public.py mentions '{forbidden}' — the public "
                "path must not read anything about the requester"
            )

    def test_the_submission_model_rejects_unknown_fields(self, client: TestClient) -> None:
        """A browser cannot volunteer an identifier alongside the story."""
        framework = _framework(client)
        link = _link(client, framework["id"])

        for smuggled in ("ip", "user_agent", "email", "name", "device_id", "session_id"):
            response = client.post(
                f"/api/public/capture/{link['token']}",
                json={"text": "A story.", smuggled: "identifying value"},
            )
            assert response.status_code == 422, f"'{smuggled}' was accepted"

    def test_rate_limiting_is_keyed_by_token_not_by_requester(self) -> None:
        """The one place a naive implementation would reach for a client IP."""
        source = inspect.getsource(public)
        assert "_rate_limit(fetch_limiter, token)" in source
        assert "_rate_limit(submit_limiter, token)" in source


class TestTimingCarriesNothing:
    def test_remote_stories_are_hour_rounded_like_every_other(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        """Minute-level timing would let a phone's arrival be correlated."""
        framework = _framework(client)
        link = _link(client, framework["id"])
        _submit(client, link["token"])

        stored = session.scalars(select(Anecdote)).one()
        assert stored.created_at_hour.minute == 0
        assert stored.created_at_hour.second == 0
        assert stored.created_at_hour.microsecond == 0

    def test_two_stories_in_the_same_hour_are_indistinguishable_by_time(
        self, client: TestClient, session
    ) -> None:  # noqa: ANN001
        framework = _framework(client)
        link = _link(client, framework["id"])
        _submit(client, link["token"])
        _submit(client, link["token"])

        stamps = {row.created_at_hour for row in session.scalars(select(Anecdote)).all()}
        assert len(stamps) == 1, "arrival order must not be recoverable from the clock"
