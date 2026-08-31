"""The widget's triad maths must agree with the server's, exactly.

``frontend/src/widgets/barycentric.js`` re-implements
``backend/barycentric.py`` so the capture widget can place a marker without a
round trip. If the two ever drift, a respondent's mark would mean one thing on
screen and another in the database — a silent corruption that no other test in
the suite would catch.

Skipped when Node is not installed, so the Python suite still runs anywhere.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from backend.barycentric import to_barycentric, to_cartesian

NODE = shutil.which("node")
JS_MODULE = Path(__file__).resolve().parent.parent / "frontend" / "src" / "widgets"

pytestmark = pytest.mark.skipif(
    NODE is None or not JS_MODULE.exists(),
    reason="Node or the frontend widget module is not available",
)

#: The same placements the Python goldens pin down.
GOLDEN_WEIGHTS = [
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
    (1 / 3, 1 / 3, 1 / 3),
    (0.5, 0.3, 0.2),
    (0.7, 0.2, 0.1),
    (0.1, 0.1, 0.8),
    (0.25, 0.25, 0.5),
    (0.5, 0.5, 0.0),
]


def _run_node(script: str) -> list:
    result = subprocess.run(
        [NODE, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=JS_MODULE,
    )
    if result.returncode != 0:
        raise AssertionError(f"node failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def test_javascript_and_python_agree_on_to_cartesian() -> None:
    """The same weights must land on the same point in both languages."""
    script = f"""
import {{ toCartesian }} from './barycentric.js';
const cases = {json.dumps([list(w) for w in GOLDEN_WEIGHTS])};
console.log(JSON.stringify(cases.map((w) => {{
  const p = toCartesian(w);
  return [p.x, p.y];
}})));
"""
    js_points = _run_node(script)

    for weights, js_point in zip(GOLDEN_WEIGHTS, js_points, strict=True):
        py_point = to_cartesian(weights)
        assert js_point[0] == pytest.approx(py_point[0], abs=1e-6), f"x differs for {weights}"
        assert js_point[1] == pytest.approx(py_point[1], abs=1e-6), f"y differs for {weights}"


def test_javascript_and_python_agree_on_to_barycentric() -> None:
    """The same point must read back as the same weights in both languages."""
    points = [list(to_cartesian(w)) for w in GOLDEN_WEIGHTS]
    script = f"""
import {{ toBarycentric }} from './barycentric.js';
const points = {json.dumps(points)};
console.log(JSON.stringify(points.map(([x, y]) => toBarycentric({{ x, y }}))));
"""
    js_weights = _run_node(script)

    for point, js_weight in zip(points, js_weights, strict=True):
        py_weight = to_barycentric((point[0], point[1]))
        assert js_weight == pytest.approx(py_weight, abs=1e-6), f"weights differ for {point}"


def test_javascript_normalise_sums_to_one() -> None:
    """PRD §3: triad barycentric sums to 1.0 — in the widget too."""
    script = """
import { normalise } from './barycentric.js';
const cases = [[1, 1, 1], [1, 2, 3], [0.333, 0.333, 0.333], [7, 11, 13], [-0.05, 0.55, 0.5]];
console.log(JSON.stringify(cases.map((c) => normalise(c))));
"""
    for weights in _run_node(script):
        assert sum(weights) == pytest.approx(1.0, abs=1e-9)
        assert all(w >= 0 for w in weights)
