"""Validation for ``frameworks.definition_json`` (PRD §3 and §5).

Every respondent-facing string lives here: the prompting question, every triad
corner, dyad pole, stones axis and chip label, every signifier question, MCQ
options, and the welcome / anonymity / thank-you / time-promise text. The Studio
edits this structure and nothing else.

Constraint 9 note: :data:`CANONICAL_ANONYMITY_TEXT` is the statement the schema
actually earns — it is the default for every new framework and is what the paper
story card prints verbatim. ``tests/test_framework_schema.py`` checks each claim
in it against the live database metadata, so the sentence cannot drift away from
what the code does.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

#: The anonymity statement. Every clause is enforced by the schema:
#: no identifier columns exist (``tests/test_schema_absence.py``) and story times
#: are hour-rounded (``backend.models.hour_rounded_now``).
CANONICAL_ANONYMITY_TEXT = (
    "This is anonymous. We do not record your name, your email, your device, or "
    "your network address — none of these exist anywhere in this app. The time "
    "your story arrives is rounded to the hour, so it cannot be traced back to "
    "you. Only your story, your placements, and the group you pick are saved."
)

DEFAULT_WELCOME_TEXT = "Thanks for sharing a real experience from your work."
DEFAULT_THANKYOU_TEXT = "Thank you. Your story has joined the picture."
DEFAULT_TIME_PROMISE_TEXT = "About 4 minutes."
DEFAULT_PROMPT_TEXT = "Tell us about a moment at work that stuck with you."

#: PRD §1.1: the Studio warns past roughly this many signifier screens.
SIGNIFIER_SCREEN_WARNING_THRESHOLD = 6

#: Rough per-screen costs used for the "respondent minutes" estimate shown in the
#: Studio. Deliberately coarse — this is an honesty aid, not a measurement.
SECONDS_STORY_ENTRY = 90
SECONDS_PER_TRIAD = 25
SECONDS_PER_DYAD = 15
SECONDS_PER_STONES = 40
SECONDS_PER_MCQ = 12
SECONDS_WELCOME_AND_THANKS = 20

NonEmptyStr = Annotated[str, Field(min_length=1, max_length=500)]
LabelStr = Annotated[str, Field(min_length=1, max_length=120)]
IdStr = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-z0-9][a-z0-9_-]*$")]


class _Strict(BaseModel):
    """Reject unknown keys so a typo in the Studio surfaces as an error."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Triad(_Strict):
    """A triangle with three named corners; answers are barycentric."""

    id: IdStr
    title: NonEmptyStr
    corners: list[LabelStr] = Field(min_length=3, max_length=3)

    @field_validator("corners")
    @classmethod
    def corners_must_be_distinct(cls, corners: list[str]) -> list[str]:
        if len({c.casefold() for c in corners}) != len(corners):
            raise ValueError("a triad's three corners must be different from each other")
        return corners


class Dyad(_Strict):
    """A slider between two opposing poles; answers are 0–1."""

    id: IdStr
    title: NonEmptyStr
    left: LabelStr
    right: LabelStr

    @model_validator(mode="after")
    def poles_must_differ(self) -> Dyad:
        if self.left.casefold() == self.right.casefold():
            raise ValueError("a dyad's two poles must be different from each other")
        return self


class StonesAxis(_Strict):
    """One axis of the stones canvas, named at both ends."""

    low: LabelStr
    high: LabelStr

    @model_validator(mode="after")
    def ends_must_differ(self) -> StonesAxis:
        if self.low.casefold() == self.high.casefold():
            raise ValueError("an axis needs two different end labels")
        return self


class Stones(_Strict):
    """A 2D canvas on which the respondent places named chips."""

    id: IdStr
    title: NonEmptyStr
    x_axis: StonesAxis
    y_axis: StonesAxis
    chips: list[LabelStr] = Field(min_length=1, max_length=12)

    @field_validator("chips")
    @classmethod
    def chips_must_be_distinct(cls, chips: list[str]) -> list[str]:
        if len({c.casefold() for c in chips}) != len(chips):
            raise ValueError("each chip needs its own label")
        return chips


