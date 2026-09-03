"""Constraint 9 — respondent anonymity is engineered, not promised.

These tests read the live SQLAlchemy metadata, so they keep working as the
schema grows: any future migration that adds a respondent identifier fails here
rather than in production. This is the guarantee that lets the on-screen
anonymity statement be literally true of the code.

This module is on the PRD §6 regression list and must stay green in every phase
from Phase 1 onward.
"""

from __future__ import annotations

import datetime as dt

import pytest
from sqlalchemy import inspect

from backend.models import Base, hour_rounded_now

#: Identifier families banned on every table without exception.
BANNED_EVERYWHERE = frozenset(
    {
        "ip",
        "ip_address",
        "ipaddress",
        "client_ip",
        "remote_addr",
        "remote_address",
        "user_agent",
        "useragent",
        "browser",
        "fingerprint",
        "browser_fingerprint",
        "device_id",
        "session_id",
        "email",
        "email_address",
    }
)

#: Additionally banned on tables that carry respondent-linked rows. ``name`` is
#: not banned globally because ``frameworks.name`` is the framework's own title
#: and ``import_jobs.filename`` is the operator's own uploaded file — neither
#: identifies a respondent. See PROGRESS.md "Decisions".
BANNED_ON_RESPONDENT_TABLES = frozenset(
    {
        "name",
        "full_name",
        "first_name",
        "last_name",
        "surname",
        "respondent_name",
        "username",
        "user_name",
        "employee_id",
        "staff_id",
    }
)

#: Tables whose rows are linked to an individual respondent.
#:
#: ``interpretations`` is deliberately not here. It carries no ``anecdote_id``
#: and no signification linkage (constraint 16), so no row in it is linked to a
#: respondent — which is also why an interpretation can never reach a landscape.
RESPONDENT_TABLES = frozenset({"anecdotes", "significations", "tags", "capture_links"})

ALL_TABLES = frozenset({"frameworks", "capture_links", "anecdotes", "significations",
                        "import_jobs", "tags",
                        # Added by the meaningfulness delta, phase D.
                        "interpretations",
                        # Added by the meaningfulness delta, phase F. Not a
                        # respondent table: it holds a machine's reading of a
                        # story, keyed by the story, and no identifier.
                        "translations"})


def _columns(table_name: str) -> set[str]:
    return {column.name.lower() for column in Base.metadata.tables[table_name].columns}


def test_the_schema_holds_exactly_the_tables_it_should() -> None:
    """PRD §3's six tables, plus the one the meaningfulness delta added.

    Still an equality check rather than a subset: a table nobody meant to add
    fails here, which is the point. Phase D's ``interpretations`` is named in
    ``ALL_TABLES`` above with the reason it is not respondent-bearing.
    """
    assert set(Base.metadata.tables) == set(ALL_TABLES)


def test_an_interpretation_has_no_route_to_a_respondent() -> None:
    """Constraint 16, read off the metadata rather than promised.

    The guarantee is structural: with no anecdote or signification column there
    is nothing for an aggregate to join on, so an interpretation cannot enter a
    landscape however the code above it is written.
    """
    columns = _columns("interpretations")

    for forbidden in ("anecdote_id", "signification_id", "story_id"):
        assert forbidden not in columns

    foreign = {
        key.column.table.name
        for key in Base.metadata.tables["interpretations"].foreign_keys
    }
    assert foreign == {"frameworks"}, foreign


@pytest.mark.parametrize("table_name", sorted(ALL_TABLES))
def test_no_banned_identifier_on_any_table(table_name: str) -> None:
    """No IP, user agent, fingerprint, device/session id or email anywhere."""
    offending = _columns(table_name) & BANNED_EVERYWHERE
    assert not offending, (
        f"Constraint 9 violated: table '{table_name}' carries respondent "
        f"identifier column(s) {sorted(offending)}."
    )


@pytest.mark.parametrize("table_name", sorted(RESPONDENT_TABLES))
def test_no_personal_name_on_respondent_tables(table_name: str) -> None:
    """No name-family column on a table whose rows are linked to a respondent."""
    offending = _columns(table_name) & BANNED_ON_RESPONDENT_TABLES
    assert not offending, (
        f"Constraint 9 violated: respondent-bearing table '{table_name}' "
        f"carries name column(s) {sorted(offending)}."
    )


@pytest.mark.parametrize("table_name", sorted(RESPONDENT_TABLES))
def test_no_new_name_suffixed_column_on_respondent_tables(table_name: str) -> None:
    """Catch identifiers this test did not anticipate, e.g. ``manager_name``.

    ``filename``-style columns are excluded because the suffix check targets
    ``*_name``, and no respondent table is permitted one at all.
    """
    offending = {column for column in _columns(table_name) if column.endswith("_name")}
    assert not offending, (
        f"Constraint 9 violated: respondent-bearing table '{table_name}' gained "
        f"name-like column(s) {sorted(offending)}."
    )


def test_anecdotes_has_no_precise_timestamp() -> None:
    """Constraint 9: respondent time is hour-rounded, so no exact clock exists.

    ``created_at_hour`` is the only time column on ``anecdotes``; a plain
    ``created_at`` would reintroduce minute-level correlation.
    """
    time_columns = {c for c in _columns("anecdotes") if "created" in c or "timestamp" in c}
    assert time_columns == {"created_at_hour"}


def test_hour_rounded_now_zeroes_sub_hour_precision() -> None:
    """The only writer of ``created_at_hour`` carries no sub-hour information."""
    stamped = hour_rounded_now()
    assert stamped.minute == 0
    assert stamped.second == 0
    assert stamped.microsecond == 0


def test_hour_rounded_now_truncates_rather_than_rounds_up() -> None:
    """13:59 must land on 13:00, never 14:00 — truncation, not rounding."""
    stamped = hour_rounded_now()
    now = dt.datetime.now(dt.UTC).replace(tzinfo=None)
    assert stamped <= now
    assert now - stamped < dt.timedelta(hours=1)


def test_anecdote_default_stamps_hour_rounded_time(session) -> None:  # noqa: ANN001
    """A row written through the ORM gets an hour-rounded stamp automatically."""
    from backend.models import Anecdote, Framework

    framework = Framework(name="Pilot", version=1, definition_json={}, edit_log_json=[])
    session.add(framework)
    session.flush()

    anecdote = Anecdote(
        framework_id=framework.id,
        text="A story about a late handover.",
        source_type="capture",
        entry_mode="admin",
        input_method="typed",
    )
    session.add(anecdote)
    session.commit()

    assert anecdote.created_at_hour.minute == 0
    assert anecdote.created_at_hour.second == 0
    assert anecdote.created_at_hour.microsecond == 0


def test_migrated_database_matches_the_identifier_rules(engine) -> None:  # noqa: ANN001
    """The rules hold against the real database, not just the model metadata."""
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        columns = {c["name"].lower() for c in inspector.get_columns(table_name)}
        assert not (columns & BANNED_EVERYWHERE)
        if table_name in RESPONDENT_TABLES:
            assert not (columns & BANNED_ON_RESPONDENT_TABLES)
