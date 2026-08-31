"""The 3D Explorer and the k-means overlay (PRD §1.5, §4).

Two things one level down from the landscape.

**The Explorer** turns every numeric answer a story gave into a named dimension —
each triad corner's weight, each dyad's position, each stone's x and y — so any
three of them can be plotted against each other. The whole set is returned once
and the axes are switched in the browser, because a person exploring changes
their mind faster than a round trip.

**The clusters** are k-means over those same dimensions, standardised so a dyad
on 0–1 does not sit quieter than a triad corner. Seed 42 and ``minit="++"``
fixed, per PRD §9 assumption 8, so the same stories always land in the same
groups.

They are labelled **"statistical clusters — descriptive only"** wherever they
appear, and that string lives here so no screen can quietly drop it. Constraint
11 and constraint 12 both bear on this: the clustering is arithmetic, not
interpretation, and a group of stories that sit near each other is not evidence
that anything caused anything.
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from scipy.cluster.vq import kmeans2

from backend.dataset import AnswerRow, StoryRow
from backend.framework_schema import FrameworkDefinition

#: PRD §9 assumption 8 pins the seed. Nothing here may vary between runs.
SEED = 42

#: The caveat that travels with every cluster, everywhere (PRD §1.5).
CLUSTER_CAVEAT = "statistical clusters — descriptive only"

#: k-means needs more points than groups to mean anything.
MIN_PER_CLUSTER = 2

DEFAULT_K = 3
MIN_K = 2
MAX_K = 6

VALUE_DECIMALS = 6


class Dimension(BaseModel):
    """One plottable axis, named the way the operator wrote the question."""

    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    #: The signifier it came from, so a screen can group the axis picker.
    signifier_id: str
    signifier_type: str


class ExplorerPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    anecdote_id: int
    #: Dimension id → value, only for dimensions this story actually answered.
    values: dict[str, float]


class ExplorerSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    framework_id: int
    framework_version: int
    dimensions: list[Dimension] = Field(default_factory=list)
    points: list[ExplorerPoint] = Field(default_factory=list)
    total: int = 0


class ClusterAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    anecdote_id: int
    cluster: int


class Cluster(BaseModel):
    model_config = ConfigDict(extra="forbid")

    index: int
    size: int
    #: Centre in the same dimension space the Explorer plots, so the overlay and
    #: the axes always agree.
    centre: dict[str, float]
    anecdote_ids: list[int]


class ClusterSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    framework_id: int
    k: int
    seed: int = SEED
    #: Never optional, never abbreviated. A cluster without this label is a
    #: claim the maths does not support.
    caveat: str = CLUSTER_CAVEAT
    dimensions: list[str] = Field(default_factory=list)
    clusters: list[Cluster] = Field(default_factory=list)
    assignments: list[ClusterAssignment] = Field(default_factory=list)
    #: False when there were too few stories, or too few answered dimensions,
    #: for k-means to say anything.
    computed: bool = False
    reason: str = ""


def dimensions_of(definition: FrameworkDefinition) -> list[Dimension]:
    """Every numeric answer this question set can produce, in respondent order."""
    found: list[Dimension] = []
    for kind, signifier in definition.signifiers_in_order():
        if kind == "triad":
            for corner in signifier.corners:
                found.append(
                    Dimension(
                        id=f"{signifier.id}:{corner}",
                        label=f"{signifier.title} — {corner}",
                        signifier_id=signifier.id,
                        signifier_type="triad",
                    )
                )
        elif kind == "dyad":
            found.append(
                Dimension(
                    id=signifier.id,
                    label=f"{signifier.title} ({signifier.left} → {signifier.right})",
                    signifier_id=signifier.id,
                    signifier_type="dyad",
                )
            )
        elif kind == "stones":
            for chip in signifier.chips:
                found.append(
                    Dimension(
                        id=f"{signifier.id}:{chip}:x",
                        label=f"{chip} — {signifier.x_axis.low} → {signifier.x_axis.high}",
                        signifier_id=signifier.id,
                        signifier_type="stones",
                    )
                )
                found.append(
                    Dimension(
                        id=f"{signifier.id}:{chip}:y",
                        label=f"{chip} — {signifier.y_axis.low} → {signifier.y_axis.high}",
                        signifier_id=signifier.id,
                        signifier_type="stones",
                    )
                )
        # MCQs are categories, not positions. Plotting them on an axis would
        # invent an order the operator never wrote.
    return found


def _values(
    definition: FrameworkDefinition, placements: list[AnswerRow]
) -> dict[str, float]:
    """One story's answers, flattened onto the dimension ids."""
    values: dict[str, float] = {}
    by_id = {placement.signifier_id: placement for placement in placements}
    for kind, signifier in definition.signifiers_in_order():
        placement = by_id.get(signifier.id)
        if placement is None:
            continue
        stored = placement.value_json
        if kind == "triad":
            for corner in signifier.corners:
                if corner in stored:
                    values[f"{signifier.id}:{corner}"] = round(
                        float(stored[corner]), VALUE_DECIMALS
                    )
        elif kind == "dyad":
            if "value" in stored:
                values[signifier.id] = round(float(stored["value"]), VALUE_DECIMALS)
        elif kind == "stones":
            for entry in stored.get("placements", []):
                values[f"{signifier.id}:{entry['label']}:x"] = round(
                    float(entry["x"]), VALUE_DECIMALS
                )
                values[f"{signifier.id}:{entry['label']}:y"] = round(
                    float(entry["y"]), VALUE_DECIMALS
                )
    return values


