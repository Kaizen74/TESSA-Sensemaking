/*
 * The Narrative Landscape (PRD §1.5, §5.4) — the one bold thing on the page.
 *
 * Constraint 13a makes this the visual anchor of the whole app, and constraint
 * 13b makes it the single exception to the ban on 3D: the height is density, so
 * the third dimension carries data rather than decorating it. That exception
 * comes with a condition, and it is enforced here — every landscape offers its
 * 2D contour twin, drawn from the identical grid, and the twin is what a
 * snapshot saves by default.
 *
 * Drawn on a canvas with the projection in `terrain.js`: 4,096 quads sorted
 * back to front. No 3D library, so nothing to install, nothing to fail on a
 * machine without WebGL, and a picture whose every pixel can be accounted for.
 *
 * Peaks are labelled directly with the number of stories under them (§1.5), and
 * clicking one opens the stories themselves — the region drill.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  DEFAULT_CAMERA,
  clampCamera,
  colourFor,
  contourSegments,
  shaded,
  project,
  surfaceQuads,
  TRIANGLE_HEIGHT,
} from "./terrain.js";
import "./patterns.css";

const VIEW = { width: 640, height: 440 };
const CONTOUR_SIZE = 460;
const CONTOUR_PAD = 44;

/** Radians of rotation per pixel dragged. */
const DRAG_SENSITIVITY = 0.008;

/*
 * The three tokens the canvas needs by value.
 *
 * A canvas cannot read a CSS variable, so these are the only place in the app
 * where a token is written twice. Held together here rather than inline, so a
 * palette change has one place to look — and a test asserts they still match
 * tokens.css, which is what stops the two drifting apart in silence.
 */
const INK = "#16181d";
const PAPER = "#fbfaf7";
const ACCENT = "#a37b18";

const MONO_STACK = 'ui-monospace, Menlo, Consolas, "Liberation Mono", monospace';

/** Peak counts on the surface: the figure the page exists to deliver. */
const PIN_PX = 13;
const PIN_PX_MAX = 22;

/** Corner labels, in CSS pixels as they should appear on screen (§5b: ≥12). */
const LABEL_PX = 13;

/** …and the ceiling, so a very narrow panel does not shout its corners. */
const LABEL_PX_MAX = 30;

/** The terrain scale, read once from tokens.css so there is one palette. */
function terrainStops() {
  if (typeof window === "undefined") return ["#00204d", "#e2cb52"];
  const styles = getComputedStyle(document.documentElement);
  const stops = [0, 1, 2, 3, 4]
    .map((index) => styles.getPropertyValue(`--nl-terrain-${index}`).trim())
    .filter(Boolean);
  return stops.length ? stops : ["#00204d", "#e2cb52"];
}

export function LandscapeView({ view, onRegion, busy = false }) {
  const [camera, setCamera] = useState(DEFAULT_CAMERA);
  const [contour, setContour] = useState(false);

  const panels = view?.panels ?? [];
  const split = Boolean(view?.split_by);

  return (
    <section className="nl-land">
      <div className="nl-land__bar">
        <div className="nl-land__toggle" role="group" aria-label="How to draw it">
          <button
            type="button"
            className={contour ? "nl-land__mode" : "nl-land__mode nl-land__mode--current"}
            aria-pressed={!contour}
            onClick={() => setContour(false)}
          >
            Terrain
          </button>
          <button
            type="button"
            className={contour ? "nl-land__mode nl-land__mode--current" : "nl-land__mode"}
            aria-pressed={contour}
            onClick={() => setContour(true)}
          >
            Contour
          </button>
        </div>
        {!contour && (
          <button
            type="button"
            className="nl-land__reset"
            onClick={() => setCamera(DEFAULT_CAMERA)}
          >
            Reset the view
          </button>
        )}
      </div>

      <div className={split ? "nl-land__panels nl-land__panels--split" : "nl-land__panels"}>
        {panels.map((panel, index) => (
          <Panel
            key={panel.panel ?? index}
            panel={panel}
            contour={contour}
            camera={camera}
            onCamera={setCamera}
            onRegion={onRegion}
            busy={busy}
          />
        ))}
      </div>
    </section>
  );
}

