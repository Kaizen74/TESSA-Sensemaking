"""Data-quality signals: centre-parking and skip rate (delta §6, phase B).

The panel these figures feed exists to catch one specific way of being misled.
A tight cluster in the middle of a landscape looks like agreement. It can also
be what a question that did not fit anybody's story looks like, because the
honest response to a trade-off you cannot make is to leave the marker where it
started. Nothing else in the app can tell those two apart, so this counts.

Every expected number below is arithmetic stated in the test rather than read
back off the endpoint: fixtures place a known number of markers in a known
place, and the assertions say what the proportion must be. A test that asked the
code what it computed and then agreed with it would pass forever.

Constraint 11 is checked structurally as well as behaviourally: the last section
proves nothing on this path can reach a language model, with the mock switched
*off* and no API key present — the configuration under which any accidental call
would fail loudly rather than quietly succeed.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.barycentric import CENTROID, distance_from_centre, to_cartesian
from backend.quality import CENTRE_AREA_SHARE, CENTRE_RADIUS
from tests.conftest import median_ms
from tests.patterns_fixtures import GOLDEN_DEFINITION
from tests.queue_fixtures import make_framework

#: Exactly the centre: equal weight on all three corners.
DEAD_CENTRE = {"Speed": 1 / 3, "Care": 1 / 3, "Cost": 1 / 3}

#: A corner, as far from the centre as a placement can get.
HARD_LEAN = {"Speed": 1.0, "Care": 0.0, "Cost": 0.0}

STORY = "A shift where the plan and the work did not line up."


def capture(client: TestClient, framework_id: int, placements: dict[str, dict]) -> int:
    """One story answering exactly the signifiers named, and no others."""
    response = client.post(
        "/api/capture",
        json={
            "framework_id": framework_id,
            "text": STORY,
            "significations": [
                {"signifier_id": signifier_id, "value": value}
                for signifier_id, value in placements.items()
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["anecdote_id"]


def quality(client: TestClient, framework_id: int, **params) -> dict:
    response = client.get(f"/api/quality/{framework_id}", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def row(report: dict, signifier_id: str) -> dict:
    return next(r for r in report["signifiers"] if r["signifier_id"] == signifier_id)


# --------------------------------------------------------------------------
# The circle itself
# --------------------------------------------------------------------------


def test_the_centre_circle_covers_the_share_it_claims() -> None:
    """The radius is derived from an area, so the claim is checkable.

    The panel tells the reader that an even spread would put about a tenth of
    the placements in this circle. That sentence is only true if the circle is
    actually a tenth of the triangle.
    """
    from backend.barycentric import TRIANGLE_AREA

    assert math.isclose(math.pi * CENTRE_RADIUS**2 / TRIANGLE_AREA, CENTRE_AREA_SHARE)


def test_the_whole_circle_fits_inside_the_triangle() -> None:
    """Otherwise the share would be clipped and the sentence above overstated.

    The incircle touches all three sides, so any radius under its own is wholly
    contained.
    """
    incircle_radius = 1.0 / (2.0 * math.sqrt(3.0))

    assert incircle_radius > CENTRE_RADIUS


def test_the_centre_is_where_equal_weights_land() -> None:
    """The centroid and "no lean at all" have to be the same point.

    To the precision the conversion claims, and no further: points are rounded
    to :data:`backend.barycentric.POINT_DECIMALS`, so a third of the way along
    each axis lands within half a unit of the last decimal rather than exactly.
    """
    from backend.barycentric import POINT_DECIMALS

    tolerance = 10.0**-POINT_DECIMALS

    assert to_cartesian((1 / 3, 1 / 3, 1 / 3)) == pytest.approx(CENTROID, abs=tolerance)
    assert distance_from_centre(to_cartesian((1 / 3, 1 / 3, 1 / 3))) == pytest.approx(
        0.0, abs=tolerance
    )


def test_a_corner_is_not_near_the_centre() -> None:
    for weights in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
        assert distance_from_centre(to_cartesian(weights)) > CENTRE_RADIUS


# --------------------------------------------------------------------------
# Centre-parking
# --------------------------------------------------------------------------


def test_every_placement_in_the_middle_reads_as_every_placement(
    client: TestClient,
) -> None:
    """Ten stories, all parked. The proportion must be exactly 1.0."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    for _ in range(10):
        capture(client, framework["id"], {"t1": DEAD_CENTRE})

    t1 = row(quality(client, framework["id"]), "t1")

    assert t1["answered"] == 10
    assert t1["centre_parked"] == 10
    assert t1["centre_parked_rate"] == 1.0


