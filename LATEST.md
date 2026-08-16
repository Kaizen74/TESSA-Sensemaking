# Narrative Lens — Latest

**Updated:** 2026-08-16
**Phase:** 7 of 9 complete — Live AI, supporting charts, exports
**Status:** green (552 tests passing · ruff clean · eslint 0 · builds · smoke test end-to-end)

---

## Where things stand

The app now reads as well as collects. There is a **Patterns** tab, and it shows
you what the stories you have validated actually add up to.

- **Charts you can check by eye.** Every breakdown is horizontal bars sorted
  biggest first, labelled where the bar ends, starting at zero. Dyads show every
  mark on the line and the distribution they make. Stones show every chip on its
  canvas. Nothing depends on colour, so it all still reads printed in grey.
- **A slim filter rail.** Narrow to one group, one way of writing a story down,
  or one place it came from, and every chart on the page narrows with it.
- **Two versions are never quietly pooled.** If you changed the meaning of a
  question, the old stories answered the old wording — so they stay separate
  until you tick the box that says otherwise, and then a chip tells you which
  versions you are looking at and how many stories each contributed.
- **Two exports, matching what is on screen.** A CSV of the stories with their
  full provenance — where each came from, who placed the markers, when it was
  validated, which version it answered — and a **Pattern Brief** in plain
  markdown. The brief's headline is a finding ("Stories pull towards Speed on
  'What drove this?'"), never a topic, and every sentence in it is arithmetic you
  could redo by hand.
- **Nothing on this page came from AI.** The figures are counted locally by
  ordinary code, and a test fails if any AI module ever becomes reachable from
  the pattern path.

**The AI now has a real path to Claude, and a tested one.** Both stages call the
service with the model and settings the spec pins, ask for strict JSON, and get
exactly one repair attempt if the reply cannot be read before failing in a
sentence. And being offline is an ordinary state: with no connection, Analyse
says so plainly while capture, patterns, exports and paper packs all keep
working.

**The first golden baseline is in.** Twenty stories with placements fixed by
arithmetic produce an aggregate stored character for character in
`tests/golden/patterns_20_anecdotes.json`. From now on any change to a rounding
rule, a sort, or a histogram bin fails that test and shows exactly what moved.

**Checked in a real browser** at laptop and phone width, on both framework
versions: the charts, the sorting, a filter narrowing everything at once, the
version chip appearing only when asked for, and both export links carrying the
current filters. Three label-clipping bugs were found this way and fixed — see
PROGRESS.md "Fixed".

**Still not verified:** the `.bat` launcher has never run on Windows, because
this build runs on Linux. It also does not yet build the frontend — you need to
run `npm run build` in `frontend/` once before the app can serve it.

## Next step

**Phase 8 — Landscape suite (primary view).** See `PROGRESS.md` for the gate.
This is the big one: the Narrative Landscape as the Patterns tab's default view
— rotatable density terrain per triad with directly-labelled peaks, its 2D
contour twin from the identical grid, region→stories drill, filter split, the 3D
Explorer, the k-means overlay, analyst notes, and PNG snapshot defaulting to the
contour. It adds the second golden: landscape peaks stable to ±0.02.

The supporting charts built this phase are deliberately quiet so the landscape
can be the one bold thing on the page when it arrives above them.

## How to resume

1. Read `CLAUDE.md`, `PRD_Narrative-Lens_v1.3_20260814.md`, `PROGRESS.md`, and
   this file.
2. Run `./run_checks.sh` to confirm the base is green **before** changing
   anything. If it is red, fix that first and say so — never build new work on a
   red base.
3. Build Phase 8 exactly per PRD §6, including its tests and gate.
4. Run the full regression list, show the gate output, commit with the phase's
   commit message, and update `PROGRESS.md` and `LATEST.md`.

**Three traps worth knowing.** If you start the server by hand to poke at the
app, kill the old one first and check the port is actually free — a stale server
once quietly served an out-of-date app, which looked exactly like a broken
feature. The CSS is global: before naming a new class, check the name is not
already taken in another stylesheet. And SVG clips text silently rather than
wrapping it, so any label that can run long needs measuring against its widest
case, not its usual one.

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
| See what the stories add up to | The **Patterns** tab |
| Get the data out | Patterns → **Download the stories (CSV)** |
| Get a written summary | Patterns → **Download the Pattern Brief** |
| Print a paper pack | Studio → **Paper pack for version 1**, then Print → Save as PDF |
| Check everything still works | Run `./run_checks.sh` — you want `ALL CHECKS PASSED` |
| Stop the app | Close the small "Narrative Lens server" window |
