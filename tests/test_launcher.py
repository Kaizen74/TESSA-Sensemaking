"""The two files the operator actually double-clicks (constraint 7).

Constraint 7 says zero terminal after install, plain-English errors with a
suggested action, and no config editing. Everything else in this suite tests the
app. Nothing tested the two files that decide whether the app ever runs at all —
and one of them spent the whole build telling the operator to "run the one-time
setup you were given", which had never been written. The app was correct and
unstartable, and every test passed.

These are static checks of file contents rather than a run: this suite runs on
Linux and these are Windows batch files, so what can be verified here is what
they *say* and what they *point at*. The one thing that cannot be checked here
is that they work on Windows, which is written down in LATEST.md as the thing
still owed to a real machine.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

SETUP = ROOT / "Set up Narrative Lens.bat"
LAUNCHER = ROOT / "Start Narrative Lens.bat"
BATCH_FILES = (SETUP, LAUNCHER)


def text_of(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------
# Both files exist, and so does everything they send the operator to
# --------------------------------------------------------------------------


@pytest.mark.parametrize("path", BATCH_FILES, ids=lambda p: p.name)
def test_the_file_the_operator_double_clicks_exists(path: Path) -> None:
    assert path.is_file(), f"{path.name} is missing"


@pytest.mark.parametrize("path", BATCH_FILES, ids=lambda p: p.name)
def test_no_message_sends_the_operator_to_a_file_that_does_not_exist(path: Path) -> None:
    """The bug this file was written for.

    An instruction naming a file is a promise that the file is there. A
    non-technical operator cannot tell the difference between "the setup failed"
    and "the setup does not exist", and both look like the app is broken.
    """
    named = set(re.findall(r'"([^"]+\.bat)"', text_of(path)))

    missing = sorted(name for name in named if not (ROOT / name).is_file())

    assert not missing, f"{path.name} points at files that do not exist: {missing}"


@pytest.mark.parametrize("path", BATCH_FILES, ids=lambda p: p.name)
def test_nothing_refers_to_a_setup_nobody_was_given(path: Path) -> None:
    """"The one-time setup you were given" named nothing and helped nobody."""
    assert "you were given" not in text_of(path)


def test_the_readme_names_the_setup_file_too() -> None:
    readme = text_of(ROOT / "README.md")

    assert "Set up Narrative Lens.bat" in readme
    assert "you were given" not in readme


# --------------------------------------------------------------------------
# The two files agree with each other, and with the project
# --------------------------------------------------------------------------


def test_setup_builds_the_python_the_launcher_looks_for() -> None:
    """The launcher prefers ``.venv``; setup has to be what puts one there."""
    assert ".venv\\Scripts\\python.exe" in text_of(LAUNCHER)
    assert "venv" in text_of(SETUP)


def test_setup_installs_everything_the_launcher_checks_for() -> None:
    """The launcher's readiness check may not ask for more than setup installs.

    The launcher decides the app is unstartable by importing four packages. If
    any of them were not in the project's dependencies, setup would finish
    successfully and the launcher would still refuse — the exact failure that
    cannot be diagnosed from either message.
    """
    checked = re.search(r'-c "import ([^"]+)"', text_of(LAUNCHER))
    assert checked, "the launcher no longer checks that its dependencies import"
    wanted = {name.strip() for name in checked.group(1).split(",")}

    declared = tomllib.loads(text_of(ROOT / "pyproject.toml"))["project"]["dependencies"]
    # "uvicorn[standard]>=0.30" -> "uvicorn"
    installed = {re.split(r"[<>=\[]", line, maxsplit=1)[0].strip() for line in declared}

    assert wanted <= installed, (
        f"the launcher imports what setup never installs: {wanted - installed}"
    )


def test_setup_builds_the_pages_the_launcher_looks_for() -> None:
    assert "frontend\\dist\\index.html" in text_of(LAUNCHER)
    assert "frontend\\dist\\index.html" in text_of(SETUP)
    assert "npm run build" in text_of(SETUP)


# --------------------------------------------------------------------------
# Windows batch traps, and constraint 7's wording rule
# --------------------------------------------------------------------------


def test_npm_is_called_rather_than_run(path: Path = SETUP) -> None:
    """``npm`` is a ``.cmd`` on Windows.

    A batch file that runs another batch file without ``call`` hands control
    over and never gets it back — so setup would stop at the npm line, skip
    every check after it, and end without saying anything was wrong. Silent
    half-completion is the worst failure this file could have.
    """
    for line in text_of(path).splitlines():
        stripped = line.strip()
        if stripped.startswith("npm ") or re.match(r"^npm\.cmd\b", stripped):
            pytest.fail(f"npm invoked without 'call': {stripped}")
    assert "call npm" in text_of(path)


@pytest.mark.parametrize("path", BATCH_FILES, ids=lambda p: p.name)
def test_every_refusal_says_what_happened_and_what_to_do(path: Path) -> None:
    """Constraint 7: a sentence about what went wrong, and one about what to do."""
    body = text_of(path)
    went_wrong = body.count("What went wrong:")
    what_to_do = body.count("What to do:")

    assert went_wrong >= 1
    assert went_wrong == what_to_do, (
        f"{path.name} has {went_wrong} 'what went wrong' and {what_to_do} 'what to do'"
    )


@pytest.mark.parametrize("path", BATCH_FILES, ids=lambda p: p.name)
def test_a_refusal_waits_to_be_read(path: Path) -> None:
    """A double-clicked window closes the instant the file ends.

    Every path that gives up has to hold the window open, or the operator sees
    a black rectangle flash and has nothing at all to act on.
    """
    body = text_of(path)
    exits = len(re.findall(r"^\s*exit /b 1\s*$", body, flags=re.MULTILINE))
    pauses = body.count("pause")

    assert exits >= 1
    assert pauses >= exits, f"{path.name}: {exits} failure exits but only {pauses} pauses"


@pytest.mark.parametrize("path", BATCH_FILES, ids=lambda p: p.name)
def test_no_message_asks_the_operator_to_use_a_terminal(path: Path) -> None:
    """Constraint 7 again: nothing here may be fixed by typing a command."""
    body = text_of(path).lower()
    for phrase in ("command prompt", "powershell", "run the command", "type the following"):
        assert phrase not in body, f"{path.name} sends the operator to a terminal: {phrase}"
