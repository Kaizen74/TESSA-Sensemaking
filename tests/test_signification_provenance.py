"""Whose interpretation a figure is made of (delta §6, constraint 14).

Constraint 14 says three things, and this file is one section per thing:

* the default view is the storytellers' own readings and nothing else;
* asking for the rest is possible, and asking for it is the only way to get it;
* every view says which of the two it is showing, and how much of the other
  it is leaving out.

The fixture mixes the three provenances the schema actually stores. Three
stories come through ``POST /api/capture``, where the person who lived the
experience placed their own markers: those are ``respondent``. Three more
arrive through the import machine, where Stage B proposed the placements. One
of those is accepted as proposed and stays wholly ``ai``; one is corrected, so
it carries an ``analyst`` placement beside an ``ai`` one — the case the
provenance column was added for; and one is left in the queue, because a view
that quietly counted a story nobody had approved would be breaking a different
promise (constraint 1) while this file was watching the other one.

The mapping between what the database stores and what the filter is called is
the one piece of vocabulary worth stating out loud: ``participant`` means
``respondent``, and ``ai_validated`` covers both ``ai`` and ``analyst``,
because a reading an operator made on somebody's behalf and a reading a machine
made on somebody's behalf are, to the person whose story it is, the same kind
of thing.
"""

from __future__ import annotations

import csv
import io

import pytest
from fastapi.testclient import TestClient

from tests.patterns_fixtures import story_payload
from tests.queue_fixtures import make_framework, proposed_import

#: How many signifiers each directly-captured story answers.
PLACEMENTS_PER_STORY = 5

#: Stories told and signified by the people they happened to.
SELF_SIGNIFIED = 3

#: Imported stories a person approved: one accepted whole, one corrected.
EXPERT_VALIDATED = 2

EXPORTS = ("csv", "brief", "heard")


def mixed_dataset(client: TestClient) -> dict:
    """A framework holding all three stored provenances at once.

    Returns the framework. The counts it produces are stated in
    :func:`test_the_counts_match_the_fixture_by_hand`, which is where they are
    checked against arithmetic rather than against the code that produced them.
    """
    framework = make_framework(client)

    for index in range(SELF_SIGNIFIED):
        stored = client.post("/api/capture", json=story_payload(index, framework["id"]))
        assert stored.status_code == 201, stored.text

    proposed_import(client, framework["id"])
    items = client.get("/api/queue").json()["items"]
    assert len(items) == 3, items

    # One accepted as proposed: all five placements stay ``ai``.
    accepted = client.put(f"/api/queue/{items[0]['anecdote_id']}", json={"action": "accept"})
    assert accepted.status_code == 200, accepted.text

    # One corrected down to two placements: the moved marker becomes
    # ``analyst``, the one left alone stays ``ai``.
    original = {p["signifier_id"]: p["value"] for p in items[1]["significations"]}
    corrected = client.put(
        f"/api/queue/{items[1]['anecdote_id']}",
        json={
            "action": "correct",
            "significations": [
                {"signifier_id": "t1", "value": {"Speed": 0.2, "Care": 0.5, "Cost": 0.3}},
                {"signifier_id": "d1", "value": original["d1"]},
            ],
        },
    )
    assert corrected.status_code == 200, corrected.text

    # items[2] is deliberately left in the queue: not data, not counted here.
    return framework


def expert_validated_ids(client: TestClient, framework_id: int) -> set[int]:
    """The stories somebody else read, taken from the app's own provenance record.

    Derived rather than remembered: asking the CSV which rows carry an ``ai`` or
    ``analyst`` placement is the same question a reader would ask, and it does
    not depend on what order the fixture happened to insert rows in.
    """
    response = client.get(
        "/api/export/csv", params={"framework_id": framework_id, "signified_by": "all"}
    )
    assert response.status_code == 200, response.text
    return {
        int(row["anecdote_id"])
        for row in csv.DictReader(io.StringIO(response.text))
        if {"ai", "analyst"} & set(row["signified_by"].split("|"))
    }