def test_placements_at_the_corners_read_as_none(client: TestClient) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)
    for _ in range(10):
        capture(client, framework["id"], {"t1": HARD_LEAN})

    t1 = row(quality(client, framework["id"]), "t1")

    assert t1["answered"] == 10
    assert t1["centre_parked"] == 0
    assert t1["centre_parked_rate"] == 0.0


def test_a_deliberate_mixture_gives_the_proportion_it_was_built_from(
    client: TestClient,
) -> None:
    """Three parked out of four is 0.75, and nothing about the code decides that."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    for _ in range(3):
        capture(client, framework["id"], {"t1": DEAD_CENTRE})
    capture(client, framework["id"], {"t1": HARD_LEAN})

    t1 = row(quality(client, framework["id"]), "t1")

    assert t1["answered"] == 4
    assert t1["centre_parked"] == 3
    assert t1["centre_parked_rate"] == 0.75


def test_the_boundary_is_inclusive_and_lands_where_it_should(
    client: TestClient,
) -> None:
    """A placement just inside the circle counts; one just outside does not.

    Built by walking a known distance from the centre towards a corner, so the
    two stories differ only in whether they cross the radius.
    """
    framework = make_framework(client, GOLDEN_DEFINITION)

    # Barycentric weights interpolate linearly to cartesian, so moving a
    # fraction t of the way from the centre to corner 0 moves exactly t of the
    # way in distance too.
    reach = distance_from_centre(to_cartesian((1.0, 0.0, 0.0)))
    for fraction, expected_inside in ((0.95, True), (1.05, False)):
        t = fraction * CENTRE_RADIUS / reach
        weights = (
            1 / 3 + t * (1 - 1 / 3),
            1 / 3 + t * (0 - 1 / 3),
            1 / 3 + t * (0 - 1 / 3),
        )
        assert (distance_from_centre(to_cartesian(weights)) <= CENTRE_RADIUS) is (
            expected_inside
        )
        capture(
            client,
            framework["id"],
            {"t1": {"Speed": weights[0], "Care": weights[1], "Cost": weights[2]}},
        )

    t1 = row(quality(client, framework["id"]), "t1")

    assert t1["answered"] == 2
    assert t1["centre_parked"] == 1


def test_each_triad_is_measured_on_its_own(client: TestClient) -> None:
    """Two triangles in one question set do not pool their placements."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    for _ in range(4):
        capture(
            client,
            framework["id"],
            {
                "t1": DEAD_CENTRE,
                "t2": {"Me": 1.0, "My team": 0.0, "Someone else": 0.0},
            },
        )

    report = quality(client, framework["id"])

    assert row(report, "t1")["centre_parked_rate"] == 1.0
    assert row(report, "t2")["centre_parked_rate"] == 0.0


def test_a_signifier_with_no_centre_says_so_rather_than_zero(
    client: TestClient,
) -> None:
    """``None`` is "does not apply"; ``0`` would be "nobody parked" — different.

    A dyad, a stones grid and a multiple choice have no three-way trade-off to
    duck, so reporting a centre-parking figure for them would be inventing one.
    """
    framework = make_framework(client, GOLDEN_DEFINITION)
    capture(
        client,
        framework["id"],
        {
            "d1": {"value": 0.5},
            "s1": {"placements": [{"label": "Planning", "x": 0.5, "y": 0.5}]},
            "m1": {"selected": ["Well"]},
        },
    )

    report = quality(client, framework["id"])

    for signifier_id in ("d1", "s1", "m1"):
        assert row(report, signifier_id)["centre_parked"] is None
        assert row(report, signifier_id)["centre_parked_rate"] is None


# --------------------------------------------------------------------------
# Skip rate
# --------------------------------------------------------------------------


def test_a_signifier_nobody_answered_reads_as_wholly_skipped(
    client: TestClient,
) -> None:
    """The delta's named case: no rows at all for a signifier."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    for _ in range(5):
        capture(client, framework["id"], {"t1": DEAD_CENTRE})

    report = quality(client, framework["id"])

    assert report["total"] == 5
    assert row(report, "t1")["skip_rate"] == 0.0
    for skipped in ("t2", "d1", "s1", "m1"):
        assert row(report, skipped)["answered"] == 0
        assert row(report, skipped)["skipped"] == 5
        assert row(report, skipped)["skip_rate"] == 1.0


def test_a_partly_answered_signifier_gives_the_proportion(client: TestClient) -> None:
    """Two of five answered is a skip rate of 0.6, stated rather than derived."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    for _ in range(2):
        capture(client, framework["id"], {"t1": DEAD_CENTRE, "d1": {"value": 0.5}})
    for _ in range(3):
        capture(client, framework["id"], {"t1": DEAD_CENTRE})

    d1 = row(quality(client, framework["id"]), "d1")

    assert d1["answered"] == 2
    assert d1["skipped"] == 3
    assert d1["skip_rate"] == 0.6


