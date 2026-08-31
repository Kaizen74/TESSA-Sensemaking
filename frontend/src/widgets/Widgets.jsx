/*
 * Shared signifier widgets (PRD §6 Phase 2).
 *
 * Used by the Studio's live preview now, and by the capture wizard in Phase 3 —
 * one component per signifier kind, so the operator's preview and the
 * respondent's screen can never drift apart.
 *
 * Passing `onChange` makes a widget interactive; without it the widget is a
 * read-only drawing, which is what the Studio preview wants.
 *
 * Visual grammar: one data hue, grey for context, accent only for a selected
 * state. No decorative 3D anywhere (constraint 13b). Every interactive widget is
 * reachable and operable from the keyboard (§5b accessibility floor), because a
 * marker you can only place by dragging is a marker some people cannot place.
 */

import { useRef } from "react";
import {
  CORNER_0,
  CORNER_1,
  CORNER_2,
  TRIANGLE_HEIGHT,
  normalise,
  toBarycentric,
  toCartesian,
} from "./barycentric.js";
import "./widgets.css";

const VIEW = 300;
const PAD = 46;

/** How far one arrow-key press moves a marker, as a fraction of the shape. */
const KEY_STEP = 0.05;

function triangleScreenPoint(corner) {
  const span = VIEW - 2 * PAD;
  return {
    x: PAD + corner.x * span,
    // SVG y grows downward; the triangle's y grows upward.
    y: PAD + (TRIANGLE_HEIGHT - corner.y) * span,
  };
}

/** Screen point back to triangle space — the inverse of triangleScreenPoint. */
function trianglePointFromScreen(px, py) {
  const span = VIEW - 2 * PAD;
  return {
    x: (px - PAD) / span,
    y: TRIANGLE_HEIGHT - (py - PAD) / span,
  };
}

/**
 * Where a pointer event landed, in the SVG's own viewBox coordinates.
 *
 * Uses the element's bounding box rather than an SVG matrix so it behaves the
 * same whether the widget is scaled to a phone or a large sheet.
 */
function pointerToViewBox(event, element, viewWidth, viewHeight) {
  const rect = element.getBoundingClientRect();
  const point = event.touches?.[0] ?? event;
  return {
    x: ((point.clientX - rect.left) / rect.width) * viewWidth,
    y: ((point.clientY - rect.top) / rect.height) * viewHeight,
  };
}

const clamp01 = (n) => Math.min(1, Math.max(0, n));

