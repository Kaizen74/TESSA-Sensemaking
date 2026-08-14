"""Shared fixtures.

Every test runs against a throwaway SQLite file, never the operator's
``data/narrative_lens.db``.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.db import make_engine
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
