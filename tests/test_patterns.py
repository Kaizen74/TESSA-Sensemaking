"""The patterns endpoint: what it counts, what it sorts, what it refuses.

Three things are being held down here. That only validated stories are counted,
because a figure on screen has to be one a person approved. That every
categorical view arrives already sorted by value, because §5b's grammar is a
contract and not a suggestion. And that two framework versions are never pooled
without someone asking for it.
"""

from __future__ import annotations

import time

from fastapi.testclient import TestClient

from tests.patterns_fixtures import GOLDEN_DEFINITION, build_golden_dataset
from tests.queue_fixtures import make_framework, proposed_import


def _patterns(client: TestClient, framework_id: int, **params) -> dict:
    response = client.get(f"/api/patterns/{framework_id}", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def _capture(client: TestClient, framework_id: int, **overrides) -> dict:
    body = {
        "framework_id": framework_id,
        "text": "A shift where the plan and the work did not line up.",
        "significations": [
            {"signifier_id": "t1", "value": {"Speed": 0.5, "Care": 0.3, "Cost": 0.2}},
            {"signifier_id": "d1", "value": {"value": 0.8}},
            {"signifier_id": "m1", "value": {"selected": ["Well"]}},
        ],
    }
    body.update(overrides)
    created = client.post("/api/capture", json=body)
    assert created.status_code == 201, created.text
    return created.json()


# --------------------------------------------------------------------------
# §5b chart grammar, as a property of the API
# --------------------------------------------------------------------------


def test_every_categorical_view_arrives_sorted_by_value(client: TestClient) -> None:
    """§5b: horizontal bars sorted by value, for every categorical view.

    Asserted against the endpoint rather than the chart, so a chart cannot be
    drawn unsorted by forgetting to sort it.
    """
    framework = build_golden_dataset(client)

    view = _patterns(client, framework["id"])

    for chart in view["mcqs"] + view["demographics"]:
        counts = [bar["count"] for bar in chart["bars"]]
        assert counts == sorted(counts, reverse=True), chart["id"]


def test_bars_tied_on_value_are_ordered_alphabetically(client: TestClient) -> None:
    """A tie must not wobble between runs, or the golden could never hold."""
    framework = build_golden_dataset(client)

    view = _patterns(client, framework["id"])
    groups = next(c for c in view["demographics"] if c["id"] == "respondent_group")

    tied = [bar["label"] for bar in groups["bars"] if bar["count"] == groups["bars"][0]["count"]]
    assert tied == sorted(tied)


def test_an_option_nobody_chose_still_gets_a_bar(client: TestClient) -> None:
    """A zero is a finding. Dropping it would quietly redraw the question."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    _capture(client, framework["id"])

    view = _patterns(client, framework["id"])

    labels = {bar["label"] for bar in view["mcqs"][0]["bars"]}
    assert labels == {"Well", "Badly", "Unresolved"}
    assert view["mcqs"][0]["bars"][-1]["count"] == 0


def test_shares_are_of_the_stories_that_answered(client: TestClient) -> None:
    """A skipped question is not a zero — nobody said nothing on purpose."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    _capture(client, framework["id"])
    _capture(
        client,
        framework["id"],
        significations=[{"signifier_id": "d1", "value": {"value": 0.4}}],
    )

    view = _patterns(client, framework["id"])

    assert view["total"] == 2
    assert view["mcqs"][0]["answered"] == 1
    assert view["mcqs"][0]["bars"][0]["share"] == 1.0
    assert view["dyads"][0]["answered"] == 2


# --------------------------------------------------------------------------
# What is counted
# --------------------------------------------------------------------------


def test_only_validated_stories_are_counted(client: TestClient) -> None:
    """The no-bypass promise, applied to what the operator actually sees."""
    framework = make_framework(client)
    proposed_import(client, framework["id"])
    _capture(client, framework["id"])

    view = _patterns(client, framework["id"])

    # Three stories are sitting in the queue; only the captured one is data.
    assert view["total"] == 1


def test_validating_a_queued_story_makes_it_count(client: TestClient) -> None:
    framework = make_framework(client)
    proposed_import(client, framework["id"])
    item = client.get("/api/queue").json()["items"][0]

    before = _patterns(client, framework["id"])["total"]
    client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "accept"})
    after = _patterns(client, framework["id"])["total"]

    assert (before, after) == (0, 1)


