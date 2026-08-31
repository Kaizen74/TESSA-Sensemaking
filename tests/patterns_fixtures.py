"""The twenty-story fixture behind the pattern golden (PRD §6, Phase 7).

Twenty stories with placements fixed by arithmetic rather than chosen by hand,
so the set can be read and re-derived by anyone, and so a change to it is a
visible change to this file rather than a mystery in a JSON blob.

The stories go in through ``POST /api/capture`` rather than straight into the
database. That means the golden is produced by the same validation, rounding and
provenance stamping the operator's own data goes through — a golden built by
bypassing the app would pin the wrong thing.

Every value is exact in decimal: triad weights are tenths that sum to one, dyad
positions are twentieths. Nothing here depends on floating-point luck.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

#: A framework touching all four signifier kinds, so the golden covers every
#: aggregation path rather than only the easy one.
GOLDEN_DEFINITION = {
    "prompt_text": "Tell us about a moment at work that stuck with you.",
    "triads": [
        {"id": "t1", "title": "What drove this?", "corners": ["Speed", "Care", "Cost"]},
        {"id": "t2", "title": "Who decided?", "corners": ["Me", "My team", "Someone else"]},
    ],
    "dyads": [{"id": "d1", "title": "How supported?", "left": "Alone", "right": "Backed"}],
    "stones": {
        "id": "s1",
        "title": "Where did the effort go?",
        "x_axis": {"low": "Routine", "high": "Novel"},
        "y_axis": {"low": "Quiet", "high": "Fraught"},
        "chips": ["Planning", "Doing", "Fixing"],
    },
    "mcqs": [
        {"id": "m1", "title": "How did it end?", "options": ["Well", "Badly", "Unresolved"]}
    ],
    "capture_settings": {"respondent_groups": ["Ops", "Deck", "Support"]},
}

STORY_COUNT = 20

GROUPS = ("Ops", "Deck", "Support")
INPUT_METHODS = ("typed", "paper", "voice")
ENTRY_MODES = ("admin", "kiosk")
OPTIONS = ("Well", "Badly", "Unresolved")

#: Triad weights in tenths, cycled. Deliberately uneven so the aggregate has a
#: direction to find rather than sitting at the centroid.
T1_WEIGHTS = ((6, 3, 1), (4, 4, 2), (2, 5, 3), (7, 2, 1), (3, 3, 4))
T2_WEIGHTS = ((5, 3, 2), (2, 6, 2), (3, 3, 4), (1, 8, 1))


def _tenths(weights: tuple[int, int, int], corners: list[str]) -> dict[str, float]:
    return {corner: part / 10 for corner, part in zip(corners, weights, strict=True)}


def story_payload(index: int, framework_id: int) -> dict:
    """One story, entirely determined by its position in the run."""
    return {
        "framework_id": framework_id,
        "text": (
            f"Story {index:02d}. A shift where the work and the plan did not "
            "quite line up, and somebody decided what to do about it."
        ),
        # Deliberately different periods. Cycling all three at once would make
        # group, method and mode perfectly correlated, and a fixture where every
        # filter is really the same filter cannot test filters combining.
        "input_method": INPUT_METHODS[(index // 2) % len(INPUT_METHODS)],
        "entry_mode": ENTRY_MODES[index % len(ENTRY_MODES)],
        "respondent_group": GROUPS[index % len(GROUPS)],
        "significations": [
            {
                "signifier_id": "t1",
                "value": _tenths(
                    T1_WEIGHTS[index % len(T1_WEIGHTS)], ["Speed", "Care", "Cost"]
                ),
            },
            {
                "signifier_id": "t2",
                "value": _tenths(
                    T2_WEIGHTS[index % len(T2_WEIGHTS)], ["Me", "My team", "Someone else"]
                ),
            },
            {"signifier_id": "d1", "value": {"value": (index % 20) / 20}},
            {
                "signifier_id": "s1",
                "value": {
                    "placements": [
                        {"label": "Planning", "x": (index % 5) / 5, "y": (index % 4) / 4},
                        {"label": "Doing", "x": (index % 4) / 4, "y": (index % 5) / 5},
                        {"label": "Fixing", "x": (index % 3) / 3, "y": (index % 2) / 2},
                    ]
                },
            },
            {
                "signifier_id": "m1",
                "value": {"selected": [OPTIONS[index % len(OPTIONS)]]},
            },
        ],
    }


def build_golden_dataset(client: TestClient) -> dict:
    """Create the framework and its twenty stories. Returns the framework."""
    created = client.post(
        "/api/frameworks", json={"name": "Hangar", "definition": GOLDEN_DEFINITION}
    )
    assert created.status_code == 201, created.text
    framework = created.json()

    for index in range(STORY_COUNT):
        stored = client.post("/api/capture", json=story_payload(index, framework["id"]))
        assert stored.status_code == 201, stored.text

    return framework
