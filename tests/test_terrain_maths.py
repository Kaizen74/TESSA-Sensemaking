"""The landscape's geometry, held to fixed answers in Node.

The terrain is drawn in the browser, so its maths lives in JavaScript — and a
projection or a contour that is subtly wrong looks *plausible*, which is the
worst failure mode a chart has. A slightly wrong isoline is still a smooth curve
in roughly the right place; nobody would spot it by looking.

So the geometry is plain JavaScript with no JSX, loaded in Node from Python, and
checked against cases whose answers are known by hand: a flat grid has no
contour, a single peak has closed rings around it, and the projection puts the
model's corners where trigonometry says they go.

Skipped when Node is not installed, so the Python suite still runs anywhere.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

NODE = shutil.which("node")
FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "src"

pytestmark = pytest.mark.skipif(
    NODE is None or not FRONTEND.exists(),
    reason="Node or the frontend source is not available",
)


def run_js(body: str) -> object:
    script = (
        'import * as terrain from "./patterns/terrain.js";\n'
        f"{body}\n"
    )
    result = subprocess.run(
        [NODE, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=FRONTEND,
    )
    if result.returncode != 0:
        raise AssertionError(f"node failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


# --------------------------------------------------------------------------
# Projection
# --------------------------------------------------------------------------


def test_the_projection_is_orthographic() -> None:
    """Two equal heights project to the same rise, wherever they sit.

    A perspective projection would make the near one taller, and the whole point
    of the height is that it is a quantity compared across the surface.
    """
    result = run_js("""
      const view = { cx: 0, cy: 0, scale: 100 };
      const camera = { azimuth: 0, elevation: 0.5 };
      const flatNear = terrain.project(0.5, 0.1, 0, camera, view);
      const tallNear = terrain.project(0.5, 0.1, 1, camera, view);
      const flatFar = terrain.project(0.5, 0.8, 0, camera, view);
      const tallFar = terrain.project(0.5, 0.8, 1, camera, view);
      console.log(JSON.stringify({
        near: flatNear.y - tallNear.y,
        far: flatFar.y - tallFar.y,
      }));
    """)

    assert result["near"] == pytest.approx(result["far"], abs=1e-9)
    assert result["near"] > 0


def test_raising_the_camera_flattens_the_terrain_towards_a_plan_view() -> None:
    """Elevation is the camera's angle above the horizon, as it sounds.

    From the horizon a hill shows its full height; from overhead it shows none,
    and the view becomes the top-down plan the contour twin draws. Everything
    between is the same landscape at a different angle — which is what makes the
    twin a twin rather than a second chart.
    """
    result = run_js("""
      const view = { cx: 0, cy: 0, scale: 100 };
      const rise = (elevation) => {
        const camera = { azimuth: 0, elevation };
        const base = terrain.project(0.5, 0.4, 0, camera, view);
        const top = terrain.project(0.5, 0.4, 1, camera, view);
        return Math.abs(base.y - top.y);
      };
      console.log(JSON.stringify([rise(0), rise(0.62), rise(1.4), rise(Math.PI / 2)]));
    """)

    horizon, default_view, steep, overhead = result
    assert horizon > default_view > steep > overhead
    # Straight down: the height has nowhere left to go on screen.
    assert overhead == pytest.approx(0.0, abs=1e-9)


def test_turning_the_camera_keeps_the_model_the_same_size() -> None:
    """Rotation moves the terrain, it does not grow or shrink it."""
    result = run_js("""
      const view = { cx: 0, cy: 0, scale: 100 };
      const spans = [];
      for (const azimuth of [0, 0.7, 1.4, 2.1, 2.8]) {
        const camera = { azimuth, elevation: 0.6 };
        const corners = [[0,0],[1,0],[0.5,0.866025]].map(([x,y]) =>
          terrain.project(x, y, 0, camera, view));
        const xs = corners.map((c) => c.x);
        spans.push(Math.max(...xs) - Math.min(...xs));
      }
      console.log(JSON.stringify(spans));
    """)

    # Every span is a chord of the same circle, so none can exceed the diameter.
    assert all(0 < span <= 100.0001 for span in result)


def test_the_camera_reset_is_the_view_it_opens_on() -> None:
    result = run_js("console.log(JSON.stringify(terrain.DEFAULT_CAMERA));")

    assert set(result) == {"azimuth", "elevation"}
    assert 0 < result["elevation"] < 1.5


def test_the_elevation_is_clamped_so_the_terrain_stays_readable() -> None:
    result = run_js("""
      console.log(JSON.stringify([
        terrain.clampCamera({ azimuth: 0, elevation: -5 }).elevation,
        terrain.clampCamera({ azimuth: 0, elevation: 99 }).elevation,
        terrain.clampCamera({ azimuth: 3, elevation: 0.5 }),
      ]));
    """)

    assert result[0] == pytest.approx(0.08)
    assert result[1] == pytest.approx(1.5)
    # Azimuth spins freely — there is no wrong way round to look at a hill.
    assert result[2]["azimuth"] == 3


# --------------------------------------------------------------------------
# The surface
# --------------------------------------------------------------------------


def test_a_grid_becomes_one_quad_per_cell_sorted_back_to_front() -> None:
    result = run_js("""
      const density = [[0,1,2],[1,2,3],[2,3,4]];
      const axis = [0, 0.5, 1];
      const quads = terrain.surfaceQuads(density, axis, axis, 4,
        { azimuth: 0.5, elevation: 0.6 }, { cx: 0, cy: 0, scale: 100 });
      console.log(JSON.stringify({
        count: quads.length,
        sorted: quads.every((q, i) => i === 0 || quads[i-1].depth <= q.depth),
        heights: quads.map((q) => q.height),
      }));
    """)

    # A 3×3 grid has 2×2 cells.
    assert result["count"] == 4
    assert result["sorted"] is True
    assert all(0 <= height <= 1 for height in result["heights"])


# --------------------------------------------------------------------------
# The contour twin
# --------------------------------------------------------------------------


def test_a_flat_landscape_has_no_contour(client=None) -> None:
    result = run_js("""
      const density = Array.from({length: 8}, () => Array(8).fill(0.5));
      const axis = Array.from({length: 8}, (_, i) => i / 7);
      console.log(JSON.stringify(terrain.contourSegments(density, axis, axis, 0.9).length));
    """)

    assert result == 0


def test_a_level_below_everything_has_no_contour() -> None:
    """Nothing crosses a level the whole grid is already above."""
    result = run_js("""
      const density = Array.from({length: 8}, () => Array(8).fill(1));
      const axis = Array.from({length: 8}, (_, i) => i / 7);
      console.log(JSON.stringify(terrain.contourSegments(density, axis, axis, 0.5).length));
    """)

    assert result == 0


def test_a_single_hill_gets_a_closed_ring_around_it() -> None:
    """The answer known by hand: one peak, one loop, and it encircles the peak."""
    result = run_js("""
      const N = 21;
      const axis = Array.from({length: N}, (_, i) => i / (N - 1));
      const density = axis.map((y) => axis.map((x) => {
        const dx = x - 0.5, dy = y - 0.5;
        return Math.exp(-(dx*dx + dy*dy) / 0.02);
      }));
      const segments = terrain.contourSegments(density, axis, axis, 0.5);
      const xs = segments.flat().map((p) => p.x);
      const ys = segments.flat().map((p) => p.y);
      console.log(JSON.stringify({
        count: segments.length,
        minX: Math.min(...xs), maxX: Math.max(...xs),
        minY: Math.min(...ys), maxY: Math.max(...ys),
      }));
    """)

    assert result["count"] > 8
    # The ring surrounds the peak at (0.5, 0.5) and stays inside the grid.
    assert result["minX"] < 0.5 < result["maxX"]
    assert result["minY"] < 0.5 < result["maxY"]
    assert result["minX"] >= 0 and result["maxX"] <= 1


def test_a_higher_level_draws_a_smaller_ring() -> None:
    """Contours nest. If they did not, the terrain would be unreadable."""
    result = run_js("""
      const N = 31;
      const axis = Array.from({length: N}, (_, i) => i / (N - 1));
      const density = axis.map((y) => axis.map((x) => {
        const dx = x - 0.5, dy = y - 0.5;
        return Math.exp(-(dx*dx + dy*dy) / 0.02);
      }));
      const width = (level) => {
        const xs = terrain.contourSegments(density, axis, axis, level).flat().map((p) => p.x);
        return Math.max(...xs) - Math.min(...xs);
      };
      console.log(JSON.stringify({ low: width(0.3), high: width(0.8) }));
    """)

    assert result["high"] < result["low"]


def test_a_ridge_contour_runs_the_length_of_the_ridge() -> None:
    result = run_js("""
      const N = 15;
      const axis = Array.from({length: N}, (_, i) => i / (N - 1));
      // Height depends on x only: a ridge running along y.
      const density = axis.map(() => axis.map((x) => x));
      const segments = terrain.contourSegments(density, axis, axis, 0.5);
      const xs = segments.flat().map((p) => p.x);
      const ys = segments.flat().map((p) => p.y);
      console.log(JSON.stringify({
        count: segments.length,
        xSpread: Math.max(...xs) - Math.min(...xs),
        ySpread: Math.max(...ys) - Math.min(...ys),
      }));
    """)

    assert result["count"] == 14
    # The line sits at x = 0.5 all the way up: no spread across, full spread along.
    assert result["xSpread"] == pytest.approx(0.0, abs=1e-9)
    assert result["ySpread"] == pytest.approx(1.0, abs=1e-9)


# --------------------------------------------------------------------------
# Colour
# --------------------------------------------------------------------------


def test_the_scale_runs_from_the_first_stop_to_the_last() -> None:
    result = run_js("""
      const stops = ["#00204d", "#31446b", "#666970", "#a19669", "#e2cb52"];
      console.log(JSON.stringify({
        low: terrain.colourFor(0, stops),
        high: terrain.colourFor(1, stops),
        under: terrain.colourFor(-3, stops),
        over: terrain.colourFor(9, stops),
        middle: terrain.colourFor(0.5, stops),
      }));
    """)

    assert result["low"] == "rgb(0, 32, 77)"
    assert result["high"] == "rgb(226, 203, 82)"
    # Out of range is clamped, never wrapped round to the other end.
    assert result["under"] == result["low"]
    assert result["over"] == result["high"]
    assert result["middle"] == "rgb(102, 105, 112)"


def test_the_scale_gets_lighter_all_the_way_up() -> None:
    """What makes the terrain survive a grayscale screenshot (§5b)."""
    result = run_js("""
      const stops = ["#00204d", "#31446b", "#666970", "#a19669", "#e2cb52"];
      const lightness = [];
      for (let i = 0; i <= 10; i += 1) {
        const [r, g, b] = terrain.colourFor(i / 10, stops)
          .match(/\\d+/g).map(Number);
        lightness.push(0.2126 * r + 0.7152 * g + 0.0722 * b);
      }
      console.log(JSON.stringify(lightness));
    """)

    assert result == sorted(result), result
    assert result[-1] > result[0] * 3
