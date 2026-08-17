"""The edit log reads as English, not as a schema path (constraint 7).

The log stores ``triads.0.corners.1`` because that points at exactly one string
and PRD §3 fixes the shape. The Studio showed it verbatim, which made the edit
log the last place in the app where a non-technical operator met a machine's
idea of a name.

The paths are generated on the Python side and translated on the JavaScript
side, so the test starts from paths the app actually produces — a real edit
through :func:`build_edit_log_entries` — and runs them through the real
translator in Node. A table of hand-written paths would have proved that the
translator handles the paths I thought of.

Skipped when Node is not installed, so the Python suite still runs anywhere.
"""

from __future__ import annotations

import datetime as dt
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from backend.edit_semantics import build_edit_log_entries
from backend.framework_schema import FrameworkDefinition
from tests.queue_fixtures import FULL_DEFINITION

NODE = shutil.which("node")
FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "src"

pytestmark = pytest.mark.skipif(
    NODE is None or not FRONTEND.exists(),
    reason="Node or the frontend source is not available",
)

DESCRIBE = """
import { describePath } from "./studio/editLog.js";

console.log(JSON.stringify(INPUT_PATHS.map(describePath)));
"""


def _describe(paths: list[str]) -> list[str]:
    script = DESCRIBE.replace("INPUT_PATHS", json.dumps(paths))
    result = subprocess.run(
        [NODE, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=FRONTEND,
    )
    if result.returncode != 0:
        raise AssertionError(f"node failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def _reworded() -> dict:
    """The full fixture with one string changed in every kind of place."""
    changed = json.loads(json.dumps(FULL_DEFINITION))
    changed["prompt_text"] = "Tell us about a shift that stayed with you."
    changed["triads"][0]["corners"][1] = "Carefulness"
    changed["dyads"][0]["left"] = "On my own"
    changed["mcqs"][0]["options"][0] = "It went well"
    changed["stones"]["chips"][0] = "Planning it"
    changed["stones"]["x_axis"]["low"] = "Everyday"
    changed["capture_settings"]["anonymity_text"] = "Nobody records who you are."
    return changed


@pytest.fixture(scope="module")
def described() -> dict[str, str]:
    """Every path a real wording fix produces, with what the Studio shows."""
    entries = build_edit_log_entries(
        FrameworkDefinition.model_validate(FULL_DEFINITION),
        FrameworkDefinition.model_validate(_reworded()),
        dt.datetime(2026, 8, 17, 9, 0, tzinfo=dt.UTC),
    )
    paths = [entry["field_path"] for entry in entries]
    return dict(zip(paths, _describe(paths), strict=True))


def test_the_real_edit_paths_are_all_translated(described: dict[str, str]) -> None:
    """Nothing falls through to the raw path — the whole surface is covered."""
    assert len(described) == 7

    for path, phrase in described.items():
        assert phrase != path, f"{path} was shown as itself"
        assert "." not in phrase, f"{path} → {phrase}"
        assert "_" not in phrase, f"{path} → {phrase}"


def test_a_repeated_signifier_is_counted_from_one(described: dict[str, str]) -> None:
    """The second corner of the first triangle, as the operator would say it."""
    assert described["triads.0.corners.1"] == "Triangle 1 · corner 2"
    assert described["mcqs.0.options.0"] == "Choice 1 · option 1"


def test_the_plain_strings_are_named_plainly(described: dict[str, str]) -> None:
    assert described["prompt_text"] == "The story prompt"
    assert described["capture_settings.anonymity_text"] == "The anonymity statement"
    assert described["stones.x_axis.low"] == "The square · the across axis · the low end"
    assert described["dyads.0.left"] == "Slider 1 · the left end"


def test_an_unknown_path_is_shown_rather_than_swallowed() -> None:
    """A log entry nobody planned for is still a record of a change."""
    assert _describe(["something.we.never.wrote"]) == ["something.we.never.wrote"]
    assert _describe([""]) == [""]
