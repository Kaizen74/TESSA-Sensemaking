"""The printable paper pack (PRD §1.2, §5b print grammar).

One HTML page the operator opens and sends to the printer — or to Print → Save
as PDF. PRD §9 assumption 11 chose browser printing over a PDF library
deliberately: no fragile Windows dependency, and print preview comes free.

The pack is three kinds of sheet, one per printed page:

1. **Story card** — the prompt, ruled writing space, respondent-group tick
   boxes, and the anonymity line printed verbatim (constraint 9).
2. **One signifier sheet per signifier** — the widget drawn large for sticky
   dots or pen, in A4 landscape.
3. **Facilitator sheet** — running instructions, materials, and the
   reconciliation grid (handed out / returned / entered).

Print grammar (§5b): pure black on white, widgets at maximum size, labels ≥14pt,
a page break per sheet, and no reliance on colour — a photocopier is the test.
Everything is inline; a printer must never need the network.
"""

from __future__ import annotations

import math
from html import escape

from backend.barycentric import CORNER_0, CORNER_1, CORNER_2
from backend.framework_schema import Dyad, FrameworkDefinition, Mcq, Stones, Triad

#: Ruled lines on the story card. Enough for a real story, few enough to fit A4.
STORY_RULE_COUNT = 12

#: Rows in the facilitator reconciliation grid.
RECONCILIATION_ROW_COUNT = 6


def _svg_triad(triad: Triad) -> str:
    """A large equilateral triangle with its three corners labelled.

    Drawn from the same corner geometry as ``backend.barycentric``, so what the
    respondent marks on paper means the same thing as a tap in the app.
    """
    size = 520.0
    pad = 90.0
    height = size * (math.sqrt(3.0) / 2.0)

    def place(corner: tuple[float, float]) -> tuple[float, float]:
        # SVG y grows downward; the triangle's y grows upward.
        return (pad + corner[0] * size, pad + (height - corner[1] * size))

    x0, y0 = place(CORNER_0)
    x1, y1 = place(CORNER_1)
    x2, y2 = place(CORNER_2)

    labels = [
        (x0 - 10, y0 + 34, "end", triad.corners[0]),
        (x1 + 10, y1 + 34, "start", triad.corners[1]),
        (x2, y2 - 22, "middle", triad.corners[2]),
    ]
    label_markup = "\n".join(
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="sheet-label">'
        f"{escape(text)}</text>"
        for x, y, anchor, text in labels
    )

    return f"""
<svg viewBox="0 0 {size + 2 * pad:.0f} {height + 2 * pad:.0f}" class="widget"
     role="img" aria-label="Triangle with corners {escape(', '.join(triad.corners))}">
  <polygon points="{x0:.1f},{y0:.1f} {x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}"
           fill="none" stroke="#000" stroke-width="2.5" />
  {label_markup}
</svg>
"""


def _svg_dyad(dyad: Dyad) -> str:
    """A long line between two named poles, with tick marks to aim at."""
    width = 660.0
    pad = 90.0
    y = 90.0
    ticks = "\n".join(
        f'<line x1="{pad + width * i / 10:.1f}" y1="{y - 12:.1f}" '
        f'x2="{pad + width * i / 10:.1f}" y2="{y + 12:.1f}" '
        f'stroke="#000" stroke-width="{2.5 if i in (0, 5, 10) else 1}" />'
        for i in range(11)
    )
    return f"""
<svg viewBox="0 0 {width + 2 * pad:.0f} 190" class="widget"
     role="img" aria-label="Scale from {escape(dyad.left)} to {escape(dyad.right)}">
  <line x1="{pad:.1f}" y1="{y:.1f}" x2="{pad + width:.1f}" y2="{y:.1f}"
        stroke="#000" stroke-width="2.5" />
  {ticks}
  <text x="{pad:.1f}" y="{y + 52:.1f}" text-anchor="start" class="sheet-label">
    {escape(dyad.left)}</text>
  <text x="{pad + width:.1f}" y="{y + 52:.1f}" text-anchor="end" class="sheet-label">
    {escape(dyad.right)}</text>
</svg>
"""


def _svg_stones(stones: Stones) -> str:
    """A square canvas with both axes named at each end."""
    size = 520.0
    pad = 110.0
    return f"""
<svg viewBox="0 0 {size + 2 * pad:.0f} {size + 2 * pad:.0f}" class="widget"
     role="img" aria-label="Grid from {escape(stones.x_axis.low)} to
     {escape(stones.x_axis.high)} across, {escape(stones.y_axis.low)} to
     {escape(stones.y_axis.high)} up">
  <rect x="{pad:.1f}" y="{pad:.1f}" width="{size:.1f}" height="{size:.1f}"
        fill="none" stroke="#000" stroke-width="2.5" />
  <line x1="{pad + size / 2:.1f}" y1="{pad:.1f}"
        x2="{pad + size / 2:.1f}" y2="{pad + size:.1f}"
        stroke="#000" stroke-width="1" stroke-dasharray="6 6" />
  <line x1="{pad:.1f}" y1="{pad + size / 2:.1f}"
        x2="{pad + size:.1f}" y2="{pad + size / 2:.1f}"
        stroke="#000" stroke-width="1" stroke-dasharray="6 6" />
  <text x="{pad:.1f}" y="{pad + size + 44:.1f}" text-anchor="start"
        class="sheet-label">{escape(stones.x_axis.low)}</text>
  <text x="{pad + size:.1f}" y="{pad + size + 44:.1f}" text-anchor="end"
        class="sheet-label">{escape(stones.x_axis.high)}</text>
  <text x="{pad + size / 2:.1f}" y="{pad - 30:.1f}" text-anchor="middle"
        class="sheet-label">{escape(stones.y_axis.high)}</text>
  <text x="{pad + size / 2:.1f}" y="{pad + size + 78:.1f}" text-anchor="middle"
        class="sheet-label">{escape(stones.y_axis.low)}</text>
</svg>
"""


