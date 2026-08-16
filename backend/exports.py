"""Exports: the dataset as CSV, and the Pattern Brief (PRD §1.7, §4).

Two rules govern this module.

**Constraint 3 — provenance on every record.** Every CSV row carries source_type,
entry_mode, input_method, source_file, source_locator, signified_by, validated_at
and the framework version, alongside the story itself. A row that left any of
those out would be a story you could not account for later.

**Constraint 13f — headlines state findings, not topics.** "Ops told most of the
stories" is a finding; "Respondent group breakdown" is a topic. So the brief is
built from templates filled with computed figures — every sentence is arithmetic
the reader could redo by hand. No language model writes a word of it
(constraint 11), and the templates are deliberately dull: they say what the
numbers say and stop, rather than reaching for a cause.

Constraint 9 survives the export: the rows carry hour-rounded times and no
identifier column, because there is no identifier column to carry.
"""

from __future__ import annotations

import csv
import datetime as dt
import io

from backend.framework_schema import FrameworkDefinition
from backend.models import Anecdote, Signification
from backend.patterns import PatternSet

#: A triad whose average placement puts this much weight on one corner is
#: leaning; below it, the stories do not agree enough to say so.
TRIAD_LEAN = 0.45

#: A dyad median this far from the midpoint is a lean rather than a split.
DYAD_LEAN = 0.10

#: A categorical view whose top bar holds at least this share is a finding worth
#: a sentence; below it the spread is the finding.
SHARE_LEAD = 0.40

#: Fewer stories than this and a "finding" is an anecdote about anecdotes.
MIN_FOR_FINDING = 3

PROVENANCE_COLUMNS = [
    "anecdote_id",
    "framework_id",
    "framework_name",
    "framework_version",
    "title",
    "text",
    "respondent_group",
    "created_at_hour",
    "status",
    "source_type",
    "entry_mode",
    "input_method",
    "source_file",
    "source_locator",
    "import_job_id",
    "signified_by",
    "validated_at",
    "lowest_ai_confidence",
]


def signifier_columns(definition: FrameworkDefinition) -> list[str]:
    """One column per answerable value, in the order respondents met them."""
    columns: list[str] = []
    for kind, signifier in definition.signifiers_in_order():
        if kind == "triad":
            columns.extend(f"{signifier.id}:{corner}" for corner in signifier.corners)
        elif kind == "dyad":
            columns.append(signifier.id)
        elif kind == "stones":
            for chip in signifier.chips:
                columns.append(f"{signifier.id}:{chip}:x")
                columns.append(f"{signifier.id}:{chip}:y")
        else:
            columns.append(signifier.id)
    return columns


def _stamp(moment: dt.datetime | None) -> str:
    return "" if moment is None else moment.isoformat(sep=" ", timespec="seconds")


def _placement_cells(
    definition: FrameworkDefinition, by_signifier: dict[str, dict]
) -> dict[str, str]:
    """One story's placements as flat cells, blank where it was skipped."""
    cells: dict[str, str] = {}
    for kind, signifier in definition.signifiers_in_order():
        value = by_signifier.get(signifier.id)
        if kind == "triad":
            for corner in signifier.corners:
                cells[f"{signifier.id}:{corner}"] = (
                    "" if value is None else str(value.get(corner, ""))
                )
        elif kind == "dyad":
            cells[signifier.id] = "" if value is None else str(value.get("value", ""))
        elif kind == "stones":
            placed = {}
            if value is not None:
                placed = {entry["label"]: entry for entry in value.get("placements", [])}
            for chip in signifier.chips:
                entry = placed.get(chip)
                cells[f"{signifier.id}:{chip}:x"] = "" if entry is None else str(entry["x"])
                cells[f"{signifier.id}:{chip}:y"] = "" if entry is None else str(entry["y"])
        else:
            cells[signifier.id] = (
                "" if value is None else "|".join(str(o) for o in value.get("selected", []))
            )
    return cells


