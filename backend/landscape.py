"""The Narrative Landscape (PRD §1.5, §4; constraints 11 and 13b).

A landscape is a density estimate over one triad. Every story that answered that
triad is a point inside the triangle; the terrain is how thickly those points
lie. That is the whole idea, and everything else here follows from two rules.

**Constraint 11 — computed, never composed.** This is scipy and arithmetic. No
model smooths, interpolates, labels, or narrates any of it. A peak is a local
maximum of a grid, its label is a count of stories, and both can be recomputed
by anyone with the same data.

**Constraint 13b — one grid, two renderings.** The 3D surface is the only place
in the app where 3D is allowed, because its z-axis carries data. It must always
offer a 2D contour twin, and the twin has to be *the same landscape* — so this
module computes one grid and hands it out once. The surface and the contour read
the same array; there is no second calculation that could disagree with the
first, and ``tests/test_landscape.py`` holds that as a single-source test.

**Determinism** (PRD §9 assumption 8): Scott-bandwidth gaussian KDE on a fixed
64×64 grid over the triangle's own bounding box. No seed, no sampling, no
adaptive anything — the same stories always give the same terrain, which is what
lets the peaks be pinned to ±0.02 in the golden.
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from scipy.stats import gaussian_kde

from backend.barycentric import CORNER_0, CORNER_1, CORNER_2
from backend.patterns import TriadChart

#: PRD §4 pins the grid at 64×64. Fine enough to place a peak, coarse enough to
#: send and to draw at sixty frames a second.
GRID = 64

#: Density values are rounded here, once, so two runs agree to the byte.
DENSITY_DECIMALS = 6
COORD_DECIMALS = 6

#: A cell must hold at least this share of the highest density to be considered
#: a peak at all. Without it, every ripple in a flat landscape is a "peak".
PEAK_FLOOR = 0.35

#: Peaks closer together than this (in triangle units) are the same hill seen
#: twice. Roughly a tenth of the triangle's width.
PEAK_SEPARATION = 0.1

#: How many peaks are worth labelling directly before the labels collide (§1.5:
#: peaks are labelled directly, not through a legend).
MAX_PEAKS = 4

#: Contour levels as shares of the highest density. Five bands: enough to read
#: shape, few enough to stay quiet.
CONTOUR_LEVELS = (0.2, 0.4, 0.6, 0.8)

#: KDE needs at least this many distinct points to estimate anything. Below it
#: the landscape is honest about being a scatter of a few dots.
MIN_FOR_KDE = 3


class Peak(BaseModel):
    """One hill in the terrain, labelled directly with what it holds."""

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    density: float
    #: Stories within :data:`PEAK_SEPARATION` of the peak — what the label says.
    count: int
    #: The corner this peak sits nearest, for a label a person can read.
    nearest_corner: str
    anecdote_ids: list[int]


class Cell(BaseModel):
    """One grid cell that actually holds stories, for the region drill."""

    model_config = ConfigDict(extra="forbid")

    ix: int
    iy: int
    anecdote_ids: list[int]


class LandscapePoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    anecdote_id: int
    x: float
    y: float


class Landscape(BaseModel):
    """One triad's terrain: the grid, and everything read off it.

    The surface and the contour twin both read ``density``. Nothing in this
    model is computed twice.
    """

    model_config = ConfigDict(extra="forbid")

    triad_id: str
    title: str
    corners: list[str]
    #: Panel label when a landscape is one of a split (PRD §1.5 filter split).
    panel: str | None = None
    grid: int = GRID
    #: x and y of each grid line, in triangle coordinates.
    x_axis: list[float] = Field(default_factory=list)
    y_axis: list[float] = Field(default_factory=list)
    #: ``density[iy][ix]`` — row-major, so a renderer walks it as it draws.
    density: list[list[float]] = Field(default_factory=list)
    #: The highest density anywhere on this grid, before any shared rescaling.
    max_density: float = 0.0
    #: The density the surface and contour are drawn against. Equal to
    #: ``max_density`` normally, and to the tallest panel's when split, so two
    #: panels side by side are honestly comparable.
    scale_density: float = 0.0
    contour_levels: list[float] = Field(default_factory=list)
    peaks: list[Peak] = Field(default_factory=list)
    points: list[LandscapePoint] = Field(default_factory=list)
    cells: list[Cell] = Field(default_factory=list)
    count: int = 0
    #: False when there were too few stories to estimate a density at all.
    has_surface: bool = False


def _round(value: float, decimals: int) -> float:
    result = round(float(value), decimals)
    return 0.0 if result == 0 else result


def _axes() -> tuple[np.ndarray, np.ndarray]:
    """The grid lines, over the triangle's own bounding box.

    Fixed to the triangle rather than to the data, so two landscapes of the same
    triad always share a coordinate system — the split panels, and the golden.
    """
    xs = np.linspace(CORNER_0[0], CORNER_1[0], GRID)
    ys = np.linspace(CORNER_0[1], CORNER_2[1], GRID)
    return xs, ys


def _cell_index(value: float, axis: np.ndarray) -> int:
    """Which grid cell a coordinate falls in — the region drill's whole basis."""
    if len(axis) < 2:
        return 0
    step = axis[1] - axis[0]
    index = int(round((value - axis[0]) / step))
    return int(np.clip(index, 0, len(axis) - 1))


