/*
 * The supporting charts (PRD §1.5, §5b — binding as constraint 13).
 *
 * Every rule in §5b's supporting-chart grammar is enforced here rather than
 * remembered per chart:
 *
 *   - Categorical views are horizontal bars sorted by value. The sort happens on
 *     the server, so a chart cannot be drawn unsorted by forgetting to sort it.
 *   - Bar axes start at zero. There is no scale option, so no chart can start
 *     anywhere else.
 *   - Direct labels on the data. No legends anywhere in this file.
 *   - No gridlines, no decorative rules, no icons.
 *   - One data hue, grey for context, and that is the whole palette — two of the
 *     four §5b allows, because these charts are support.
 *   - Secondary weight: bars at 65% and labels at 45% of full strength, per the
 *     quiet test. From Phase 8 the landscape is the one bold thing on screen,
 *     and nothing here may draw the eye before it does.
 *   - Chart text never goes below 12px.
 *
 * Everything survives a grayscale screenshot because nothing depends on hue:
 * a bar's meaning is its length, and each is labelled where it ends.
 */

import "./patterns.css";

const BAR_HEIGHT = 26;
const BAR_GAP = 8;
const LABEL_WIDTH = 132;
/* Room for the widest label a bar can carry — "20 · 100%" — plus its gap. A
   value that runs off the viewBox is silently clipped rather than wrapped, so
   this is measured against the longest case rather than the usual one. */
const VALUE_WIDTH = 96;
const CHART_WIDTH = 520;

/** Half the width of the widest median label, so it can never leave the plot. */
const MEDIAN_LABEL_INSET = 48;

/**
 * Horizontal bars, sorted by value, labelled directly.
 *
 * Widths are a share of the largest bar rather than of the total, so a set of
 * small values is still readable — but the axis still starts at zero, so the
 * comparison between bars stays honest.
 */
export function BarChart({ chart, unit = "stories" }) {
  const bars = chart.bars ?? [];
  const largest = bars.reduce((most, bar) => Math.max(most, bar.count), 0);
  const plotWidth = CHART_WIDTH - LABEL_WIDTH - VALUE_WIDTH;
  const height = Math.max(bars.length, 1) * (BAR_HEIGHT + BAR_GAP);

  if (bars.length === 0) {
    return <ChartFrame chart={chart} unit={unit} empty />;
  }

  return (
    <ChartFrame chart={chart} unit={unit}>
      <svg
        className="nl-chart__svg"
        viewBox={`0 0 ${CHART_WIDTH} ${height}`}
        role="img"
        aria-label={`${chart.title}: ${bars
          .map((bar) => `${bar.label} ${bar.count}`)
          .join(", ")}`}
      >
        {bars.map((bar, index) => {
          const y = index * (BAR_HEIGHT + BAR_GAP);
          const width = largest ? (bar.count / largest) * plotWidth : 0;
          return (
            <g key={bar.label}>
              <text
                className="nl-chart__label"
                x={LABEL_WIDTH - 8}
                y={y + BAR_HEIGHT / 2}
                textAnchor="end"
                dominantBaseline="middle"
              >
                {bar.label}
              </text>
              {/* Zero-based by construction: every bar starts at LABEL_WIDTH. */}
              <rect
                className="nl-chart__bar"
                x={LABEL_WIDTH}
                y={y}
                width={Math.max(width, bar.count > 0 ? 2 : 0)}
                height={BAR_HEIGHT}
              />
              <text
                className="nl-chart__value"
                x={LABEL_WIDTH + Math.max(width, 2) + 8}
                y={y + BAR_HEIGHT / 2}
                dominantBaseline="middle"
              >
                {bar.count}
                {bar.share > 0 && (
                  <tspan className="nl-chart__share"> · {Math.round(bar.share * 100)}%</tspan>
                )}
              </text>
            </g>
          );
        })}
      </svg>
    </ChartFrame>
  );
}

/**
 * A dyad: every mark on its line, and the distribution they make (§1.5).
 *
 * The strip shows where people actually put their markers, which a histogram
 * alone hides — twenty marks piled on one spot and twenty spread across a bin
 * make the same bar.
 */
