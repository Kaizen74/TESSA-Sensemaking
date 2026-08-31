"""Database engine and session plumbing (constraint 4: SQLite + local files)."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend import settings


def _connect_args(url: str) -> dict:
    """SQLite needs ``check_same_thread=False`` to serve requests from a pool."""
    return {"check_same_thread": False} if url.startswith("sqlite") else {}


def make_engine(url: str | None = None) -> Engine:
    """Build an engine, enabling SQLite foreign-key enforcement.

    SQLite ignores ``REFERENCES`` clauses unless ``PRAGMA foreign_keys`` is on,
    and it is off by default for every new connection.
    """
    resolved = url or settings.database_url()
    engine = create_engine(resolved, connect_args=_connect_args(resolved), future=True)

    if resolved.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _connection_record):  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = make_engine()

SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False, future=True)


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a session that always closes."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
