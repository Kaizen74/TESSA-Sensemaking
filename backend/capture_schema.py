"""Validating a submitted capture against the framework it answers (PRD §4).

A placement is only meaningful next to the question that produced it, so every
submitted signification is checked against the exact framework version being
answered: the signifier must exist, its value must match that signifier's shape,
and the numbers must be in range. Triad weights must sum to 1.0 — that is the
same invariant ``backend/barycentric.py`` holds, reached through the same code.

Nothing here is AI-adjacent. Constraint 1 governs AI-organised anecdotes and
AI-proposed significations; a respondent placing their own dot is first-hand
testimony, and is stored as such. See PROGRESS.md "Decisions" for that call.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.barycentric import BarycentricError, normalise, sums_to_one
from backend.framework_schema import FrameworkDefinition

#: What a directly-captured record records as its origin. Ingestion uses its own
#: value from Phase 5 onward.
SOURCE_TYPE_CAPTURE = "capture"

#: Who made the interpretation. A paper transcription is still the respondent's
#: judgement — the operator only typed it in, and ``input_method`` already
#: records that it came off paper.
SIGNIFIED_BY_RESPONDENT = "respondent"

#: Input methods a live capture may declare. ``imported`` is not among them —
#: that value belongs to the ingestion pipeline, and letting a browser claim it
#: would let AI-derived content pose as first-hand testimony (constraint 1).
CAPTURE_INPUT_METHODS = ("typed", "voice", "paper")

#: Entry modes the *local* endpoint accepts. ``link`` is missing on purpose: it
#: is derived from the token by the public endpoint, never stated by a caller.
LOCAL_ENTRY_MODES = ("admin", "kiosk")

MAX_STORY_CHARS = 20_000


class CaptureError(ValueError):
    """A submitted capture that cannot be stored as given."""

    def __init__(self, message: str, action: str) -> None:
        super().__init__(message)
        self.action = action


class SubmittedSignification(BaseModel):
    """One placement as it arrives from the wizard or paper batch entry."""

    model_config = ConfigDict(extra="forbid")

    signifier_id: Annotated[str, Field(min_length=1, max_length=64)]
    value: dict


class CaptureSubmission(BaseModel):
    """A whole capture: one story plus its placements.

    Note what is *not* here: no id, no device, no timing, nothing a browser
    could volunteer about who is submitting. ``extra="forbid"`` means a client
    cannot smuggle one in either, and ``tests/test_capture.py`` proves it.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    framework_id: int
    text: Annotated[str, Field(min_length=1, max_length=MAX_STORY_CHARS)]
    input_method: Literal["typed", "voice", "paper"] = "typed"
    respondent_group: Annotated[str, Field(max_length=200)] | None = None
    significations: list[SubmittedSignification] = Field(default_factory=list)


class LocalCaptureSubmission(CaptureSubmission):
    """A capture from the operator's own machine: admin, paper entry, or kiosk.

    Only the local endpoint lets the caller name its entry mode, because only
    the local endpoint is the operator. See PROGRESS.md "Decisions".
    """

    entry_mode: Literal["admin", "kiosk"] = "admin"


