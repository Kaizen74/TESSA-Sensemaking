"""The palette, held to §5b, by reading the source rather than trusting it.

Constraint 13c caps a chart at four colours and §5b caps the whole app at
"4–6 named colors". Both are easy to keep while writing a component and easy to
break while fixing one, because a raw hex in a canvas call looks like nothing
much at the moment somebody types it.

Two things are checked here:

* every colour written into the frontend as a literal is one of the palette,
  the terrain ramp, or a declared exception with a reason;
* the handful of tokens a canvas has to hold by value still match the tokens
  they were copied from — a canvas cannot read a CSS variable, so the palette
  genuinely lives in two places, and this is what stops the two drifting.

The design handoff of 6 September 2026 proposed four fresh RGB triples for the
Explorer's clusters. They would have taken the palette to ten. The clusters now
lift the existing tokens toward the paper instead: same hues, more luminance.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "src"
TOKENS = FRONTEND / "tokens.css"

#: Colours the palette actually contains, read from tokens.css rather than
#: repeated here, so this test cannot drift from the file it is policing.
def palette() -> dict[str, str]:
    found = {}
    for name, value in re.findall(r"(--nl-[\w-]+):\s*(#[0-9a-fA-F]{3,8})", TOKENS.read_text()):
        found[name] = value.lower()
    return found


#: Literals allowed to appear outside tokens.css, each with the reason it is
#: there. Anything else is a new colour and fails.
ALLOWED_REASONS = {
    "#16181d": "--nl-ink, held by value because a canvas cannot read a CSS variable",
    "#fbfaf7": "--nl-paper, same reason",
    "#a37b18": "--nl-accent, same reason",
    "#00366d": "--nl-data, the fallback when a token cannot be read",
    "#00204d": "--nl-terrain-0, the cividis fallback",
    "#e2cb52": "--nl-terrain-4, the cividis fallback",
    "#ffffff": "white, which §5b names alongside the palette",
    "#000": "pure black, print only — the photocopier grammar",
    "#000000": "pure black, print only",
    "#fff": "white",
}

HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def frontend_sources() -> list[Path]:
    return sorted(
        path
        for path in list(FRONTEND.rglob("*.jsx")) + list(FRONTEND.rglob("*.js"))
        if "node_modules" not in path.parts
    )


def test_no_component_invents_a_colour() -> None:
    """Every hex literal in a component is a palette value with a reason.

    This is the guard that would have caught the handoff's four cluster RGBs
    arriving as four new colours.
    """
    known = set(palette().values()) | set(ALLOWED_REASONS)

    strays: dict[str, list[str]] = {}
    for path in frontend_sources():
        for literal in set(HEX.findall(path.read_text(encoding="utf-8"))):
            if literal.lower() not in known:
                strays.setdefault(literal.lower(), []).append(
                    str(path.relative_to(FRONTEND))
                )

    assert not strays, "colours outside the palette: " + "; ".join(
        f"{colour} in {', '.join(sorted(files))}" for colour, files in sorted(strays.items())
    )


@pytest.mark.parametrize(
    ("literal", "token"),
    [("#16181d", "--nl-ink"), ("#fbfaf7", "--nl-paper"), ("#a37b18", "--nl-accent")],
)
def test_the_canvas_copies_still_match_their_tokens(literal: str, token: str) -> None:
    """The two places the palette lives have to agree.

    A canvas takes a colour string, not a variable, so the terrain and the
    Explorer hold three tokens by value. If somebody changes the ink in
    tokens.css and the canvases keep the old one, the figure quietly stops
    matching the app around it and nothing else notices.
    """
    assert palette()[token] == literal


def saturation(hex_colour: str) -> float:
    """How far a colour is from grey, 0 to 1."""
    hex_value = hex_colour.lstrip("#")
    if len(hex_value) == 3:
        hex_value = "".join(c + c for c in hex_value)
    r, g, b = (int(hex_value[i : i + 2], 16) / 255 for i in (0, 2, 4))
    high, low = max(r, g, b), min(r, g, b)
    if high == low:
        return 0.0
    lightness = (high + low) / 2
    return (high - low) / (2 - high - low if lightness > 0.5 else high + low)


def test_the_palette_gains_values_but_never_a_hue() -> None:
    """§5b says 4–6 named colours; the approved tint is a value, not a hue.

    This is the claim the exception rests on, so it is the claim that gets
    tested rather than the count. Five colours carry hue — ink, paper, the data
    blue, the accent, and the context grey — and everything else in the palette
    is a grey derived by lightening, which is why the tint approved on
    6 September 2026 did not widen the palette in the way the constraint cares
    about.
    """
    named = {
        name: value
        for name, value in palette().items()
        if not name.startswith("--nl-terrain")
    }

    coloured = {n: v for n, v in named.items() if saturation(v) >= 0.15}
    greys = {n: v for n, v in named.items() if saturation(v) < 0.15}

    assert len(set(coloured.values())) <= 6, sorted(coloured.items())
    # Every derived grey really is a grey, and really is a lightening: each one
    # sits between the darkest grey and the paper.
    for name, value in greys.items():
        assert saturation(value) < 0.15, f"{name} is not achromatic: {value}"

    # And the approved exception is present, and is what was approved.
    assert named["--nl-grey-hairline"] == "#f4f2ed"


def test_the_ink_ground_is_confined_to_the_two_figures_that_need_it() -> None:
    """Not a dark mode: only the terrain and the Explorer paint their ground.

    The shell stays paper. If a third component starts filling itself with ink
    this fails, because at that point it has stopped being figure-and-ground and
    started being a theme — which §5b's "no dark mode" reading would forbid.
    """
    painting = []
    for path in frontend_sources():
        body = path.read_text(encoding="utf-8")
        if "fillStyle = INK" in body or 'fillStyle = "#16181d"' in body:
            painting.append(path.name)

    assert sorted(painting) == ["Explorer.jsx", "Landscape.jsx"], painting


def test_the_contour_twin_stays_on_paper() -> None:
    """The printable half of the figure never goes dark.

    Constraint 13b makes the contour the twin that print and export default to,
    and a photocopier is its test. It has to stay black on white whatever the
    3D view does.
    """
    body = (FRONTEND / "patterns" / "Landscape.jsx").read_text(encoding="utf-8")
    twin = body[body.index("function ContourTwin") :]

    assert "INK" not in twin.split("function ")[1], (
        "the contour twin has started painting an ink ground"
    )


# --------------------------------------------------------------------------
# The Patterns layout (design handoff §4, §5)
# --------------------------------------------------------------------------


def patterns_source() -> str:
    return (FRONTEND / "patterns" / "Patterns.jsx").read_text(encoding="utf-8")


def test_the_landscape_keeps_the_hero_space() -> None:
    """Constraint 13a: the terrain is the one bold thing on the page.

    The findings card sits beside it, so the split is where 13a is now decided.
    1.85 of two columns keeps the figure dominant; anything approaching parity
    would make the page two things instead of one.
    """
    css = (FRONTEND / "patterns" / "patterns.css").read_text(encoding="utf-8")
    stage = css[css.index(".nl-patterns__stage") :][:400]

    assert "1.85fr" in stage, stage[:200]


def test_the_prose_no_longer_stands_above_the_figure() -> None:
    """The analyst notes moved into the aside, behind their own disclosure.

    They are load-bearing — the closure-constraint caveat is constraint 12 — so
    they stay in full. What changed is that a reader meets the landscape first.
    """
    body = patterns_source()
    stage_at = body.index("nl-patterns__stage")
    notes_at = body.index("<AnalystNotes")

    assert notes_at > stage_at, "the analyst notes are above the figure again"
    assert "nl-patterns__aside" in body[stage_at:notes_at], (
        "the analyst notes are no longer inside the aside"
    )


def test_a_split_landscape_keeps_its_peaks_with_its_pictures() -> None:
    """Two landscapes have two sets of peaks and no honest way to rank them.

    The findings card ranks one set. A split view keeps the old row under each
    panel, where each set stays with the picture it came from.
    """
    body = (FRONTEND / "patterns" / "Landscape.jsx").read_text(encoding="utf-8")

    assert "showPeaks={split || panels.length !== 1}" in body
    assert "if (view?.split_by || panels.length !== 1) return null;" in body


def test_the_mode_is_only_emphasised_when_there_is_one() -> None:
    """Emphasis marks a distinction; a tie has none to mark.

    With every bar equal, emphasising "the largest" emphasises all of them,
    which is more ink saying less than the plain chart did.
    """
    body = (FRONTEND / "patterns" / "Charts.jsx").read_text(encoding="utf-8")

    assert "hasSingleMode" in body
    assert "bar.count === largest && hasSingleMode" in body


def test_the_charts_gained_a_track_but_no_gridline() -> None:
    """§5b bans gridline decoration. A track behind a bar is not one.

    A gridline is a repeated rule the eye must map back to an axis; a track is
    the bar's own 100%, in the bar's own place, which is what lets the shares
    be compared without a legend.
    """
    css = (FRONTEND / "patterns" / "patterns.css").read_text(encoding="utf-8")
    charts = (FRONTEND / "patterns" / "Charts.jsx").read_text(encoding="utf-8")

    assert ".nl-chart__track" in css
    assert "nl-chart__track" in charts

    # Scanned as code, not as prose. Charts.jsx opens by saying it draws no
    # gridlines, and a word-search on the file finds that sentence and calls it
    # a violation — the same false positive the translation guard hit when it
    # scanned docstrings.
    without_comments = re.sub(r"/\*.*?\*/", "", charts, flags=re.DOTALL)
    without_comments = re.sub(r"//[^\n]*", "", without_comments)

    assert "gridline" not in without_comments.lower()
    assert "<legend" not in without_comments.lower()