export function TriadWidget({ triad, value = null, onChange = null }) {
  const svgRef = useRef(null);
  const interactive = Boolean(onChange);

  const p0 = triangleScreenPoint(CORNER_0);
  const p1 = triangleScreenPoint(CORNER_1);
  const p2 = triangleScreenPoint(CORNER_2);

  const marker = value ? triangleScreenPoint(toCartesian(value)) : null;
  const corners = triad.corners ?? ["", "", ""];

  function place(event) {
    if (!interactive || !svgRef.current) return;
    const { x, y } = pointerToViewBox(event, svgRef.current, VIEW, VIEW * 0.95);
    // normalise clamps to the triangle, so a mark just outside the edge lands
    // on the nearest legal reading rather than being thrown away.
    onChange(normalise(toBarycentric(trianglePointFromScreen(x, y))));
  }

  function onKeyDown(event) {
    if (!interactive) return;
    const current = value ?? [1 / 3, 1 / 3, 1 / 3];
    const point = toCartesian(current);
    const moves = {
      ArrowLeft: { x: -KEY_STEP, y: 0 },
      ArrowRight: { x: KEY_STEP, y: 0 },
      ArrowUp: { x: 0, y: KEY_STEP },
      ArrowDown: { x: 0, y: -KEY_STEP },
    };
    const move = moves[event.key];
    if (!move) return;
    event.preventDefault();
    onChange(normalise(toBarycentric({ x: point.x + move.x, y: point.y + move.y })));
  }

  return (
    <figure className="nl-widget">
      <figcaption className="nl-widget__title">{triad.title}</figcaption>
      <svg
        ref={svgRef}
        viewBox={`0 0 ${VIEW} ${VIEW * 0.95}`}
        className={
          interactive ? "nl-widget__canvas nl-widget__canvas--live" : "nl-widget__canvas"
        }
        role={interactive ? "application" : "img"}
        tabIndex={interactive ? 0 : undefined}
        aria-label={
          interactive
            ? `Place your mark in the triangle. Corners: ${corners.join(", ")}. ` +
              `Use the arrow keys, or tap inside the triangle.`
            : `Triangle with corners ${corners.join(", ")}`
        }
        onClick={place}
        onKeyDown={onKeyDown}
      >
        <polygon
          points={`${p0.x},${p0.y} ${p1.x},${p1.y} ${p2.x},${p2.y}`}
          className="nl-widget__shape"
        />
        <text x={p0.x - 4} y={p0.y + 18} textAnchor="end" className="nl-widget__label">
          {corners[0]}
        </text>
        <text x={p1.x + 4} y={p1.y + 18} textAnchor="start" className="nl-widget__label">
          {corners[1]}
        </text>
        <text x={p2.x} y={p2.y - 12} textAnchor="middle" className="nl-widget__label">
          {corners[2]}
        </text>
        {marker && <circle cx={marker.x} cy={marker.y} r="6" className="nl-widget__marker" />}
      </svg>
    </figure>
  );
}

export function DyadWidget({ dyad, value = null, onChange = null }) {
  const svgRef = useRef(null);
  const interactive = Boolean(onChange);

  const trackY = 44;
  const left = PAD;
  const right = VIEW - PAD;
  const markerX = value === null ? null : left + (right - left) * clamp01(value);

  function place(event) {
    if (!interactive || !svgRef.current) return;
    const { x } = pointerToViewBox(event, svgRef.current, VIEW, 96);
    onChange(clamp01((x - left) / (right - left)));
  }

  function onKeyDown(event) {
    if (!interactive) return;
    const current = value ?? 0.5;
    if (event.key === "ArrowLeft" || event.key === "ArrowDown") {
      event.preventDefault();
      onChange(clamp01(current - KEY_STEP));
    } else if (event.key === "ArrowRight" || event.key === "ArrowUp") {
      event.preventDefault();
      onChange(clamp01(current + KEY_STEP));
    }
  }

  return (
    <figure className="nl-widget">
      <figcaption className="nl-widget__title">{dyad.title}</figcaption>
      <svg
        ref={svgRef}
        viewBox={`0 0 ${VIEW} 96`}
        className={
          interactive ? "nl-widget__canvas nl-widget__canvas--live" : "nl-widget__canvas"
        }
        role={interactive ? "slider" : "img"}
        tabIndex={interactive ? 0 : undefined}
        aria-valuemin={interactive ? 0 : undefined}
        aria-valuemax={interactive ? 1 : undefined}
        aria-valuenow={interactive ? (value ?? 0.5) : undefined}
        aria-valuetext={
          interactive
            ? value === null
              ? "not placed yet"
              : `${Math.round(value * 100)}% towards ${dyad.right}`
            : undefined
        }
        aria-label={
          interactive
            ? `Place your mark between ${dyad.left} and ${dyad.right}. Use the arrow keys, or tap the line.`
            : `Scale from ${dyad.left} to ${dyad.right}`
        }
        onClick={place}
        onKeyDown={onKeyDown}
      >
        <line x1={left} y1={trackY} x2={right} y2={trackY} className="nl-widget__shape" />
        {[0, 0.5, 1].map((stop) => (
          <line
            key={stop}
            x1={left + (right - left) * stop}
            y1={trackY - 7}
            x2={left + (right - left) * stop}
            y2={trackY + 7}
            className="nl-widget__tick"
          />
        ))}
        {markerX !== null && (
          <circle cx={markerX} cy={trackY} r="6" className="nl-widget__marker" />
        )}
        <text x={left} y={trackY + 30} textAnchor="start" className="nl-widget__label">
          {dyad.left}
        </text>
        <text x={right} y={trackY + 30} textAnchor="end" className="nl-widget__label">
          {dyad.right}
        </text>
      </svg>
    </figure>
  );
}

