"""Rewrite the pattern golden. Run deliberately, never automatically.

    python -m tests.regenerate_golden

A golden that regenerates itself when it fails is not a golden — it is a
comment. So this is a separate command a person has to type, and its whole
output is a diff for review: if the numbers moved and you did not mean them to,
that diff is the bug report.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from backend.db import get_session, make_engine
from backend.main import app
from backend.models import Base
from tests.test_patterns_golden import GOLDEN, produce


def main() -> None:
    with TemporaryDirectory() as directory:
        engine = make_engine(f"sqlite:///{Path(directory) / 'golden.db'}")
        Base.metadata.create_all(engine)
        factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)

        def override() -> Iterator[Session]:
            session = factory()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_session] = override
        try:
            with TestClient(app) as client:
                produced = produce(client)
        finally:
            app.dependency_overrides.clear()
            engine.dispose()

    GOLDEN.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN.write_text(produced, encoding="utf-8")
    print(f"wrote {GOLDEN.relative_to(Path.cwd())} ({len(produced)} bytes)")


if __name__ == "__main__":
    main()
