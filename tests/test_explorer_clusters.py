"""The 3D Explorer and the k-means overlay.

Acceptance criterion 11: the Explorer plots any three dimensions, and the
cluster overlay is deterministic and always labelled "descriptive only". Both
halves of that are load-bearing. The determinism is what makes a cluster
something two people can discuss rather than something that moves when you look
away; the label is what stops a group of nearby dots being read as a finding
about why they are near each other.
"""

from __future__ import annotations

import time

from fastapi.testclient import TestClient

from backend.clusters import CLUSTER_CAVEAT, SEED
from tests.patterns_fixtures import GOLDEN_DEFINITION, build_golden_dataset
from tests.queue_fixtures import make_framework, proposed_import


def _explorer(client: TestClient, framework_id: int, **params) -> dict:
    response = client.get(f"/api/explorer/{framework_id}", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def _clusters(client: TestClient, framework_id: int, **params) -> dict:
    response = client.get(f"/api/clusters/{framework_id}", params=params)
    assert response.status_code == 200, response.text
    return response.json()


# --------------------------------------------------------------------------
# The Explorer
# --------------------------------------------------------------------------


def test_every_numeric_answer_becomes_a_plottable_dimension(
    client: TestClient,
) -> None:
    framework = build_golden_dataset(client)

    view = _explorer(client, framework["id"])

    ids = [dimension["id"] for dimension in view["dimensions"]]
    # Two triads of three corners, one dyad, three chips of two axes each.
    assert ids[:3] == ["t1:Speed", "t1:Care", "t1:Cost"]
    assert "d1" in ids
    assert "s1:Planning:x" in ids and "s1:Planning:y" in ids
    assert len(ids) == 6 + 1 + 6


def test_an_mcq_is_not_offered_as_an_axis(client: TestClient) -> None:
    """Plotting a category on an axis would invent an order nobody wrote."""
    framework = build_golden_dataset(client)

    view = _explorer(client, framework["id"])

    assert all("m1" not in dimension["id"] for dimension in view["dimensions"])


def test_dimensions_are_labelled_in_the_operators_own_words(
    client: TestClient,
) -> None:
    framework = build_golden_dataset(client)

    view = _explorer(client, framework["id"])

    by_id = {dimension["id"]: dimension for dimension in view["dimensions"]}
    assert by_id["t1:Speed"]["label"] == "What drove this? — Speed"
    assert by_id["d1"]["label"] == "How supported? (Alone → Backed)"
    assert by_id["s1:Planning:x"]["label"] == "Planning — Routine → Novel"


def test_every_story_carries_the_values_it_answered(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    view = _explorer(client, framework["id"])

    assert view["total"] == 20
    first = view["points"][0]
    assert round(sum(first["values"][f"t1:{c}"] for c in ("Speed", "Care", "Cost")), 6) == 1.0
    assert 0.0 <= first["values"]["d1"] <= 1.0


def test_a_skipped_question_leaves_a_gap_rather_than_a_zero(
    client: TestClient,
) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)
    client.post(
        "/api/capture",
        json={
            "framework_id": framework["id"],
            "text": "A story with one answer only.",
            "significations": [{"signifier_id": "d1", "value": {"value": 0.7}}],
        },
    )

    view = _explorer(client, framework["id"])

    assert view["points"][0]["values"] == {"d1": 0.7}


def test_the_explorer_reads_the_same_stories_as_everything_else(
    client: TestClient,
) -> None:
    framework = make_framework(client)
    proposed_import(client, framework["id"])

    assert _explorer(client, framework["id"])["total"] == 0


def test_a_filter_narrows_the_explorer_too(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    assert _explorer(client, framework["id"], respondent_group="Ops")["total"] == 7


# --------------------------------------------------------------------------
# The clusters
# --------------------------------------------------------------------------


def test_clusters_are_deterministic(client: TestClient) -> None:
    """PRD §9 assumption 8 pins the seed; the same stories always group the same."""
    framework = build_golden_dataset(client)

    first = _clusters(client, framework["id"], k=3)
    second = _clusters(client, framework["id"], k=3)

    assert first == second
    assert first["seed"] == SEED == 42


def test_every_story_lands_in_exactly_one_cluster(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    view = _clusters(client, framework["id"], k=3)

    assert view["computed"] is True
    members = [i for entry in view["clusters"] for i in entry["anecdote_ids"]]
    assert len(members) == len(set(members)) == 20
    assert len(view["assignments"]) == 20
    assert sum(entry["size"] for entry in view["clusters"]) == 20


def test_the_caveat_travels_with_the_clusters_always(client: TestClient) -> None:
    """Acceptance criterion 11: always labelled "descriptive only"."""
    framework = build_golden_dataset(client)

    view = _clusters(client, framework["id"], k=3)

    assert view["caveat"] == CLUSTER_CAVEAT == "statistical clusters — descriptive only"


def test_the_caveat_is_there_even_when_nothing_could_be_computed(
    client: TestClient,
) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)

    view = _clusters(client, framework["id"], k=3)

    assert view["computed"] is False
    assert view["caveat"] == CLUSTER_CAVEAT


def test_a_centre_is_in_the_readers_own_units(client: TestClient) -> None:
    """Standardised inside, but a centre you could point at on the widget."""
    framework = build_golden_dataset(client)

    view = _clusters(client, framework["id"], k=3)

    centre = view["clusters"][0]["centre"]
    assert 0.0 <= centre["d1"] <= 1.0
    assert round(sum(centre[f"t1:{c}"] for c in ("Speed", "Care", "Cost")), 3) == 1.0


def test_too_few_stories_says_so_rather_than_grouping_anyway(
    client: TestClient,
) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)
    for index in range(3):
        client.post(
            "/api/capture",
            json={
                "framework_id": framework["id"],
                "text": f"Story {index}.",
                "significations": [{"signifier_id": "d1", "value": {"value": index / 4}}],
            },
        )

    view = _clusters(client, framework["id"], k=3)

    assert view["computed"] is False
    assert "too few" in view["reason"]
    assert view["clusters"] == []


def test_stories_that_are_all_alike_say_so(client: TestClient) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)
    for index in range(8):
        client.post(
            "/api/capture",
            json={
                "framework_id": framework["id"],
                "text": f"Story {index}.",
                "significations": [{"signifier_id": "d1", "value": {"value": 0.5}}],
            },
        )

    view = _clusters(client, framework["id"], k=3)

    assert view["computed"] is False
    assert "too alike" in view["reason"]


def test_only_questions_everyone_answered_are_grouped_on(client: TestClient) -> None:
    """Filling a gap with a mean would be inventing an answer."""
    framework = build_golden_dataset(client)
    client.post(
        "/api/capture",
        json={
            "framework_id": framework["id"],
            "text": "A story that answered only the slider.",
            "significations": [{"signifier_id": "d1", "value": {"value": 0.3}}],
        },
    )

    view = _clusters(client, framework["id"], k=2)

    assert view["dimensions"] == ["d1"]
    assert len(view["assignments"]) == 21


def test_k_is_held_inside_a_range_that_means_something(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    assert client.get(f"/api/clusters/{framework['id']}", params={"k": 1}).status_code == 422
    assert client.get(f"/api/clusters/{framework['id']}", params={"k": 9}).status_code == 422
    assert _clusters(client, framework["id"], k=2)["k"] == 2
    assert _clusters(client, framework["id"], k=6)["k"] == 6


def test_clusters_are_inside_the_200ms_budget(client: TestClient) -> None:
    framework = build_golden_dataset(client)

    start = time.perf_counter()
    client.get(f"/api/clusters/{framework['id']}", params={"k": 3})
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 200
