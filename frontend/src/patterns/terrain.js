/*
 * The landscape's geometry: projection, and contour lines.
 *
 * Written by hand rather than by pulling in a 3D library, for three reasons.
 * The app is local-first and offline (constraint 4), so every byte shipped is a
 * byte the operator has to install; a density grid is 4,096 quads, which is a
 * rounding error to a canvas and nothing like the workload a WebGL engine is
 * for; and a hand-rolled projection runs on any machine, where WebGL is one
 * driver away from a blank rectangle on the one laptop that matters.
 *
 * Plain JavaScript with no JSX, so `tests/test_terrain_maths.py` can load it in
 * Node and hold the maths to fixed answers — the same arrangement the
 * barycentric widget maths and the placement converters use.
 *
 * Constraint 13b is why this file exists at all: the landscape is the one place
 * 3D is allowed, because its z-axis carries density. Everything here serves
 * that one exception and nothing else.
 */

/** The triangle's own height — corner 2 sits at (0.5, √3/2). */
export const TRIANGLE_HEIGHT = Math.sqrt(3) / 2;

/** How tall the terrain stands relative to the triangle's width. */
export const HEIGHT_SCALE = 0.55;

/** The camera the view opens on, and returns to (§5.4: camera reset). */
export const DEFAULT_CAMERA = { azimuth: -0.6, elevation: 0.62 };

export const MIN_ELEVATION = 0.08;
export const MAX_ELEVATION = 1.5;

/**
 * One model point to screen, orthographically.
 *
 * Orthographic rather than perspective on purpose: a perspective terrain makes
 * near peaks look taller than far ones, and the whole point of the height is
 * that it is a quantity the reader compares across the surface.
 */
export function project(x, y, z, camera, view) {
  const cx = x - 0.5;
  const cy = y - TRIANGLE_HEIGHT / 2;
  const cz = z * HEIGHT_SCALE;

  const ca = Math.cos(camera.azimuth);
  const sa = Math.sin(camera.azimuth);
  const rx = cx * ca - cy * sa;
  const ry = cx * sa + cy * ca;

  const ce = Math.cos(camera.elevation);
  const se = Math.sin(camera.elevation);

  return {
    x: view.cx + rx * view.scale,
    // Screen y grows downward; the model's z grows upward.
    y: view.cy - (cz * ce - ry * se) * view.scale,
    // Distance from the eye, for painter's-algorithm sorting.
    depth: ry * ce + cz * se,
  };
}

/**
 * The surface as quads, furthest first.
 *
 * Painter's algorithm: no depth buffer, no z-fighting, and a draw order a
 * person could check by hand. Every quad carries the height of its corner so
 * the colour and the geometry cannot disagree.
 */
export function surfaceQuads(density, xAxis, yAxis, scaleDensity, camera, view) {
  const quads = [];
  const top = scaleDensity > 0 ? scaleDensity : 1;
  for (let iy = 0; iy < density.length - 1; iy += 1) {
    for (let ix = 0; ix < density[iy].length - 1; ix += 1) {
      const heights = [
        density[iy][ix],
        density[iy][ix + 1],
        density[iy + 1][ix + 1],
        density[iy + 1][ix],
      ];
      const corners = [
        [xAxis[ix], yAxis[iy]],
        [xAxis[ix + 1], yAxis[iy]],
        [xAxis[ix + 1], yAxis[iy + 1]],
        [xAxis[ix], yAxis[iy + 1]],
      ];
      const points = corners.map(([x, y], index) =>
        project(x, y, heights[index] / top, camera, view),
      );
      const mean = heights.reduce((sum, value) => sum + value, 0) / heights.length;
      quads.push({
        points,
        height: mean / top,
        depth: points.reduce((sum, point) => sum + point.depth, 0) / points.length,
      });
    }
  }
  quads.sort((a, b) => a.depth - b.depth);
  return quads;
}

/* -------------------------------------------------------------- contour -- */

/** Where a level crosses the segment between two corner values. */
function crossing(v0, v1) {
  if (v1 === v0) return 0.5;
  return (v0 - v1) === 0 ? 0.5 : v0 / (v0 - v1);
}

