"""Golden maths for triad placements.

These values are the contract between the capture widget, the paper pack, and
every later pattern view. They are on the PRD §6 regression list: once written
they do not change, because changing them would silently move every stored
answer.
"""

from __future__ import annotations

import math

import pytest

from backend.barycentric import (
    CORNER_0,
    CORNER_1,
    CORNER_2,
    BarycentricError,
    from_value_json,
    is_inside,
    normalise,
    sums_to_one,
    to_barycentric,
    to_cartesian,
)

#: Height of the reference triangle, used throughout the goldens.
H = math.sqrt(3.0) / 2.0


class TestGoldenCorners:
    """Each corner weight of 1.0 lands exactly on that corner."""

    @pytest.mark.parametrize(
        ("weights", "expected"),
        [
            ((1.0, 0.0, 0.0), CORNER_0),
            ((0.0, 1.0, 0.0), CORNER_1),
            ((0.0, 0.0, 1.0), CORNER_2),
        ],
    )
    def test_corner_weights_map_to_corner_points(self, weights, expected) -> None:
        assert to_cartesian(weights) == pytest.approx(expected, abs=1e-9)

    @pytest.mark.parametrize(
        ("point", "expected"),
        [
            (CORNER_0, (1.0, 0.0, 0.0)),
            (CORNER_1, (0.0, 1.0, 0.0)),
            (CORNER_2, (0.0, 0.0, 1.0)),
        ],
    )
    def test_corner_points_map_back_to_corner_weights(self, point, expected) -> None:
        assert to_barycentric(point) == pytest.approx(expected, abs=1e-9)


class TestGoldenCentroid:
    """The dead centre is the equal-weight answer — the most-read position."""

    GOLDEN_CENTROID_POINT = (0.5, H / 3.0)

    def test_equal_weights_land_at_the_centroid(self) -> None:
        x, y = to_cartesian((1 / 3, 1 / 3, 1 / 3))
        assert x == pytest.approx(0.5, abs=1e-6)
        assert y == pytest.approx(H / 3.0, abs=1e-6)

    def test_centroid_reads_back_as_equal_weights(self) -> None:
        weights = to_barycentric(self.GOLDEN_CENTROID_POINT)
        assert weights == pytest.approx((1 / 3, 1 / 3, 1 / 3), abs=1e-6)


class TestGoldenEdgeMidpoints:
    """Two-way ties sit halfway along an edge, with the third corner at zero."""

    @pytest.mark.parametrize(
        ("weights", "expected_point"),
        [
            ((0.5, 0.5, 0.0), (0.5, 0.0)),
            ((0.5, 0.0, 0.5), (0.25, H / 2.0)),
            ((0.0, 0.5, 0.5), (0.75, H / 2.0)),
        ],
    )
    def test_edge_midpoints(self, weights, expected_point) -> None:
        assert to_cartesian(weights) == pytest.approx(expected_point, abs=1e-6)
        assert to_barycentric(expected_point) == pytest.approx(weights, abs=1e-6)


class TestGoldenAsymmetricPlacements:
    """Fixed off-centre answers — the ones a real respondent actually gives."""

    # Derived exactly from the triangle rather than typed as rounded decimals:
    # x = b + c/2, y = c * H. Writing them in closed form keeps the goldens
    # analytically true instead of true-to-six-places.
    GOLDENS = [
        ((0.5, 0.3, 0.2), (0.3 + 0.2 / 2, 0.2 * H)),
        ((0.7, 0.2, 0.1), (0.2 + 0.1 / 2, 0.1 * H)),
        ((0.1, 0.1, 0.8), (0.1 + 0.8 / 2, 0.8 * H)),
        ((0.25, 0.25, 0.5), (0.25 + 0.5 / 2, 0.5 * H)),
    ]

    @pytest.mark.parametrize(("weights", "expected_point"), GOLDENS)
    def test_weights_to_point(self, weights, expected_point) -> None:
        assert to_cartesian(weights) == pytest.approx(expected_point, abs=1e-6)

    @pytest.mark.parametrize(("expected_weights", "point"), GOLDENS)
    def test_point_to_weights(self, expected_weights, point) -> None:
        assert to_barycentric(point) == pytest.approx(expected_weights, abs=1e-6)


