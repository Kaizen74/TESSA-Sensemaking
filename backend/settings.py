"""Runtime settings.

Constraint 7 (non-technical operator) forbids config editing, so every value
here has a working default. Environment variables exist for the test suite and
for developers, never as something the operator is expected to set.
"""

from __future__ import annotations

import os
from pathlib import Path

#: Repository root — the directory holding ``pyproject.toml``.
ROOT_DIR = Path(__file__).resolve().parent.parent

#: Where the SQLite file and any future local artefacts live (constraint 4).
DATA_DIR = Path(os.environ.get("NL_DATA_DIR", ROOT_DIR / "data"))

#: Port for the local server. See PROGRESS.md "Decisions" for why 8756.
PORT = int(os.environ.get("NL_PORT", "8756"))

HOST = os.environ.get("NL_HOST", "127.0.0.1")


def database_url() -> str:
    """Return the SQLAlchemy URL for the local SQLite database."""
    override = os.environ.get("NL_DATABASE_URL")
    if override:
        return override
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DATA_DIR / 'narrative_lens.db'}"
