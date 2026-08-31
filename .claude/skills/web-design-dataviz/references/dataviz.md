# Data Visualization Reference — 2026

## First principle

Start from the decision the visual supports, not the data available. One question per view; the answer placed where the eye lands first. The test: can the viewer act without asking an analyst what it means?

## Chart selection

| Question | Chart | Notes |
|---|---|---|
| How has X changed over time? | Line (or area for volume) | Never pie/bar for trends |
| How do categories compare? | Horizontal bar | Sort by value unless order is inherent |
| What are the parts of a whole? | Stacked bar or treemap; donut only if ≤5 slices | Center of donut can hold the headline number |
| Do X and Y relate? | Scatter | Clusters/outliers visible at a glance |
| How is X distributed? | Histogram | |
| How do many units compare on many dimensions? | Heatmap grid | Preferred over radar charts — radars distort |
| How did a change decompose? | Waterfall (diverging if +/-) | |
| Before/after or two-point comparison per item? | Dumbbell | Preferred over paired bars |
| When in doubt | Bar chart | |

Never: 3D effects, truncated y-axes to exaggerate trends, dual y-axes without extreme care, pie charts with >5 slices, decorative gridlines/icons that carry no data (maximize data-ink ratio).

## Dashboard hierarchy

- **F-pattern:** primary KPI top-left, largest and highest contrast; secondary metrics top-right; detail and drill-down in the lower half
- **40-30-20-10 space rule:** 40% of screen to the single most important metric, 30% to 2–3 secondary KPIs, 20% to trend context (sparklines, comparisons), 10% to navigation/filters — never a "democratic layout" where everything gets equal space
- **Three-band vertical logic:** top = status (are we okay?), middle = trends (what's changing?), bottom = detail (why?)
- **Visual weight:** primary number 2–3× larger; primary data at full opacity, secondary at ~65%, labels at ~45%
- **10-second test:** a first-time viewer can state what the dashboard is for and whether things are on track within 10 seconds

## Interactivity discipline

Interaction is friction as well as power:
- Filters only when users genuinely need 3+ views of the same data; if 80% use one default view, hard-code it
- Drill-down only when a minority needs the detail — if most do, promote it to the top level
- Never require multiple selections before showing anything; always load a meaningful default
- Every click costs seconds and cognitive load; daily-use dashboards should answer the routine question with zero clicks

## Color encoding

- ≤4 colors per chart; one hue for the data, one accent for the highlight, gray for context
- Sequential scales for magnitude, diverging scales for +/- around a meaningful midpoint; NEVER traffic-light red/green as the primary encoding (8% of men are colorblind)
- Colorblind-safe by construction: pair color with position, pattern, icon, or direct label. If it works in grayscale, it works
- Consistent color = consistent meaning across every view in the same product

## Integrity rules (non-negotiable)

- Y-axis starts at zero for bar charts, always; line charts may zoom with the axis break made visible
- Show uncertainty when it exists (ranges, confidence notes) rather than false precision
- Label directly on the data where possible — direct labels beat legends for clarity and accessibility
- Source and as-of date on anything decision-grade
- The chart's headline is a finding ("APAC drove 72% of growth"), never a topic ("Revenue by Region")

## Accessibility floor

- Minimum 12px chart text (16px preferred for labels users must read)
- WCAG AA contrast for all text and essential marks
- Alt text stating chart type, data, and the key insight
- Keyboard-reachable interactive elements

## Narrative dashboards

2026 practice: dashboards read as structured narratives, not chart collections. Sequence views to answer status → drivers → action. Where AI-generated summaries accompany charts, the summary states the finding and the recommended next step in one or two sentences — facts first, interpretation clearly marked.