export function StonesWidget({ stones, value = null, onChange = null }) {
  const svgRef = useRef(null);
  const interactive = Boolean(onChange);
  const box = VIEW - 2 * PAD;

  const placed = value ?? [];
  const placedLabels = new Set(placed.map((chip) => chip.label));
  const chips = stones.chips ?? [];
  // Whichever item still needs a home. Placing them in order means the
  // respondent never has to choose a chip before choosing a spot.
  const nextChip = chips.find((chip) => !placedLabels.has(chip)) ?? null;

  function place(event) {
    if (!interactive || !svgRef.current || !nextChip) return;
    const { x, y } = pointerToViewBox(event, svgRef.current, VIEW, VIEW);
    onChange([
      ...placed,
      {
        label: nextChip,
        x: clamp01((x - PAD) / box),
        // The square's y grows upward; the SVG's grows down.
        y: clamp01(1 - (y - PAD) / box),
      },
    ]);
  }

  function onKeyDown(event) {
    if (!interactive) return;
    if (event.key === "Enter" || event.key === " ") {
      // Keyboard users drop the next item in the middle, then nudge it.
      if (!nextChip) return;
      event.preventDefault();
      onChange([...placed, { label: nextChip, x: 0.5, y: 0.5 }]);
      return;
    }
    const moves = {
      ArrowLeft: { x: -KEY_STEP, y: 0 },
      ArrowRight: { x: KEY_STEP, y: 0 },
      ArrowUp: { x: 0, y: KEY_STEP },
      ArrowDown: { x: 0, y: -KEY_STEP },
    };
    const move = moves[event.key];
    if (!move || placed.length === 0) return;
    event.preventDefault();
    const last = placed[placed.length - 1];
    onChange([
      ...placed.slice(0, -1),
      { label: last.label, x: clamp01(last.x + move.x), y: clamp01(last.y + move.y) },
    ]);
  }

  return (
    <figure className="nl-widget">
      <figcaption className="nl-widget__title">{stones.title}</figcaption>
      <svg
        ref={svgRef}
        viewBox={`0 0 ${VIEW} ${VIEW}`}
        className={
          interactive ? "nl-widget__canvas nl-widget__canvas--live" : "nl-widget__canvas"
        }
        role={interactive ? "application" : "img"}
        tabIndex={interactive ? 0 : undefined}
        aria-label={
          interactive
            ? `Place each item on the square. Across: ${stones.x_axis?.low} to ` +
              `${stones.x_axis?.high}. Up: ${stones.y_axis?.low} to ${stones.y_axis?.high}. ` +
              (nextChip
                ? `Next to place: ${nextChip}. Press Enter to drop it, then use the arrow keys.`
                : "All items placed.")
            : `Grid from ${stones.x_axis?.low} to ${stones.x_axis?.high} across, ` +
              `${stones.y_axis?.low} to ${stones.y_axis?.high} up`
        }
        onClick={place}
        onKeyDown={onKeyDown}
      >
        <rect x={PAD} y={PAD} width={box} height={box} className="nl-widget__shape" />
        <line
          x1={PAD + box / 2}
          y1={PAD}
          x2={PAD + box / 2}
          y2={PAD + box}
          className="nl-widget__guide"
        />
        <line
          x1={PAD}
          y1={PAD + box / 2}
          x2={PAD + box}
          y2={PAD + box / 2}
          className="nl-widget__guide"
        />
        {(value ?? []).map((chip) => (
          <g key={chip.label}>
            <circle
              cx={PAD + chip.x * box}
              cy={PAD + (1 - chip.y) * box}
              r="5"
              className="nl-widget__marker"
            />
            <text
              x={PAD + chip.x * box + 9}
              y={PAD + (1 - chip.y) * box + 4}
              className="nl-widget__label nl-widget__label--small"
            >
              {chip.label}
            </text>
          </g>
        ))}
        <text x={PAD} y={PAD + box + 20} textAnchor="start" className="nl-widget__label">
          {stones.x_axis?.low}
        </text>
        <text x={PAD + box} y={PAD + box + 20} textAnchor="end" className="nl-widget__label">
          {stones.x_axis?.high}
        </text>
        <text x={PAD + box / 2} y={PAD - 14} textAnchor="middle" className="nl-widget__label">
          {stones.y_axis?.high}
        </text>
        <text
          x={PAD + box / 2}
          y={PAD + box + 38}
          textAnchor="middle"
          className="nl-widget__label"
        >
          {stones.y_axis?.low}
        </text>
      </svg>
      {stones.chips?.length > 0 && (
        <p className="nl-widget__chips">
          {interactive
            ? nextChip
              ? `Tap where “${nextChip}” belongs.`
              : "All placed. Tap an item below to move it again."
            : `Place: ${stones.chips.join(" · ")}`}
        </p>
      )}
      {interactive && placed.length > 0 && (
        <button
          type="button"
          className="nl-widget__undo"
          onClick={() => onChange(placed.slice(0, -1))}
        >
          Undo last placement
        </button>
      )}
    </figure>
  );
}

