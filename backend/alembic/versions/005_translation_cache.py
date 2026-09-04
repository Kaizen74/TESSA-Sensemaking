"""translations — a read-time display cache, and nothing more

Spec delta §3, the migration that delta calls "004". Numbered 005 here because
migrations are numbered in the order they are applied; see PROGRESS.md
"Decisions" and the note in ``003_interpretations.py``.

Additive, per constraint 5: one new table, nothing existing touched.

**This table is a cache.** Deleting every row must leave the app fully correct,
only slower — and ``tests/test_translation_readtime.py`` asserts exactly that,
comparing every pattern, landscape and export byte for byte across a wipe. That
test is the reason this table is allowed to exist at all: a cache that fails it
has stopped being a cache and become the record, which is the failure
constraint 15 names.

The unique constraint is what makes it a cache rather than a log: one
translation per story per target language, replaced rather than accumulated.

Revision ID: 005
Revises: 004
Create Date: 2026-09-03

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anecdote_id", sa.Integer(), nullable=False),
        sa.Column("target_language_code", sa.String(length=35), nullable=False),
        sa.Column("translated_text", sa.Text(), nullable=False),
        sa.Column("translated_at", sa.DateTime(), nullable=False),
        sa.Column("model_used", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["anecdote_id"],
            ["anecdotes.id"],
            name=op.f("fk_translations_anecdote_id_anecdotes"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_translations")),
        sa.UniqueConstraint(
            "anecdote_id",
            "target_language_code",
            name=op.f("uq_translations_anecdote_id_target_language_code"),
        ),
    )


def downgrade() -> None:
    op.drop_table("translations")