/**
 * Isolines of one level, by marching squares.
 *
 * This is the 2D contour twin constraint 13b requires, and it reads the very
 * same density grid the surface does — the twin is not a second calculation, it
 * is a second way of looking at the first.
 *
 * Returns segments in triangle coordinates, so the caller scales them the same
 * way it scales the story dots.
 */
export function contourSegments(density, xAxis, yAxis, level) {
  const segments = [];
  for (let iy = 0; iy < density.length - 1; iy += 1) {
    for (let ix = 0; ix < density[iy].length - 1; ix += 1) {
      // Corner values, anticlockwise from bottom-left of the cell.
      const a = density[iy][ix] - level;
      const b = density[iy][ix + 1] - level;
      const c = density[iy + 1][ix + 1] - level;
      const d = density[iy + 1][ix] - level;

      const state =
        (a >= 0 ? 1 : 0) | (b >= 0 ? 2 : 0) | (c >= 0 ? 4 : 0) | (d >= 0 ? 8 : 0);
      if (state === 0 || state === 15) continue;

      const x0 = xAxis[ix];
      const x1 = xAxis[ix + 1];
      const y0 = yAxis[iy];
      const y1 = yAxis[iy + 1];

      // Where the level crosses each of the four edges.
      const bottom = { x: x0 + (x1 - x0) * crossing(a, b), y: y0 };
      const right = { x: x1, y: y0 + (y1 - y0) * crossing(b, c) };
      const topEdge = { x: x0 + (x1 - x0) * crossing(d, c), y: y1 };
      const left = { x: x0, y: y0 + (y1 - y0) * crossing(a, d) };

      const push = (from, to) => segments.push([from, to]);

      switch (state) {
        case 1:
        case 14:
          push(left, bottom);
          break;
        case 2:
        case 13:
          push(bottom, right);
          break;
        case 3:
        case 12:
          push(left, right);
          break;
        case 4:
        case 11:
          push(right, topEdge);
          break;
        case 6:
        case 9:
          push(bottom, topEdge);
          break;
        case 7:
        case 8:
          push(left, topEdge);
          break;
        // The two ambiguous cells: opposite corners above the level. The cell's
        // own average decides which way the lines join, which is the standard
        // disambiguation and keeps neighbouring cells agreeing.
        case 5: {
          if ((a + b + c + d) / 4 >= 0) {
            push(left, topEdge);
            push(bottom, right);
          } else {
            push(left, bottom);
            push(right, topEdge);
          }
          break;
        }
        case 10: {
          if ((a + b + c + d) / 4 >= 0) {
            push(left, bottom);
            push(right, topEdge);
          } else {
            push(left, topEdge);
            push(bottom, right);
          }
          break;
        }
        default:
          break;
      }
    }
  }
  return segments;
}

/* --------------------------------------------------------------- colour -- */

/**
 * A colour from a sequential scale, by height.
 *
 * The stops come from `tokens.css` — cividis, monotonic in lightness, which is
 * what makes the terrain readable to a colourblind reader and still readable
 * printed in grey (§5b, acceptance criterion 10).
 */
export function colourFor(t, stops) {
  if (stops.length === 0) return "#000000";
  const clamped = Math.min(Math.max(t, 0), 1);
  const position = clamped * (stops.length - 1);
  const low = Math.floor(position);
  const high = Math.min(low + 1, stops.length - 1);
  return mix(stops[low], stops[high], position - low);
}

function channels(colour) {
  const hex = colour.trim().replace("#", "");
  const full =
    hex.length === 3
      ? hex
          .split("")
          .map((character) => character + character)
          .join("")
      : hex;
  return [
    parseInt(full.slice(0, 2), 16),
    parseInt(full.slice(2, 4), 16),
    parseInt(full.slice(4, 6), 16),
  ];
}

function mix(from, to, amount) {
  const a = channels(from);
  const b = channels(to);
  const parts = a.map((value, index) =>
    Math.round(value + (b[index] - value) * amount),
  );
  return `rgb(${parts[0]}, ${parts[1]}, ${parts[2]})`;
}

/** Clamp a camera to angles that keep the terrain readable. */
export function clampCamera(camera) {
  return {
    azimuth: camera.azimuth,
    elevation: Math.min(Math.max(camera.elevation, MIN_ELEVATION), MAX_ELEVATION),
  };
}
