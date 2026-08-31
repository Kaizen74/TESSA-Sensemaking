"""initial schema — the six tables of PRD §3

Creates frameworks (with edit_log_json and parent_framework_id), capture_links,
anecdotes (with the four-value input_method), significations, import_jobs and
tags.

Constraint 5 is additive-only migrations: never edit this file to change the
schema — add a new revision instead.

Revision ID: 001
Revises:
Create Date: 2026-08-14

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "frameworks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("definition_json", sa.JSON(), nullable=False),
        sa.Column("edit_log_json", sa.JSON(), nullable=False),
        sa.Column("parent_framework_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_framework_id"],
            ["frameworks.id"],
            name=op.f("fk_frameworks_parent_framework_id_frameworks"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_frameworks")),
    )
    op.create_table(
        "import_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=500), nullable=False),
        sa.Column("file_type", sa.String(length=20), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("stage", sa.String(length=30), nullable=False),
        sa.Column("normalised_json", sa.JSON(), nullable=True),
        sa.Column("column_mapping_json", sa.JSON(), nullable=True),
        sa.Column("segments_found", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "stage IN ('uploaded', 'organised', 'mapping_confirmed', 'proposed', 'done', 'failed')",
            name=op.f("ck_import_jobs_stage"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_import_jobs")),
    )
    op.create_table(
        "capture_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("framework_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["framework_id"],
            ["frameworks.id"],
            name=op.f("fk_capture_links_framework_id_frameworks"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_capture_links")),
        sa.UniqueConstraint("token", name=op.f("uq_capture_links_token")),
    )
    op.create_table(
        "anecdotes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("framework_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("title_auto", sa.String(length=200), nullable=True),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("entry_mode", sa.String(length=20), nullable=False),
        sa.Column("capture_link_id", sa.Integer(), nullable=True),
        sa.Column("input_method", sa.String(length=20), nullable=False),
        sa.Column("source_file", sa.String(length=500), nullable=True),
        sa.Column("source_locator", sa.String(length=500), nullable=True),
        sa.Column("import_job_id", sa.Integer(), nullable=True),
        sa.Column("respondent_group", sa.String(length=200), nullable=True),
        sa.Column("created_at_hour", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.CheckConstraint(
            "entry_mode IN ('admin', 'link', 'kiosk')", name=op.f("ck_anecdotes_entry_mode")
        ),
        sa.CheckConstraint(
            "input_method IN ('typed', 'voice', 'paper', 'imported')",
            name=op.f("ck_anecdotes_input_method"),
        ),
        sa.CheckConstraint(
            "status IN ('pending_validation', 'validated', 'rejected')",
            name=op.f("ck_anecdotes_status"),
        ),
        sa.ForeignKeyConstraint(
            ["capture_link_id"],
            ["capture_links.id"],
            name=op.f("fk_anecdotes_capture_link_id_capture_links"),
        ),
        sa.ForeignKeyConstraint(
            ["framework_id"], ["frameworks.id"], name=op.f("fk_anecdotes_framework_id_frameworks")
        ),
        sa.ForeignKeyConstraint(
            ["import_job_id"],
            ["import_jobs.id"],
            name=op.f("fk_anecdotes_import_job_id_import_jobs"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anecdotes")),
    )
    op.create_table(
        "significations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anecdote_id", sa.Integer(), nullable=False),
        sa.Column("signifier_id", sa.String(length=100), nullable=False),
        sa.Column("signifier_type", sa.String(length=20), nullable=False),
        sa.Column("value_json", sa.JSON(), nullable=False),
        sa.Column("ai_confidence", sa.Float(), nullable=True),
        sa.Column("signified_by", sa.String(length=50), nullable=False),
        sa.Column("validated_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "signifier_type IN ('triad', 'dyad', 'stones', 'mcq')",
            name=op.f("ck_significations_signifier_type"),
        ),
        sa.ForeignKeyConstraint(
            ["anecdote_id"], ["anecdotes.id"], name=op.f("fk_significations_anecdote_id_anecdotes")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_significations")),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anecdote_id", sa.Integer(), nullable=False),
        sa.Column("tag_text", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["anecdote_id"], ["anecdotes.id"], name=op.f("fk_tags_anecdote_id_anecdotes")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tags")),
    )


def downgrade() -> None:
    # Reverse dependency order so foreign keys never dangle.
    op.drop_table("tags")
    op.drop_table("significations")
    op.drop_table("anecdotes")
    op.drop_table("capture_links")
    op.drop_table("import_jobs")
    op.drop_table("frameworks")
