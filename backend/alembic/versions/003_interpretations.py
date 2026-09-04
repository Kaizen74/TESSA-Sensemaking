"""interpretations — what a room concluded, stored as an artefact

Spec delta §3, the migration that delta calls "005". It is numbered 003 here
because the delta's own sentence is "four new migrations, applied in phase
order", and phase D lands before phases E and F: this is the third migration to
be applied, so it is the third revision in the chain. Alembic follows
``down_revision``, not the filename, but a chain that ran 001 → 002 → 005 → 003
would be a puzzle for whoever maintains this next. See PROGRESS.md "Decisions".

Additive, per constraint 5: one new table, nothing existing touched.

Constraint 16 is enforced by what this table does *not* have. There is no
``anecdote_id`` and no signification linkage, so an interpretation has no route
into the KDE, into a landscape, or into any aggregate — not by policy, but
because no column exists to carry it there.

Revision ID: 003
Revises: 002
Create Date: 2026-09-02

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "interpretations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("framework_id", sa.Integer(), nullable=False),
        sa.Column("signifier_id", sa.String(length=100), nullable=True),
        sa.Column("filter_state_json", sa.JSON(), nullable=False),
        sa.Column("view_kind", sa.String(length=20), nullable=False),
        sa.Column("session_label", sa.String(length=200), nullable=True),
        sa.Column("interpretation_text", sa.Text(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("participant_count", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "view_kind IN ('landscape', 'contour', 'supporting')",
            name=op.f("ck_interpretations_view_kind"),
        ),
        sa.ForeignKeyConstraint(
            ["framework_id"],
            ["frameworks.id"],
            name=op.f("fk_interpretations_framework_id_frameworks"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_interpretations")),
    )


def downgrade() -> None:
    op.drop_table("interpretations")
