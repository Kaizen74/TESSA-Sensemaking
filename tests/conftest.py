"""Shared fixtures.

Every test runs against a throwaway SQLite file, never the operator's
``data/narrative_lens.db``.
"""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from backend import ai_client

# Constraint 6: the whole suite runs with zero network. Set before anything
# imports the client, so no test can reach api.anthropic.com even by mistake.
# ``setdefault`` leaves an explicit NL_MOCK_AI=0 alone, which is how the live
# path gets exercised deliberately rather than accidentally.
os.environ.setdefault(ai_client.MOCK_ENV_VAR, "1")

from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.db import get_session, make_engine
from backend.main import app
from backend.models import Base


def median_ms(call, samples: int = 5) -> float:
    """How long a call takes, measured as a median rather than a single sample.

    PRD §4 budgets 200ms for the non-AI endpoints. That is a promise about what
    the operator feels, and this suite runs on shared machines where any one
    sample can be stolen by whatever else is running — a first call also pays
    for caches it will never pay for again. A median over a handful of calls is
    the honest reading, and a real regression moves it; a busy neighbour does
    not.
    """
    timings = []
    for _ in range(samples):
        start = time.perf_counter()
        call()
        timings.append((time.perf_counter() - start) * 1000)
    timings.sort()
    return timings[len(timings) // 2]


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Path to a fresh SQLite file for one test."""
    return tmp_path / "test.db"


@pytest.fixture
def db_url(db_path: Path) -> str:
    return f"sqlite:///{db_path}"


@pytest.fixture
def engine(db_url: str) -> Iterator[Engine]:
    """Engine over an empty database with the schema created from the models."""
    eng = make_engine(db_url)
    Base.metadata.create_all(eng)
    try:
        yield eng
    finally:
        eng.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    with factory() as s:
        yield s


@pytest.fixture
def client(engine: Engine) -> Iterator[TestClient]:
    """API client wired to the test database, never the operator's own."""
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    def override_get_session() -> Iterator[Session]:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
