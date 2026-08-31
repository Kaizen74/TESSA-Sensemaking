"""A stored placement must survive the round trip to a widget and back.

The server and the widgets speak different dialects of the same value. A triad
is ``{"Speed": 0.6, "Care": 0.3, "Cost": 0.1}`` in the database and ``[0.6, 0.3,
0.1]`` on screen; stones are ``{"placements": [...]}`` in one and a bare array in
the other. ``toSubmission`` translates screen to server, and ``fromStored``
translates back.

This test exists because the pair got out of step the first time the validation
queue read a stored placement onto a widget: the widget was handed the database
shape, tried to destructure an object as an array, and took the whole screen
down. No Python test could have caught it, and no JavaScript unit test would
have either — the bug was in the *agreement* between the two, so the test has to
start from a value the Python side actually produces.

Skipped when Node is not installed, so the Python suite still runs anywhere.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from backend.framework_schema import FrameworkDefinition
from backend.propose import propose
from tests.queue_fixtures import FULL_DEFINITION

NODE = shutil.which("node")
FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "src"

pytestmark = pytest.mark.skipif(
    NODE is None or not FRONTEND.exists(),
    reason="Node or the frontend source is not available",
)

STORIES = [
    "The parts arrived three hours before the deadline and nobody had told the "
    "night shift they were coming.",
    "The checklist assumed you had both hands free, which on a wet deck you "
    "never do.",
]

ROUND_TRIP = """
import { fromStored, toSubmission } from "./capture/placements.js";

const definition = INPUT_DEFINITION;
const stored = INPUT_STORED;

const order = [
  ...(definition.triads ?? []).map((s) => ["triad", s]),
  ...(definition.dyads ?? []).map((s) => ["dyad", s]),
  ...(definition.stones ? [["stones", definition.stones]] : []),
  ...(definition.mcqs ?? []).map((s) => ["mcq", s]),
];

const out = stored.map((placements) => {
  const byId = Object.fromEntries(placements.map((p) => [p.signifier_id, p.value]));
  const widgetValues = {};
  for (const [kind, signifier] of order) {
    if (byId[signifier.id] !== undefined) {
      widgetValues[signifier.id] = fromStored(kind, signifier, byId[signifier.id]);
    }
  }
  return { widget: widgetValues, back: toSubmission(definition, widgetValues) };
});

console.log(JSON.stringify(out));
"""


def _run_node(script: str) -> list:
    """Run one ES module through Node and read its JSON back."""
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


def _stored_placements() -> list[list[dict]]:
    """Exactly what Stage B writes to the database, for every signifier kind."""
    definition = FrameworkDefinition.model_validate(FULL_DEFINITION)
    return [
        [
            {"signifier_id": placement.signifier_id, "value": placement.value}
            for placement in proposal.placements
        ]
        for proposal in propose(definition, STORIES)
    ]


@pytest.fixture(scope="module")
def round_trip() -> list[dict]:
    stored = _stored_placements()
    script = ROUND_TRIP.replace(
        "INPUT_DEFINITION", json.dumps(FULL_DEFINITION)
    ).replace("INPUT_STORED", json.dumps(stored))
    return _run_node(script)


def test_a_stored_placement_survives_the_round_trip(round_trip: list[dict]) -> None:
    """server shape → widget shape → server shape, unchanged."""
    stored = _stored_placements()

    for original, result in zip(stored, round_trip, strict=True):
        by_id = {entry["signifier_id"]: entry["value"] for entry in original}
        returned = {entry["signifier_id"]: entry["value"] for entry in result["back"]}
        assert returned == by_id


def test_a_triad_reaches_the_widget_as_ordered_numbers(
    round_trip: list[dict],
) -> None:
    """The shape the widget's own maths destructures, in corner order."""
    widget = round_trip[0]["widget"]

    assert isinstance(widget["t1"], list)
    assert len(widget["t1"]) == 3
    assert all(isinstance(weight, (int, float)) for weight in widget["t1"])


def test_a_dyad_reaches_the_widget_as_one_number(round_trip: list[dict]) -> None:
    assert isinstance(round_trip[0]["widget"]["d1"], (int, float))


def test_stones_reach_the_widget_as_a_bare_list(round_trip: list[dict]) -> None:
    placements = round_trip[0]["widget"]["s1"]

    assert isinstance(placements, list)
    assert {entry["label"] for entry in placements} == {"Planning", "Doing", "Fixing"}


def test_an_mcq_keeps_its_own_shape(round_trip: list[dict]) -> None:
    """The one kind whose two dialects happen to agree."""
    assert set(round_trip[0]["widget"]["m1"]) == {"selected"}