def test_answered_and_skipped_always_account_for_every_story(
    client: TestClient,
) -> None:
    """The two numbers are a partition of the stories in scope, not estimates."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    capture(client, framework["id"], {"t1": DEAD_CENTRE, "m1": {"selected": ["Well"]}})
    capture(client, framework["id"], {"d1": {"value": 0.2}})
    capture(client, framework["id"], {})

    report = quality(client, framework["id"])

    assert report["total"] == 3
    for signifier in report["signifiers"]:
        assert signifier["answered"] + signifier["skipped"] == report["total"]


def test_the_stones_grid_counts_a_story_once_not_once_per_chip(
    client: TestClient,
) -> None:
    """Three chips is one answer to one question.

    Counting rows here would report more answers than there are stories, and
    then a skip rate below zero — so this is the arithmetic that has to be
    counted by story rather than by row.
    """
    framework = make_framework(client, GOLDEN_DEFINITION)
    capture(
        client,
        framework["id"],
        {
            "s1": {
                "placements": [
                    {"label": "Planning", "x": 0.2, "y": 0.3},
                    {"label": "Doing", "x": 0.4, "y": 0.5},
                    {"label": "Fixing", "x": 0.6, "y": 0.7},
                ]
            }
        },
    )
    capture(client, framework["id"], {"t1": DEAD_CENTRE})

    s1 = row(quality(client, framework["id"]), "s1")

    assert s1["answered"] == 1
    assert s1["skipped"] == 1
    assert s1["skip_rate"] == 0.5


def test_an_empty_question_set_divides_by_nothing_rather_than_falling_over(
    client: TestClient,
) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)

    report = quality(client, framework["id"])

    assert report["total"] == 0
    for signifier in report["signifiers"]:
        assert signifier["skip_rate"] == 0.0
        assert signifier["answered"] == 0


# --------------------------------------------------------------------------
# The same scope as everything else
# --------------------------------------------------------------------------


def test_every_signifier_appears_in_the_order_the_respondent_met_it(
    client: TestClient,
) -> None:
    """The panel reads down the questionnaire, not down a query result."""
    framework = make_framework(client, GOLDEN_DEFINITION)

    report = quality(client, framework["id"])

    assert [s["signifier_id"] for s in report["signifiers"]] == [
        "t1",
        "t2",
        "d1",
        "s1",
        "m1",
    ]


def test_a_filter_narrows_the_signals_the_way_it_narrows_the_charts(
    client: TestClient,
) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)
    for group, value in (("Ops", DEAD_CENTRE), ("Deck", HARD_LEAN)):
        client.post(
            "/api/capture",
            json={
                "framework_id": framework["id"],
                "text": STORY,
                "respondent_group": group,
                "significations": [{"signifier_id": "t1", "value": value}],
            },
        )

    ops = quality(client, framework["id"], respondent_group="Ops")
    deck = quality(client, framework["id"], respondent_group="Deck")

    assert ops["total"] == 1
    assert row(ops, "t1")["centre_parked_rate"] == 1.0
    assert row(deck, "t1")["centre_parked_rate"] == 0.0


def test_the_report_states_whose_readings_it_counted(client: TestClient) -> None:
    """Constraint 14 reaches this panel too — it aggregates significations."""
    framework = make_framework(client, GOLDEN_DEFINITION)
    capture(client, framework["id"], {"t1": DEAD_CENTRE})

    report = quality(client, framework["id"])

    assert report["signified_by_applied"] == "participant"
    assert report["counts_by_signified_by"] == {"participant": 1, "ai_validated": 0}


def test_an_unknown_provenance_choice_is_refused_here_too(client: TestClient) -> None:
    framework = make_framework(client, GOLDEN_DEFINITION)

    response = client.get(
        f"/api/quality/{framework['id']}", params={"signified_by": "whoever"}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unknown_signified_by"


def test_a_question_set_that_does_not_exist_says_so_in_plain_english(
    client: TestClient,
) -> None:
    response = client.get("/api/quality/9999")

    assert response.status_code == 404
    body = response.json()["error"]
    assert body["code"] == "framework_not_found"
    assert body["action"]


# --------------------------------------------------------------------------
# Constraint 11: nothing here can reach a language model
# --------------------------------------------------------------------------


def test_the_endpoint_answers_with_the_mock_off_and_no_key_present(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The configuration in which an accidental AI call could not be silent.

    With ``NL_MOCK_AI=0`` there is no mock to answer, and with no key there is
    nothing to authenticate with, so any call would raise rather than quietly
    succeed. The endpoint has to be entirely indifferent to both.
    """
    from backend.ai_client import API_KEY_ENV_VAR, MOCK_ENV_VAR

    framework = make_framework(client, GOLDEN_DEFINITION)
    capture(client, framework["id"], {"t1": DEAD_CENTRE})

    monkeypatch.setenv(MOCK_ENV_VAR, "0")
    monkeypatch.delenv(API_KEY_ENV_VAR, raising=False)

    report = quality(client, framework["id"])

    assert row(report, "t1")["centre_parked_rate"] == 1.0