def _local_maxima(density: np.ndarray, floor: float) -> list[tuple[int, int, float]]:
    """Cells at least as high as all eight neighbours, tallest first.

    Done by comparing the grid against nine shifted copies of itself rather than
    by walking it. Four thousand cells is a small number to a Python loop and a
    tiny one to numpy, and this runs on every landscape request.
    """
    padded = np.pad(density, 1, mode="constant", constant_values=-np.inf)
    height, width = density.shape
    neighbourhood = np.maximum.reduce(
        [
            padded[dy : dy + height, dx : dx + width]
            for dy in range(3)
            for dx in range(3)
        ]
    )
    ys, xs = np.nonzero((density >= neighbourhood) & (density >= floor))
    found = [(int(x), int(y), float(density[y, x])) for y, x in zip(ys, xs, strict=True)]
    found.sort(key=lambda entry: (-entry[2], entry[1], entry[0]))
    return found


def _nearest_corner(x: float, y: float, corners: list[str]) -> str:
    positions = (CORNER_0, CORNER_1, CORNER_2)
    distances = [
        (x - corner[0]) ** 2 + (y - corner[1]) ** 2 for corner in positions
    ]
    return corners[int(np.argmin(distances))]


def _peaks(
    density: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
    points: list[LandscapePoint],
    corners: list[str],
) -> list[Peak]:
    """The hills worth labelling, with the stories that make each one.

    A peak's count is the stories near it rather than the density value, because
    "nine stories sit here" is a fact the reader can check and "0.83" is not.
    """
    top = float(density.max()) if density.size else 0.0
    if top <= 0 or not points:
        return []

    # Point coordinates as arrays, so "which stories are near this hill" is one
    # vectorised comparison rather than a scan of every story per candidate.
    point_x = np.array([point.x for point in points])
    point_y = np.array([point.y for point in points])
    ids = np.array([point.anecdote_id for point in points])
    radius = PEAK_SEPARATION**2

    chosen: list[Peak] = []
    for ix, iy, value in _local_maxima(density, top * PEAK_FLOOR):
        x, y = float(xs[ix]), float(ys[iy])
        if any((x - peak.x) ** 2 + (y - peak.y) ** 2 < radius for peak in chosen):
            continue
        near = ids[((point_x - x) ** 2 + (point_y - y) ** 2) < radius]
        # A hill with no stories under it is an artefact of the smoothing, not a
        # place anybody's story is.
        if near.size == 0:
            continue
        chosen.append(
            Peak(
                x=_round(x, COORD_DECIMALS),
                y=_round(y, COORD_DECIMALS),
                density=_round(value, DENSITY_DECIMALS),
                count=int(near.size),
                nearest_corner=_nearest_corner(x, y, corners),
                anecdote_ids=sorted(int(value) for value in near),
            )
        )
        if len(chosen) == MAX_PEAKS:
            break
    return chosen


