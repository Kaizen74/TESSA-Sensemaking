/*
 * The 3D Explorer and the k-means overlay (PRD §1.5, acceptance criterion 11).
 *
 * One level down from the landscape, and deliberately plainer: three axes the
 * analyst picks, every story as a dot, and an optional overlay of statistical
 * clusters. It reuses the landscape's projection, so the two views turn the
 * same way and a person who has learned to read one can read the other.
 *
 * The clusters carry their caveat wherever they appear. A group of dots sitting
 * near each other is a fact about arithmetic; reading it as a fact about the
 * world is the mistake the label exists to prevent, so the label is not
 * dismissible and not abbreviated.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { DEFAULT_CAMERA, clampCamera, liftedForInk, project } from "./terrain.js";
import "./patterns.css";

const VIEW = { width: 560, height: 440 };
const DRAG_SENSITIVITY = 0.008;

/* The two tokens this canvas needs by value; see Landscape.jsx for why. */
const INK = "#16181d";
const PAPER = "#fbfaf7";

/** Up to four cluster colours. §5b caps a chart at four, and so does this. */
const CLUSTER_TOKENS = ["--nl-data", "--nl-accent", "--nl-grey", "--nl-terrain-1"];

export function ExplorerView({ explorer, clusters, k, onK, showClusters, onShowClusters }) {
  const dimensions = explorer?.dimensions ?? [];
  const [axes, setAxes] = useState(() => dimensions.slice(0, 3).map((d) => d.id));

  // A new question set means new axes; keeping the old ids would plot nothing.
  useEffect(() => {
    setAxes(dimensions.slice(0, 3).map((dimension) => dimension.id));
  }, [explorer?.framework_id]); // eslint-disable-line react-hooks/exhaustive-deps

  const [camera, setCamera] = useState(DEFAULT_CAMERA);

  if (dimensions.length < 3) {
    return (
      <p className="nl-patterns__empty">
        The Explorer plots three answers against each other, and this question
        set has {dimensions.length} to choose from. Add a triangle or a slider in
        the <strong>Studio</strong> and it will have something to show.
      </p>
    );
  }

  const plotted = (explorer.points ?? []).filter((point) =>
    axes.every((axis) => point.values[axis] !== undefined),
  );
  const clusterOf = new Map(
    (clusters?.assignments ?? []).map((entry) => [entry.anecdote_id, entry.cluster]),
  );

  return (
    <section className="nl-explorer">
      <div className="nl-explorer__axes">
        {["Across", "Into the screen", "Up"].map((label, index) => (
          <label key={label} className="nl-explorer__axis">
            <span className="nl-rail__label">{label}</span>
            <select
              className="nl-rail__select"
              value={axes[index] ?? ""}
              onChange={(event) =>
                setAxes((current) =>
                  current.map((value, position) =>
                    position === index ? event.target.value : value,
                  ),
                )
              }
            >
              {dimensions.map((dimension) => (
                <option key={dimension.id} value={dimension.id}>
                  {dimension.label}
                </option>
              ))}
            </select>
          </label>
        ))}
        <button
          type="button"
          className="nl-land__reset"
          onClick={() => setCamera(DEFAULT_CAMERA)}
        >
          Reset the view
        </button>
      </div>

      <Scatter
        points={plotted}
        axes={axes}
        camera={camera}
        onCamera={setCamera}
        clusterOf={showClusters ? clusterOf : new Map()}
      />

      <p className="nl-explorer__count">
        {plotted.length} of {explorer.total}{" "}
        {explorer.total === 1 ? "story" : "stories"} answered all three of these.
      </p>

      <div className="nl-explorer__clusters">
        <label className="nl-rail__check">
          <input
            type="checkbox"
            checked={showClusters}
            onChange={(event) => onShowClusters(event.target.checked)}
          />
          <span>Show statistical clusters</span>
        </label>
        {showClusters && (
          <>
            <label className="nl-explorer__k">
              <span className="nl-rail__label">Groups</span>
              <select
                className="nl-rail__select"
                value={k}
                onChange={(event) => onK(Number(event.target.value))}
              >
                {[2, 3, 4, 5, 6].map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </label>
            <p className="nl-explorer__caveat">
              {clusters?.computed
                ? `${clusters.caveat}. They describe where answers sit, and say nothing about why.`
                : clusters?.reason || "Not enough to group yet."}
            </p>
          </>
        )}
      </div>
    </section>
  );
}

function Scatter({ points, axes, camera, onCamera, clusterOf }) {
  const canvasRef = useRef(null);
  const dragRef = useRef(null);

  const colours = useMemo(() => {
    if (typeof window === "undefined") return [PAPER];
    const styles = getComputedStyle(document.documentElement);
    // Lifted toward the paper for the ink ground: same hues, more luminance.
    // The data hue is #00366d, which on ink is very nearly the ground itself.
    return CLUSTER_TOKENS.map((token) =>
      liftedForInk(styles.getPropertyValue(token).trim() || "#00366d"),
    );
  }, []);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = VIEW.width * ratio;
    canvas.height = VIEW.height * ratio;
    const context = canvas.getContext("2d");
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, VIEW.width, VIEW.height);

    const frame = { cx: VIEW.width / 2, cy: VIEW.height / 2 + 30, scale: VIEW.width * 0.5 };

    // The same ink ground as the terrain, for the same reason: these are the
    // two figures where depth is doing work, and a light ground flattens both.
    context.fillStyle = INK;
    context.fillRect(0, 0, VIEW.width, VIEW.height);

    /*
     * A floor grid, and a drop line from every dot to it.
     *
     * A projected scatter with neither is an unreadable cloud — two dots an inch
     * apart on screen may be neighbours or a whole axis apart, and there is
     * nothing in the picture to say which. The grid gives depth a reference and
     * the drop line says where each story stands on it.
     *
     * Constraint 13d bans decorative gridlines *behind data*. This is a plane
     * with no data on it, drawn to make the third dimension legible, which is
     * the opposite of decoration — without it the encoding cannot be read at all.
     */
    context.strokeStyle = "rgba(251, 250, 247, 0.1)";
    context.lineWidth = 1;
    for (let i = 0; i <= 4; i += 1) {
      const t = i / 4;
      const a = project(t, 0, 0, camera, frame);
      const b = project(t, 1, 0, camera, frame);
      const c = project(0, t, 0, camera, frame);
      const d = project(1, t, 0, camera, frame);
      context.beginPath();
      context.moveTo(a.x, a.y);
      context.lineTo(b.x, b.y);
      context.moveTo(c.x, c.y);
      context.lineTo(d.x, d.y);
      context.stroke();
    }

    // The unit square's edge, so a dot's position is readable as a position.
    context.strokeStyle = "rgba(251, 250, 247, 0.22)";
    context.beginPath();
    [
      [0, 0],
      [1, 0],
      [1, 1],
      [0, 1],
    ].forEach(([x, y], index) => {
      const at = project(x, y, 0, camera, frame);
      if (index === 0) context.moveTo(at.x, at.y);
      else context.lineTo(at.x, at.y);
    });
    context.closePath();
    context.stroke();

    const drawn = points
      .map((point) => {
        const at = project(
          point.values[axes[0]],
          point.values[axes[1]],
          point.values[axes[2]],
          camera,
          frame,
        );
        const floor = project(
          point.values[axes[0]],
          point.values[axes[1]],
          0,
          camera,
          frame,
        );
        return { at, floor, cluster: clusterOf.get(point.anecdote_id) };
      })
      .sort((a, b) => a.at.depth - b.at.depth);

    context.strokeStyle = "rgba(251, 250, 247, 0.16)";
    context.lineWidth = 0.75;
    context.beginPath();
    for (const item of drawn) {
      context.moveTo(item.floor.x, item.floor.y);
      context.lineTo(item.at.x, item.at.y);
    }
    context.stroke();

    // Near dots larger and more opaque, far dots smaller and fainter — the
    // oldest depth cue there is, and the one a flat scatter throws away.
    const depths = drawn.map((item) => item.at.depth);
    const near = depths.length ? Math.min(...depths) : 0;
    const far = depths.length ? Math.max(...depths) : 1;
    for (const item of drawn) {
      const t = far === near ? 1 : (item.at.depth - near) / (far - near);
      context.beginPath();
      context.arc(item.at.x, item.at.y, 3.2 + t * 2.2, 0, Math.PI * 2);
      context.fillStyle =
        item.cluster === undefined ? colours[0] : colours[item.cluster % colours.length];
      context.globalAlpha = 0.4 + t * 0.5;
      context.fill();
      context.globalAlpha = 1;
    }
  }, [points, axes, camera, clusterOf, colours]);

  useEffect(() => {
    draw();
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

  return (
    <canvas
      ref={canvasRef}
      className="nl-land__canvas"
      style={{ width: "100%", aspectRatio: `${VIEW.width} / ${VIEW.height}` }}
      role="img"
      aria-label={`Explorer: ${points.length} stories plotted on three answers`}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
    />
  );
}