function Panel({ panel, contour, camera, onCamera, onRegion, busy }) {
  return (
    <figure className="nl-land__panel">
      {panel.panel && <figcaption className="nl-land__panel-name">{panel.panel}</figcaption>}
      {!panel.has_surface ? (
        <ThinLandscape panel={panel} />
      ) : contour ? (
        <ContourTwin panel={panel} onRegion={onRegion} busy={busy} />
      ) : (
        // The peaks under the picture are the way into a region from the
        // terrain; a rotating surface has no stable place to click.
        <Terrain panel={panel} camera={camera} onCamera={onCamera} />
      )}
      <PeakLabels panel={panel} onRegion={onRegion} />
    </figure>
  );
}

/**
 * Too few stories for a density estimate — so it says so, and shows the dots.
 *
 * Drawing a smooth hill over four points would be the app inventing a shape
 * nobody's data has.
 */
function ThinLandscape({ panel }) {
  return (
    <div className="nl-land__thin">
      <ContourFrame panel={panel} segments={[]} />
      <p className="nl-land__empty">
        {panel.count === 0
          ? "No stories have answered this triangle yet. Collect some under Capture & Links, or work the queue under Import & Validate."
          : `${panel.count} ${panel.count === 1 ? "story" : "stories"} — too few, or too alike, to draw a landscape from. The marks are shown as they are.`}
      </p>
    </div>
  );
}

