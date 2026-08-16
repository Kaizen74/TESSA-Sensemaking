# Narrative Lens — Latest

**Updated:** 2026-08-16
**Phase:** 6 of 9 complete — Stage B + validation queue
**Status:** green (493 tests passing · ruff clean · eslint 0 · builds · smoke test end-to-end)

---

## Where things stand

The import pipeline now runs end to end. A file of stories goes in, the AI
suggests where each story sits on your questions, and every one of those
suggestions waits for you before it counts as data.

- **The AI marks up, you decide.** After you confirm what a file contains, one
  button asks the AI where each story sits on your triads, dyads, stones and
  multiple-choice questions. It reads twenty stories at a time.
- **Nothing it suggests is your data yet.** Every marked-up story lands in
  **Waiting for you**, and stays there until you say so — however sure the
  suggestion looked. There is no "accept all", on purpose.
- **You see what it saw.** Each story is shown whole, with the suggestions drawn
  on the same triangles and sliders a respondent would have used, and how sure
  the AI was next to each one. Less certain than 70% is flagged amber; it waits
  in exactly the same queue either way.
- **Three answers, and the record says which you gave.** *That looks right*
  keeps the placements and notes that you agreed. *Change the answers* hands you
  the same widgets to move yourself — and only the markers you actually move are
  recorded as your judgement; the ones you leave keep saying the AI made them.
  *Not a usable story* sets it aside; it stays on file so the import can be
  audited, and it never counts.
- **A file finishes when its queue empties**, not when the AI stops. That is the
  last step of the pipeline, and only a person can reach it.

**The promise that nothing slips past you is now tested two ways.** A file is
driven through both AI stages and the data is then swept: nothing is in it. Every
other endpoint is tried against those waiting stories and none of them moves one.
And structurally, there are exactly two places in the whole app that can mark a
story as data — typing one in yourself, and this queue — with a test that fails
if a third ever appears.

**Checked in a real browser** at laptop and phone width: a workbook driven from
upload all the way into the queue, one story corrected on the live widgets, one
accepted, one set aside, and the file reaching "finished" as the queue emptied.
A look in the database afterwards confirmed the corrected marker stored as
yours and the untouched ones still the AI's. Three bugs were found this way and
fixed — see PROGRESS.md "Fixed".

**Still not verified:** the `.bat` launcher has never run on Windows, because
this build runs on Linux. It also does not yet build the frontend — you need to
run `npm run build` in `frontend/` once before the app can serve it.

## Next step

**Phase 7 — Live AI + supporting charts + exports.** See `PROGRESS.md` for the
gate. It switches both AI stages from their practice data to the real Claude
service, builds the supporting charts to the §5b grammar (sorted horizontal
bars, direct labels, quiet weight), adds the filters and the version chip, and
produces the CSV export and the Pattern Brief. It also introduces the first
golden baseline, `patterns_20_anecdotes.json`, which must stay byte-identical
from then on.

## How to resume

1. Read `CLAUDE.md`, `PRD_Narrative-Lens_v1.3_20260814.md`, `PROGRESS.md`, and
   this file.
2. Run `./run_checks.sh` to confirm the base is green **before** changing
   anything. If it is red, fix that first and say so — never build new work on a
   red base.
3. Build Phase 7 exactly per PRD §6, including its tests and gate.
4. Run the full regression list, show the gate output, commit with the phase's
   commit message, and update `PROGRESS.md` and `LATEST.md`.

**Two traps worth knowing.** If you start the server by hand to poke at the app,
kill the old one first and check the port is actually free — a stale server once
quietly served an out-of-date app, which looked exactly like a broken feature.
And the CSS is global: before naming a new class, check the name is not already
taken in another stylesheet. That cost an afternoon in Phase 6.

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
| Print a paper pack | Studio → **Paper pack for version 1**, then Print → Save as PDF |
| Check everything still works | Run `./run_checks.sh` — you want `ALL CHECKS PASSED` |
| Stop the app | Close the small "Narrative Lens server" window |
