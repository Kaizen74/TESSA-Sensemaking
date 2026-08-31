"""The six-table schema from PRD §3.

Two constraints shape this module directly:

* **Constraint 9** — respondent anonymity is engineered, not promised. No IP,
  fingerprint, user agent, name, or email column exists on any respondent-bearing
  table, and respondent timestamps are hour-rounded by :func:`hour_rounded_now`,
  which is the only writer of ``anecdotes.created_at_hour``. ``tests/
  test_schema_absence.py`` enforces both halves of this against the live
  metadata, so the on-screen anonymity statement stays literally true of the code.
* **Constraint 5** — additive-only migrations. Changing a column here means a new
  Alembic revision, never an edit to an existing one.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Deterministic constraint names. SQLite cannot ALTER a constraint in place, so
# Alembic needs batch mode with predictable names to stay additive later.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Vocabularies from PRD §3. Held as tuples so both the CHECK constraints and the
# tests read from one source.
ENTRY_MODES = ("admin", "link", "kiosk")
INPUT_METHODS = ("typed", "voice", "paper", "imported")
ANECDOTE_STATUSES = ("pending_validation", "validated", "rejected")
IMPORT_STAGES = ("uploaded", "organised", "mapping_confirmed", "proposed", "done", "failed")
SIGNIFIER_TYPES = ("triad", "dyad", "stones", "mcq")

#: The only ``kind`` an edit-log entry may carry. A meaning change creates a new
#: framework row rather than a log entry (PRD §3).
EDIT_LOG_KINDS = ("wording_fix",)


def _in_clause(column: str, allowed: tuple[str, ...]) -> str:
    """Render a SQL ``IN`` predicate for a CHECK constraint."""
    values = ", ".join(f"'{value}'" for value in allowed)
    return f"{column} IN ({values})"


def utcnow() -> dt.datetime:
    """Naive UTC now, for operator-side records that carry no respondent link."""
    return dt.datetime.now(dt.UTC).replace(tzinfo=None)


def hour_rounded_now() -> dt.datetime:
    """Naive UTC now truncated to the hour (constraint 9).

    Minutes, seconds and microseconds are zeroed, so a stored value carries no
    sub-hour information that could help correlate a story with the person who
    told it. This is the only function that may write
    ``anecdotes.created_at_hour``.
    """
    return utcnow().replace(minute=0, second=0, microsecond=0)


class Base(DeclarativeBase):
    """Declarative base carrying the shared naming convention."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Framework(Base):
    """A version of the question set respondents see.

    ``parent_framework_id`` links version n+1 back to n. A *wording fix* appends
    to ``edit_log_json`` in place; a *meaning change* creates a new row. Anecdotes
    stay bound to the framework whose wording they actually answered.
    """

    __tablename__ = "frameworks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    definition_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    edit_log_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    parent_framework_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("frameworks.id"), nullable=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class CaptureLink(Base):
    """A token-gated capture URL pointing at one exact framework version."""

    __tablename__ = "capture_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    framework_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("frameworks.id"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    revoked_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)


class Anecdote(Base):
    """One story, bound to the exact framework version it was told against.

    Deliberately absent: ip, user_agent, email, name (constraint 9).
    """

    __tablename__ = "anecdotes"
    __table_args__ = (
        CheckConstraint(_in_clause("entry_mode", ENTRY_MODES), name="entry_mode"),
        CheckConstraint(_in_clause("input_method", INPUT_METHODS), name="input_method"),
        CheckConstraint(_in_clause("status", ANECDOTE_STATUSES), name="status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    framework_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("frameworks.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    title_auto: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entry_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    capture_link_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("capture_links.id"), nullable=True
    )
    input_method: Mapped[str] = mapped_column(String(20), nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_locator: Mapped[str | None] = mapped_column(String(500), nullable=True)
    import_job_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("import_jobs.id"), nullable=True
    )
    respondent_group: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at_hour: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=hour_rounded_now
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending_validation")


class Signification(Base):
    """One respondent (or validated AI) placement on one signifier.

    ``value_json`` shape by ``signifier_type``: triad barycentric summing to 1.0;
    dyad 0–1; stones ``[{label, x, y}]``; mcq ``{selected: []}``.
    """

    __tablename__ = "significations"
    __table_args__ = (
        CheckConstraint(_in_clause("signifier_type", SIGNIFIER_TYPES), name="signifier_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    anecdote_id: Mapped[int] = mapped_column(Integer, ForeignKey("anecdotes.id"), nullable=False)
    signifier_id: Mapped[str] = mapped_column(String(100), nullable=False)
    signifier_type: Mapped[str] = mapped_column(String(20), nullable=False)
    value_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    signified_by: Mapped[str] = mapped_column(String(50), nullable=False)
    validated_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)


class ImportJob(Base):
    """One uploaded file moving through the two-stage ingestion machine."""

    __tablename__ = "import_jobs"
    __table_args__ = (CheckConstraint(_in_clause("stage", IMPORT_STAGES), name="stage"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    stage: Mapped[str] = mapped_column(String(30), nullable=False, default="uploaded")
    normalised_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    column_mapping_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    segments_found: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False, default=utcnow)


class Tag(Base):
    """A free-text tag the analyst attaches to a story."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    anecdote_id: Mapped[int] = mapped_column(Integer, ForeignKey("anecdotes.id"), nullable=False)
    tag_text: Mapped[str] = mapped_column(String(100), nullable=False)