def compute(chart: TriadChart, panel: str | None = None) -> Landscape:
    """One triad's landscape, grid and all.

    Takes the already-aggregated triad chart rather than raw rows, so the points
    under the terrain are exactly the points the supporting charts drew — there
    is no second path from stories to coordinates that could disagree.
    """
    xs, ys = _axes()
    points = [
        LandscapePoint(anecdote_id=point.anecdote_id, x=point.x, y=point.y)
        for point in chart.points
    ]

    cells: dict[tuple[int, int], list[int]] = {}
    for point in points:
        key = (_cell_index(point.x, xs), _cell_index(point.y, ys))
        cells.setdefault(key, []).append(point.anecdote_id)

    landscape = Landscape(
        triad_id=chart.id,
        title=chart.title,
        corners=list(chart.corners),
        panel=panel,
        x_axis=[_round(value, COORD_DECIMALS) for value in xs],
        y_axis=[_round(value, COORD_DECIMALS) for value in ys],
        points=points,
        cells=[
            Cell(ix=ix, iy=iy, anecdote_ids=sorted(ids))
            for (ix, iy), ids in sorted(cells.items())
        ],
        count=len(points),
    )

    coordinates = np.array([[p.x for p in points], [p.y for p in points]])
    # gaussian_kde needs spread in both directions; identical points give a
    # singular covariance matrix and no estimate at all.
    distinct = {(p.x, p.y) for p in points}
    if len(points) < MIN_FOR_KDE or len(distinct) < MIN_FOR_KDE:
        return landscape

    try:
        # Scott's rule is scipy's default and PRD §9 assumption 8 pins it.
        kernel = gaussian_kde(coordinates, bw_method="scott")
    except np.linalg.LinAlgError:
        # Collinear points — a real dataset, just not one with an area.
        return landscape

    mesh_x, mesh_y = np.meshgrid(xs, ys)
    flat = np.vstack([mesh_x.ravel(), mesh_y.ravel()])
    density = kernel(flat).reshape(GRID, GRID)

    top = float(density.max())
    # Rounded in numpy rather than cell by cell: four thousand Python round()
    # calls on every request add up, and `.tolist()` gives plain floats that
    # serialise identically.
    landscape.density = np.round(density, DENSITY_DECIMALS).tolist()
    landscape.max_density = _round(top, DENSITY_DECIMALS)
    landscape.scale_density = landscape.max_density
    landscape.contour_levels = [
        _round(top * level, DENSITY_DECIMALS) for level in CONTOUR_LEVELS
    ]
    landscape.peaks = _peaks(density, xs, ys, points, list(chart.corners))
    landscape.has_surface = True
    return landscape


def share_scale(panels: list[Landscape]) -> list[Landscape]:
    """Put split panels on one density scale (PRD §1.5 filter split).

    Two terrains drawn to their own maxima look equally tall however many
    stories each holds, which is exactly the comparison a split is for. So the
    panels are drawn against the tallest of them, and each keeps its own
    ``max_density`` so the difference stays readable.
    """
    tallest = max((panel.max_density for panel in panels), default=0.0)
    for panel in panels:
        panel.scale_density = tallest
        panel.contour_levels = [
            _round(tallest * level, DENSITY_DECIMALS) for level in CONTOUR_LEVELS
        ]
    return panels


def stories_in_region(
    landscape: Landscape, ix0: int, iy0: int, ix1: int, iy1: int
) -> list[int]:
    """Every story inside a rectangle of grid cells, and no others.

    The region drill of PRD §1.5. Exact by construction: a story is in exactly
    one cell, so a region is the union of its cells and nothing else.
    """
    low_x, high_x = sorted((ix0, ix1))
    low_y, high_y = sorted((iy0, iy1))
    found: set[int] = set()
    for cell in landscape.cells:
        if low_x <= cell.ix <= high_x and low_y <= cell.iy <= high_y:
            found.update(cell.anecdote_ids)
    return sorted(found)