export function DyadChart({ chart }) {
  const points = chart.points ?? [];
  const histogram = chart.histogram ?? [];
  const tallest = histogram.reduce((most, bin) => Math.max(most, bin.count), 0);
  const width = CHART_WIDTH;
  const stripY = 26;
  const histTop = 58;
  const histHeight = 92;
  const inset = 12;
  const plot = width - inset * 2;

  if (points.length === 0) {
    return <ChartFrame chart={chart} unit="stories" empty />;
  }

  return (
    <ChartFrame chart={chart} unit="stories">
      <svg
        className="nl-chart__svg"
        viewBox={`0 0 ${width} ${histTop + histHeight + 26}`}
        role="img"
        aria-label={`${chart.title}: ${points.length} stories between ${chart.left} and ${chart.right}, median ${chart.median}`}
      >
        <line
          className="nl-chart__axis"
          x1={inset}
          y1={stripY}
          x2={width - inset}
          y2={stripY}
        />
        {points.map((point) => (
          <circle
            key={point.anecdote_id}
            className="nl-chart__dot"
            cx={inset + point.value * plot}
            cy={stripY}
            r={5}
          />
        ))}
        {chart.median !== null && (
          <g>
            <line
              className="nl-chart__median"
              x1={inset + chart.median * plot}
              y1={stripY - 14}
              x2={inset + chart.median * plot}
              y2={stripY + 14}
            />
            {/* Held inside the plot. A median of 0.00 or 1.00 is a real reading,
                and a centred label at either end runs off the edge and is
                clipped away entirely. */}
            <text
              className="nl-chart__value"
              x={Math.min(
                Math.max(inset + chart.median * plot, MEDIAN_LABEL_INSET),
                width - MEDIAN_LABEL_INSET,
              )}
              y={stripY - 18}
              textAnchor="middle"
            >
              median {chart.median.toFixed(2)}
            </text>
          </g>
        )}

        {histogram.map((bin, index) => {
          const barWidth = plot / histogram.length;
          const barHeight = tallest ? (bin.count / tallest) * histHeight : 0;
          return (
            <rect
              key={`${bin.lower}`}
              className="nl-chart__bar"
              x={inset + index * barWidth + 1}
              y={histTop + histHeight - barHeight}
              width={barWidth - 2}
              height={barHeight}
            />
          );
        })}

        <text className="nl-chart__label" x={inset} y={histTop + histHeight + 18}>
          {chart.left}
        </text>
        <text
          className="nl-chart__label"
          x={width - inset}
          y={histTop + histHeight + 18}
          textAnchor="end"
        >
          {chart.right}
        </text>
      </svg>
    </ChartFrame>
  );
}

/** Stones: chips on a 2D canvas, with the axes named at both ends (§1.5). */
export function StonesChart({ chart }) {
  const points = chart.points ?? [];
  const size = 340;
  const pad = 52;
  const plot = size - pad * 2;

  if (points.length === 0) {
    return <ChartFrame chart={chart} unit="stories" empty />;
  }

  return (
    <ChartFrame chart={chart} unit="stories">
      <svg
        className="nl-chart__svg nl-chart__svg--square"
        viewBox={`0 0 ${size} ${size}`}
        role="img"
        aria-label={`${chart.title}: ${points.length} placements between ${chart.x_axis[0]} and ${chart.x_axis[1]}, ${chart.y_axis[0]} and ${chart.y_axis[1]}`}
      >
        <rect
          className="nl-chart__frame"
          x={pad}
          y={pad}
          width={plot}
          height={plot}
        />
        {points.map((point, index) => (
          <circle
            key={`${point.anecdote_id}-${point.label}-${index}`}
            className="nl-chart__dot"
            cx={pad + point.x * plot}
            // SVG y grows downward; the canvas's y grows upward.
            cy={pad + (1 - point.y) * plot}
            r={4}
          />
        ))}
        <text className="nl-chart__label" x={pad} y={size - 16}>
          {chart.x_axis[0]}
        </text>
        <text className="nl-chart__label" x={size - pad} y={size - 16} textAnchor="end">
          {chart.x_axis[1]}
        </text>
        {/* The vertical axis is labelled along itself. Set horizontally to the
            side, a word like "Fraught" runs off the viewBox and is clipped. */}
        <text
          className="nl-chart__label"
          transform={`translate(18, ${pad + plot}) rotate(-90)`}
        >
          {chart.y_axis[0]}
        </text>
        <text
          className="nl-chart__label"
          transform={`translate(18, ${pad}) rotate(-90)`}
          textAnchor="end"
        >
          {chart.y_axis[1]}
        </text>
      </svg>
    </ChartFrame>
  );
}

function ChartFrame({ chart, unit, empty = false, children }) {
  return (
    <figure className="nl-chart">
      <figcaption className="nl-chart__title">
        {chart.title}
        <span className="nl-chart__count">
          {" "}
          · {chart.answered} {unit}
        </span>
      </figcaption>
      {empty ? (
        <p className="nl-chart__empty">Nobody has answered this one yet.</p>
      ) : (
        children
      )}
    </figure>
  );
}
