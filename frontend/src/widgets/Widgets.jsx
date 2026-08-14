/*
 * Shared signifier widgets (PRD §6 Phase 2).
 *
 * Used by the Studio's live preview now, and by the capture wizard in Phase 3 —
 * one component per signifier kind, so the operator's preview and the
 * respondent's screen can never drift apart.
 *
 * Every widget is read-only here (`interactive` defaults to false). Phase 3 adds
 * the placement interaction; this phase only has to draw them truthfully.
 *
 * Visual grammar: one data hue, grey for context, accent only for a selected
 * state. No decorative 3D anywhere (constraint 13b).
 */

import { CORNER_0, CORNER_1, CORNER_2, TRIANGLE_HEIGHT, toCartesian } from "./barycentric.js";
import "./widgets.css";

const VIEW = 300;
const PAD = 46;

function triangleScreenPoint(corner) {
  const span = VIEW - 2 * PAD;
  return {
    x: PAD + corner.x * span,
    // SVG y grows downward; the triangle's y grows upward.
    y: PAD + (TRIANGLE_HEIGHT - corner.y) * span,
  };
}

export function TriadWidget({ triad, value = null }) {
  const p0 = triangleScreenPoint(CORNER_0);
  const p1 = triangleScreenPoint(CORNER_1);
  const p2 = triangleScreenPoint(CORNER_2);

  const marker = value ? triangleScreenPoint(toCartesian(value)) : null;
  const corners = triad.corners ?? ["", "", ""];

  return (
    <figure className="nl-widget">
      <figcaption className="nl-widget__title">{triad.title}</figcaption>
      <svg
        viewBox={`0 0 ${VIEW} ${VIEW * 0.95}`}
        className="nl-widget__canvas"
        role="img"
        aria-label={`Triangle with corners ${corners.join(", ")}`}
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

export function DyadWidget({ dyad, value = null }) {
  const trackY = 44;
  const left = PAD;
  const right = VIEW - PAD;
  const markerX = value === null ? null : left + (right - left) * Math.min(1, Math.max(0, value));

  return (
    <figure className="nl-widget">
      <figcaption className="nl-widget__title">{dyad.title}</figcaption>
      <svg
        viewBox={`0 0 ${VIEW} 96`}
        className="nl-widget__canvas"
        role="img"
        aria-label={`Scale from ${dyad.left} to ${dyad.right}`}
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

export function StonesWidget({ stones, value = null }) {
  const box = VIEW - 2 * PAD;

  return (
    <figure className="nl-widget">
      <figcaption className="nl-widget__title">{stones.title}</figcaption>
      <svg
        viewBox={`0 0 ${VIEW} ${VIEW}`}
        className="nl-widget__canvas"
        role="img"
        aria-label={
          `Grid from ${stones.x_axis?.low} to ${stones.x_axis?.high} across, ` +
          `${stones.y_axis?.low} to ${stones.y_axis?.high} up`
        }
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
        <p className="nl-widget__chips">Place: {stones.chips.join(" · ")}</p>
      )}
    </figure>
  );
}

export function McqWidget({ mcq, value = null }) {
  const selected = new Set(value?.selected ?? []);

  return (
    <figure className="nl-widget">
      <figcaption className="nl-widget__title">{mcq.title}</figcaption>
      <ul className="nl-widget__options">
        {(mcq.options ?? []).map((option) => (
          <li
            key={option}
            className={
              selected.has(option)
                ? "nl-widget__option nl-widget__option--selected"
                : "nl-widget__option"
            }
          >
            <span
              className={mcq.multi ? "nl-widget__box" : "nl-widget__box nl-widget__box--round"}
              aria-hidden="true"
            />
            <span>{option}</span>
          </li>
        ))}
      </ul>
      <p className="nl-widget__hint">{mcq.multi ? "Choose any that apply." : "Choose one."}</p>
    </figure>
  );
}

/** Render whichever widget matches the signifier kind. */
export function SignifierWidget({ kind, signifier, value = null }) {
  if (kind === "triad") return <TriadWidget triad={signifier} value={value} />;
  if (kind === "dyad") return <DyadWidget dyad={signifier} value={value} />;
  if (kind === "stones") return <StonesWidget stones={signifier} value={value} />;
  if (kind === "mcq") return <McqWidget mcq={signifier} value={value} />;
  return null;
}
