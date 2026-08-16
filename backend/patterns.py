"""Two-dimensional pattern aggregation (PRD §1.5, §4; constraint 11).

Constraint 11 is the whole design of this module: *patterns are computed, never
composed*. Everything here is ordinary arithmetic over the stored placements —
counting, sorting, binning, converting barycentric weights to a point. No
language model is imported, called, or consulted; nothing is smoothed,
interpolated, labelled, or narrated. The landscape's KDE arrives in Phase 8 and
will be the same kind of code.

Two further rules shape it:

* **Only validated stories count** (:mod:`backend.dataset`). A figure on screen
  is a figure a person approved, which is what makes constraint 1 mean anything
  once the data is being read rather than written.
* **Determinism, to the decimal.** Every list has a total order — bars by value
  then label, points by anecdote id — and every float is rounded to a fixed
  number of places. That is what lets ``tests/test_patterns_golden.py`` hold the
  whole aggregate byte-identical from this phase onward, so a later refactor
  cannot quietly move a number.

The §5b grammar is served here rather than in the browser: every categorical
view returns its bars already sorted by value, so a chart cannot be drawn
unsorted by accident, and a test can assert the rule against the API.
"""

from __future__ import annotations

from collections import Counter

from pydantic import BaseModel, ConfigDict, Field

from backend.barycentric import from_value_json, to_cartesian
from backend.framework_schema import Dyad, FrameworkDefinition, Mcq, Stones, Triad
from backend.models import Anecdote, Signification

#: Coordinates are rounded here, once. Six places is far finer than any screen
#: and coarse enough that two runs agree exactly.
COORD_DECIMALS = 6

#: Shares are proportions of the filtered total, not percentages.
SHARE_DECIMALS = 4

#: Dyad histograms use fixed bins so two runs — and two versions of the app —
#: bin the same value the same way. Ten across 0–1.
HISTOGRAM_BINS = 10

#: The provenance fields a pattern view may be filtered on (PRD §1.5 filter
#: rail). Every one of them is a column that carries no respondent identity.
FILTERABLE = ("respondent_group", "input_method", "entry_mode", "source_type")


class Bar(BaseModel):
    """One bar of a categorical view, already in its drawn order."""

    model_config = ConfigDict(extra="forbid")

    label: str
    count: int
    share: float


class CategoryChart(BaseModel):
    """A categorical breakdown: horizontal bars sorted by value (§5b)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    bars: list[Bar]
    #: Stories that answered this question at all. Skipped questions are not
    #: counted as a zero — a respondent who said nothing said nothing.
    answered: int


class TriadPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    anecdote_id: int
    x: float
    y: float


class TriadChart(BaseModel):
    """Placements inside one triangle, as points on the unit triangle."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    corners: list[str]
    points: list[TriadPoint]
    answered: int