def test_a_rejected_story_never_counts(client: TestClient) -> None:
    framework = make_framework(client)
    proposed_import(client, framework["id"])
    for item in client.get("/api/queue").json()["items"]:
        client.put(f"/api/queue/{item['anecdote_id']}", json={"action": "reject"})

    assert _patterns(client, framework["id"])["total"] == 0


def test_triad_points_are_the_barycentric_maths_the_widget_uses(
    client: TestClient,
) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)
    _capture(
        client,
        framework["id"],
        significations=[
            {"signifier_id": "t1", "value": {"Speed": 1.0, "Care": 0.0, "Cost": 0.0}}
        ],
    )

    view = _patterns(client, framework["id"])

    # Corner 0 of the unit triangle is the origin.
    assert view["triads"][0]["points"][0]["x"] == 0.0
    assert view["triads"][0]["points"][0]["y"] == 0.0


def test_dyad_histogram_puts_the_far_end_in_the_last_bin(client: TestClient) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)
    _capture(
        client,
        framework["id"],
        significations=[{"signifier_id": "d1", "value": {"value": 1.0}}],
    )

    histogram = _patterns(client, framework["id"])["dyads"][0]["histogram"]

    assert len(histogram) == 10
    assert histogram[-1]["count"] == 1
    assert sum(entry["count"] for entry in histogram) == 1


# --------------------------------------------------------------------------
# Filters
# --------------------------------------------------------------------------


