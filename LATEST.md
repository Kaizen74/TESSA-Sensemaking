# Narrative Lens — Latest

**Updated:** 2026-08-17
**Phase:** 9 of 9 complete — the build is finished
**Status:** green (1025 tests passing · ruff clean · eslint 0 · builds · smoke test end-to-end)

---

## Where things stand

**All nine phases are done.** The app writes the questions, collects the stories
five ways, brings in files you already have, keeps every AI suggestion waiting
for a human, draws the landscape, and now closes the loop by handing something
back to the people who told the stories.

Phase 9 added the last of it, and hardened the rest for the person who has to
use it:

- **"What we heard."** A summary safe to give back to the room: no story text,
  nothing about how a story arrived, and nothing that fewer than five people
  said. The floor is applied to every slice, not to the total, and it is applied
  *after* any filter — a filtered view is a smaller room, which is exactly when
  it matters. When something is withheld, the page says so; a reader who cannot
  see that something is missing reads the rest as the whole.
- **Every error now speaks English.** The app's own refusals already did. What
  changed is everything else: a mistyped address, a request the page malformed,
  a fault in the app itself — all of them now leave by the same door, in the one
  shape the PRD names, as a sentence with something to do about it. There is no
  path left that answers with "Internal Server Error" or a validator's field
  dump. A test reads every message in the backend out of the source and holds it
  to the rule, so the next one written in a hurry cannot slip through.
- **Every empty screen tells you what to do next**, and the app says "question
  set" everywhere it used to say "framework" in one place and not the other.
- **A README written for you** rather than for a developer, with two one-pagers:
  printing a paper pack, and reading a landscape.
- **A critique pass over every view**, with one element removed from each: a
  dead "coming soon" branch, a schema path in the edit log (now the Studio's own
  words), a row of buttons offering one choice, and a chart that could only ever
  say 100%.

**Checked in a real browser, at 1440px and 375px, and again in grayscale.** The
landscape is the single boldest thing on the Patterns page at both widths. The
contour, the supporting charts and the Explorer all survive being drained of
colour, because length, position and direct labels carry the meaning. One real
bug came out of the grayscale pass and three out of the browser pass — see
PROGRESS.md "Fixed".

**The manual smoke the PRD asks for.** A two-sheet `workshop.xlsx` went through
the whole machine over HTTP — upload, the stage gate refusing to skip a step,
Organise, the mapping, a reconciliation that balanced at five rows, Stage B, four
stories queued, then accept, accept, correct and reject — and the patterns, the
CSV and "What we heard" all agreed afterwards about which five stories exist. The
paper pack printed to a real A4 PDF from Chromium: story card with the verbatim
anonymity line, one sheet per question, facilitator sheet with the reconciliation
grid, and every colour on the page measured as black on white.

**Still not verified, and it should be said plainly:**

- **A phone over Tailscale.** This build has one machine and no second device.
  The respondent's wizard was exercised at 375px in a browser, which is not the
  same as a handset on the mesh.
- **The `.bat` launcher on Windows.** It has been read carefully and fixed
  twice; it has never been run. Its first real run belongs to the operator.
- The frontend must be built once (`npm run build` in `frontend/`) before the
  app can serve its own pages. The launcher now says so plainly instead of
  starting into a blank screen.

## Next step

There is no next phase. What is left is real use: run a session, and let what
breaks decide what gets built. PRD §1 scope item 6 — the story browser, with
full-text search, tags and stars — was never assigned a phase and is the obvious
first candidate for a v2 if it turns out to be wanted.

## How to resume

1. Read `CLAUDE.md`, `PRD_Narrative-Lens_v1.3_20260814.md`, `PROGRESS.md`, and
   this file.
2. Run `./run_checks.sh` to confirm the base is green **before** changing
   anything. If it is red, fix that first and say so — never build new work on a
   red base.
3. Anything new is beyond v1.3. Decide with the operator what it is worth before
   building it, and record the decision in `PROGRESS.md` under "Decisions".

**Five traps worth knowing.** Kill any server you started by hand before
starting another — a stale one once quietly served an out-of-date app, which
looked exactly like a broken feature. The CSS is global, so check a new class
name is not already taken in another stylesheet. SVG and canvas both clip text
silently rather than wrapping it, and a canvas stretched to fit also shrinks its
own text below the legibility floor — measure any label against its widest case
*and* its narrowest screen. Time an endpoint with `median_ms` from
`tests/conftest.py`, never with a single sample; this machine is shared, and one
sample measures the neighbours. And JSX drops the line break between an element
and the text after it, which silently runs two words together.

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
| Give something back to the room | Patterns → **Download "What we heard"** |
| Print a paper pack | Studio → **Paper pack for version 1**, then Print → Save as PDF |
| Check everything still works | Run `./run_checks.sh` — you want `ALL CHECKS PASSED` |
| Stop the app | Close the small "Narrative Lens server" window |