def explorer(
    definition: FrameworkDefinition,
    anecdotes: list[StoryRow],
    significations: list[AnswerRow],
    *,
    framework_id: int,
    framework_version: int,
) -> ExplorerSet:
    """Every story's numeric answers, ready to plot on any three axes."""
    by_anecdote: dict[int, list[AnswerRow]] = {}
    keep = {anecdote.id for anecdote in anecdotes}
    for placement in significations:
        if placement.anecdote_id in keep:
            by_anecdote.setdefault(placement.anecdote_id, []).append(placement)

    points = [
        ExplorerPoint(
            anecdote_id=anecdote.id,
            values=_values(definition, by_anecdote.get(anecdote.id, [])),
        )
        for anecdote in anecdotes
    ]
    return ExplorerSet(
        framework_id=framework_id,
        framework_version=framework_version,
        dimensions=dimensions_of(definition),
        points=points,
        total=len(points),
    )


def cluster(explorer_set: ExplorerSet, k: int = DEFAULT_K) -> ClusterSet:
    """k-means over every dimension every story answered.

    Only dimensions answered by *all* the stories are used: filling a gap with a
    mean would be inventing an answer, and dropping the story would silently
    shrink the picture.
    """
    k = int(np.clip(k, MIN_K, MAX_K))
    result = ClusterSet(framework_id=explorer_set.framework_id, k=k)

    shared = [
        dimension.id
        for dimension in explorer_set.dimensions
        if explorer_set.points
        and all(dimension.id in point.values for point in explorer_set.points)
    ]
    result.dimensions = shared

    if len(explorer_set.points) < k * MIN_PER_CLUSTER:
        result.reason = (
            f"There are {len(explorer_set.points)} stories here, which is too few "
            f"to split into {k} groups."
        )
        return result
    if not shared:
        result.reason = (
            "These stories did not all answer the same questions, so there is no "
            "common ground to group them on."
        )
        return result

    matrix = np.array(
        [[point.values[dim] for dim in shared] for point in explorer_set.points],
        dtype=float,
    )
    # Standardise so a dyad on 0–1 counts as much as a triad corner on 0–1 that
    # happens to vary less. A zero-variance column carries no information and is
    # left flat rather than divided by nothing.
    spread = matrix.std(axis=0)
    spread[spread == 0] = 1.0
    standardised = (matrix - matrix.mean(axis=0)) / spread

    if len(np.unique(standardised, axis=0)) < k:
        result.reason = (
            "These stories are too alike to split into groups — they all sit in "
            "the same place."
        )
        return result

    centres, labels = kmeans2(
        standardised, k, minit="++", seed=SEED, missing="warn"
    )

    middle = matrix.mean(axis=0)
    grouped: dict[int, list[int]] = {index: [] for index in range(k)}
    for point, label in zip(explorer_set.points, labels, strict=True):
        grouped[int(label)].append(point.anecdote_id)

    result.assignments = [
        ClusterAssignment(anecdote_id=point.anecdote_id, cluster=int(label))
        for point, label in zip(explorer_set.points, labels, strict=True)
    ]
    result.clusters = [
        Cluster(
            index=index,
            size=len(members),
            # Back into the reader's own units, so a centre is a placement they
            # could point at rather than a standardised score.
            centre={
                dim: round(
                    float(centres[index][position] * spread[position] + middle[position]),
                    VALUE_DECIMALS,
                )
                for position, dim in enumerate(shared)
            },
            anecdote_ids=sorted(members),
        )
        for index, members in sorted(grouped.items())
    ]
    result.computed = True
    return result