def test_a_filter_narrows_every_chart_at_once(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    everything = _patterns(client, framework["id"])
    ops = _patterns(client, framework["id"], respondent_group="Ops")

    assert everything["total"] == 20
    assert ops["total"] == 7
    assert ops["filters"] == {"respondent_group": "Ops"}
    assert ops["triads"][0]["answered"] == 7
    assert sum(bar["count"] for bar in ops["mcqs"][0]["bars"]) == 7


def test_filters_combine(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    group_only = _patterns(client, framework["id"], respondent_group="Ops")
    both = _patterns(client, framework["id"], respondent_group="Ops", input_method="typed")

    assert 0 < both["total"] < group_only["total"]
    assert both["filters"] == {"respondent_group": "Ops", "input_method": "typed"}


def test_a_filter_that_matches_nothing_is_an_empty_view_not_an_error(
    client: TestClient,
) -> None:
    framework = build_golden_dataset(client)

    view = _patterns(client, framework["id"], respondent_group="Nobody")

    assert view["total"] == 0
    assert view["triads"][0]["points"] == []
    assert all(bar["count"] == 0 for bar in view["mcqs"][0]["bars"])


# --------------------------------------------------------------------------
# Version mixing (PRD §4)
# --------------------------------------------------------------------------


def _second_version(client: TestClient, framework: dict) -> dict:
    """A meaning change: version n+1, old stories left on the old wording."""
    changed = dict(GOLDEN_DEFINITION)
    changed["triads"] = [
        {"id": "t1", "title": "What really drove it?", "corners": ["Speed", "Care", "Cost"]},
        GOLDEN_DEFINITION["triads"][1],
    ]
    response = client.put(
        f"/api/frameworks/{framework['id']}",
        json={"definition": changed, "edit_kind": "meaning_change"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_versions_are_not_pooled_without_being_asked(client: TestClient) -> None:
    """PRD §4: no silent mixing. A v1 answer is not an answer to v2."""
    framework = build_golden_dataset(client)
    second = _second_version(client, framework)
    _capture(client, second["id"])

    v1 = _patterns(client, framework["id"])
    v2 = _patterns(client, second["id"])

    assert v1["total"] == 20
    assert v2["total"] == 1
    assert v1["mixed"] is False and v2["mixed"] is False
    assert v1["versions"] == [] and v2["versions"] == []


def test_mixing_is_available_but_has_to_be_asked_for(client: TestClient) -> None:
    framework = build_golden_dataset(client)
    second = _second_version(client, framework)
    _capture(client, second["id"])

    mixed = _patterns(client, second["id"], mixed=True)

    assert mixed["mixed"] is True
    assert mixed["total"] == 21


def test_mixing_returns_the_version_chip_data(client: TestClient) -> None:
    """§5.4: any view spanning versions must be able to say so on screen."""
    framework = build_golden_dataset(client)
    second = _second_version(client, framework)
    _capture(client, second["id"])

    mixed = _patterns(client, second["id"], mixed=True)

    assert [(entry["version"], entry["count"]) for entry in mixed["versions"]] == [
        (1, 20),
        (2, 1),
    ]
    assert [entry["framework_id"] for entry in mixed["versions"]] == [
        framework["id"],
        second["id"],
    ]


def test_a_mixed_view_still_uses_the_version_you_asked_from(
    client: TestClient,
) -> None:
    """The questions drawn are the ones the operator is looking at."""
    framework = build_golden_dataset(client)
    second = _second_version(client, framework)

    mixed = _patterns(client, second["id"], mixed=True)

    assert mixed["framework_version"] == 2
    assert mixed["triads"][0]["title"] == "What really drove it?"


def test_a_wording_fix_does_not_split_the_data(client: TestClient) -> None:
    """A typo correction stays one version, so nothing needs mixing."""
    framework = build_golden_dataset(client)
    fixed = dict(GOLDEN_DEFINITION)
    fixed["prompt_text"] = "Tell us about a moment at work that stuck with you today."
    response = client.put(
        f"/api/frameworks/{framework['id']}",
        json={"definition": fixed, "edit_kind": "wording_fix"},
    )
    assert response.status_code == 200, response.text

    view = _patterns(client, framework["id"])

    assert view["total"] == 20
    assert view["framework_version"] == 1


# --------------------------------------------------------------------------
# Housekeeping
# --------------------------------------------------------------------------


def test_an_unknown_framework_says_so_in_plain_english(client: TestClient) -> None:
    response = client.get("/api/patterns/404")

    assert response.status_code == 404
    error = response.json()["detail"]["error"]
    assert error["code"] == "framework_not_found"
    assert "Studio" in error["action"]


def test_a_framework_with_no_stories_is_an_empty_view(client: TestClient) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)

    view = _patterns(client, framework["id"])

    assert view["total"] == 0
    assert view["triads"][0]["answered"] == 0
    assert view["stones"]["points"] == []


def test_patterns_are_inside_the_200ms_budget(client: TestClient) -> None:
    """PRD §4: 200ms for non-AI endpoints."""
    framework = build_golden_dataset(client)

    start = time.perf_counter()
    client.get(f"/api/patterns/{framework['id']}")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 200


def test_no_ai_module_is_reachable_from_the_pattern_path() -> None:
    """Constraint 11: patterns are computed, never composed.

    Structural, like the constraint-4 test on the AI client: the promise is
    about the import graph, so a future edit that starts consulting a model to
    smooth or label a pattern has to fail here.
    """
    from pathlib import Path

    backend = Path(__file__).resolve().parent.parent / "backend"
    for name in ("patterns.py", "exports.py", "routers/patterns.py", "routers/exports.py"):
        source = (backend / name).read_text(encoding="utf-8")
        assert "ai_client" not in source, name
        assert "anthropic" not in source.lower(), name
        assert "propose" not in source.replace("proposed", ""), name
