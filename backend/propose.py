"""Stage B — Propose (PRD §4a, constraint 1).

Stage B reads a story and *suggests* where it sits on each of the framework's
signifiers. Like Stage A it only proposes: every placement it returns is stored
with ``signified_by="ai"``, ``validated_at=None``, and on an anecdote whose
status is ``pending_validation``. None of that is data until a person works
through the queue and says so (:mod:`backend.dataset`).

Three things constrain the design:

* **Chunked at twenty.** PRD §4a caps a Stage B call at twenty anecdotes. A
  thirty-story import is two calls, and each call sees the whole framework, so
  the questions a story is being placed against never change mid-file.
* **Every proposal is checked against the framework before it is stored.** The
  same validator that guards a respondent's own submission
  (:func:`backend.capture_schema.validate_significations`) runs over the model's
  answer: the signifier must exist, the value must match that signifier's shape,
  triad weights must sum to one, an MCQ option must be one of the real options.
  A model cannot invent a corner or a chip and have it reach the queue.
* **Confidence changes the colour, not the route** (constraint 2). A placement
  at 0.31 and a placement at 0.98 both land in the queue and both wait for the
  same person to say yes.

The mock is deterministic: placements are derived from a hash of the story text
and the signifier's own id, so the same file organised twice proposes the same
thing, and a fixture that changes changes the answer.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend import ai_client
from backend.capture_schema import (
    CaptureError,
    SubmittedSignification,
    validate_significations,
)
from backend.framework_schema import FrameworkDefinition

#: PRD §4a: Stage B is chunked at twenty anecdotes per call.
CHUNK_SIZE = 20

#: What an imported record records as its origin (constraint 3). Distinct from
#: ``capture`` so a provenance column can tell first-hand testimony from a file.
SOURCE_TYPE_IMPORT = "import"

#: Who made the interpretation, for significations Stage B proposed. It stays
#: ``ai`` after a person approves it unchanged — the honest record is that a
#: model placed the marker and a human agreed, not that the human placed it.
SIGNIFIED_BY_AI = "ai"

#: Who made the interpretation once a person has moved the marker themselves.
SIGNIFIED_BY_ANALYST = "analyst"


class ProposeError(Exception):
    """Stage B produced something that does not fit the framework."""

    def __init__(self, code: str, message: str, action: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action


class ProposedPlacement(BaseModel):
    """One suggested placement on one signifier."""

    model_config = ConfigDict(extra="forbid")

    signifier_id: str
    value: dict
    confidence: float = Field(ge=0.0, le=1.0)


class ProposedStory(BaseModel):
    """Stage B's answer for one story in the chunk."""

    model_config = ConfigDict(extra="forbid")

    #: Position of the story within the chunk it was sent in.
    index: int = Field(ge=0)
    placements: list[ProposedPlacement] = Field(default_factory=list)


class ProposalBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stories: list[ProposedStory]


class Placement(BaseModel):
    """A validated proposal, ready to be written as a signification."""

    model_config = ConfigDict(extra="forbid")

    signifier_id: str
    signifier_type: str
    value: dict
    confidence: float


class StoryProposal(BaseModel):
    """Everything Stage B has to say about one story."""

    model_config = ConfigDict(extra="forbid")

    index: int
    placements: list[Placement] = Field(default_factory=list)

    @property
    def has_low_confidence(self) -> bool:
        """Constraint 2 — flagged amber, routed identically."""
        return any(
            placement.confidence < ai_client.LOW_CONFIDENCE for placement in self.placements
        )


PROPOSE_SYSTEM = (
    "You are helping an analyst mark up collected stories. You are given a set "
    "of questions and a numbered list of stories. For each story, say where it "
    "sits on each question, judging only from what the story itself says.\n\n"
    "Rules you must not break:\n"
    "- Return one entry per story you were given, using the index you were "
    "given.\n"
    "- Use only the signifier ids and the exact labels you were given. Never "
    "invent a corner, a chip, or an option.\n"
    "- Each value must match the shape stated for that question.\n"
    "- If a story says nothing that bears on a question, leave that question "
    "out of its placements rather than guessing. A missing answer is better "
    "than an invented one.\n"
    "- confidence is your own 0 to 1 estimate that the placement is right. Be "
    "honest and low when the story is thin; a person checks every one of these.\n"
    "- Do not summarise, rewrite, or comment on the stories.\n\n"
    'Return {"stories": [{"index": int, "placements": [{"signifier_id": str, '
    '"value": object, "confidence": number}]}]}.'
)


def describe_signifiers(definition: FrameworkDefinition) -> list[dict[str, Any]]:
    """The questions, with the exact answer shape each one takes.

    Written out in full rather than referred to, because this is the only thing
    standing between the model and an invented corner label.
    """
    described: list[dict[str, Any]] = []
    for kind, signifier in definition.signifiers_in_order():
        if kind == "triad":
            described.append(
                {
                    "signifier_id": signifier.id,
                    "kind": "triad",
                    "question": signifier.title,
                    "corners": list(signifier.corners),
                    "value_shape": (
                        "an object with one number per corner label, all at "
                        "least 0 and adding up to 1"
                    ),
                }
            )
        elif kind == "dyad":
            described.append(
                {
                    "signifier_id": signifier.id,
                    "kind": "dyad",
                    "question": signifier.title,
                    "left": signifier.left,
                    "right": signifier.right,
                    "value_shape": (
                        '{"value": number} from 0 at the left pole to 1 at the '
                        "right pole"
                    ),
                }
            )
        elif kind == "stones":
            described.append(
                {
                    "signifier_id": signifier.id,
                    "kind": "stones",
                    "question": signifier.title,
                    "x_axis": [signifier.x_axis.low, signifier.x_axis.high],
                    "y_axis": [signifier.y_axis.low, signifier.y_axis.high],
                    "chips": list(signifier.chips),
                    "value_shape": (
                        '{"placements": [{"label": chip, "x": number 0-1, '
                        '"y": number 0-1}]}, each chip at most once'
                    ),
                }
            )
        else:
            described.append(
                {
                    "signifier_id": signifier.id,
                    "kind": "mcq",
                    "question": signifier.title,
                    "options": list(signifier.options),
                    "multi": signifier.multi,
                    "value_shape": (
                        '{"selected": [option]}'
                        + ("" if signifier.multi else ", exactly one option")
                    ),
                }
            )
    return described