class HistogramBin(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lower: float
    upper: float
    count: int


class DyadPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    anecdote_id: int
    value: float


class DyadChart(BaseModel):
    """One slider: every mark, plus the distribution they make (§1.5)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    left: str
    right: str
    points: list[DyadPoint]
    histogram: list[HistogramBin]
    median: float | None
    answered: int


class StonePoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    anecdote_id: int
    label: str
    x: float
    y: float


class StonesChart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    x_axis: list[str]
    y_axis: list[str]
    points: list[StonePoint]
    answered: int


class VersionCount(BaseModel):
    """One version's share of a mixed view — the version chip's data (§5.4)."""

    model_config = ConfigDict(extra="forbid")

    framework_id: int
    version: int
    count: int


class PatternSet(BaseModel):
    """Everything the supporting charts of one framework version need."""

    model_config = ConfigDict(extra="forbid")

    framework_id: int
    framework_name: str
    framework_version: int
    #: Stories in the view after filters. The denominator for every share.
    total: int
    #: True when the view deliberately spans framework versions (PRD §4).
    mixed: bool
    versions: list[VersionCount] = Field(default_factory=list)
    filters: dict[str, str] = Field(default_factory=dict)
    triads: list[TriadChart] = Field(default_factory=list)
    dyads: list[DyadChart] = Field(default_factory=list)
    stones: StonesChart | None = None
    mcqs: list[CategoryChart] = Field(default_factory=list)
    #: Provenance breakdowns — who answered, and how the story arrived.
    demographics: list[CategoryChart] = Field(default_factory=list)


def _round(value: float, decimals: int) -> float:
    """Round, and never hand back ``-0.0``, which is not equal to its own text."""
    result = round(value, decimals)
    return 0.0 if result == 0 else result


def _share(count: int, total: int) -> float:
    return _round(count / total, SHARE_DECIMALS) if total else 0.0


def _bars(counter: Counter[str], total: int) -> list[Bar]:
    """Bars in drawn order: biggest first, ties broken alphabetically.

    §5b requires categorical views to be sorted by value. Doing it here rather
    than in the chart means the order is part of the contract, and the tie-break
    means the order does not wobble between runs.
    """
    return [
        Bar(label=label, count=count, share=_share(count, total))
        for label, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return _round(ordered[middle], COORD_DECIMALS)
    return _round((ordered[middle - 1] + ordered[middle]) / 2, COORD_DECIMALS)


def _histogram(values: list[float]) -> list[HistogramBin]:
    """Fixed bins across 0–1, with 1.0 landing in the last bin, not past it."""
    counts = [0] * HISTOGRAM_BINS
    for value in values:
        index = min(int(value * HISTOGRAM_BINS), HISTOGRAM_BINS - 1)
        counts[index] += 1
    return [
        HistogramBin(
            lower=_round(index / HISTOGRAM_BINS, COORD_DECIMALS),
            upper=_round((index + 1) / HISTOGRAM_BINS, COORD_DECIMALS),
            count=count,
        )
        for index, count in enumerate(counts)
    ]


def _triad_chart(
    triad: Triad, placements: list[tuple[int, dict]], total: int
) -> TriadChart:
    points: list[TriadPoint] = []
    for anecdote_id, value in placements:
        weights = from_value_json(value, tuple(triad.corners))  # type: ignore[arg-type]
        x, y = to_cartesian(weights)  # type: ignore[arg-type]
        points.append(
            TriadPoint(
                anecdote_id=anecdote_id,
                x=_round(x, COORD_DECIMALS),
                y=_round(y, COORD_DECIMALS),
            )
        )
    points.sort(key=lambda point: point.anecdote_id)
    return TriadChart(
        id=triad.id,
        title=triad.title,
        corners=list(triad.corners),
        points=points,
        answered=len(points),
    )


def _dyad_chart(dyad: Dyad, placements: list[tuple[int, dict]], total: int) -> DyadChart:
    points = sorted(
        (
            DyadPoint(
                anecdote_id=anecdote_id,
                value=_round(float(value.get("value", 0.0)), COORD_DECIMALS),
            )
            for anecdote_id, value in placements
        ),
        key=lambda point: point.anecdote_id,
    )
    values = [point.value for point in points]
    return DyadChart(
        id=dyad.id,
        title=dyad.title,
        left=dyad.left,
        right=dyad.right,
        points=points,
        histogram=_histogram(values),
        median=_median(values),
        answered=len(points),
    )


def _stones_chart(
    stones: Stones, placements: list[tuple[int, dict]], total: int
) -> StonesChart:
    points: list[StonePoint] = []
    for anecdote_id, value in placements:
        for placement in value.get("placements", []):
            points.append(
                StonePoint(
                    anecdote_id=anecdote_id,
                    label=str(placement["label"]),
                    x=_round(float(placement["x"]), COORD_DECIMALS),
                    y=_round(float(placement["y"]), COORD_DECIMALS),
                )
            )
    points.sort(key=lambda point: (point.anecdote_id, point.label))
    return StonesChart(
        id=stones.id,
        title=stones.title,
        x_axis=[stones.x_axis.low, stones.x_axis.high],
        y_axis=[stones.y_axis.low, stones.y_axis.high],
        points=points,
        answered=len({point.anecdote_id for point in points}),
    )


def _mcq_chart(mcq: Mcq, placements: list[tuple[int, dict]], total: int) -> CategoryChart:
    counter: Counter[str] = Counter()
    for _, value in placements:
        for option in value.get("selected", []):
            counter[str(option)] += 1
    # Options nobody chose still get a bar: a zero is a finding, and dropping it
    # would quietly redraw the question.
    for option in mcq.options:
        counter.setdefault(option, 0)
    answered = len(placements)
    return CategoryChart(
        id=mcq.id, title=mcq.title, bars=_bars(counter, answered), answered=answered
    )


#: How each provenance breakdown is titled. Plain English, no column names.
DEMOGRAPHIC_TITLES = {
    "respondent_group": "Who told the story",
    "input_method": "How it was written down",
    "entry_mode": "Where it came from",
    "source_type": "How it reached Narrative Lens",
}


def _demographics(anecdotes: list[Anecdote]) -> list[CategoryChart]:
    charts: list[CategoryChart] = []
    for field, title in DEMOGRAPHIC_TITLES.items():
        counter: Counter[str] = Counter()
        for anecdote in anecdotes:
            value = getattr(anecdote, field)
            if value:
                counter[str(value)] += 1
        answered = sum(counter.values())
        charts.append(
            CategoryChart(id=field, title=title, bars=_bars(counter, answered), answered=answered)
        )
    return charts


def aggregate(
    definition: FrameworkDefinition,
    anecdotes: list[Anecdote],
    significations: list[Signification],
    *,
    framework_id: int,
    framework_name: str,
    framework_version: int,
    mixed: bool = False,
    versions: list[VersionCount] | None = None,
    filters: dict[str, str] | None = None,
) -> PatternSet:
    """Compute every supporting chart for one view of the data.

    Takes the stories and their placements already filtered by the caller, so
    this function has no opinion about which stories count — only about what the
    ones it was given add up to.
    """
    keep = {anecdote.id for anecdote in anecdotes}
    by_signifier: dict[str, list[tuple[int, dict]]] = {}
    for placement in significations:
        if placement.anecdote_id in keep:
            by_signifier.setdefault(placement.signifier_id, []).append(
                (placement.anecdote_id, placement.value_json)
            )

    total = len(anecdotes)
    return PatternSet(
        framework_id=framework_id,
        framework_name=framework_name,
        framework_version=framework_version,
        total=total,
        mixed=mixed,
        versions=versions or [],
        filters=filters or {},
        triads=[
            _triad_chart(triad, by_signifier.get(triad.id, []), total)
            for triad in definition.triads
        ],
        dyads=[
            _dyad_chart(dyad, by_signifier.get(dyad.id, []), total)
            for dyad in definition.dyads
        ],
        stones=(
            _stones_chart(definition.stones, by_signifier.get(definition.stones.id, []), total)
            if definition.stones
            else None
        ),
        mcqs=[_mcq_chart(mcq, by_signifier.get(mcq.id, []), total) for mcq in definition.mcqs],
        demographics=_demographics(anecdotes),
    )
