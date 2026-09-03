"""Alembic migration 001 — up, down, and agreement with the models.

Constraint 5 is additive-only migrations. The drift test below is the guard: if
someone changes ``backend/models.py`` without adding a revision, autogenerate
finds a difference and this test fails.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect

from backend.db import make_engine
from backend.models import Base

EXPECTED_TABLES = {
    "frameworks",
    "capture_links",
    "anecdotes",
    "significations",
    "import_jobs",
    "tags",
    # Added by the meaningfulness delta, phase D (revision 003).
    "interpretations",
    # Added by the meaningfulness delta, phase F (revision 005). A display
    # cache: deleting every row must leave the app correct, only slower.
    "translations",
}

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def alembic_config(db_url: str) -> Config:
    config = Config(str(REPO_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "backend" / "alembic"))
    config.set_main_option("sqlalchemy.url", db_url)
    return config


def _table_names(db_url: str) -> set[str]:
    engine = make_engine(db_url)
    try:
        return set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


def test_upgrade_head_creates_every_table(alembic_config: Config, db_url: str) -> None:
    command.upgrade(alembic_config, "head")

    tables = _table_names(db_url)
    assert tables >= EXPECTED_TABLES
    assert tables - EXPECTED_TABLES == {"alembic_version"}


def test_downgrade_base_removes_them_again(alembic_config: Config, db_url: str) -> None:
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")

    tables = _table_names(db_url)
    assert not (EXPECTED_TABLES & tables)


def test_upgrade_downgrade_upgrade_is_repeatable(alembic_config: Config, db_url: str) -> None:
    """A migration that only works once is a migration that will strand the app."""
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")

    assert _table_names(db_url) >= EXPECTED_TABLES


def test_migration_001_matches_the_models(alembic_config: Config, db_url: str) -> None:
    """No drift between the migration chain and ``backend/models.py``."""
    command.upgrade(alembic_config, "head")

    engine = make_engine(db_url)
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            diff = compare_metadata(context, Base.metadata)
    finally:
        engine.dispose()

    assert diff == [], (
        "backend/models.py and the migrations disagree. Constraint 5 forbids "
        f"editing an existing migration — add a new revision instead. Diff: {diff}"
    )


def test_the_four_value_input_method_survives_migration(
    alembic_config: Config, db_url: str
) -> None:
    """The CHECK constraint reaches the migrated database, not just the models."""
    command.upgrade(alembic_config, "head")

    engine = make_engine(db_url)
    try:
        check_clauses = [
            constraint["sqltext"]
            for constraint in inspect(engine).get_check_constraints("anecdotes")
        ]
    finally:
        engine.dispose()

    joined = " ".join(check_clauses)
    for value in ("typed", "voice", "paper", "imported"):
        assert value in joined, f"input_method value '{value}' missing from migrated CHECK"


def test_frameworks_keeps_edit_log_and_parent_link(alembic_config: Config, db_url: str) -> None:
    """The two columns v1.3 added to frameworks reach the database."""
    command.upgrade(alembic_config, "head")

    engine = make_engine(db_url)
    try:
        columns = {c["name"] for c in inspect(engine).get_columns("frameworks")}
    finally:
        engine.dispose()

    assert "edit_log_json" in columns
    assert "parent_framework_id" in columns
