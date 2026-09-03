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
    UniqueConstraint,
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

#: How the app came to believe a story's language (delta §3). Mirrors
#: ``backend.languages.LANGUAGE_SOURCES``; held here too so the CHECK constraint
#: and the schema tests read from the models the way every other vocabulary does.
LANGUAGE_SOURCES = ("respondent_selected", "admin_entered", "unknown")

#: Which picture a room was looking at when it wrote something down (delta §3).
INTERPRETATION_VIEW_KINDS = ("landscape", "contour", "supporting")


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
    #: The name the storyteller gave their own story (delta §3, migration 002).
    #: Kept beside ``title_auto`` rather than over it: which of the two a reader
    #: is looking at is exactly the distinction this column exists to make.
    respondent_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    #: The language this story was told in — BCP-47, e.g. "ms", "zh-Hans"
    #: (delta §3, constraint 15). Null means nobody recorded one, which reads as
    #: unknown and never as English.
    language_code: Mapped[str | None] = mapped_column(String(35), nullable=True)
    #: How the app came to believe that. A respondent who chose their language
    #: and an operator who guessed while typing up paper are making claims of
    #: very different strength, and a column holding only the tag would flatten
    #: the two.
    language_source: Mapped[str | None] = mapped_column(String(30), nullable=True)
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


class Interpretation(Base):
    """What a room concluded about a pattern, in the room's own words.

    Constraint 16 in table form. Note what is *absent*: no ``anecdote_id``, no
    ``signification_id``, no numeric value, no place for a marker. That absence
    is the design. An interpretation is an artefact recorded alongside a
    pattern, never a reading merged into one — it cannot enter the KDE because
    there is no column through which it could.

    What it does carry is enough to say what was on screen when the room spoke:
    the framework version, the signifier being looked at, the filters in force
    and the moment. Six months later that is the difference between a sentence
    somebody wrote and a sentence you can put back in front of the picture it
    was about.

    ``interpretation_text`` is free text on purpose (delta §9 assumption 5). A
    room's conclusion resists a schema, and forcing one would be the same error
    as machine-coding a story.
    """

    __tablename__ = "interpretations"
    __table_args__ = (
        CheckConstraint(
            _in_clause("view_kind", INTERPRETATION_VIEW_KINDS), name="view_kind"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    #: The exact framework version the room was reading. No lineage pooling: a
    #: conclusion about version 1's wording is not about version 2's.
    framework_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("frameworks.id"), nullable=False
    )
    #: Which triad or question was on screen. Null for the supporting charts,
    #: which are about the set rather than about one signifier.
    signifier_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    #: The filters in force, exactly as the endpoint received them.
    filter_state_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    view_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    #: What the room called itself — "Ops workshop, March". Optional.
    session_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    interpretation_text: Mapped[str] = mapped_column(Text, nullable=False)
    #: Exact, not hour-rounded. Constraint 9 protects respondents, and this row
    #: carries no respondent link at all; a facilitator wants the order the room
    #: said things in.
    recorded_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow
    )
    #: How many people were in the room, when anybody counted.
    participant_count: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Translation(Base):
    """A cached read-time translation of one story into one language.

    Constraint 15 in table form, and the constraint turns almost entirely on
    what this table *is not*. It is not the story. It is not a signification.
    Nothing computes from it, nothing exports from it, and Stage B never sees
    it. It exists so that reading the same story twice does not cost two API
    calls — and that is the whole of its job.

    The test of that claim is blunt and lives in
    ``tests/test_translation_readtime.py``: delete every row here and the app
    must be fully correct, only slower. Every pattern, every landscape, every
    export byte-identical. A cache that failed that test would have stopped
    being a cache and started being the record.

    ``model_used`` is kept because a translation is a machine's reading of
    somebody's words, and six months on the only honest answer to "who said
    that?" is the name of the model that said it.
    """

    __tablename__ = "translations"
    # One translation per story per target language, replaced rather than
    # accumulated — which is what makes this a cache and not a log. No explicit
    # name: the ``uq`` naming convention builds it from the columns.
    __table_args__ = (UniqueConstraint("anecdote_id", "target_language_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    anecdote_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("anecdotes.id"), nullable=False
    )
    target_language_code: Mapped[str] = mapped_column(String(35), nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow
    )
    #: Which model produced it. A translation is somebody else's reading of a
    #: person's words, and the reader deserves to know whose.
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)


class Tag(Base):
    """A free-text tag the analyst attaches to a story."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    anecdote_id: Mapped[int] = mapped_column(Integer, ForeignKey("anecdotes.id"), nullable=False)
    tag_text: Mapped[str] = mapped_column(String(100), nullable=False)
