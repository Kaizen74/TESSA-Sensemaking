# Narrative Lens — Latest

**Updated:** 2026-08-17
**Phase:** 9 of 9 complete, plus a completeness pass against PRD §1
**Status:** green (1081 tests passing · ruff clean · eslint 0 · builds · smoke test end-to-end)

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

**The end-to-end run found a real bug, which is what it is for.** A wording fix
that renames a triangle's corner — "Care" to "Carefulness", exactly the edit the
guardrail is built to bless — left every stored answer keyed by a word the
question set no longer had. The Patterns tab failed outright; a renamed option or
tile quietly stopped being counted, which is worse. A wording fix now carries the
answers along with the words, and five tests hold it there. No unit test could
have caught it: every piece was behaving exactly as written.

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

## The completeness pass, after Phase 9

Asked whether the build was actually finished, I checked it against PRD **§1**
rather than against the phase plan — and the answer was no. All nine phases were
green while three things §1 asks for had no phase at all, so nothing was failing
and nothing was looking. They are built now:

- **The story browser.** The stories themselves: search them, star the ones
  worth returning to, tag them in your own words, tick a few and download just
  those. It is the fourth way of looking on the Patterns tab, and it is where a
  surprising hill in the landscape should send you.
- **The QR of the open link, on the screen the app opens on.** A workshop starts
  with a laptop and a room full of phones; the first screen now already has the
  thing they scan.
- **The supporting charts as a picture**, black on white like the contour.

And one thing that was failing quietly: **the 200ms promise, measured at the
size the PRD names.** The tests only ever tried a thousand stories; the PRD
sizes the budget at five thousand, and at five thousand every reading screen was
over — the landscape at more than twice its budget. Most of it turned out to be
work nobody needed, and taking it out roughly halved every one of them. What is
left of the landscape is one call to the statistics library the PRD pins us to.

Two standing tests now guard the things a phase plan cannot: one walks every
numbered item of §1's scope against the code, and one compares every address the
browser can ask for against every address the server answers, in both
directions.

## Next step

There is no next phase, and no scope item left unbuilt. What remains is real
use: run a session, and let what breaks decide what gets built next.

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
| Find one story again | Patterns → **Story browser** → search, or filter by star or tag |
| Keep a story to come back to | Story browser → **☆ Star** |
| Take a few stories out | Story browser → tick them → **Download the ticked stories** |
| Save the charts for a document | Patterns → **Supporting charts** → **Save these charts as a picture** |
| Give something back to the room | Patterns → **Download "What we heard"** |
| Print a paper pack | Studio → **Paper pack for version 1**, then Print → Save as PDF |
| Check everything still works | Run `./run_checks.sh` — you want `ALL CHECKS PASSED` |
| Stop the app | Close the small "Narrative Lens server" window |
