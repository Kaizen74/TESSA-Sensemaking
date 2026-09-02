"""The landscape golden — peaks stable to ±0.02 (PRD §6, Phase 8).

The second of the two goldens. The pattern golden is byte-identical because a 2D
aggregate is counting; a landscape is a density estimate, and pinning it to the
last decimal would fail on a scipy point release without anything being wrong.

±0.02 of the triangle's width is the right size of tolerance: about a fiftieth
of the shape, far tighter than any reading a person takes off the terrain, and
loose enough to survive a library rounding its arithmetic differently. A peak
that has genuinely moved — because the bandwidth rule changed, or the grid, or
the way points are placed — moves much further than that.

Counts are held exactly. A peak's label says "four stories sit here", and that
is arithmetic, not estimation.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from tests.patterns_fixtures import build_golden_dataset

PEAKS_GOLDEN = Path(__file__).resolve().parent / "golden" / "landscape_peaks.json"

#: PRD §6: "landscape peaks on golden set stable ±0.02".
TOLERANCE = 0.02


def peaks_of(
    client: TestClient,
    framework_id: int,
    triad_id: str,
    signified_by: str = "all",
) -> list[dict]:
    """The peaks of one triangle, under a stated provenance choice.

    ``all`` by default, because this golden was written before the delta gave
    the endpoint a choice at all, and back then it drew every placement. Saying
    so explicitly keeps the stored peaks measuring the population they were
    measured on, rather than silently following the new default (delta §6,
    baseline block).
    """
    response = client.get(
        f"/api/landscape/{framework_id}/{triad_id}",
        params={"signified_by": signified_by},
    )
    assert response.status_code == 200, response.text
    panel = response.json()["panels"][0]
    return [
        {
            "x": peak["x"],
            "y": peak["y"],
            "count": peak["count"],
            "nearest_corner": peak["nearest_corner"],
        }
        for peak in panel["peaks"]
    ]


def produce_peaks(client: TestClient) -> str:
    framework = build_golden_dataset(client)
    payload = {
        triad_id: peaks_of(client, framework["id"], triad_id)
        for triad_id in ("t1", "t2")
    }
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def test_the_landscape_golden_exists() -> None:
    assert PEAKS_GOLDEN.is_file(), (
        "the landscape golden is missing; regenerate it with "
        "`python -m tests.regenerate_golden`"
    )


def test_peaks_are_stable_within_tolerance(client: TestClient) -> None:
    """The headline guarantee: the terrain does not drift under anyone's feet."""
    stored = json.loads(PEAKS_GOLDEN.read_text(encoding="utf-8"))
    framework = build_golden_dataset(client)

    for triad_id, expected in stored.items():
        produced = peaks_of(client, framework["id"], triad_id)
        assert len(produced) == len(expected), triad_id
        for got, want in zip(produced, expected, strict=True):
            assert abs(got["x"] - want["x"]) <= TOLERANCE, (triad_id, got, want)
            assert abs(got["y"] - want["y"]) <= TOLERANCE, (triad_id, got, want)
            # Counts are counting, not estimating.
            assert got["count"] == want["count"], (triad_id, got, want)
            assert got["nearest_corner"] == want["nearest_corner"], (triad_id, got, want)


def test_the_golden_holds_real_peaks() -> None:
    """A golden of empty lists would pass the tolerance test forever."""
    stored = json.loads(PEAKS_GOLDEN.read_text(encoding="utf-8"))

    assert set(stored) == {"t1", "t2"}
    for triad_id, peaks in stored.items():
        assert peaks, triad_id
        for peak in peaks:
            assert peak["count"] > 0
            assert 0.0 <= peak["x"] <= 1.0
            assert 0.0 <= peak["y"] <= 1.0


def test_the_new_default_finds_the_same_peaks_on_this_fixture(client: TestClient) -> None:
    """The delta changed which placements are drawn, not where they land.

    Every story in the golden set was signified by the person who told it, so
    the participant default and ``all`` cover the same points and must produce
    the same terrain — exactly, not within tolerance, because it is the same
    arithmetic on the same numbers. This is the evidence that the stored peaks
    did not move when the default flipped; if it ever fails, the filter is
    dropping placements a storyteller made.
    """
    stored = json.loads(PEAKS_GOLDEN.read_text(encoding="utf-8"))
    framework = build_golden_dataset(client)

    for triad_id in stored:
        assert peaks_of(client, framework["id"], triad_id, signified_by="participant") == peaks_of(
            client, framework["id"], triad_id, signified_by="all"
        ), triad_id


def test_the_same_stories_give_the_same_peaks_twice(client: TestClient) -> None:
    """Determinism against itself, not only against the stored file."""
    framework = build_golden_dataset(client)

    first = peaks_of(client, framework["id"], "t1")
    second = peaks_of(client, framework["id"], "t1")

    assert first == second
