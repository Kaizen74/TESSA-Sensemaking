"""Triad barycentric maths.

A triad answer is a point inside an equilateral triangle, stored as three
weights summing to 1.0 (PRD §3). This module is the single source of that
conversion: the capture widget, the paper pack, and every later pattern view
must agree on where a placement sits, so they all come through here.

Constraint 11 — patterns are computed, never composed. Everything in this file
is deterministic, closed-form, and free of randomness or AI.

The reference triangle has corner 0 at bottom-left, corner 1 at bottom-right and
corner 2 at top, matching how the widget draws it:

        2
       / \\
      /   \\
     0-----1

Its side length is 1.0, so corner 0 is (0, 0), corner 1 is (1, 0) and corner 2
is (0.5, sqrt(3)/2).

This module is on the PRD §6 regression list; ``tests/test_barycentric.py`` holds
its golden values and must stay green in every later phase.
"""

from __future__ import annotations

import math

#: Cartesian positions of the three corners, in corner order.
CORNER_0 = (0.0, 0.0)
CORNER_1 = (1.0, 0.0)
CORNER_2 = (0.5, math.sqrt(3.0) / 2.0)

CORNERS = (CORNER_0, CORNER_1, CORNER_2)

#: Weights are rounded to this many decimals so that repeated round-trips settle
#: instead of drifting in the last bits of the float.
WEIGHT_DECIMALS = 6

#: Cartesian points keep more precision than the weights they came from. If a
#: point were rounded to the same 6 decimals, reading it back would lose up to
#: 1e-6 of weight — exactly the precision the weights claim to have. The extra
#: digits here keep the round trip lossless at the weights' stated precision.
POINT_DECIMALS = 9

#: Tolerance for "these weights sum to 1.0".
SUM_TOLERANCE = 1e-6


class BarycentricError(ValueError):
    """Raised when a placement cannot be read as a triad answer."""


def to_cartesian(weights: tuple[float, float, float]) -> tuple[float, float]:
    """Convert three corner weights into a point inside the triangle.

    >>> to_cartesian((1.0, 0.0, 0.0))
    (0.0, 0.0)
    """
    a, b, c = _validated(weights)
    x = a * CORNER_0[0] + b * CORNER_1[0] + c * CORNER_2[0]
    y = a * CORNER_0[1] + b * CORNER_1[1] + c * CORNER_2[1]
    return (round(x, POINT_DECIMALS), round(y, POINT_DECIMALS))


def to_barycentric(point: tuple[float, float]) -> tuple[float, float, float]:
    """Convert a point in the triangle into three corner weights summing to 1.0.

    The closed form below is the standard inverse of :func:`to_cartesian` for
    this specific triangle. Points on an edge or corner give exact zeros.
    """
    x, y = point
    height = CORNER_2[1]

    c = y / height
    b = x - y * (CORNER_2[0] / height)
    a = 1.0 - b - c

    return normalise((a, b, c))


def normalise(weights: tuple[float, float, float]) -> tuple[float, float, float]:
    """Clamp to the triangle and rescale so the three weights sum to exactly 1.0.

    A respondent can only drop a marker inside the triangle, but a placement that
    arrives from an import or a paper transcription may sit a hair outside it.
    Clamping is the honest repair: it moves the point to the nearest legal
    reading rather than rejecting a real answer.
    """
    clamped = [max(0.0, float(w)) for w in weights]
    total = sum(clamped)

    if total <= 0.0:
        raise BarycentricError(
            "a triad placement needs at least one corner weight above zero; "
            "got all zeros or negatives"
        )

    scaled = [w / total for w in clamped]
    rounded = [round(w, WEIGHT_DECIMALS) for w in scaled]

    # Rounding three values independently can leave the sum a hair off 1.0. Put
    # the remainder on the largest weight, where it is proportionally smallest.
    drift = round(1.0 - sum(rounded), WEIGHT_DECIMALS)
    if drift:
        largest = rounded.index(max(rounded))
        rounded[largest] = round(rounded[largest] + drift, WEIGHT_DECIMALS)

    return (rounded[0], rounded[1], rounded[2])


def sums_to_one(weights: tuple[float, float, float]) -> bool:
    """Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`."""
    return abs(sum(weights) - 1.0) <= SUM_TOLERANCE


def is_inside(weights: tuple[float, float, float]) -> bool:
    """Whether the weights describe a point in or on the triangle."""
    return all(w >= 0.0 for w in weights) and sums_to_one(weights)


def _validated(weights: tuple[float, float, float]) -> tuple[float, float, float]:
    """Reject anything that is not a usable triad answer."""
    if len(weights) != 3:
        raise BarycentricError(f"a triad answer needs exactly 3 weights, got {len(weights)}")

    numeric = []
    for weight in weights:
        if isinstance(weight, bool) or not isinstance(weight, int | float):
            raise BarycentricError(f"triad weights must be numbers, got {weight!r}")
        if math.isnan(weight) or math.isinf(weight):
            raise BarycentricError("triad weights must be ordinary numbers")
        numeric.append(float(weight))

    if any(weight < 0.0 for weight in numeric):
        raise BarycentricError(f"triad weights cannot be negative, got {tuple(numeric)}")

    if not sums_to_one((numeric[0], numeric[1], numeric[2])):
        raise BarycentricError(
            f"triad weights must sum to 1.0, got {sum(numeric)} from {tuple(numeric)}"
        )

    return (numeric[0], numeric[1], numeric[2])


def from_value_json(value_json: dict, corner_ids: tuple[str, str, str]) -> tuple[float, ...]:
    """Read a stored ``significations.value_json`` into ordered weights."""
    try:
        weights = tuple(float(value_json[corner_id]) for corner_id in corner_ids)
    except (KeyError, TypeError, ValueError) as exc:
        raise BarycentricError(
            f"a triad placement must carry all three corners {corner_ids}; got {value_json!r}"
        ) from exc
    return _validated(weights)  # type: ignore[arg-type]
