"""The wording-fix vs meaning-change guardrail (PRD §1.1, constraint 13g).

While a framework has no stories, edits apply freely. Once stories exist, an
edit must declare itself:

* **wording fix** — same meaning, different words. Patched in place and appended
  to the framework's edit log, so the change stays auditable.
* **meaning change** — creates version n+1. Existing anecdotes keep pointing at
  the version whose wording they actually answered.

PRD §9 assumption 12 is explicit that the app cannot verify a wording fix really
preserves meaning — that judgement is the operator's, and the log is what makes
it auditable. What the app *can* verify is that a wording fix does not change
the *shape* of the framework: adding or removing a signifier, a corner, or an
option would strand significations that already point at the old structure. That
check lives in :func:`structural_signature`.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from backend.framework_schema import FrameworkDefinition

#: Kinds an edit-log entry may carry. A meaning change creates a new row rather
#: than a log entry, so ``wording_fix`` is the only value that ever appears.
EDIT_LOG_KIND_WORDING_FIX = "wording_fix"


def structural_signature(definition: FrameworkDefinition) -> dict[str, Any]:
    """The shape of a framework, ignoring every word in it.

    Two definitions with the same signature differ only in wording. A change
    here means existing significations would no longer line up, so it cannot be
    a wording fix.
    """
    return {
        "triads": [(triad.id, len(triad.corners)) for triad in definition.triads],
        "dyads": [dyad.id for dyad in definition.dyads],
        "mcqs": [(mcq.id, len(mcq.options), mcq.multi) for mcq in definition.mcqs],
        "stones": (
            None
            if definition.stones is None
            else (definition.stones.id, len(definition.stones.chips))
        ),
        "has_alt_prompt": definition.prompt_text_alt is not None,
    }


def is_structural_change(old: FrameworkDefinition, new: FrameworkDefinition) -> bool:
    """Whether the edit changes the framework's shape rather than its words."""
    return structural_signature(old) != structural_signature(new)


def _walk_text(value: Any, path: str) -> dict[str, str]:
    """Flatten a definition into ``{field_path: text}`` for every string leaf."""
    flattened: dict[str, str] = {}

    if isinstance(value, str):
        flattened[path] = value
    elif isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            flattened.update(_walk_text(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            flattened.update(_walk_text(child, f"{path}.{index}"))

    return flattened


def diff_text_fields(
    old: FrameworkDefinition, new: FrameworkDefinition
) -> list[tuple[str, str, str]]:
    """Every changed string, as ``(field_path, old_text, new_text)``.

    Field paths read the way the schema does — ``prompt_text``,
    ``triads.0.corners.1``, ``capture_settings.welcome_text`` — so an entry in
    the edit log points at exactly what the operator changed.
    """
    old_texts = _walk_text(old.model_dump(mode="json"), "")
    new_texts = _walk_text(new.model_dump(mode="json"), "")

    changes: list[tuple[str, str, str]] = []
    for path in sorted(old_texts.keys() & new_texts.keys()):
        if old_texts[path] != new_texts[path]:
            changes.append((path, old_texts[path], new_texts[path]))
    return changes


def build_edit_log_entries(
    old: FrameworkDefinition,
    new: FrameworkDefinition,
    edited_at: dt.datetime,
) -> list[dict[str, str]]:
    """Edit-log entries for a wording fix, in the PRD §3 shape."""
    return [
        {
            "field_path": field_path,
            "old_text": old_text,
            "new_text": new_text,
            "edited_at": edited_at.isoformat(),
            "kind": EDIT_LOG_KIND_WORDING_FIX,
        }
        for field_path, old_text, new_text in diff_text_fields(old, new)
    ]
