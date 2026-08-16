# Narrative Lens — Latest

**Updated:** 2026-08-16
**Phase:** 8 of 9 complete — the Narrative Landscape
**Status:** green (617 tests passing · ruff clean · eslint 0 · builds · smoke test end-to-end)

---

## Where things stand

The Patterns tab now opens on the thing the whole app was built to show: the
**Narrative Landscape**.

- **A terrain you can turn.** Every story that answered a triangle is a point
  inside it; the landscape is how thickly those points lie. Drag it to look from
  another angle, or use the arrow keys. One button puts it back where it
  started.
- **The peaks are labelled with what they hold** — "4 near Speed", not a colour
  key. Click one and you get exactly the stories sitting under it. Not roughly
  those stories: exactly them, because every story sits in one square of the
  grid and a peak is the squares around it.
- **A contour twin, one tap away.** The same landscape seen from directly above,
  as nested rings with every story as a dot. Use it when you want to measure
  rather than to look — and it is what a saved picture gives you, in black on
  white, because a contour can be read off a printed page.
- **Side by side.** Split the landscape by who told the stories, or how they
  arrived, and you get a panel each — drawn to one shared height so comparing
  them by eye is honest.
- **A 3D Explorer**, one level down, plotting any three answers against each
  other, with an optional overlay of statistical clusters. Those clusters always
  carry their label: *statistical clusters — descriptive only*. They describe
  where answers sit and say nothing about why.
- **Notes on how to read it**, under the picture: that height is thickness and
  not importance, that triangles are closure-constrained so a rise on one corner
  is a fall on another, and that a cluster tells you where to look next rather
  than what caused what.

**The landscape maths is pinned and tested.** Scott-bandwidth density on a fixed
64×64 grid, no seed and no sampling, so the same stories always give the same
terrain. The peaks on the twenty-story set are held to within a fiftieth of the
triangle's width, and the surface and the contour are not two calculations that
agree — they are one calculation looked at twice, which is a test.

**And there is now one test that runs the whole app end to end**: write the
questions, collect stories four ways, import a spreadsheet through both AI
stages, work the queue, then check that the patterns, the landscape, the
Explorer, the CSV and the brief all agree about which stories exist and what
they say. That is the test that catches the joins between phases rather than the
phases themselves.

**Checked in a real browser** at 1440px and 375px: it opens on the Landscape,
the terrain paints and turns, the camera resets, a peak lists its four stories,
the contour draws 557 rings and all twenty dots, a split gives three panels, the
Explorer plots and clusters, and the snapshot downloads. Three layout bugs were
found this way and fixed — see PROGRESS.md "Fixed".

**Still not verified:** the `.bat` launcher has never run on Windows, because
this build runs on Linux. It also does not yet build the frontend — you need to
run `npm run build` in `frontend/` once before the app can serve it.

## Next step

**Phase 9 — Closing the loop + operator hardening + critique pass.** The last
one. It adds "What We Heard" for respondents with small-group suppression
(nothing under five people is shown), a pass over every error message in plain
English, empty states everywhere, the README written for you rather than for a
developer — including one-pagers on printing a paper pack and reading a
landscape — and a design critique pass: remove one element per view, confirm the
landscape is the single boldest thing on screen, and check every view in
grayscale.

Its gate is the full regression plus a manual smoke: one phone over Tailscale,
one xlsx through the pipeline, and one paper pack printed to PDF.

## How to resume

1. Read `CLAUDE.md`, `PRD_Narrative-Lens_v1.3_20260814.md`, `PROGRESS.md`, and
   this file.
2. Run `./run_checks.sh` to confirm the base is green **before** changing
   anything. If it is red, fix that first and say so — never build new work on a
   red base.
3. Build Phase 9 exactly per PRD §6, including its tests and gate.
4. Run the full regression list, show the gate output, commit with the phase's
   commit message, and update `PROGRESS.md` and `LATEST.md`.

**Four traps worth knowing.** Kill any server you started by hand before
starting another — a stale one once quietly served an out-of-date app, which
looked exactly like a broken feature. The CSS is global, so check a new class
name is not already taken in another stylesheet. SVG and canvas both clip text
silently rather than wrapping it, so any label that can run long needs measuring
against its widest case. And time an endpoint with `median_ms` from
`tests/conftest.py`, never with a single sample — this machine is shared, and one
sample measures the neighbours.

## Running it yourself

| What you want | What to do |
|---|---|
| First time only | In `frontend/`, run `npm install`, then `npm run build` |
| Start the app | Double-click `Start Narrative Lens.bat` |
| Write the questions | The **Studio** tab |
| Enter a story yourself | **Capture & Links** → "One at a time" |
| Type up returned paper | **Capture & Links** → "From paper" |
| Collect from phones | **Capture & Links** → "Links & QR" → open a link → **QR poster** → print it |
| Stop collecting from a poster | **Links & QR** → **Close link** (permanent) |
| Run a workshop machine | **Capture & Links** → "Kiosk" |
| Bring in a file of stories | **Import & Validate** → choose a file → **Organise** → check it → **Confirm** → **Mark up these stories** |
| Check what the AI suggested | **Import & Validate** → **Waiting for you** |
| See where stories cluster | The **Patterns** tab — it opens on the landscape |
| Read the landscape precisely | Patterns → **Contour** |
| See the stories under a peak | Patterns → click a peak under the picture |
| Compare two groups | Patterns → **Side by side** in the rail |
| Save a picture for a document | Patterns → **Save the contour as a picture** |
| Get the data out | Patterns → **Download the stories (CSV)** |
| Get a written summary | Patterns → **Download the Pattern Brief** |
| Print a paper pack | Studio → **Paper pack for version 1**, then Print → Save as PDF |
| Check everything still works | Run `./run_checks.sh` — you want `ALL CHECKS PASSED` |
| Stop the app | Close the small "Narrative Lens server" window |
