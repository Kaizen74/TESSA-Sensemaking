"""What counts as data, in one place (constraint 1).

An anecdote exists in three conditions, and only one of them is the dataset:

* ``pending_validation`` — it is in the validation queue. A person has not yet
  looked at what the AI proposed for it.
* ``validated`` — a person has said yes. **This, and only this, is the data.**
  Patterns, landscapes, exports, and counts all read from here.
* ``rejected`` — a person has said no. It stays on disk so the import remains
  auditable, and it is never data.

Having one module say this is the point. Constraint 1 promises no AI-proposed
signification reaches the dataset without explicit human validation, and
acceptance criterion 7 requires a test proving it. A promise spread across a
dozen ``.where(...)`` clauses cannot be tested; a single filter can, and
``tests/test_no_bypass.py`` tests it — behaviourally, and structurally by
asserting that the two places allowed to write ``validated`` are the only two
that do.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Row, Select

from backend.models import Anecdote

STATUS_PENDING = "pending_validation"
STATUS_VALIDATED = "validated"
STATUS_REJECTED = "rejected"

#: How the read path carries a story and an answer: a row of columns rather than
#: a mapped object.
#:
#: Attribute access is identical — ``row.id``, ``row.respondent_group``,
#: ``row.value_json`` — which is why every reader downstream works the same way
#: on either. What differs is that SQLAlchemy builds no instrumented entity per
#: row, and at five thousand stories building twenty thousand of them was most
#: of what a patterns request spent its time on (PRD §4's 200ms budget).
#:
#: Writers still use the mapped classes. This is the read side only.
StoryRow = Row[Any]
AnswerRow = Row[Any]

#: The columns a story is read with — every column of the table, because the
#: CSV export carries the whole provenance record (constraint 3) and reads
#: through the same loader as the charts.
STORY_COLUMNS = (
    Anecdote.id,
    Anecdote.framework_id,
    Anecdote.text,
    Anecdote.title_auto,
    Anecdote.respondent_title,
    Anecdote.source_type,
    Anecdote.entry_mode,
    Anecdote.input_method,
    Anecdote.source_file,
    Anecdote.source_locator,
    Anecdote.import_job_id,
    Anecdote.respondent_group,
    Anecdote.created_at_hour,
    Anecdote.status,
)


def only_validated(statement: Select) -> Select:
    """Narrow a query to the stories a person has actually approved.

    Every read that feeds a figure the operator or a respondent will see goes
    through here. Nothing downstream is allowed its own idea of what "in the
    data" means.
    """
    return statement.where(Anecdote.status == STATUS_VALIDATED)


def only_pending(statement: Select) -> Select:
    """Narrow a query to the stories still waiting on a person."""
    return statement.where(Anecdote.status == STATUS_PENDING)