class PublicCaptureSubmission(CaptureSubmission):
    """A capture arriving through a capture link.

    ``framework_id`` is not accepted: the token decides which version is being
    answered, so a respondent's browser cannot point its story at a different
    question set. The public router supplies it from the link.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    framework_id: int | None = None


def _check_triad(value: dict, corner_ids: list[str], title: str) -> dict:
    """Triad weights: one per corner, non-negative, summing to 1.0."""
    missing = [corner for corner in corner_ids if corner not in value]
    if missing:
        raise CaptureError(
            f"The answer to '{title}' is missing a corner.",
            "Place the marker inside the triangle and try again.",
        )

    extra = set(value) - set(corner_ids)
    if extra:
        raise CaptureError(
            f"The answer to '{title}' has a corner that question does not have.",
            "Reload the page so you have the current questions, then try again.",
        )

    try:
        weights = tuple(float(value[corner]) for corner in corner_ids)
    except (TypeError, ValueError) as exc:
        raise CaptureError(
            f"The answer to '{title}' is not a position on the triangle.",
            "Place the marker inside the triangle and try again.",
        ) from exc

    if any(weight < 0 for weight in weights):
        raise CaptureError(
            f"The answer to '{title}' sits outside the triangle.",
            "Place the marker inside the triangle and try again.",
        )

    if not sums_to_one(weights):  # type: ignore[arg-type]
        try:
            weights = normalise(weights)  # type: ignore[arg-type]
        except BarycentricError as exc:
            raise CaptureError(
                f"The answer to '{title}' is not a position on the triangle.",
                "Place the marker inside the triangle and try again.",
            ) from exc

    return dict(zip(corner_ids, weights, strict=True))


def _check_dyad(value: dict, title: str) -> dict:
    """Dyad value: a single number from 0 to 1."""
    if set(value) != {"value"}:
        raise CaptureError(
            f"The answer to '{title}' is not a position on the line.",
            "Place the marker on the line and try again.",
        )
    try:
        position = float(value["value"])
    except (TypeError, ValueError) as exc:
        raise CaptureError(
            f"The answer to '{title}' is not a position on the line.",
            "Place the marker on the line and try again.",
        ) from exc

    if not 0.0 <= position <= 1.0:
        raise CaptureError(
            f"The answer to '{title}' sits off the end of the line.",
            "Place the marker somewhere on the line and try again.",
        )

    return {"value": position}


def _check_stones(value: dict, chips: list[str], title: str) -> dict:
    """Stones value: a placement per chip, each inside the square."""
    if set(value) != {"placements"}:
        raise CaptureError(
            f"The answer to '{title}' is not a set of placements.",
            "Place each item on the square and try again.",
        )

    placements = value["placements"]
    if not isinstance(placements, list):
        raise CaptureError(
            f"The answer to '{title}' is not a set of placements.",
            "Place each item on the square and try again.",
        )

    cleaned = []
    seen: set[str] = set()
    for placement in placements:
        if not isinstance(placement, dict) or set(placement) != {"label", "x", "y"}:
            raise CaptureError(
                f"One of the placements on '{title}' is not readable.",
                "Place each item on the square and try again.",
            )
        label = placement["label"]
        if label not in chips:
            raise CaptureError(
                f"'{label}' is not one of the items on '{title}'.",
                "Reload the page so you have the current questions, then try again.",
            )
        if label in seen:
            raise CaptureError(
                f"'{label}' has been placed twice on '{title}'.",
                "Place each item once, then try again.",
            )
        seen.add(label)

        try:
            x = float(placement["x"])
            y = float(placement["y"])
        except (TypeError, ValueError) as exc:
            raise CaptureError(
                f"One of the placements on '{title}' is not readable.",
                "Place each item on the square and try again.",
            ) from exc

        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            raise CaptureError(
                f"'{label}' sits outside the square on '{title}'.",
                "Place each item inside the square and try again.",
            )

        cleaned.append({"label": label, "x": x, "y": y})

    return {"placements": cleaned}


def _check_mcq(value: dict, options: list[str], multi: bool, title: str) -> dict:
    """MCQ value: chosen options, one unless the question allows more."""
    if set(value) != {"selected"}:
        raise CaptureError(
            f"The answer to '{title}' is not a choice.",
            "Choose an option and try again.",
        )

    selected = value["selected"]
    if not isinstance(selected, list) or any(not isinstance(item, str) for item in selected):
        raise CaptureError(
            f"The answer to '{title}' is not a choice.",
            "Choose an option and try again.",
        )

    unknown = [item for item in selected if item not in options]
    if unknown:
        raise CaptureError(
            f"'{unknown[0]}' is not one of the options on '{title}'.",
            "Reload the page so you have the current questions, then try again.",
        )

    if len(set(selected)) != len(selected):
        raise CaptureError(
            f"The same option is chosen twice on '{title}'.",
            "Choose each option once, then try again.",
        )

    if not multi and len(selected) > 1:
        raise CaptureError(
            f"'{title}' takes one answer, but more than one was chosen.",
            "Choose a single option and try again.",
        )

    return {"selected": list(selected)}


def validate_significations(
    definition: FrameworkDefinition,
    submitted: list[SubmittedSignification],
) -> list[tuple[str, str, dict]]:
    """Check every placement against its question.

    Returns ``(signifier_id, signifier_type, cleaned_value)`` per placement.
    Unanswered signifiers are allowed — a respondent may skip a question, and
    forcing an answer would put a number in the dataset that nobody meant.
    """
    by_id = {
        signifier.id: (kind, signifier)
        for kind, signifier in definition.signifiers_in_order()
    }

    seen: set[str] = set()
    cleaned: list[tuple[str, str, dict]] = []

    for placement in submitted:
        entry = by_id.get(placement.signifier_id)
        if entry is None:
            raise CaptureError(
                "This answer refers to a question that is not part of this set.",
                "Reload the page so you have the current questions, then try again.",
            )
        if placement.signifier_id in seen:
            raise CaptureError(
                "The same question has been answered twice.",
                "Reload the page and answer each question once.",
            )
        seen.add(placement.signifier_id)

        kind, signifier = entry
        if kind == "triad":
            value = _check_triad(placement.value, list(signifier.corners), signifier.title)
        elif kind == "dyad":
            value = _check_dyad(placement.value, signifier.title)
        elif kind == "stones":
            value = _check_stones(placement.value, list(signifier.chips), signifier.title)
        else:
            value = _check_mcq(
                placement.value, list(signifier.options), signifier.multi, signifier.title
            )

        cleaned.append((placement.signifier_id, kind, value))

    return cleaned