def _prompt(definition: FrameworkDefinition, stories: list[str]) -> str:
    return (
        "Questions:\n"
        + json.dumps(describe_signifiers(definition), ensure_ascii=False, indent=1)
        + "\n\nStories:\n"
        + json.dumps(
            [{"index": index, "text": text} for index, text in enumerate(stories)],
            ensure_ascii=False,
            indent=1,
        )
    )


def _unit(*parts: str) -> float:
    """A stable 0–1 number from the given strings.

    ``hash()`` is salted per process, so two runs of the same import would
    disagree. A digest is the same everywhere, forever, which is what makes the
    mock's output a fixture the tests can rely on.
    """
    digest = hashlib.sha256("".join(parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def _mock_confidence(text: str, signifier_id: str) -> float:
    """Spread across constraint 2's threshold, so amber is exercised for real."""
    return round(0.45 + _unit("confidence", text, signifier_id) * 0.54, 2)


def _mock_value(kind: str, signifier: Any, text: str) -> dict[str, Any]:
    if kind == "triad":
        raw = [_unit("triad", text, signifier.id, corner) + 0.01 for corner in signifier.corners]
        total = sum(raw)
        return {
            corner: round(weight / total, 6)
            for corner, weight in zip(signifier.corners, raw, strict=True)
        }
    if kind == "dyad":
        return {"value": round(_unit("dyad", text, signifier.id), 6)}
    if kind == "stones":
        return {
            "placements": [
                {
                    "label": chip,
                    "x": round(_unit("stones-x", text, signifier.id, chip), 6),
                    "y": round(_unit("stones-y", text, signifier.id, chip), 6),
                }
                for chip in signifier.chips
            ]
        }
    options = list(signifier.options)
    chosen = options[int(_unit("mcq", text, signifier.id) * len(options)) % len(options)]
    return {"selected": [chosen]}


def _mock_batch(definition: FrameworkDefinition, stories: list[str]) -> dict[str, Any]:
    """A placement on every signifier of every story, derived from the text."""
    return {
        "stories": [
            {
                "index": index,
                "placements": [
                    {
                        "signifier_id": signifier.id,
                        "value": _mock_value(kind, signifier, text),
                        "confidence": _mock_confidence(text, signifier.id),
                    }
                    for kind, signifier in definition.signifiers_in_order()
                ],
            }
            for index, text in enumerate(stories)
        ]
    }


def _check_batch(
    definition: FrameworkDefinition, stories: list[str], batch: ProposalBatch
) -> list[StoryProposal]:
    """Hold Stage B to the framework, exactly as a respondent is held to it."""
    seen = {story.index for story in batch.stories}
    if seen != set(range(len(stories))):
        raise ProposeError(
            "propose_stories_mismatch",
            "The AI did not answer for every story it was given, so Narrative "
            "Lens stopped rather than guess which was which.",
            "Click Mark up again. If it keeps happening, import a smaller part "
            "of the file.",
        )

    proposals: list[StoryProposal] = []
    for story in sorted(batch.stories, key=lambda item: item.index):
        try:
            cleaned = validate_significations(
                definition,
                [
                    SubmittedSignification(
                        signifier_id=placement.signifier_id, value=placement.value
                    )
                    for placement in story.placements
                ],
            )
        except CaptureError as exc:
            raise ProposeError(
                "propose_invalid_placement",
                "The AI suggested an answer that does not fit these questions, "
                "so Narrative Lens stopped rather than store it.",
                "Click Mark up again. If it keeps happening, check the question "
                "set in the Studio.",
            ) from exc

        confidence_by_id = {
            placement.signifier_id: placement.confidence for placement in story.placements
        }
        proposals.append(
            StoryProposal(
                index=story.index,
                placements=[
                    Placement(
                        signifier_id=signifier_id,
                        signifier_type=signifier_type,
                        value=value,
                        confidence=confidence_by_id[signifier_id],
                    )
                    for signifier_id, signifier_type, value in cleaned
                ],
            )
        )
    return proposals


def chunks(stories: list[str], size: int = CHUNK_SIZE) -> list[list[str]]:
    """Split the stories into calls of at most ``size`` (PRD §4a)."""
    return [stories[start : start + size] for start in range(0, len(stories), size)]


def propose(definition: FrameworkDefinition, stories: list[str]) -> list[StoryProposal]:
    """Run Stage B over a file's stories and return checked proposals.

    Nothing is written here. The caller stores the result as significations on
    anecdotes that are ``pending_validation`` — in the queue, not in the data.
    """
    proposals: list[StoryProposal] = []
    offset = 0
    for chunk in chunks(stories):
        batch = ai_client.request_json(
            system=PROPOSE_SYSTEM,
            prompt=_prompt(definition, chunk),
            shape=ProposalBatch,
            mock=lambda chunk=chunk: _mock_batch(definition, chunk),
        )
        for proposal in _check_batch(definition, chunk, batch):
            proposals.append(
                StoryProposal(index=proposal.index + offset, placements=proposal.placements)
            )
        offset += len(chunk)
    return proposals
