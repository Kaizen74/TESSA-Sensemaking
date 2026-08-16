"""Rewrite both goldens. Run deliberately, never automatically.

    python -m tests.regenerate_golden

A golden that regenerates itself when it fails is not a golden — it is a
comment. So this is a separate command a person has to type, and its whole
output is a diff for review: if the numbers moved and you did not mean them to,
that diff is the bug report.

Two files come out of it: the 2D pattern aggregate, held byte-identical, and the
landscape peaks, held to ±0.02.
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
from tests.test_landscape_golden import PEAKS_GOLDEN, produce_peaks
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
            # A second client on a second database, so the landscape golden is
            # built from its own twenty stories rather than from forty.
            with TestClient(app) as client:
                peaks = produce_peaks(client)
        finally:
            app.dependency_overrides.clear()
            engine.dispose()

    for path, content in ((GOLDEN, produced), (PEAKS_GOLDEN, peaks)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(Path.cwd())} ({len(content)} bytes)")


if __name__ == "__main__":
    main()
