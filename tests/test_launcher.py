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


@pytest.mark.parametrize("path", BATCH_FILES, ids=lambda p: p.name)
def test_no_message_names_a_file_by_an_extension_the_operator_cannot_see(
    path: Path,
) -> None:
    """Windows Explorer hides ``.bat``.

    A message saying to double-click "Set up Narrative Lens.bat" names something
    that is not on the operator's screen: what they see is "Set up Narrative
    Lens", one row above the file they just clicked, with a near-identical name.
    Telling somebody to look for a filename they cannot see is how they end up
    clicking the same wrong file twice.

    Only lines the operator reads are checked. ``call "Set up Narrative
    Lens.bat"`` is a command and needs the real name.
    """
    spoken = [
        line for line in text_of(path).splitlines()
        if line.strip().lower().startswith("echo ")
    ]

    offenders = [line.strip() for line in spoken if ".bat" in line.lower()]

    assert not offenders, f"{path.name} names a hidden extension to the operator: {offenders}"


# --------------------------------------------------------------------------
# The launcher does the setup rather than sending the operator away
# --------------------------------------------------------------------------


def test_the_launcher_offers_to_run_the_setup_itself() -> None:
    """The second thing the first real Windows run found.

    The launcher knew exactly what was missing and exactly which file fixed it,
    and still made the operator go and find that file — which they did not, and
    the app failed to start a second time in the same way. Knowing the answer
    and not acting on it is a design choice, and it was the wrong one.
    """
    body = text_of(LAUNCHER)

    assert 'call "Set up Narrative Lens.bat"' in body, (
        "the launcher no longer runs the setup for the operator"
    )
    assert "choice" in body, "the launcher runs the setup without asking first"


def test_the_launcher_checks_again_after_setting_up() -> None:
    """Setup can fail. Starting anyway would replace a clear message with a
    confusing one, so readiness is asked a second time and the answer decides.
    """
    body = text_of(LAUNCHER)

    assert body.count("call :check_ready") >= 2
    assert ":setup_failed" in body


def test_declining_the_setup_is_a_real_answer() -> None:
    """N means no, and says how to change your mind. It is not a dead end."""
    body = text_of(LAUNCHER)

    assert ":declined" in body
    assert "press Y" in body


def test_the_setup_does_not_stop_to_be_thanked_when_the_launcher_called_it() -> None:
    """Two "press any key"s in a row, for one double-click, is one too many."""
    body = text_of(SETUP)

    assert 'if /i "%~1"=="from-launcher"' in body
    assert "from-launcher" in text_of(LAUNCHER)


# --------------------------------------------------------------------------
# Batch mechanics that cannot be run here and would fail silently there
# --------------------------------------------------------------------------


@pytest.mark.parametrize("path", BATCH_FILES, ids=lambda p: p.name)
def test_every_jump_lands_on_a_label_that_exists(path: Path) -> None:
    """``goto`` at a label that is not there aborts the script mid-way.

    On Windows that prints one line about a missing batch label into a window
    that then closes. There is no way for the operator to read it, so it looks
    exactly like nothing happening at all.
    """
    body = text_of(path)
    labels = set(re.findall(r"^\s*:([A-Za-z_]\w*)", body, re.MULTILINE))
    jumps = set(re.findall(r"goto\s+:?([A-Za-z_]\w*)", body, re.IGNORECASE))
    jumps |= set(re.findall(r"call\s+:([A-Za-z_]\w*)", body, re.IGNORECASE))

    missing = sorted(jumps - labels - {"eof"})

    assert not missing, f"{path.name} jumps to labels that do not exist: {missing}"


def test_the_yes_no_answer_is_tested_in_the_order_batch_requires() -> None:
    """``if errorlevel N`` means "N or more", not "exactly N".

    ``choice`` answers Y with 1 and N with 2, so testing 1 first matches *both*
    and the operator's "no" would silently start a several-minute install they
    just declined. The 2 has to be tested first, and this is the kind of thing
    that reads correctly and behaves backwards.
    """
    body = text_of(LAUNCHER)
    after_choice = body.split("choice ", 1)[1]
    checks = re.findall(r"if errorlevel (\d)", after_choice)

    assert checks, "the answer to the setup question is never tested"
    assert checks[0] == "2", f"the yes/no answer is tested in the wrong order: {checks}"


def test_the_main_flow_stops_before_the_helpers() -> None:
    """Subroutines live at the bottom; batch will run straight into them.

    Without an explicit exit, a successful start would fall through and run
    ``:find_python`` and ``:check_ready`` again as if they were the next steps.
    """
    body = text_of(LAUNCHER)
    first_helper = body.index("\n:find_python")
    before = body[:first_helper]

    assert re.search(r"^exit /b 0\s*$", before, re.MULTILINE), (
        "the launcher runs on into its own helpers after starting the app"
    )