class Mcq(_Strict):
    """A multiple-choice question."""

    id: IdStr
    title: NonEmptyStr
    options: list[LabelStr] = Field(min_length=2, max_length=12)
    multi: bool = False

    @field_validator("options")
    @classmethod
    def options_must_be_distinct(cls, options: list[str]) -> list[str]:
        if len({o.casefold() for o in options}) != len(options):
            raise ValueError("each option needs its own label")
        return options


class CaptureSettings(_Strict):
    """Every non-signifier string the respondent reads, plus capture toggles."""

    welcome_text: NonEmptyStr = DEFAULT_WELCOME_TEXT
    anonymity_text: NonEmptyStr = CANONICAL_ANONYMITY_TEXT
    thankyou_text: NonEmptyStr = DEFAULT_THANKYOU_TEXT
    time_promise_text: LabelStr = DEFAULT_TIME_PROMISE_TEXT
    # Constraint 10: reflection on by default, voice always paired with typing.
    reflection_enabled: bool = True
    voice_enabled: bool = True
    respondent_groups: list[LabelStr] = Field(default_factory=list, max_length=20)


class FrameworkDefinition(_Strict):
    """The whole respondent-facing definition of one framework version."""

    prompt_text: NonEmptyStr = DEFAULT_PROMPT_TEXT
    prompt_text_alt: NonEmptyStr | None = None
    triads: list[Triad] = Field(default_factory=list, max_length=10)
    dyads: list[Dyad] = Field(default_factory=list, max_length=10)
    stones: Stones | None = None
    mcqs: list[Mcq] = Field(default_factory=list, max_length=10)
    capture_settings: CaptureSettings = Field(default_factory=CaptureSettings)

    @model_validator(mode="after")
    def signifier_ids_must_be_unique(self) -> FrameworkDefinition:
        """One id namespace across all signifier kinds — significations key on it."""
        seen: dict[str, str] = {}
        for kind, items in (
            ("triad", self.triads),
            ("dyad", self.dyads),
            ("mcq", self.mcqs),
            ("stones", [self.stones] if self.stones else []),
        ):
            for item in items:
                if item.id in seen:
                    raise ValueError(
                        f"signifier id '{item.id}' is used twice "
                        f"(as {seen[item.id]} and as {kind}); each needs its own id"
                    )
                seen[item.id] = kind
        return self

    @property
    def signifier_count(self) -> int:
        """How many signifier screens the respondent will see."""
        return len(self.triads) + len(self.dyads) + len(self.mcqs) + (1 if self.stones else 0)

    @property
    def exceeds_screen_warning(self) -> bool:
        """PRD §1.1: warn past roughly six signifier screens."""
        return self.signifier_count > SIGNIFIER_SCREEN_WARNING_THRESHOLD

    def estimated_seconds(self) -> int:
        """Coarse 'respondent minutes' estimate shown live in the Studio."""
        return (
            SECONDS_WELCOME_AND_THANKS
            + SECONDS_STORY_ENTRY
            + len(self.triads) * SECONDS_PER_TRIAD
            + len(self.dyads) * SECONDS_PER_DYAD
            + len(self.mcqs) * SECONDS_PER_MCQ
            + (SECONDS_PER_STONES if self.stones else 0)
        )

    def estimated_minutes(self) -> float:
        """Estimated respondent time, rounded to one decimal."""
        return round(self.estimated_seconds() / 60, 1)

    def signifiers_in_order(self) -> list[tuple[str, Triad | Dyad | Stones | Mcq]]:
        """Every signifier with its kind, in the order the respondent meets them."""
        ordered: list[tuple[str, Triad | Dyad | Stones | Mcq]] = []
        ordered.extend(("triad", triad) for triad in self.triads)
        ordered.extend(("dyad", dyad) for dyad in self.dyads)
        if self.stones:
            ordered.append(("stones", self.stones))
        ordered.extend(("mcq", mcq) for mcq in self.mcqs)
        return ordered


#: Kinds a PUT may declare on a framework that already has stories (PRD §4).
EditKind = Literal["wording_fix", "meaning_change"]


def validate_definition(raw: dict) -> FrameworkDefinition:
    """Parse and validate a raw ``definition_json`` payload."""
    return FrameworkDefinition.model_validate(raw)


def default_definition() -> FrameworkDefinition:
    """A minimal, valid definition — what a brand-new framework starts from."""
    return FrameworkDefinition()