class TestRoundTrip:
    def test_round_trip_is_stable_over_many_placements(self) -> None:
        """Weights survive a there-and-back trip without drifting."""
        step = 0.05
        checked = 0
        a = 0.0
        while a <= 1.0 + 1e-9:
            b = 0.0
            while a + b <= 1.0 + 1e-9:
                c = round(1.0 - a - b, 6)
                original = normalise((a, b, c))
                returned = to_barycentric(to_cartesian(original))
                assert returned == pytest.approx(original, abs=1e-6)
                checked += 1
                b = round(b + step, 6)
            a = round(a + step, 6)

        assert checked > 200, "the sweep should cover the whole triangle"

    def test_repeated_round_trips_do_not_creep(self) -> None:
        """Ten trips land where one trip landed — no accumulating drift."""
        weights = normalise((0.37, 0.41, 0.22))
        once = to_barycentric(to_cartesian(weights))

        drifting = weights
        for _ in range(10):
            drifting = to_barycentric(to_cartesian(drifting))

        assert drifting == pytest.approx(once, abs=1e-9)


class TestSumsToOne:
    """PRD §3: triad barycentric sums to 1.0."""

    @pytest.mark.parametrize(
        "weights",
        [(1.0, 0.0, 0.0), (1 / 3, 1 / 3, 1 / 3), (0.5, 0.3, 0.2), (0.1, 0.1, 0.8)],
    )
    def test_valid_weights_sum_to_one(self, weights) -> None:
        assert sums_to_one(weights)
        assert is_inside(weights)

    def test_normalise_rescales_to_exactly_one(self) -> None:
        weights = normalise((2.0, 1.0, 1.0))
        assert sum(weights) == pytest.approx(1.0, abs=1e-9)
        assert weights == pytest.approx((0.5, 0.25, 0.25), abs=1e-9)

    def test_normalise_output_always_sums_to_one_exactly(self) -> None:
        """Even awkward thirds land on a sum of exactly 1.0 after rounding."""
        for raw in [(1, 1, 1), (1, 2, 3), (0.333, 0.333, 0.333), (7, 11, 13)]:
            weights = normalise(raw)  # type: ignore[arg-type]
            assert sum(weights) == 1.0, f"{raw} normalised to {weights}, summing to {sum(weights)}"

    def test_normalise_clamps_a_placement_that_strayed_outside(self) -> None:
        """An imported point a hair outside the triangle is pulled to its edge."""
        weights = normalise((-0.05, 0.55, 0.5))
        assert weights[0] == 0.0
        assert sum(weights) == pytest.approx(1.0, abs=1e-9)
        assert is_inside(weights)


class TestRejections:
    def test_wrong_number_of_weights(self) -> None:
        with pytest.raises(BarycentricError, match="exactly 3 weights"):
            to_cartesian((0.5, 0.5))  # type: ignore[arg-type]

    def test_negative_weight(self) -> None:
        with pytest.raises(BarycentricError, match="cannot be negative"):
            to_cartesian((-0.1, 0.6, 0.5))

    def test_weights_that_do_not_sum_to_one(self) -> None:
        with pytest.raises(BarycentricError, match="must sum to 1.0"):
            to_cartesian((0.5, 0.2, 0.1))

    def test_non_numeric_weight(self) -> None:
        with pytest.raises(BarycentricError, match="must be numbers"):
            to_cartesian((0.5, "0.3", 0.2))  # type: ignore[arg-type]

    def test_nan_weight(self) -> None:
        with pytest.raises(BarycentricError, match="ordinary numbers"):
            to_cartesian((float("nan"), 0.5, 0.5))

    def test_all_zero_weights(self) -> None:
        with pytest.raises(BarycentricError, match="above zero"):
            normalise((0.0, 0.0, 0.0))


class TestFromValueJson:
    """Reading a stored signification back into ordered weights."""

    CORNER_IDS = ("speed", "care", "cost")

    def test_reads_stored_placement(self) -> None:
        stored = {"speed": 0.5, "care": 0.3, "cost": 0.2}
        assert from_value_json(stored, self.CORNER_IDS) == pytest.approx((0.5, 0.3, 0.2))

    def test_order_follows_the_corner_ids_not_the_dict(self) -> None:
        """Dict ordering must never decide which corner is which."""
        stored = {"cost": 0.2, "speed": 0.5, "care": 0.3}
        assert from_value_json(stored, self.CORNER_IDS) == pytest.approx((0.5, 0.3, 0.2))

    def test_missing_corner_is_rejected(self) -> None:
        with pytest.raises(BarycentricError, match="all three corners"):
            from_value_json({"speed": 0.5, "care": 0.5}, self.CORNER_IDS)

    def test_placement_that_does_not_sum_to_one_is_rejected(self) -> None:
        with pytest.raises(BarycentricError, match="must sum to 1.0"):
            from_value_json({"speed": 0.5, "care": 0.3, "cost": 0.1}, self.CORNER_IDS)