/** The 3D surface. Drag to turn it. */
function Terrain({ panel, camera, onCamera }) {
  const canvasRef = useRef(null);
  const dragRef = useRef(null);
  const stops = useMemo(terrainStops, []);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = VIEW.width * ratio;
    canvas.height = VIEW.height * ratio;
    const context = canvas.getContext("2d");
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, VIEW.width, VIEW.height);

    const frame = {
      cx: VIEW.width / 2,
      cy: VIEW.height / 2 + 40,
      scale: VIEW.width * 0.52,
    };
    const quads = surfaceQuads(
      panel.density,
      panel.x_axis,
      panel.y_axis,
      panel.scale_density,
      camera,
      frame,
    );

    /*
     * The figure sits on ink, and only the figure.
     *
     * Cividis runs dark-blue to yellow. On paper that puts the heaviest ink on
     * the emptiest region, so the flat plateau advances toward the reader and
     * the peaks recede — the encoding read backwards. On an ink ground the ramp
     * reads monotonically as luminance: dark is empty, bright is dense. The
     * shell around this canvas stays paper, and the contour twin stays on paper
     * too, so this is figure and ground inside one element rather than a theme.
     */
    context.fillStyle = INK;
    context.fillRect(0, 0, VIEW.width, VIEW.height);

    const footprint = [
      [0, 0],
      [1, 0],
      [0.5, TRIANGLE_HEIGHT],
    ].map(([x, y]) => project(x, y, 0, camera, frame));

    const pool = context.createRadialGradient(
      frame.cx,
      footprint[0].y - 50,
      20,
      frame.cx,
      footprint[0].y - 50,
      VIEW.width * 0.52,
    );
    pool.addColorStop(0, "rgba(0, 54, 109, 0.36)");
    pool.addColorStop(1, "rgba(22, 24, 29, 0)");
    context.fillStyle = pool;
    context.fillRect(0, 0, VIEW.width, VIEW.height);

    // A base plate, so the surface sits on something instead of floating.
    context.beginPath();
    context.moveTo(footprint[0].x, footprint[0].y);
    for (const point of footprint.slice(1)) context.lineTo(point.x, point.y);
    context.closePath();
    context.fillStyle = "rgba(251, 250, 247, 0.06)";
    context.fill();
    context.strokeStyle = "rgba(251, 250, 247, 0.22)";
    context.lineWidth = 1;
    context.stroke();

    for (const quad of quads) {
      // The height still chooses the colour; the slope only decides how much
      // light that colour catches. Nothing here changes what the colour means.
      const colour = shaded(colourFor(quad.height, stops), quad.shade);
      context.beginPath();
      context.moveTo(quad.points[0].x, quad.points[0].y);
      for (const point of quad.points.slice(1)) context.lineTo(point.x, point.y);
      context.closePath();
      context.fillStyle = colour;
      // A hairline in the fill colour closes the seams between quads without
      // drawing a grid the reader would mistake for data.
      context.strokeStyle = colour;
      context.lineWidth = 0.5;
      context.fill();
      context.stroke();
    }

    /*
     * Isolines draped on the surface, at their own height rather than at zero.
     *
     * The same marching squares the contour twin runs, projected at the level
     * they belong to, which makes height countable on the 3D view instead of
     * only visible. No new geometry — the twin and the drape are one function.
     */
    context.strokeStyle = "rgba(251, 250, 247, 0.34)";
    context.lineWidth = 0.9;
    context.beginPath();
    const top = panel.scale_density > 0 ? panel.scale_density : 1;
    for (const level of panel.contour_levels ?? []) {
      for (const segment of contourSegments(
        panel.density,
        panel.x_axis,
        panel.y_axis,
        level,
      )) {
        const a = project(segment[0].x, segment[0].y, level / top, camera, frame);
        const b = project(segment[1].x, segment[1].y, level / top, camera, frame);
        context.moveTo(a.x, a.y);
        context.lineTo(b.x, b.y);
      }
    }
    context.stroke();

    // The corners, so the terrain is anchored to the question it is about.
    // On the ink ground they need a plate to stay readable where they cross the
    // surface, and paper-coloured text rather than ink.
    // The canvas draws in a fixed 640-unit space and is then stretched to
    // whatever width it has been given, so a font set in canvas units shrinks
    // with the picture — on a 375px phone, 13 units lands at about 7px, half
    // the 12px floor §5b sets for chart text. Scaling the font by how much the
    // canvas was squeezed keeps the label the same size on screen at every
    // width.
    const shownWidth = canvas.clientWidth || VIEW.width;
    const labelPx = Math.min(LABEL_PX * (VIEW.width / shownWidth), LABEL_PX_MAX);
    context.font = `${labelPx.toFixed(1)}px ui-sans-serif, system-ui, sans-serif`;
    const corners = [
      [0, 0],
      [1, 0],
      [0.5, TRIANGLE_HEIGHT],
    ];
    const placed = [];
    corners.forEach(([x, y], index) => {
      const at = project(x, y, 0, camera, frame);
      // The terrain turns, so which side of the picture a corner ends up on
      // changes with it. Aligning by where it actually landed — and holding the
      // text inside the canvas — stops a label sliding off the edge and being
      // clipped away as the view rotates.
      const label = panel.corners[index];
      const outward = at.x < frame.cx ? "right" : "left";
      context.textAlign = outward;
      const width = context.measureText(label).width;
      const nudge = outward === "right" ? -6 : 6;
      const clamped = Math.min(
        Math.max(at.x + nudge, outward === "right" ? width + 4 : 4),
        outward === "right" ? VIEW.width - 4 : VIEW.width - width - 4,
      );
      const baseline = Math.min(Math.max(at.y + 4, 14), VIEW.height - 6);
      const boxX = (outward === "right" ? clamped - width : clamped) - 6;
      const boxY = baseline - labelPx + 1;
      context.fillStyle = "rgba(22, 24, 29, 0.66)";
      context.fillRect(boxX, boxY, width + 12, labelPx + 6);
      context.fillStyle = PAPER;
      context.fillText(label, clamped, baseline);
      placed.push({ x: boxX, y: boxY, w: width + 12, h: labelPx + 6 });
    });

    /*
     * Peak pins — the three findings, on the surface (PRD acceptance 9:
     * "directly-labelled peaks").
     *
     * Placed front to back, and a pin whose label would land on something
     * already placed grows its stem until it is clear. Without that, three
     * adjacent hills print three counts on top of each other and the figure
     * delivers none of them.
     */
    const pinPx = Math.min(Math.max(PIN_PX * (VIEW.width / shownWidth), PIN_PX), PIN_PX_MAX);
    context.font = `700 ${pinPx.toFixed(1)}px ${MONO_STACK}`;
    context.textAlign = "center";

    const pins = (panel.peaks ?? [])
      .map((peak) => ({
        peak,
        at: project(peak.x, peak.y, (peak.density ?? 0) / top, camera, frame),
      }))
      .sort((a, b) => b.at.y - a.at.y);

    const STEM = 26;
    for (const { peak, at } of pins) {
      const boxW = Math.max(26, context.measureText(String(peak.count)).width + 14);
      const boxH = 24;
      const boxX = at.x - boxW / 2;
      const clashesAt = (y) =>
        placed.some(
          (b) =>
            boxX < b.x + b.w + 6 &&
            boxX + boxW + 6 > b.x &&
            y < b.y + b.h + 4 &&
            y + boxH + 4 > b.y,
        );

      /*
       * Lengthen the stem until the label is clear of everything already
       * placed. Two things bound it.
       *
       * It may not leave the canvas: a pin pushed off the top edge is worse
       * than a pin close to its neighbour, because one is a number you can
       * read and the other is a number that is not there. A peak that projects
       * near the top has no room above it at all, so its pin hangs *below*
       * instead — the stem is a pointer, and it points just as well downward.
       */
      const MARGIN = 4;
      const MIN_STEM = 8;
      // A peak near the top of the frame gets a shorter stem rather than a
      // label hanging the other way: a pin that points down lands its number
      // in the middle of the scene, next to a hill it does not belong to.
      // Hanging below is the last resort, for a summit with no room at all.
      const ceiling = at.y - boxH - MARGIN;
      const direction = ceiling >= MIN_STEM ? -1 : 1;
      const boxTopFor = (length) =>
        direction < 0 ? at.y - length - boxH : at.y + length;
      const fits = (length) => {
        const y = boxTopFor(length);
        return y >= MARGIN && y + boxH <= VIEW.height - MARGIN;
      };

      let stem = direction < 0 ? Math.min(STEM, ceiling) : STEM;
      for (let guard = 0; guard < 8; guard += 1) {
        if (!clashesAt(boxTopFor(stem))) break;
        const next = stem + boxH + 8;
        if (!fits(next)) break;
        stem = next;
      }
      if (!fits(stem)) stem = Math.max(MIN_STEM, Math.min(STEM, ceiling));
      const boxY = boxTopFor(stem);
      placed.push({ x: boxX, y: boxY, w: boxW, h: boxH });

      const tip = at.y + direction * stem;
      const disc = tip + direction * 6;
      context.strokeStyle = ACCENT;
      context.lineWidth = 1.5;
      context.beginPath();
      context.moveTo(at.x, at.y);
      context.lineTo(at.x, tip);
      context.stroke();

      context.beginPath();
      context.arc(at.x, disc, 12, 0, Math.PI * 2);
      context.fillStyle = PAPER;
      context.fill();
      context.strokeStyle = ACCENT;
      context.stroke();

      context.fillStyle = INK;
      context.fillText(String(peak.count), at.x, disc + pinPx / 2 - 1);
    }
  }, [panel, camera, stops]);

  useEffect(() => {
    draw();
    // The label size depends on how wide the canvas ended up, so a window that
    // changes width has to be drawn again or the corners are left at the size
    // of the width before last.
    window.addEventListener("resize", draw);
    return () => window.removeEventListener("resize", draw);
  }, [draw]);

  function onPointerDown(event) {
    dragRef.current = { x: event.clientX, y: event.clientY, camera };
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function onPointerMove(event) {
    const drag = dragRef.current;
    if (!drag) return;
    onCamera(
      clampCamera({
        azimuth: drag.camera.azimuth + (event.clientX - drag.x) * DRAG_SENSITIVITY,
        elevation: drag.camera.elevation + (event.clientY - drag.y) * DRAG_SENSITIVITY,
      }),
    );
  }

  function onPointerUp(event) {
    dragRef.current = null;
    event.currentTarget.releasePointerCapture?.(event.pointerId);
  }

  function onKeyDown(event) {
    const step = 0.12;
    const moves = {
      ArrowLeft: { azimuth: -step, elevation: 0 },
      ArrowRight: { azimuth: step, elevation: 0 },
      ArrowUp: { azimuth: 0, elevation: step },
      ArrowDown: { azimuth: 0, elevation: -step },
    };
    const move = moves[event.key];
    if (!move) return;
    event.preventDefault();
    onCamera(
      clampCamera({
        azimuth: camera.azimuth + move.azimuth,
        elevation: camera.elevation + move.elevation,
      }),
    );
  }

  return (
    <canvas
      ref={canvasRef}
      className="nl-land__canvas"
      style={{ width: "100%", aspectRatio: `${VIEW.width} / ${VIEW.height}` }}
      tabIndex={0}
      role="img"
      aria-label={`Landscape of ${panel.title}: ${panel.count} stories, ${panel.peaks.length} peaks`}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
      onKeyDown={onKeyDown}
    />
  );
}

