"""respondent_title — the name the storyteller gave their own story

Spec delta §3, migration 002. Additive, per constraint 5: a nullable column on
``anecdotes``, and nothing else touched.

``title_auto`` stays exactly as it is. The display rule is ``respondent_title``
when present, else ``title_auto`` — both are kept, and both are exported, so a
reader can always see which one they are looking at. Overwriting the machine's
title with the person's would destroy the distinction the delta exists to make.

Revision ID: 002
Revises: 001
Create Date: 2026-09-02

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("anecdotes", sa.Column("respondent_title", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("anecdotes", "respondent_title")
