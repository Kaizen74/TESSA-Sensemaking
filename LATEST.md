# Narrative Lens — Latest

**Updated:** 2026-08-14
**Phase:** 2 of 9 complete — Studio + widgets + tokens + paper pack
**Status:** green (198 tests passing · ruff clean · eslint 0 · builds · smoke test end-to-end)

---

## Where things stand

There is now something to look at. The Studio is the first working screen.

- **The Studio** shows every word a respondent will read on one page — the story
  prompt, every triangle corner, slider end, canvas axis and choice option, plus
  the welcome, anonymity, thank-you and time-promise text. A phone-shaped
  preview beside it updates as you type, at exactly the 375px width the promise
  is made at.
- **The honesty meter** above the editor shows the estimated respondent time and
  the number of question screens, and warns when either goes past the promise.
- **The guardrail works.** Editing a framework with no stories just saves.
  Editing one that already has stories opens a dialog asking whether this is a
  wording fix or a change of meaning. A wording fix applies now and is recorded
  in that version's edit log, visible in the left rail. A meaning change starts
  version n+1 and leaves the existing stories attached to the words people
  actually saw. The server refuses to guess if the dialog is ever bypassed.
- **The paper pack prints.** One button per version opens a print-ready page:
  a story card with the anonymity line word for word, one large sheet per
  signifier for sticky dots or pen, and a facilitator sheet with the
  handed-out / returned / entered grid. Black on white, one sheet per page,
  self-contained — a photocopier is the test and it passes.
- **The design tokens are set** in `frontend/src/tokens.css`: six colours, two
  typefaces, one spacing unit. Everything is deliberately quiet, because the
  landscape in Phase 8 is meant to be the one bold thing in the app.

**Checked in a real browser** at 1440px and 375px: the Studio renders, the
preview updates, there are no console errors and nothing overflows sideways.
That check found two real bugs, both now fixed — see PROGRESS.md "Fixed".

**Still not verified:** the `.bat` launcher has never run on Windows, because
this build runs on Linux. It also still starts only the server; wiring it to
serve the built frontend belongs to a later phase.

## Next step

**Phase 3 — Capture wizard (local) + paper batch entry.** See `PROGRESS.md` for
the specification and gate. It adds the respondent wizard per PRD §5a, the rapid
paper transcription mode with Enter-to-advance, and provenance stamping
including `input_method=paper`. Its gate is the full regression list plus p95
under 200ms on submit.

## How to resume

1. Read `CLAUDE.md`, `PRD_Narrative-Lens_v1.3_20260814.md`, `PROGRESS.md`, and
   this file.
2. Run `./run_checks.sh` to confirm the base is green **before** changing
   anything. If it is red, fix that first and say so — never build new work on a
   red base.
3. Build Phase 3 exactly per PRD §6, including its tests and gate.
4. Run the full regression list, show the gate output, commit with the phase's
   commit message, and update `PROGRESS.md` and `LATEST.md`.

## Running it yourself

| What you want | What to do |
|---|---|
| Start the app | Double-click `Start Narrative Lens.bat` |
| See the Studio | In `frontend/`, run `npm install` once, then `npm run dev`, and open the address it prints |
| Print a paper pack | In the Studio, click **Paper pack for version 1**, then use your browser's Print → Save as PDF |
| Check everything still works | Run `./run_checks.sh` — you want `ALL CHECKS PASSED` |
| Stop the app | Close the small "Narrative Lens server" window |