/**
 * The 2D contour twin — the same grid, read from directly above.
 *
 * This is what a snapshot saves and what prints (constraint 13b), because a
 * contour can be measured off the page and a rendered hill cannot.
 */
function ContourTwin({ panel, onRegion }) {
  const segments = useMemo(
    () =>
      panel.contour_levels.map((level) => ({
        level,
        lines: contourSegments(panel.density, panel.x_axis, panel.y_axis, level),
      })),
    [panel],
  );

  return <ContourFrame panel={panel} segments={segments} onRegion={onRegion} />;
}

function ContourFrame({ panel, segments, onRegion = null }) {
  const plot = CONTOUR_SIZE - CONTOUR_PAD * 2;
  const toScreen = (x, y) => ({
    x: CONTOUR_PAD + x * plot,
    // SVG y grows downward; the triangle's y grows upward.
    y: CONTOUR_PAD + (1 - y / TRIANGLE_HEIGHT) * plot,
  });
  const corners = [
    [0, 0],
    [1, 0],
    [0.5, TRIANGLE_HEIGHT],
  ].map(([x, y]) => toScreen(x, y));

  return (
    <svg
      className="nl-land__contour"
      viewBox={`0 0 ${CONTOUR_SIZE} ${CONTOUR_SIZE}`}
      role="img"
      aria-label={`Contour of ${panel.title}: ${panel.count} stories`}
    >
      <polygon
        className="nl-land__triangle"
        points={corners.map((point) => `${point.x},${point.y}`).join(" ")}
      />
      {segments.map(({ level, lines }, band) =>
        lines.map((line, index) => {
          const from = toScreen(line[0].x, line[0].y);
          const to = toScreen(line[1].x, line[1].y);
          return (
            <line
              key={`${level}-${index}`}
              className="nl-land__isoline"
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              // Higher bands draw heavier, so the shape reads without colour.
              strokeWidth={1 + band * 0.6}
            />
          );
        }),
      )}
      {panel.points.map((point) => {
        const at = toScreen(point.x, point.y);
        return <circle key={point.anecdote_id} className="nl-land__dot" cx={at.x} cy={at.y} r={3} />;
      })}
      {panel.peaks.map((peak) => {
        const at = toScreen(peak.x, peak.y);
        return (
          <g key={`${peak.x}-${peak.y}`}>
            <circle className="nl-land__peak-mark" cx={at.x} cy={at.y} r={7} />
            <text
              className="nl-land__peak-label"
              x={at.x}
              y={at.y - 12}
              textAnchor="middle"
              onClick={onRegion ? () => onRegion(peak) : undefined}
            >
              {peak.count}
            </text>
          </g>
        );
      })}
      {/* The base labels are anchored *inwards* from their corners rather than
          outwards. Set outwards, a long word runs past the viewBox and SVG
          clips it away silently — "Speed" arrives as "peed". */}
      {[
        { label: panel.corners[0], at: corners[0], anchor: "start", dy: 18 },
        { label: panel.corners[1], at: corners[1], anchor: "end", dy: 18 },
        { label: panel.corners[2], at: corners[2], anchor: "middle", dy: -12 },
      ].map(({ label, at, anchor, dy }) => (
        <text
          key={label}
          className="nl-land__corner"
          x={at.x}
          y={at.y + dy}
          textAnchor={anchor}
        >
          {label}
        </text>
      ))}
    </svg>
  );
}

/**
 * Peaks, labelled directly (§1.5), and each one a way into its stories.
 *
 * Under the picture rather than floating on it: a label pinned to a rotating
 * surface either follows it — and collides with its neighbours — or stops
 * matching the hill it names.
 */
function PeakLabels({ panel, onRegion }) {
  if (!panel.peaks.length) return null;
  return (
    <div className="nl-land__peaks">
      <span className="nl-land__peaks-title">Where stories gather:</span>
      {panel.peaks.map((peak) => (
        <button
          key={`${peak.x}-${peak.y}`}
          type="button"
          className="nl-land__peak"
          onClick={() => onRegion?.(peak)}
        >
          <strong>{peak.count}</strong> near {peak.nearest_corner}
        </button>
      ))}
    </div>
  );
}