def _mcq_options(mcq: Mcq) -> str:
    """Tick boxes, one per option, big enough to mark with a pen."""
    rows = "\n".join(
        f'<li class="tick-row"><span class="tick-box" aria-hidden="true"></span>'
        f'<span class="sheet-label">{escape(option)}</span></li>'
        for option in mcq.options
    )
    hint = "Tick as many as apply." if mcq.multi else "Tick one."
    return f'<p class="hint">{hint}</p>\n<ul class="tick-list">{rows}</ul>'


def _signifier_sheet(kind: str, signifier: Triad | Dyad | Stones | Mcq) -> str:
    """One A4 landscape sheet for one signifier."""
    if kind == "triad":
        body = _svg_triad(signifier)  # type: ignore[arg-type]
        instruction = "Put one mark inside the triangle, nearer the corners that fit best."
    elif kind == "dyad":
        body = _svg_dyad(signifier)  # type: ignore[arg-type]
        instruction = "Put one mark on the line."
    elif kind == "stones":
        chips = ", ".join(signifier.chips)  # type: ignore[union-attr]
        body = _svg_stones(signifier) + (  # type: ignore[arg-type]
            f'<p class="hint">Place one mark for each: {escape(chips)}. '
            "Write the label next to each mark.</p>"
        )
        instruction = "Place one mark per item, then label it."
    else:
        body = _mcq_options(signifier)  # type: ignore[arg-type]
        instruction = ""

    instruction_markup = f'<p class="hint">{escape(instruction)}</p>' if instruction else ""

    return f"""
<section class="sheet sheet--landscape" data-sheet="signifier" data-kind="{kind}">
  <h2 class="sheet-title">{escape(signifier.title)}</h2>
  {instruction_markup}
  {body}
  <p class="sheet-foot">Story number: ______</p>
</section>
"""


def _story_card(definition: FrameworkDefinition, framework_name: str) -> str:
    """The A4 story card: prompt, ruled space, groups, anonymity line."""
    rules = "\n".join('<div class="rule"></div>' for _ in range(STORY_RULE_COUNT))

    groups = definition.capture_settings.respondent_groups
    if groups:
        group_rows = "\n".join(
            f'<li class="tick-row"><span class="tick-box" aria-hidden="true"></span>'
            f'<span class="sheet-label">{escape(group)}</span></li>'
            for group in groups
        )
        group_block = (
            '<div class="groups"><p class="hint">Which group are you in?</p>'
            f'<ul class="tick-list tick-list--inline">{group_rows}</ul></div>'
        )
    else:
        group_block = ""

    alt = definition.prompt_text_alt
    alt_block = f'<p class="prompt-alt">Or: {escape(alt)}</p>' if alt else ""

    return f"""
<section class="sheet" data-sheet="story-card">
  <p class="eyebrow">{escape(framework_name)}</p>
  <h2 class="sheet-title">{escape(definition.prompt_text)}</h2>
  {alt_block}
  <p class="sheet-foot">Story number: ______</p>
  <div class="rules">{rules}</div>
  {group_block}
  <p class="anonymity">{escape(definition.capture_settings.anonymity_text)}</p>
</section>
"""


