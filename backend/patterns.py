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

from backend.barycentric import point_from_value_json
from backend.dataset import AnswerRow, StoryRow
from backend.framework_schema import Dyad, FrameworkDefinition, Mcq, Stones, Triad

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
#:
#: These are *story* fields: they filter which anecdotes a view is about, they
#: are the demographic breakdowns, and they are what a landscape may be split
#: by. ``signified_by`` is not among them because it is not one of them — it
#: lives on the signification, and it filters which *placements* count rather
#: than which stories do. It has its own vocabulary below.
FILTERABLE = ("respondent_group", "input_method", "entry_mode", "source_type")

# --------------------------------------------------------------------------
# Whose interpretation a view is showing (delta §1 item 1, constraint 14)
# --------------------------------------------------------------------------
#
# The database records who placed each marker: ``respondent`` when the person
# who lived the story placed it themselves, ``ai`` for a Stage B proposal an
# analyst accepted as it stood, ``analyst`` for one they moved. The delta asks
# views to speak in two words rather than three, because the distinction that
# matters to a reader is not which of the two expert routes a point took — it is
# whether the meaning came from the storyteller or from somebody else.

#: Placed by the person whose story it is.
SIGNIFIED_BY_PARTICIPANT = "participant"

#: Placed on their behalf and validated by an expert — an accepted AI proposal
#: or an analyst's own correction. Both are somebody else's reading.
SIGNIFIED_BY_AI_VALIDATED = "ai_validated"

#: Both, together, and never silently: constraint 14 requires a view that mixes
#: them to say so.
SIGNIFIED_BY_ALL = "all"

SIGNIFIED_BY_CHOICES = (
    SIGNIFIED_BY_PARTICIPANT,
    SIGNIFIED_BY_AI_VALIDATED,
    SIGNIFIED_BY_ALL,
)

#: Constraint 14: participant-signified only, unless the reader asks otherwise.
SIGNIFIED_BY_DEFAULT = SIGNIFIED_BY_PARTICIPANT

#: The stored ``significations.signified_by`` values each choice covers.
SIGNIFIED_BY_STORED = {
    SIGNIFIED_BY_PARTICIPANT: ("respondent",),
    SIGNIFIED_BY_AI_VALIDATED: ("ai", "analyst"),
}


class SignifiedByCounts(BaseModel):
    """How many placements each provenance holds, before the filter is applied.

    Reported on every aggregating view so the screen can say what it is showing
    *and* what it is leaving out — the second half of constraint 14. Counted in
    placements rather than in stories because a single story can hold both: the
    validation queue's "correct" action stamps the markers the analyst moved as
    ``analyst`` and leaves the rest as the AI proposed them.
    """

    model_config = ConfigDict(extra="forbid")

    participant: int = 0
    ai_validated: int = 0

    @property
    def total(self) -> int:
        return self.participant + self.ai_validated


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
    #: Whose interpretation these figures are, and what the other choice holds
    #: (constraint 14). Always present, so a screen can never draw this view
    #: without having been told what it is looking at.
    signified_by_applied: str = SIGNIFIED_BY_DEFAULT
    counts_by_signified_by: SignifiedByCounts = Field(default_factory=SignifiedByCounts)
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
    corners = tuple(triad.corners)
    points: list[TriadPoint] = []
    for anecdote_id, value in placements:
        x, y = point_from_value_json(value, corners)  # type: ignore[arg-type]
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


def _demographics(anecdotes: list[StoryRow]) -> list[CategoryChart]:
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


def placements_by_signifier(
    anecdotes: list[StoryRow], significations: list[AnswerRow]
) -> dict[str, list[tuple[int, dict]]]:
    """Placements grouped by the question they answer, for the stories given."""
    keep = {anecdote.id for anecdote in anecdotes}
    grouped: dict[str, list[tuple[int, dict]]] = {}
    for placement in significations:
        if placement.anecdote_id in keep:
            grouped.setdefault(placement.signifier_id, []).append(
                (placement.anecdote_id, placement.value_json)
            )
    return grouped


def one_triad(
    definition: FrameworkDefinition,
    anecdotes: list[StoryRow],
    significations: list[AnswerRow],
    triad_id: str,
) -> TriadChart | None:
    """Just one triangle's points, without computing every other chart.

    The landscape needs one triad and nothing else. Running the full aggregate
    for it would build every bar, histogram and scatter on the framework as
    well — free at twenty stories, and the difference between meeting and
    missing PRD §4's 200ms budget at a thousand.
    """
    triad = next((entry for entry in definition.triads if entry.id == triad_id), None)
    if triad is None:
        return None
    grouped = placements_by_signifier(anecdotes, significations)
    return _triad_chart(triad, grouped.get(triad_id, []), len(anecdotes))


def triad_from_answers(
    definition: FrameworkDefinition,
    answers: list[tuple[int, dict]],
    triad_id: str,
    total: int,
) -> TriadChart | None:
    """The same chart as :func:`one_triad`, from rows rather than from objects.

    Identical arithmetic — both end in :func:`_triad_chart` — so the landscape
    cannot drift from the supporting charts. What differs is only how the
    answers arrived: two columns out of the database instead of an object per
    story (PRD §4's 200ms at 5,000 anecdotes).
    """
    triad = next((entry for entry in definition.triads if entry.id == triad_id), None)
    if triad is None:
        return None
    return _triad_chart(triad, answers, total)


def aggregate(
    definition: FrameworkDefinition,
    anecdotes: list[StoryRow],
    significations: list[AnswerRow],
    *,
    framework_id: int,
    framework_name: str,
    framework_version: int,
    mixed: bool = False,
    versions: list[VersionCount] | None = None,
    filters: dict[str, str] | None = None,
    signified_by: str = SIGNIFIED_BY_DEFAULT,
    counts_by_signified_by: SignifiedByCounts | None = None,
) -> PatternSet:
    """Compute every supporting chart for one view of the data.

    Takes the stories and their placements already filtered by the caller, so
    this function has no opinion about which stories count — only about what the
    ones it was given add up to. ``signified_by`` and its counts are carried
    through rather than applied here for the same reason: the filtering happened
    in the query, and this reports what was asked for so the screen can say it.
    """
    by_signifier = placements_by_signifier(anecdotes, significations)
    total = len(anecdotes)
    return PatternSet(
        framework_id=framework_id,
        framework_name=framework_name,
        framework_version=framework_version,
        total=total,
        mixed=mixed,
        versions=versions or [],
        filters=filters or {},
        signified_by_applied=signified_by,
        counts_by_signified_by=counts_by_signified_by or SignifiedByCounts(),
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
