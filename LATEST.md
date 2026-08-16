# Narrative Lens — Latest

**Updated:** 2026-08-16
**Phase:** 5 of 9 complete — Ingestion + Stage A
**Status:** green (428 tests passing · ruff clean · eslint 0 · builds · smoke test end-to-end)

---

## Where things stand

Stories no longer have to be typed into Narrative Lens to get into it. You can
hand it a file that already has stories in it, and it will read the file, show
you what it found, and wait.

- **Nine kinds of file.** Word, plain text, Markdown, PDF, PowerPoint, Excel,
  CSV, and `.vtt` or `.srt` transcripts. Anything else is turned away at the
  door with a sentence saying what to save it as instead.
- **Every passage keeps its address.** "page 3, paragraph 2", "slide 4 notes",
  "cue 7", "Responses row 5" — so when you want to check a story against the
  original, the app tells you exactly where to look.
- **The AI suggests; you decide.** Organise is a button you press. For written
  text it suggests where one person's account ends and the next begins, and you
  untick anything that is a heading or half of someone else's story. For a
  spreadsheet it suggests which column holds the story and which sheets are
  lookup tables to skip — and you can overrule any of it. Nothing goes into the
  data until you confirm.
- **The rows add up, and you can see them add up.** Confirm a spreadsheet and
  the screen shows the arithmetic: rows with a story, rows where the story cell
  was empty, rows on sheets you skipped, and the file's own total. If those ever
  failed to balance the import would stop rather than show you a figure it could
  not stand behind.
- **The order cannot be skipped.** You cannot confirm a mapping for a file that
  has not been organised, and you cannot organise the same file twice. Trying
  gets a plain refusal saying where the file has actually got to.
- **Less-certain suggestions are flagged amber** and treated exactly the same as
  the confident ones — they go on the same list and wait for the same yes.

**All of it runs with no internet at all in the tests.** There is one file in
the whole app that can reach the AI service, and a test that fails if a second
one ever starts to. When the service is unreachable the file simply stays where
it was, with a note, so Organise can be clicked again later.

**Checked in a real browser** at laptop and phone width: an unreadable file
refused, a two-sheet workbook driven through upload → organise → mapping →
confirmation with its reconciliation read on screen, and a text file organised,
trimmed by one passage, and confirmed. Two small layout bugs were found that way
and fixed — see PROGRESS.md "Fixed".

**Still not verified:** the `.bat` launcher has never run on Windows, because
this build runs on Linux. It also does not yet build the frontend — you need to
run `npm run build` in `frontend/` once before the app can serve it.

## Next step

**Phase 6 — Stage B + validation queue (mock-first).** See `PROGRESS.md` for the
gate. It adds `/propose` — the AI suggesting where each story sits on your
triads and dyads — and the validation queue where you approve or correct every
one of those suggestions before it reaches the data. It also adds the no-bypass
test. Its gate is the full suite green with `NL_MOCK_AI=1`.

The edge Stage B will hang off is already in the stage machine and already
refused, so Phase 6 attaches a handler to a door that is already locked.

## How to resume

1. Read `CLAUDE.md`, `PRD_Narrative-Lens_v1.3_20260814.md`, `PROGRESS.md`, and
   this file.
2. Run `./run_checks.sh` to confirm the base is green **before** changing
   anything. If it is red, fix that first and say so — never build new work on a
   red base.
3. Build Phase 6 exactly per PRD §6, including its tests and gate.
4. Run the full regression list, show the gate output, commit with the phase's
   commit message, and update `PROGRESS.md` and `LATEST.md`.

**One trap worth knowing:** if you start the server by hand to poke at the app,
kill the old one first and check the port is actually free. A stale server from
an earlier session once kept the port and quietly served an out-of-date app,
which looked exactly like a broken feature. `./run_checks.sh` is unaffected — it
uses its own port and its own throwaway database.

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
| Bring in a file of stories | **Import & Validate** → choose a file → **Organise** → check it → **Confirm** |
| Print a paper pack | Studio → **Paper pack for version 1**, then Print → Save as PDF |
| Check everything still works | Run `./run_checks.sh` — you want `ALL CHECKS PASSED` |
| Stop the app | Close the small "Narrative Lens server" window |
