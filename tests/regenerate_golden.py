"""Rewrite the goldens. Run deliberately, never automatically.

    python -m tests.regenerate_golden              # all three
    python -m tests.regenerate_golden participant  # only the named one

A golden that regenerates itself when it fails is not a golden — it is a
comment. So this is a separate command a person has to type, and its whole
output is a diff for review: if the numbers moved and you did not mean them to,
that diff is the bug report.

Three files come out of it: the 2D pattern aggregate under ``signified_by=all``,
held byte-identical; the same twenty stories under the delta's participant
default, also byte-identical; and the landscape peaks, held to ±0.02.

The selector argument exists because of the meaningfulness delta, whose §6
forbids regenerating a pre-existing baseline during any of its phases. Naming
one golden lets a new one be written without touching the files that must not
move.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from backend.db import get_session, make_engine
from backend.main import app
from backend.models import Base
from tests.test_landscape_golden import PEAKS_GOLDEN, produce_peaks
from tests.test_patterns_golden import (
    GOLDEN,
    PARTICIPANT_GOLDEN,
    produce,
    produce_participant,
)


def main(only: str | None = None) -> None:
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

        # A fresh client per golden, each on its own twenty stories rather than
        # on forty accumulated from the run before it.
        app.dependency_overrides[get_session] = override
        try:
            written: list[tuple[Path, str]] = []
            if only in (None, "aggregate"):
                with TestClient(app) as client:
                    written.append((GOLDEN, produce(client)))
            if only in (None, "participant"):
                with TestClient(app) as client:
                    written.append((PARTICIPANT_GOLDEN, produce_participant(client)))
            if only in (None, "peaks"):
                with TestClient(app) as client:
                    written.append((PEAKS_GOLDEN, produce_peaks(client)))
        finally:
            app.dependency_overrides.clear()
            engine.dispose()

    if not written:
        raise SystemExit(f"no golden called {only!r}; try aggregate, participant or peaks")

    for path, content in written:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(Path.cwd())} ({len(content)} bytes)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