def _facilitator_sheet(definition: FrameworkDefinition, framework_name: str) -> str:
    """Running instructions, materials, and the reconciliation grid."""
    signifiers = definition.signifiers_in_order()
    sheet_list = "\n".join(
        f"<li>{escape(signifier.title)} <span class='muted'>({kind})</span></li>"
        for kind, signifier in signifiers
    )

    reconciliation_rows = "\n".join(
        '<tr><td class="grid-cell"></td><td class="grid-cell"></td>'
        '<td class="grid-cell"></td><td class="grid-cell"></td></tr>'
        for _ in range(RECONCILIATION_ROW_COUNT)
    )

    return f"""
<section class="sheet" data-sheet="facilitator">
  <p class="eyebrow">Facilitator sheet — not for respondents</p>
  <h2 class="sheet-title">{escape(framework_name)}</h2>

  <h3 class="sheet-subtitle">Running the session</h3>
  <ol class="steps">
    <li>Hand every person one story card and one set of the
        {len(signifiers)} signifier sheet{"" if len(signifiers) == 1 else "s"}.</li>
    <li>Ask them to write the story first, in their own words. No names.</li>
    <li>Number each person's sheets with the same story number, so their
        marks stay together.</li>
    <li>Then ask them to mark each signifier sheet. There are no wrong marks.</li>
    <li>Collect everything before people leave. Count them against the grid below.</li>
    <li>Type the responses into Narrative Lens using paper batch entry.</li>
  </ol>

  <h3 class="sheet-subtitle">Materials</h3>
  <ul class="steps">
    <li>Story cards and signifier sheets, one set per person</li>
    <li>Pens, and sticky dots if you are marking the large sheets as a group</li>
    <li>An envelope or folder for collected sheets</li>
  </ul>

  <h3 class="sheet-subtitle">Sheets in this pack</h3>
  <ul class="steps">{sheet_list}</ul>

  <h3 class="sheet-subtitle">Reconciliation</h3>
  <p class="hint">Fill this in as you go, so nothing goes missing.</p>
  <table class="grid">
    <thead>
      <tr><th>Group / session</th><th>Handed out</th><th>Returned</th><th>Entered</th></tr>
    </thead>
    <tbody>{reconciliation_rows}</tbody>
  </table>
</section>
"""


#: Print CSS. ``page-break-after: always`` on every sheet is what makes the pack
#: come out one sheet per page (PRD §6 asserts these rules are present).
PRINT_CSS = """
:root { color-scheme: only light; }

* { box-sizing: border-box; }

body {
  margin: 0;
  background: #fff;
  color: #000;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 12pt;
  line-height: 1.5;
}

.pack-intro {
  max-width: 44rem;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  border-bottom: 1px solid #000;
}

.sheet {
  page-break-after: always;
  break-after: page;
  page-break-inside: avoid;
  break-inside: avoid;
  padding: 18mm 16mm;
  max-width: 210mm;
  margin: 0 auto;
  min-height: 250mm;
}

.sheet:last-of-type { page-break-after: auto; break-after: auto; }

.sheet--landscape { max-width: 297mm; min-height: 180mm; }

.eyebrow { font-size: 12pt; letter-spacing: 0.06em; text-transform: uppercase; margin: 0 0 6mm; }
.sheet-title { font-size: 22pt; line-height: 1.25; margin: 0 0 6mm; font-weight: 700; }
.sheet-subtitle { font-size: 14pt; margin: 8mm 0 3mm; }
.prompt-alt { font-size: 14pt; font-style: italic; margin: 0 0 6mm; }
.sheet-foot { font-size: 12pt; margin: 4mm 0; }
.hint { font-size: 14pt; margin: 0 0 5mm; }
.muted { color: #000; }

.rules { margin: 6mm 0; }
.rule { border-bottom: 1px solid #000; height: 11mm; }

.tick-list { list-style: none; margin: 0; padding: 0; }
.tick-list--inline { display: flex; flex-wrap: wrap; gap: 4mm 8mm; }
.tick-row { display: flex; align-items: center; gap: 3mm; margin: 0 0 4mm; }
.tick-box { display: inline-block; width: 7mm; height: 7mm; border: 1.5pt solid #000; }

.widget { display: block; width: 100%; height: auto; margin: 0 auto; }
.sheet-label { font-size: 16pt; fill: #000; font-family: Georgia, serif; }

.anonymity {
  font-size: 12pt;
  margin: 8mm 0 0;
  padding-top: 4mm;
  border-top: 1px solid #000;
}

.steps { font-size: 12pt; padding-left: 6mm; }
.steps li { margin: 0 0 2mm; }

.grid { width: 100%; border-collapse: collapse; margin-top: 4mm; }
.grid th, .grid td { border: 1pt solid #000; padding: 4mm 3mm; text-align: left; font-size: 12pt; }
.grid-cell { height: 12mm; }

@media print {
  .pack-intro { display: none; }
  .sheet { margin: 0; }
  @page { size: A4 portrait; margin: 0; }
}
"""


def render_paper_pack(
    definition: FrameworkDefinition,
    framework_name: str,
    version: int,
) -> str:
    """Render the whole pack as one self-contained, printable HTML page."""
    sheets = [_story_card(definition, framework_name)]
    sheets.extend(
        _signifier_sheet(kind, signifier)
        for kind, signifier in definition.signifiers_in_order()
    )
    sheets.append(_facilitator_sheet(definition, framework_name))

    title = f"Paper pack — {framework_name} (version {version})"
    sheet_count = len(sheets)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>{PRINT_CSS}</style>
</head>
<body>
<div class="pack-intro">
  <h1>{escape(title)}</h1>
  <p>This is {sheet_count} printed page{"" if sheet_count == 1 else "s"}: one story
     card, {len(definition.signifiers_in_order())} signifier
     sheet{"" if len(definition.signifiers_in_order()) == 1 else "s"}, and one
     facilitator sheet.</p>
  <p><strong>To print:</strong> use your browser's Print command, choose A4, and
     set margins to Default. To keep a copy, choose "Save as PDF" as the
     printer. This box does not print.</p>
</div>
{"".join(sheets)}
</body>
</html>
"""