def dataset_csv(
    definition: FrameworkDefinition,
    anecdotes: list[Anecdote],
    significations: list[Signification],
    framework_names: dict[int, tuple[str, int]],
) -> str:
    """The whole filtered dataset, one row per story, provenance intact.

    ``framework_names`` maps a framework id to its ``(name, version)`` so a
    mixed-version export says which wording each story actually answered — the
    single most important thing to know when reading two versions side by side.
    """
    by_anecdote: dict[int, list[Signification]] = {}
    for placement in significations:
        by_anecdote.setdefault(placement.anecdote_id, []).append(placement)

    columns = PROVENANCE_COLUMNS + signifier_columns(definition)
    buffer = io.StringIO()
    # Windows opens a .csv in Excel, which wants CRLF; newline="" keeps csv in
    # charge of line endings rather than the platform.
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\r\n")
    writer.writeheader()

    for anecdote in anecdotes:
        placements = by_anecdote.get(anecdote.id, [])
        name, version = framework_names.get(anecdote.framework_id, ("", 0))
        confidences = [p.ai_confidence for p in placements if p.ai_confidence is not None]
        validated = [p.validated_at for p in placements if p.validated_at is not None]

        row = {
            "anecdote_id": anecdote.id,
            "framework_id": anecdote.framework_id,
            "framework_name": name,
            "framework_version": version,
            "title": anecdote.title_auto or "",
            "text": anecdote.text,
            "respondent_group": anecdote.respondent_group or "",
            "created_at_hour": _stamp(anecdote.created_at_hour),
            "status": anecdote.status,
            "source_type": anecdote.source_type,
            "entry_mode": anecdote.entry_mode,
            "input_method": anecdote.input_method,
            "source_file": anecdote.source_file or "",
            "source_locator": anecdote.source_locator or "",
            "import_job_id": anecdote.import_job_id or "",
            # Usually one value; two when the operator moved some markers and
            # left others, which is exactly the case worth being able to see.
            "signified_by": "|".join(sorted({p.signified_by for p in placements})),
            "validated_at": _stamp(min(validated)) if validated else "",
            "lowest_ai_confidence": min(confidences) if confidences else "",
        }
        row.update(
            _placement_cells(
                definition, {p.signifier_id: p.value_json for p in placements}
            )
        )
        writer.writerow(row)

    return buffer.getvalue()


# --------------------------------------------------------------------------
# The Pattern Brief
# --------------------------------------------------------------------------


def _nearest_corner(chart) -> tuple[str, float] | None:
    """Which corner the average placement leans to, and by how much.

    Worked back from the points rather than kept alongside them, so the brief
    cannot disagree with the chart the reader is looking at.
    """
    if not chart.points:
        return None
    from backend.barycentric import to_barycentric

    weights = [to_barycentric((point.x, point.y)) for point in chart.points]
    means = [sum(w[index] for w in weights) / len(weights) for index in range(3)]
    best = max(range(3), key=lambda index: means[index])
    return chart.corners[best], means[best]


def _triad_finding(chart) -> str | None:
    lean = _nearest_corner(chart)
    if lean is None or chart.answered < MIN_FOR_FINDING:
        return None
    corner, weight = lean
    if weight >= TRIAD_LEAN:
        return (
            f"On *{chart.title}*, stories pull towards **{corner}** "
            f"({round(weight * 100)}% of the average placement, {chart.answered} stories)."
        )
    return (
        f"On *{chart.title}*, stories spread across all three corners with no "
        f"clear pull ({chart.answered} stories)."
    )


def _dyad_finding(chart) -> str | None:
    if chart.median is None or chart.answered < MIN_FOR_FINDING:
        return None
    distance = chart.median - 0.5
    if abs(distance) < DYAD_LEAN:
        return (
            f"On *{chart.title}*, stories sit near the middle between "
            f"{chart.left} and {chart.right} ({chart.answered} stories)."
        )
    pole = chart.right if distance > 0 else chart.left
    return (
        f"On *{chart.title}*, stories lean towards **{pole}** "
        f"(median {chart.median:.2f}, {chart.answered} stories)."
    )


def _join(labels: list[str]) -> str:
    """Plain-English list: 'a', 'a and b', 'a, b and c'."""
    if len(labels) <= 1:
        return "".join(labels)
    return f"{', '.join(labels[:-1])} and {labels[-1]}"


def _category_finding(chart, noun: str) -> str | None:
    bars = [bar for bar in chart.bars if bar.count]
    if not bars or chart.answered < MIN_FOR_FINDING:
        return None
    top = bars[0]
    if len(bars) > 1 and top.count == bars[1].count:
        tied = _join([f"**{bar.label}**" for bar in bars if bar.count == top.count])
        return f"{noun} splits evenly between {tied} ({top.count} stories each)."
    if top.share >= SHARE_LEAD:
        return (
            f"{noun}: **{top.label}** leads with {round(top.share * 100)}% "
            f"({top.count} of {chart.answered})."
        )
    return (
        f"{noun} is spread thin — the largest single answer, **{top.label}**, is "
        f"only {round(top.share * 100)}% ({top.count} of {chart.answered})."
    )


def findings(patterns: PatternSet) -> list[str]:
    """Every sentence the brief can honestly say, in reading order."""
    lines: list[str] = []
    for chart in patterns.triads:
        line = _triad_finding(chart)
        if line:
            lines.append(line)
    for chart in patterns.dyads:
        line = _dyad_finding(chart)
        if line:
            lines.append(line)
    for chart in patterns.mcqs:
        line = _category_finding(chart, f"On *{chart.title}*, the answer")
        if line:
            lines.append(line)
    for chart in patterns.demographics:
        line = _category_finding(chart, chart.title)
        if line:
            lines.append(line)
    return lines