export function McqWidget({ mcq, value = null, onChange = null }) {
  const interactive = Boolean(onChange);
  const selected = new Set(value?.selected ?? []);

  function toggle(option) {
    if (!interactive) return;
    if (mcq.multi) {
      const next = new Set(selected);
      if (next.has(option)) next.delete(option);
      else next.add(option);
      onChange({ selected: [...next] });
    } else {
      // Tapping the chosen option again clears it, so a mis-tap is recoverable
      // without a separate "clear" control.
      onChange({ selected: selected.has(option) ? [] : [option] });
    }
  }

  return (
    <figure className="nl-widget">
      <figcaption className="nl-widget__title">{mcq.title}</figcaption>
      <ul className="nl-widget__options" role={interactive ? "group" : undefined}>
        {(mcq.options ?? []).map((option) => {
          const isSelected = selected.has(option);
          const className = isSelected
            ? "nl-widget__option nl-widget__option--selected"
            : "nl-widget__option";
          const box = (
            <span
              className={mcq.multi ? "nl-widget__box" : "nl-widget__box nl-widget__box--round"}
              aria-hidden="true"
            />
          );

          if (!interactive) {
            return (
              <li key={option} className={className}>
                {box}
                <span>{option}</span>
              </li>
            );
          }

          return (
            <li key={option}>
              <button
                type="button"
                className={`${className} nl-widget__option--live`}
                role={mcq.multi ? "checkbox" : "radio"}
                aria-checked={isSelected}
                onClick={() => toggle(option)}
              >
                {box}
                <span>{option}</span>
              </button>
            </li>
          );
        })}
      </ul>
      <p className="nl-widget__hint">{mcq.multi ? "Choose any that apply." : "Choose one."}</p>
    </figure>
  );
}

/** Render whichever widget matches the signifier kind. */
export function SignifierWidget({ kind, signifier, value = null, onChange = null }) {
  if (kind === "triad") {
    return <TriadWidget triad={signifier} value={value} onChange={onChange} />;
  }
  if (kind === "dyad") {
    return <DyadWidget dyad={signifier} value={value} onChange={onChange} />;
  }
  if (kind === "stones") {
    return <StonesWidget stones={signifier} value={value} onChange={onChange} />;
  }
  if (kind === "mcq") {
    return <McqWidget mcq={signifier} value={value} onChange={onChange} />;
  }
  return null;
}
