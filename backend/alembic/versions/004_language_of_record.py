"""language_code and language_source — the language a story was told in

Spec delta §3, the migration that delta calls "003". It is numbered 004 here
because migrations are numbered in the order they are applied and phase D landed
first; see PROGRESS.md "Decisions" and the note in ``003_interpretations.py``.

Additive, per constraint 5: two nullable columns on ``anecdotes``, nothing
existing touched. Every story already in the database keeps a null language,
which reads as unknown — not as English. A backfill guessing at the language of
stories already told would be inventing the very record constraint 15 says must
be original.

No CHECK constraint on ``language_source``. SQLite cannot add one to an existing
table without rebuilding it, which is exactly the kind of rewrite additive-only
migrations exist to avoid, and it would be the first time this schema rebuilt a
table holding real stories. The vocabulary is enforced where
``significations.signified_by``'s is — in the schema layer above.

No column stores a translation, and none may: translation is read-time and
display-only (constraint 15). Phase F adds a separate cache table whose deletion
must change nothing.

Revision ID: 004
Revises: 003
Create Date: 2026-09-03

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("anecdotes", sa.Column("language_code", sa.String(length=35), nullable=True))
    op.add_column(
        "anecdotes", sa.Column("language_source", sa.String(length=30), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("anecdotes", "language_source")
    op.drop_column("anecdotes", "language_code")
