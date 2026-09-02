"""The framework design linter (delta §4a, item 3).

The one AI call in this app that never looks at data.

Every other model call in Narrative Lens reads what people wrote — Stage A finds
the stories in a file, Stage B proposes where they sit. This one reads the
*questions*, before anybody has answered them, and says what a respondent might
trip over. A triad with an obviously right corner turns the other two into
decoys. A dyad with one end plainly good collects agreement rather than
experience. A prompting question with a hypothesis inside it collects the
hypothesis back.

Three rules bound it, and each is a test rather than a promise:

* **It reads ``definition_json`` and nothing else.** No story text, no
  placements, no counts. There is nothing in this module that can reach an
  anecdote, and ``tests/test_design_linter.py`` asserts the prompt's contents.
* **It never writes.** Linting a framework leaves the framework byte-identical.
  The endpoint holds a session only to read one row.
* **It cannot block anything.** Findings are advisory. Publishing works with
  every finding outstanding, because the operator is the one who knows the
  workforce and the model is guessing at them.

Constraint 11 is not in tension with any of this: patterns are computed and
never composed, and a critique of question wording is not a pattern. What the
model must never do — and what the system prompt forbids in as many words — is
say anything about the stories or the figures, because it will not have seen
either.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from backend import ai_client
from backend.framework_schema import FrameworkDefinition

#: The mock reply, shipped with the app rather than with the tests.
#:
#: ``NL_MOCK_AI=1`` is a mode the *backend* implements (constraint 6), exactly as
#: Stage A and Stage B keep their mocks in ``backend/``. A mock the app could
#: only find when the test tree happened to be installed beside it would make
#: "runs everything with zero network" untrue of a real install. See PROGRESS.md
#: "Decisions" for the deviation from the delta's stated path.
MOCK_PATH = Path(__file__).resolve().parent / "fixtures" / "mock_lint_response.json"

#: Roughly how many words a label can carry before a respondent stops reading
#: it. Named here because the system prompt quotes it and a test checks it does.
LABEL_WORD_LIMIT = 6

LINT_SYSTEM = (
    "You are reviewing the DESIGN of a set of questions before anyone has "
    "answered them. You are a critical friend to the person who wrote them.\n\n"
    "You are given the question set as JSON. You are given no stories, no "
    "answers, and no data, because none has been collected yet — and even if it "
    "had, it would be none of your concern here.\n\n"
    "Judge only the design. For each problem you find, report:\n"
    "- severity: 'warning' if a respondent would likely be misled or unable to "
    "answer, 'info' if it is worth a second look but would still work.\n"
    "- location: the JSON field path it refers to, for example "
    "'triads[0].corners[1]' or 'prompt_text'. Use paths that exist in what you "
    "were given.\n"
    "- finding: one plain sentence saying what the problem is.\n"
    "- suggestion: one plain sentence saying what to try instead. Offer wording "
    "the person can copy; do not rewrite the question set for them.\n\n"
    "What to look for:\n"
    "- A triad with one corner a respondent would read as the 'right' answer, "
    "making the other two decoys.\n"
    "- Triad corners that are not mutually exhaustive enough for a real story to "
    "be placed anywhere, or not in enough tension for placing it to require a "
    "trade-off.\n"
    "- A dyad with one pole obviously good and the other obviously bad, which "
    "collects agreement rather than experience.\n"
    "- A prompting question that embeds a hypothesis, or leads toward the kind "
    "of story the author is hoping for.\n"
    f"- Any label longer than about {LABEL_WORD_LIMIT} words, or written above a "
    "plain reading level appropriate to a frontline workforce.\n\n"
    "Rules you must not break:\n"
    "- Say nothing about stories, respondents, results, patterns or data. You "
    "have not seen any.\n"
    "- Do not rewrite the question set. You report; the person decides.\n"
    "- If the design is sound, return an empty findings list. An invented "
    "problem costs more than a missed one.\n\n"
    'Return {"findings": [{"severity": str, "location": str, "finding": str, '
    '"suggestion": str}]}.'
)


class LintFinding(BaseModel):
    """One thing worth a second look, and what to try instead."""

    model_config = ConfigDict(extra="forbid")

    #: Constraint 2's amber has no equivalent here — a finding is not a
    #: confidence. Two levels, and neither of them stops anything.
    severity: Literal["info", "warning"]
    #: The field it is about, so the panel can say which question is meant.
    location: str = Field(min_length=1, max_length=200)
    finding: str = Field(min_length=1, max_length=1000)
    suggestion: str = Field(min_length=1, max_length=1000)


class LintReport(BaseModel):
    """Everything the model had to say about one question set's design."""

    model_config = ConfigDict(extra="forbid")

    findings: list[LintFinding] = Field(default_factory=list, max_length=50)

    @property
    def warnings(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def lint_prompt(definition: FrameworkDefinition) -> str:
    """What the model is asked about: the question set, and nothing else.

    ``model_dump`` of the definition and no other source. Written as its own
    function so a test can assert what goes into it — the assertion the delta
    asks for, and the one that keeps constraint 1's boundary visible: no story
    text can reach this call because no story text is reachable from here.
    """
    return json.dumps(definition.model_dump(mode="json"), indent=2, sort_keys=True)


@lru_cache(maxsize=1)
def _mock_reply() -> dict[str, Any]:
    """The practice reply, read once from the file that holds it.

    Deliberately the same object every time and deliberately not derived from
    the framework being linted. A mock that computed plausible findings would be
    a second, worse linter — and the thing worth exercising offline is the
    path, the shape and the panel, not a judgement only the model can make.
    """
    return json.loads(MOCK_PATH.read_text(encoding="utf-8"))


def lint(definition: FrameworkDefinition) -> LintReport:
    """Ask for a critique of the design. Never touches a story, never writes.

    Failures come back as :class:`backend.ai_client.AiError` with the operator's
    sentence already in them, so the Studio can say what happened and carry on
    (constraint 6). Nothing is written either way — there is no state here to
    leave half-finished.
    """
    return ai_client.request_json(
        system=LINT_SYSTEM,
        prompt=lint_prompt(definition),
        shape=LintReport,
        mock=_mock_reply,
    )
