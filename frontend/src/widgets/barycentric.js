/*
 * Triad geometry, mirroring backend/barycentric.py exactly.
 *
 * The corner order and the triangle's shape must agree with the server, or a
 * placement would mean one thing in the widget and another in the database.
 * The golden values in tests/test_barycentric.py are the contract both sides
 * are held to.
 */

export const CORNER_0 = { x: 0, y: 0 };
export const CORNER_1 = { x: 1, y: 0 };
export const CORNER_2 = { x: 0.5, y: Math.sqrt(3) / 2 };

export const TRIANGLE_HEIGHT = CORNER_2.y;

const WEIGHT_DECIMALS = 6;

function roundTo(value, decimals) {
  const factor = 10 ** decimals;
  return Math.round(value * factor) / factor;
}

/** Clamp to the triangle and rescale so the three weights sum to exactly 1. */
export function normalise([a, b, c]) {
  const clamped = [a, b, c].map((w) => Math.max(0, Number(w) || 0));
  const total = clamped.reduce((sum, w) => sum + w, 0);

  if (total <= 0) {
    return [1 / 3, 1 / 3, 1 / 3];
  }

  const rounded = clamped.map((w) => roundTo(w / total, WEIGHT_DECIMALS));

  // Put any rounding remainder on the largest weight, as the server does.
  const drift = roundTo(1 - rounded.reduce((sum, w) => sum + w, 0), WEIGHT_DECIMALS);
  if (drift !== 0) {
    const largest = rounded.indexOf(Math.max(...rounded));
    rounded[largest] = roundTo(rounded[largest] + drift, WEIGHT_DECIMALS);
  }

  return rounded;
}

/** Three corner weights to a point inside the triangle. */
export function toCartesian(weights) {
  const [a, b, c] = normalise(weights);
  return {
    x: a * CORNER_0.x + b * CORNER_1.x + c * CORNER_2.x,
    y: a * CORNER_0.y + b * CORNER_1.y + c * CORNER_2.y,
  };
}

/** A point inside the triangle to three corner weights summing to 1. */
export function toBarycentric({ x, y }) {
  const c = y / TRIANGLE_HEIGHT;
  const b = x - y * (CORNER_2.x / TRIANGLE_HEIGHT);
  const a = 1 - b - c;
  return normalise([a, b, c]);
}
