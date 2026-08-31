"""Every screen tells the operator what to do next (PRD §6, Phase 9).

A fresh install is all empty screens, and an empty screen that says nothing —
or says only "no data" — is where a non-technical operator gets stuck
(constraint 7). So each screen must have an empty state, and each empty state
must point somewhere: a tab to visit, or something to do.

The check reads the screens' source rather than rendering them. The app has no
browser test harness — the frontend is checked by eslint, by the build, and by
the maths-parity tests that run Node directly — and adding a DOM stack to assert
on eleven sentences would be a heavier apparatus than the thing it guards. What
is asserted here is exactly what a reader of the code can confirm by eye: every
screen has empty-state copy, and that copy names a next step.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "frontend" / "src"

#: The screens an operator can arrive at. Each must have an empty state; the
#: list is explicit so that a new screen has to be added here deliberately.
SCREENS = [
    "studio/Studio.jsx",
    "capture/CaptureTab.jsx",
    "capture/LinkManager.jsx",
    "import/ImportTab.jsx",
    "import/ValidationQueue.jsx",
    "patterns/Patterns.jsx",
    "patterns/Explorer.jsx",
    "patterns/Landscape.jsx",
    "patterns/StoryBrowser.jsx",
]

#: Copy that is a state of the app rather than a state of the data. "Loading…"
#: is honest and needs no instruction — it is about to become something else.
TRANSIENT = ("loading", "drawing the landscape", "all done", "finished")

#: An empty state earns its place by naming somewhere to go or something to do.
NEXT_STEPS = (
    "studio",
    "capture",
    "import",
    "patterns",
    "queue",
    "choose",
    "add",
    "make one",
    "collect",
    "open",
    "print",
    "type",
    "check",
    "pick",
    "write",
)

#: An empty state is marked by its class, so the check is on the same thing the
#: stylesheet is: ``nl-empty``, or any block-level ``…__empty``.
EMPTY_BLOCK = re.compile(r'className="[^"]*(?:nl-empty|__empty)[^"]*"\s*>(.*?)</p>', re.DOTALL)


def _copy(path: Path) -> list[str]:
    """The text of every empty-state paragraph in one screen, tags stripped."""
    source = path.read_text(encoding="utf-8")
    found = []
    for block in EMPTY_BLOCK.findall(source):
        text = re.sub(r"<[^>]+>", " ", block)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            found.append(text)
    return found


@pytest.mark.parametrize("screen", SCREENS)
def test_every_screen_has_an_empty_state(screen: str) -> None:
    assert _copy(SRC / screen), f"{screen} has no empty-state copy"


@pytest.mark.parametrize("screen", SCREENS)
def test_every_empty_state_points_somewhere(screen: str) -> None:
    for text in _copy(SRC / screen):
        lowered = text.lower()
        if any(word in lowered for word in TRANSIENT):
            continue
        assert any(step in lowered for step in NEXT_STEPS), f"{screen}: {text!r}"


@pytest.mark.parametrize("screen", SCREENS)
def test_no_empty_state_is_a_shrug(screen: str) -> None:
    """"No data" is a fact about the database, not help for the person reading."""
    for text in _copy(SRC / screen):
        lowered = text.lower()
        assert "no data" not in lowered, f"{screen}: {text!r}"
        assert lowered.strip(" .") not in {"none", "empty", "nothing"}, f"{screen}: {text!r}"


def test_the_first_screen_of_a_fresh_install_says_where_to_start() -> None:
    """The Studio is the tab the app opens on, so it carries the first word."""
    copy = " ".join(_copy(SRC / "studio" / "Studio.jsx")).lower()

    assert "no question sets yet" in copy
    assert "new" in copy


def test_the_screens_agree_on_what_a_question_set_is_called() -> None:
    """One name for the thing, in every place the operator can read it.

    The code calls it a framework throughout, which is the PRD's word and the
    schema's. The person using it should not have to learn two.
    """
    for screen in SCREENS:
        source = (SRC / screen).read_text(encoding="utf-8")
        # Text between tags that reads as prose rather than as code: no
        # punctuation an expression would carry, and it starts like a sentence.
        rendered = [
            text.strip()
            for text in re.findall(r">([^<>{}=();\[\]|&]*[Ff]ramework[^<>{}=();\[\]|&]*)<", source)
            if text.strip() and text.strip()[0].isalpha()
        ]

        assert not rendered, f"{screen}: {rendered}"
