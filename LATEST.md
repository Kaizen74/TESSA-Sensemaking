# Narrative Lens — Latest

**Updated:** 2026-08-14
**Phase:** 3 of 9 complete — Capture wizard + paper batch entry
**Status:** green (241 tests passing · ruff clean · eslint 0 · builds · smoke test end-to-end)

---

## Where things stand

Stories can now go in. The app has two working tabs.

- **The capture wizard** asks one thing per screen: welcome, then the story,
  then each scale on its own screen, then the group, then it shows the
  respondent their own mark, then thanks them. A progress bar counts the screens
  that are actual work — the welcome and thank-you are not counted, because
  padding the number would be dishonest.
- **You can answer every scale by tapping or by keyboard.** Tap inside the
  triangle to place a mark; arrow keys nudge it. The slider takes arrow keys.
  Items on the canvas drop where you tap. A scale you skip stores nothing at all,
  rather than a made-up middle value.
- **A half-written story survives a reload.** If someone's phone locks or the
  page reloads, the next visit offers to pick up where they left off — and says
  so plainly rather than silently reinstating it. Nothing about who wrote it is
  stored; the saved draft is keyed to the question set, not the person.
- **Paper entry is a transcription desk.** One returned sheet per entry: type the
  story, mark each scale where the respondent marked it, press Enter, and the
  next blank sheet appears with a running count. The group is kept between
  entries, since a pile of sheets is usually one group.
- **Every record carries its provenance.** Each story is stamped with how it
  arrived (typed or paper), which entry mode, which exact question-set version,
  and a time rounded to the hour.

**Checked in a real browser**, not just in tests: the whole wizard was driven end
to end at phone width — story typed, triangle marked by tapping, slider moved by
keyboard, choice picked, story sent, own mark shown back. The draft was tested
against a genuine page reload. Paper entry was driven through two sheets. That
check found one real bug, now fixed — see PROGRESS.md "Fixed".

**Still not verified:** the `.bat` launcher has never run on Windows, because
this build runs on Linux. It also still starts only the server, not the built
frontend.

## Next step

**Phase 4 — Remote links, kiosk, voice.** See `PROGRESS.md` for the gate. It adds
the QR capture link over Tailscale, kiosk mode, and voice dictation paired with
typing. The wizard built this phase is the one those modes will reuse, which is
why the entry mode was not hard-coded into it.

## How to resume

1. Read `CLAUDE.md`, `PRD_Narrative-Lens_v1.3_20260814.md`, `PROGRESS.md`, and
   this file.
2. Run `./run_checks.sh` to confirm the base is green **before** changing
   anything. If it is red, fix that first and say so — never build new work on a
   red base.
3. Build Phase 4 exactly per PRD §6, including its tests and gate.
4. Run the full regression list, show the gate output, commit with the phase's
   commit message, and update `PROGRESS.md` and `LATEST.md`.

**One trap worth knowing:** if you start the server by hand to poke at the app,
kill the old one first. A stale server from an earlier session kept port 8756 and
quietly served an out-of-date app, which looked exactly like a broken feature.
`./run_checks.sh` is unaffected — it uses its own port and its own throwaway
database.

## Running it yourself

| What you want | What to do |
|---|---|
| Start the app | Double-click `Start Narrative Lens.bat` |
| See it | In `frontend/`, run `npm install` once, then `npm run dev`, and open the address it prints |
| Write the questions | The **Studio** tab |
| Enter a story yourself | **Capture & Links** → "One at a time" |
| Type up returned paper | **Capture & Links** → "From paper" |
| Print a paper pack | Studio → **Paper pack for version 1**, then Print → Save as PDF |
| Check everything still works | Run `./run_checks.sh` — you want `ALL CHECKS PASSED` |
| Stop the app | Close the small "Narrative Lens server" window |
