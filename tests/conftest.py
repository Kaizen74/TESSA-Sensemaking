"""Shared fixtures.

Every test runs against a throwaway SQLite file, never the operator's
``data/narrative_lens.db``.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.db import get_session, make_engine
from backend.main import app
from backend.models import Base


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