def test_an_ai_call_from_this_path_would_fail_loudly(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Proves the previous test would actually have caught something.

    A test that passes because nothing was ever going to be called looks exactly
    like a test that passes because the path is clean. So the AI entry point is
    replaced with something that raises: if anything on this path reached it,
    the request above would have failed.
    """
    from backend import ai_client

    called: list[str] = []

    def explode(*args: object, **kwargs: object) -> None:
        called.append("request_json")
        raise AssertionError("the quality endpoint reached the AI client")

    monkeypatch.setattr(ai_client, "request_json", explode)
    monkeypatch.setenv(ai_client.MOCK_ENV_VAR, "0")
    monkeypatch.delenv(ai_client.API_KEY_ENV_VAR, raising=False)

    framework = make_framework(client, GOLDEN_DEFINITION)
    capture(client, framework["id"], {"t1": DEAD_CENTRE})
    quality(client, framework["id"])

    assert called == []


def test_the_quality_modules_import_nothing_ai_shaped() -> None:
    """Structural, not behavioural: the door is not there to be left open.

    Behaviour tests prove no call happened on the paths they exercised. This
    proves there is no way to make one, which is the promise constraint 11
    actually makes.
    """
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    for name in ("backend/quality.py", "backend/routers/quality.py"):
        source = (root / name).read_text(encoding="utf-8")
        for banned in ("ai_client", "anthropic", "propose", "organise"):
            assert banned not in source.replace(
                "no AI", ""
            ), f"{name} mentions {banned}"


# --------------------------------------------------------------------------
# The panel respects the visual grammar (delta §5, constraints 11 and 13)
# --------------------------------------------------------------------------
#
# Read out of the frontend source, the way this project's other frontend
# assertions are written. It cannot prove the panel *looks* quiet, but it can
# prove the three things that would make it loud were not done.


FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "src" / "patterns"


def patterns_jsx() -> str:
    return (FRONTEND / "Patterns.jsx").read_text(encoding="utf-8")


def quality_css() -> str:
    """Just the panel's own declarations, with the prose taken out.

    Comments are stripped first. Scanning them too would mean a rule could be
    broken by describing it and kept by not mentioning it, which is the opposite
    of what these assertions are for.
    """
    raw = (FRONTEND / "patterns.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    blocks = [block for block in css.split("}") if ".nl-quality" in block.split("{")[0]]
    assert blocks, "the quality panel has no styles of its own"
    return "\n".join(blocks)


def quality_jsx() -> str:
    """The panel component, with its comments stripped, for the same reason."""
    source = patterns_jsx().split("function QualityPanel")[1].split("\nfunction ")[0]
    return re.sub(r"\{/\*.*?\*/\}", "", source, flags=re.S)


def test_the_panel_is_closed_until_it_is_asked_for() -> None:
    """Collapsed by default (delta §5). A ``details`` with no ``open``."""
    panel = quality_jsx()

    assert '<details className="nl-quality"' in panel
    assert "open" not in panel.split("<details")[1].split(">")[0]


def test_the_panel_sits_below_the_supporting_charts() -> None:
    """Below them, not beside them — it is a check read after the answers."""
    source = patterns_jsx()
    rendered = source.split("function PatternsTab")[1].split("\nfunction ")[0]

    assert rendered.index("nl-patterns__band") < rendered.index("<QualityPanel")


#: Design tokens the quality panel is allowed to reach for. Greys, lines, the
#: spacing scale, the two smallest text sizes, and the medium weight — the
#: vocabulary of something quiet. The data hue and the accent are deliberately
#: absent: this panel encodes nothing in colour.
QUIET_TOKENS = {
    "--nl-grey",
    "--nl-grey-line",
    "--nl-text-sm",
    "--nl-text-xs",
    "--nl-weight-medium",
    "--nl-tap-target",
    "--nl-leading-body",
    "--nl-space-2",
    "--nl-space-3",
    "--nl-space-4",
    "--nl-space-6",
}


def test_the_panel_encodes_nothing_in_colour() -> None:
    """Constraint 13c, and the reason this panel can be read in greyscale.

    Every figure is a number and a percentage. A red row would be the panel
    deciding which questions are bad, which is the judgement constraint 11
    reserves for the operator. Checked by enumerating the tokens the panel
    actually uses rather than by hunting for particular words — a colour it
    reached for under a name nobody thought to ban would still fail this.
    """
    css = quality_css()

    used = set(re.findall(r"--nl-[a-z0-9-]+", css))

    assert used <= QUIET_TOKENS, f"the panel uses {sorted(used - QUIET_TOKENS)}"
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", css), "a raw colour literal"
    assert "rgb" not in css and "hsl" not in css


def test_the_panel_never_shouts() -> None:
    """Quiet weight (13a). The landscape is the one bold element on this tab.

    Nothing here may be larger than body text or heavier than medium, and the
    figures must not drop below the 12px floor (13e) — which they cannot, since
    ``--nl-text-xs`` *is* the floor and the token set above admits nothing
    smaller.
    """
    css = quality_css()

    assert "--nl-text-sm" in css
    for loud in ("--nl-text-lg", "--nl-text-xl", "font-weight: 700", "font-weight: 600"):
        assert loud not in css, f"the quality panel uses {loud}"


def test_the_wide_table_scrolls_inside_itself() -> None:
    """Constraint 10: a phone at 375px must not be pushed sideways by a table."""
    css = quality_css()

    assert "overflow-x: auto" in css


def test_the_panel_states_proportions_and_judges_none_of_them() -> None:
    """Constraint 11: it reports, and offers no reading of this data.

    The one interpretive sentence it shows is fixed prose written by a person
    and identical for every question set. What must not be there is a threshold
    — a comparison that decides a number is high and says so — because that is
    the app forming a view about the pattern rather than computing it.
    """
    panel = quality_jsx()

    for judgement in ("> 0.", "< 0.", ">= 0.", "<= 0.", "concern", "warning", "problem"):
        assert judgement not in panel, f"the panel judges a figure ({judgement})"


# --------------------------------------------------------------------------
# The budget (delta §4: 200ms, like every other non-AI read)
# --------------------------------------------------------------------------


def test_five_thousand_stories_cost_less_than_the_charts_beside_them(
    client: TestClient, session: Session
) -> None:
    """Measured against the patterns endpoint in the same run, not in milliseconds.

    PRD §4 budgets 200ms at five thousand anecdotes, and the delta puts this
    endpoint under the same budget. An absolute ceiling here would be the
    mistake ``tests/test_landscape.py`` documents at length: these containers
    differ by a factor of three or more on Python work, so a number that fits on
    one machine fails on another with nothing wrong.

    The reference is the patterns endpoint on the same data. It is the right
    yardstick because it is the same kind of work — the same scope query, the
    same provenance filter, the same rows read — and the PRD already budgets it
    at 200ms. This panel does strictly less: it counts placements and converts
    the triads, where patterns aggregates every chart. So it must come in under
    patterns, and on the container this was written on it came in at about a
    third of it.
    """
    from backend.models import Anecdote, Signification, hour_rounded_now

    framework = make_framework(client, GOLDEN_DEFINITION)
    for index in range(5000):
        anecdote = Anecdote(
            framework_id=framework["id"],
            text=f"Story {index}",
            source_type="capture",
            entry_mode="admin",
            input_method="typed",
            respondent_group=["Ops", "Deck", "Support"][index % 3],
            created_at_hour=hour_rounded_now(),
            status="validated",
        )
        session.add(anecdote)
        session.flush()
        a = ((index * 37) % 100) / 300
        b = ((index * 53) % 100) / 300
        session.add(
            Signification(
                anecdote_id=anecdote.id,
                signifier_id="t1",
                signifier_type="triad",
                value_json={"Speed": a, "Care": b, "Cost": round(1 - a - b, 6)},
                ai_confidence=None,
                signified_by="respondent",
                validated_at=hour_rounded_now(),
            )
        )
    session.commit()

    # Both warmed once: the first call to either pays for SQL compilation and
    # response validators it never pays for again.
    client.get(f"/api/quality/{framework['id']}")
    client.get(f"/api/patterns/{framework['id']}")

    ours = median_ms(lambda: client.get(f"/api/quality/{framework['id']}"))
    reference = median_ms(lambda: client.get(f"/api/patterns/{framework['id']}"))

    assert ours < reference, (
        f"the quality panel took {ours:.0f}ms against the patterns endpoint's "
        f"{reference:.0f}ms on the same five thousand stories"
    )
