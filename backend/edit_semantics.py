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


# --------------------------------------------------------------------------
# Carrying the stored answers through a rename
# --------------------------------------------------------------------------
#
# Three of the four signifier kinds store an answer *by the label it was given*:
# a triad is ``{corner: weight}``, stones are ``{"placements": [{"label": chip,
# …}]}``, and an MCQ is ``{"selected": [option, …]}``. A wording fix is allowed
# to rewrite those labels — "Care" to "Carefulness" is exactly the kind of edit
# the guardrail blesses — and when it does, every stored answer is suddenly
# keyed by a word the framework no longer contains.
#
# So a wording fix rewrites the answers along with the words. It is sound to do
# positionally because :func:`structural_signature` has already refused anything
# that adds, removes or reshapes: corner two is corner two on both sides of the
# edit, whatever it is now called.


def label_renames(
    old: FrameworkDefinition, new: FrameworkDefinition
) -> dict[str, dict[str, str]]:
    """``{signifier_id: {old_label: new_label}}`` for every renamed label.

    Only labels that answers are stored under — triad corners, stones chips and
    MCQ options. Titles, prompts and pole names are wording the reader sees;
    they key nothing.
    """
    renames: dict[str, dict[str, str]] = {}

    def pairs(before: list[str], after: list[str]) -> dict[str, str]:
        return {was: now for was, now in zip(before, after, strict=True) if was != now}

    for was_triad, now_triad in zip(old.triads, new.triads, strict=True):
        changed = pairs(list(was_triad.corners), list(now_triad.corners))
        if changed:
            renames[now_triad.id] = changed

    if old.stones is not None and new.stones is not None:
        changed = pairs(list(old.stones.chips), list(new.stones.chips))
        if changed:
            renames[new.stones.id] = changed

    for was_mcq, now_mcq in zip(old.mcqs, new.mcqs, strict=True):
        changed = pairs(list(was_mcq.options), list(now_mcq.options))
        if changed:
            renames[now_mcq.id] = changed

    return renames


def rename_in_value(value_json: Any, renames: dict[str, str]) -> Any:
    """One stored answer with its labels brought up to date, or unchanged.

    Shape-agnostic on purpose: it recognises the three storage shapes rather
    than being told which kind it is, so a caller that has only the row cannot
    pass the wrong kind.
    """
    if not isinstance(value_json, dict):
        return value_json

    # Stones: a list of placements, each naming its chip.
    if isinstance(value_json.get("placements"), list):
        return {
            **value_json,
            "placements": [
                {**placement, "label": renames.get(placement.get("label"), placement.get("label"))}
                if isinstance(placement, dict)
                else placement
                for placement in value_json["placements"]
            ],
        }

    # MCQ: the chosen options, by name.
    if isinstance(value_json.get("selected"), list):
        return {
            **value_json,
            "selected": [renames.get(option, option) for option in value_json["selected"]],
        }

    # Triad: weights keyed by corner. A dyad is ``{"value": …}`` and has no
    # label to rename, so it falls through this untouched.
    return {renames.get(key, key): weight for key, weight in value_json.items()}
