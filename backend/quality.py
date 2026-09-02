"""Data-quality signals: centre-parking and skip rate (delta §1 item 4, §5).

Two questions about the *questions*, not about the stories.

**Did the question fit?** A triad asks somebody to trade three things off against
each other. When it fits their story they lean somewhere; when it does not, the
honest move is to leave the marker in the middle. So a pile of placements sitting
near the centroid is a signal about the question's design, and it is the one
signal that looks exactly like consensus if nobody counts it: a tight cluster in
the centre of a landscape reads as "everyone agrees" when it may mean "nobody
could answer this".

**Did they answer at all?** A signifier a lot of people skipped is telling you
something too, and skips leave no row, so nothing else in the app notices them.
They are derivable without any schema change: a story in scope with no
signification for a signifier skipped it.

Constraint 11 governs this file completely. Everything here is counting and
closed-form arithmetic — proportions the operator could recompute by hand from
the CSV. Nothing is generated, smoothed, labelled or narrated, and no AI is
reachable from this module: it reports what the numbers are and says nothing
about what they mean. The one interpretive sentence the panel shows is a fixed
reading note written by a person, not a finding computed about this data.

Constraint 14 applies here as much as anywhere: this aggregates significations,
so it takes the same provenance choice as every other view and states which one
it applied. A skip rate pooled across the storytellers' own readings and
somebody else's would be a mixture, and mixtures are what constraint 14 forbids.
"""

from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict, Field

from backend.barycentric import TRIANGLE_AREA, BarycentricError, distance_from_centre
from backend.barycentric import point_from_value_json as triad_point
from backend.framework_schema import FrameworkDefinition
from backend.patterns import SIGNIFIED_BY_DEFAULT, SignifiedByCounts

#: What fraction of the triangle the "centre" circle covers.
#:
#: A radius has to come from somewhere, and "small" is not a number. This is the
#: honest way to fix one: choose the share of the triangle's *area* the circle
#: should cover, and derive the radius from it. At a tenth, placements spread
#: evenly across the triangle would put about 10% of themselves in the circle —
#: so the reading is not "10% is high" but "10% is what randomness looks like,
#: and this is more". The panel says exactly that, which is what makes the
#: proportion interpretable without anybody interpreting it for the reader.
CENTRE_AREA_SHARE = 0.10

#: The radius that covers :data:`CENTRE_AREA_SHARE` of the triangle. About
#: 0.117 of a side, comfortably inside the incircle (radius ≈ 0.289), so the
#: whole circle lies within the triangle and the share is exact rather than
#: clipped.
CENTRE_RADIUS = math.sqrt(CENTRE_AREA_SHARE * TRIANGLE_AREA / math.pi)

#: Signifier kinds that have a centre to park in. Only the triad does.
#:
#: A dyad's midpoint and a stones grid's middle are real places too, but the
#: delta names the triad centroid, and a centre-parking figure means something
#: precise there: three-way trade-offs are what people duck when a question does
#: not fit. Reporting ``None`` for the other kinds says "this does not apply"
#: rather than reporting a zero, which would read as "nobody parked in the
#: centre" — a different and false claim. See PROGRESS.md "Decisions".
KINDS_WITH_A_CENTRE = ("triad",)


class SignifierQuality(BaseModel):
    """The two signals for one signifier, with the counts they came from."""

    model_config = ConfigDict(extra="forbid")

    signifier_id: str
    signifier_type: str
    title: str

    #: Stories in scope that placed a marker on this signifier.
    answered: int = 0
    #: Stories in scope that did not. ``answered + skipped == total``.
    skipped: int = 0
    #: ``skipped / total``, or 0.0 when there are no stories to divide by.
    skip_rate: float = 0.0

    #: Placements inside the centre circle, and their share of ``answered``.
    #: ``None`` for every kind without a centre — not applicable, not zero.
    centre_parked: int | None = None
    centre_parked_rate: float | None = None


class QualityReport(BaseModel):
    """Every signifier's signals, and what population they were measured on."""

    model_config = ConfigDict(extra="forbid")

    framework_id: int
    framework_name: str
    framework_version: int
    mixed: bool
    filters: dict[str, str] = Field(default_factory=dict)

    #: Constraint 14: which readings these proportions are made of, and how many
    #: of each kind exist in scope, so the panel can label itself honestly.
    signified_by_applied: str = SIGNIFIED_BY_DEFAULT
    counts_by_signified_by: SignifiedByCounts = Field(default_factory=SignifiedByCounts)

    #: Stories in scope — the denominator of every skip rate below.
    total: int = 0

    #: The circle the centre-parking figures used, and the share of placements
    #: that would fall inside it if they were spread evenly. Both travel with
    #: the report so a reader never has to take the threshold on trust.
    centre_radius: float = CENTRE_RADIUS
    centre_share_if_even: float = CENTRE_AREA_SHARE

    signifiers: list[SignifierQuality] = Field(default_factory=list)


def _rate(part: int, whole: int) -> float:
    """A proportion, rounded, with the empty case answered rather than raised."""
    if whole <= 0:
        return 0.0
    return round(part / whole, 6)


def centre_parked_count(
    values: list[dict],
    corner_ids: tuple[str, str, str],
) -> int:
    """How many of one triad's placements sit inside the centre circle.

    Reads each stored answer through the same conversion the landscape uses, so
    "near the middle" means the same thing in this panel as it does in the
    picture above it. A placement that cannot be read as a triad answer is not
    counted as parked — it is not evidence of parking, and this module's job is
    to count, not to repair.
    """
    parked = 0
    for value in values:
        try:
            point = triad_point(value, corner_ids)
        except BarycentricError:  # pragma: no cover - validation rejects these on entry
            continue
        if distance_from_centre(point) <= CENTRE_RADIUS:
            parked += 1
    return parked


def report(
    definition: FrameworkDefinition,
    *,
    framework_id: int,
    framework_name: str,
    framework_version: int,
    mixed: bool,
    filters: dict[str, str],
    signified_by: str,
    counts_by_signified_by: SignifiedByCounts,
    total: int,
    answered_by_signifier: dict[str, int],
    triad_values: dict[str, list[dict]],
) -> QualityReport:
    """Assemble the report from counts the caller has already read.

    Takes numbers rather than a session on purpose: every figure here is
    arithmetic on counts, and keeping the database out of this module is what
    lets the tests state an expected proportion and check it directly.

    Signifiers come back in the order the respondent met them
    (``signifiers_in_order``), so the panel reads down the questionnaire rather
    than in whatever order the counts arrived.
    """
    rows: list[SignifierQuality] = []

    for kind, signifier in definition.signifiers_in_order():
        answered = answered_by_signifier.get(signifier.id, 0)
        skipped = max(0, total - answered)

        parked: int | None = None
        parked_rate: float | None = None
        if kind in KINDS_WITH_A_CENTRE:
            corners = tuple(signifier.corners)  # type: ignore[union-attr]
            parked = centre_parked_count(triad_values.get(signifier.id, []), corners)
            parked_rate = _rate(parked, answered)

        rows.append(
            SignifierQuality(
                signifier_id=signifier.id,
                signifier_type=kind,
                title=signifier.title,
                answered=answered,
                skipped=skipped,
                skip_rate=_rate(skipped, total),
                centre_parked=parked,
                centre_parked_rate=parked_rate,
            )
        )

    return QualityReport(
        framework_id=framework_id,
        framework_name=framework_name,
        framework_version=framework_version,
        mixed=mixed,
        filters=filters,
        signified_by_applied=signified_by,
        counts_by_signified_by=counts_by_signified_by,
        total=total,
        signifiers=rows,
    )