def _headlines(patterns: PatternSet) -> list[str]:
    """Finding-first sentences, short enough to be a title (constraint 13f).

    Written separately from the bullets rather than derived from them. A bullet
    starts by naming the question — right in a list, wrong as a headline, where
    "On *What drove this?*, stories pull towards Speed" reads as a topic with a
    finding tacked on. A headline has to lead with what was found.
    """
    lines: list[str] = []

    for chart in patterns.triads:
        lean = _nearest_corner(chart)
        if lean is None or chart.answered < MIN_FOR_FINDING:
            continue
        corner, weight = lean
        if weight >= TRIAD_LEAN:
            lines.append(f"Stories pull towards {corner} on “{chart.title}”")

    for chart in patterns.dyads:
        if chart.median is None or chart.answered < MIN_FOR_FINDING:
            continue
        distance = chart.median - 0.5
        if abs(distance) >= DYAD_LEAN:
            pole = chart.right if distance > 0 else chart.left
            lines.append(f"Stories lean towards {pole} on “{chart.title}”")

    for chart in patterns.mcqs:
        bars = [bar for bar in chart.bars if bar.count]
        if not bars or chart.answered < MIN_FOR_FINDING:
            continue
        if bars[0].share >= SHARE_LEAD and (
            len(bars) == 1 or bars[0].count > bars[1].count
        ):
            lines.append(
                f"Most stories answer “{chart.title}” with {bars[0].label} "
                f"({round(bars[0].share * 100)}%)"
            )

    groups = next(
        (chart for chart in patterns.demographics if chart.id == "respondent_group"), None
    )
    if groups and groups.answered >= MIN_FOR_FINDING:
        bars = [bar for bar in groups.bars if bar.count]
        if bars and bars[0].share >= SHARE_LEAD and (
            len(bars) == 1 or bars[0].count > bars[1].count
        ):
            lines.append(
                f"{bars[0].label} told most of the stories "
                f"({bars[0].count} of {groups.answered})"
            )

    return lines


def headline(patterns: PatternSet) -> str:
    """One sentence that is a finding, never a topic (constraint 13f)."""
    if patterns.total == 0:
        return "No stories match these filters yet"
    if patterns.total < MIN_FOR_FINDING:
        return (
            f"Only {patterns.total} "
            f"{'story' if patterns.total == 1 else 'stories'} match these filters — "
            "too few to read a pattern from"
        )
    found = _headlines(patterns)
    if not found:
        return f"{patterns.total} stories, and no single answer stands out yet"
    # The first is the strongest signifier in respondent order — the order the
    # operator themselves put the questions in.
    return found[0]


def pattern_brief(patterns: PatternSet, generated_at: dt.datetime) -> str:
    """The analyst's Pattern Brief as markdown.

    Deliberately short. It states what the figures say, records the filters and
    versions the figures came from, and repeats the caveat that reading a
    landscape is abductive rather than causal (constraint 12).
    """
    lines: list[str] = []
    lines.append(f"# {headline(patterns)}")
    lines.append("")
    lines.append(
        f"*{patterns.framework_name} — version {patterns.framework_version} · "
        f"{patterns.total} {'story' if patterns.total == 1 else 'stories'} · "
        f"prepared {generated_at:%d %B %Y}*"
    )
    lines.append("")

    if patterns.filters:
        shown = ", ".join(
            f"{field.replace('_', ' ')} = {value}"
            for field, value in sorted(patterns.filters.items())
        )
        lines.append(f"**Filtered to:** {shown}")
        lines.append("")

    if patterns.mixed and patterns.versions:
        spread = ", ".join(
            f"version {entry.version} ({entry.count})" for entry in patterns.versions
        )
        lines.append(
            f"**This view mixes framework versions:** {spread}. Stories answered "
            "different wording, so read comparisons between versions with care."
        )
        lines.append("")

    lines.append("## What the figures say")
    lines.append("")
    said = findings(patterns)
    if said:
        lines.extend(f"- {line}" for line in said)
    else:
        lines.append("- Not enough answers yet to say anything worth writing down.")
    lines.append("")

    lines.append("## How to read this")
    lines.append("")
    lines.append(
        "- Every figure above is counted from stories a person validated. "
        "Nothing here was written or interpreted by AI."
    )
    lines.append(
        "- Triads are closure-constrained: three weights that must sum to one, "
        "so a rise on one corner is a fall on another. Read the shape, not the "
        "cause."
    )
    lines.append(
        "- Patterns point at where to look next. They are not evidence of what "
        "caused what."
    )
    lines.append("")
    return "\n".join(lines)