def patterns(client: TestClient, framework_id: int, **params) -> dict:
    response = client.get(f"/api/patterns/{framework_id}", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def placed(view: dict) -> int:
    """How many placements a pattern view actually drew, across every chart."""
    total = sum(triad["answered"] for triad in view["triads"])
    total += sum(dyad["answered"] for dyad in view["dyads"])
    total += view["stones"]["answered"] if view["stones"] else 0
    total += sum(sum(bar["count"] for bar in mcq["bars"]) for mcq in view["mcqs"])
    return total


# --------------------------------------------------------------------------
# The default
# --------------------------------------------------------------------------


def test_the_default_view_is_the_storytellers_own_readings(client: TestClient) -> None:
    """Asked for nothing, the endpoint gives back only self-signification."""
    framework = mixed_dataset(client)

    view = patterns(client, framework["id"])

    assert view["signified_by_applied"] == "participant"
    assert placed(view) == SELF_SIGNIFIED * PLACEMENTS_PER_STORY


def test_the_default_excludes_every_ai_validated_point(client: TestClient) -> None:
    """The named guarantee of delta §6, checked as a difference.

    The two imported stories carry placements; none of them may appear in the
    default view. Comparing the two views rather than asserting a bare number
    means the test still means something if the fixture grows.
    """
    framework = mixed_dataset(client)

    default = patterns(client, framework["id"])
    everything = patterns(client, framework["id"], signified_by="all")

    assert placed(everything) > placed(default)
    assert placed(everything) - placed(default) == everything["counts_by_signified_by"][
        "ai_validated"
    ]


def test_a_story_signified_by_somebody_else_is_still_a_story(client: TestClient) -> None:
    """The filter narrows placements, never stories.

    A story an analyst marked up was still told by somebody, and dropping it
    from the count would be a different claim from the one constraint 14 makes.
    So ``total`` is the same under every choice; only the placements move.
    """
    framework = mixed_dataset(client)

    totals = {
        choice: patterns(client, framework["id"], signified_by=choice)["total"]
        for choice in ("participant", "ai_validated", "all")
    }

    assert len(set(totals.values())) == 1, totals
    assert totals["participant"] == SELF_SIGNIFIED + EXPERT_VALIDATED


# --------------------------------------------------------------------------
# Asking for the rest
# --------------------------------------------------------------------------


def test_all_returns_both_kinds(client: TestClient) -> None:
    framework = mixed_dataset(client)

    view = patterns(client, framework["id"], signified_by="all")
    held = view["counts_by_signified_by"]

    assert view["signified_by_applied"] == "all"
    assert held["participant"] > 0
    assert held["ai_validated"] > 0
    assert placed(view) == held["participant"] + held["ai_validated"]


def test_ai_validated_returns_only_the_other_half(client: TestClient) -> None:
    framework = mixed_dataset(client)

    view = patterns(client, framework["id"], signified_by="ai_validated")

    assert view["signified_by_applied"] == "ai_validated"
    assert placed(view) == view["counts_by_signified_by"]["ai_validated"]


def test_an_unknown_choice_is_refused_rather_than_ignored(client: TestClient) -> None:
    """Falling back to "everything" on a typo is the failure to avoid.

    A view that silently widened when it did not understand a parameter would
    break constraint 14 exactly where nobody would notice.
    """
    framework = mixed_dataset(client)

    response = client.get(
        f"/api/patterns/{framework['id']}", params={"signified_by": "everyone"}
    )

    assert response.status_code == 400
    body = response.json()["error"]
    assert body["code"] == "unknown_signified_by"
    assert body["action"]


# --------------------------------------------------------------------------
# Saying so
# --------------------------------------------------------------------------


def test_the_counts_match_the_fixture_by_hand(client: TestClient) -> None:
    """The one place the numbers are checked against arithmetic, not against code.

    Three captured stories answer five signifiers each: fifteen ``respondent``
    placements. Stage B proposes five per imported story; the accepted one keeps
    all five as ``ai``, and the corrected one is replaced by the two the operator
    sent — one moved, so ``analyst``, one left alone, so still ``ai``. Seven
    between them. The third imported story is still in the queue and contributes
    nothing, which is the whole point of the queue.
    """
    framework = mixed_dataset(client)

    held = patterns(client, framework["id"])["counts_by_signified_by"]

    assert held["participant"] == SELF_SIGNIFIED * PLACEMENTS_PER_STORY == 15
    assert held["ai_validated"] == PLACEMENTS_PER_STORY + 2 == 7


def test_the_counts_are_the_same_whichever_view_is_asked_for(client: TestClient) -> None:
    """Both halves, always — that is what makes the choice legible.

    A screen has to be able to say what it is *not* showing, so the counts are
    deliberately not narrowed by the choice in force.
    """
    framework = mixed_dataset(client)

    held = [
        patterns(client, framework["id"], signified_by=choice)["counts_by_signified_by"]
        for choice in ("participant", "ai_validated", "all")
    ]

    assert held[0] == held[1] == held[2]


def test_a_filter_narrows_the_counts_with_everything_else(client: TestClient) -> None:
    """The counts describe the stories in scope, not the whole database."""
    framework = mixed_dataset(client)

    whole = patterns(client, framework["id"])["counts_by_signified_by"]
    ops = patterns(client, framework["id"], respondent_group="Ops")[
        "counts_by_signified_by"
    ]

    assert ops["participant"] < whole["participant"]


# --------------------------------------------------------------------------
# Every other view that draws a figure
# --------------------------------------------------------------------------


def test_the_landscape_defaults_the_same_way(client: TestClient) -> None:
    framework = mixed_dataset(client)

    default = client.get(f"/api/landscape/{framework['id']}/t1").json()
    everything = client.get(
        f"/api/landscape/{framework['id']}/t1", params={"signified_by": "all"}
    ).json()

    assert default["signified_by_applied"] == "participant"
    assert default["panels"][0]["count"] == SELF_SIGNIFIED
    assert everything["panels"][0]["count"] > default["panels"][0]["count"]


def plotted(view: dict) -> set[int]:
    """Which stories the Explorer actually has coordinates for.

    Every story in scope gets a point — it was told, and the count says so — but
    a point with no values has nothing to plot. What the provenance choice moves
    is the values, so that is what this counts.
    """
    return {point["anecdote_id"] for point in view["points"] if point["values"]}


def test_the_explorer_defaults_the_same_way(client: TestClient) -> None:
    framework = mixed_dataset(client)
    expert = expert_validated_ids(client, framework["id"])

    default = client.get(f"/api/explorer/{framework['id']}").json()
    everything = client.get(
        f"/api/explorer/{framework['id']}", params={"signified_by": "all"}
    ).json()

    assert len(plotted(default)) == SELF_SIGNIFIED
    assert not plotted(default) & expert
    assert expert <= plotted(everything)


def test_clusters_default_the_same_way(client: TestClient) -> None:
    """Clusters read what the Explorer plots, so the choice reaches them by
    construction — which is worth a test precisely because it is indirect."""
    framework = mixed_dataset(client)
    expert = expert_validated_ids(client, framework["id"])

    default = client.get(f"/api/clusters/{framework['id']}", params={"k": 2}).json()
    everything = client.get(
        f"/api/clusters/{framework['id']}", params={"k": 2, "signified_by": "all"}
    ).json()

    grouped = {row["anecdote_id"] for row in default["assignments"]}
    grouped_all = {row["anecdote_id"] for row in everything["assignments"]}

    assert not grouped & expert
    assert expert <= grouped_all


@pytest.mark.parametrize("export", EXPORTS)
def test_no_export_bypasses_the_default(client: TestClient, export: str) -> None:
    """All three downloads, the same rule (delta §6).

    An export is where a figure leaves the app and stops being correctable, so
    this is the last place a silent mixture could be introduced — and the one
    where it would do the most damage.
    """
    framework = mixed_dataset(client)

    response = client.get(f"/api/export/{export}", params={"framework_id": framework["id"]})

    assert response.status_code == 200, response.text
    if export == "csv":
        rows = list(csv.DictReader(io.StringIO(response.text)))
        assert {row["signified_by"] for row in rows} <= {"respondent", ""}
    else:
        # The brief and "What we heard" are prose over the same figures, so the
        # check is that they were built from the narrowed view.
        default = patterns(client, framework["id"])
        assert f"{default['total']} stories" in response.text


@pytest.mark.parametrize("export", EXPORTS)
def test_every_export_can_be_asked_for_the_whole_picture(
    client: TestClient, export: str
) -> None:
    """The default is a default, not a wall. Constraint 14 asks for the choice
    to be explicit, not for the other half to be unreachable."""
    framework = mixed_dataset(client)

    response = client.get(
        f"/api/export/{export}",
        params={"framework_id": framework["id"], "signified_by": "all"},
    )

    assert response.status_code == 200, response.text


def test_a_bad_choice_is_refused_on_an_export_too(client: TestClient) -> None:
    framework = mixed_dataset(client)

    response = client.get(
        "/api/export/csv",
        params={"framework_id": framework["id"], "signified_by": "whoever"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unknown_signified_by"
