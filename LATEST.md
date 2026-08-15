# Narrative Lens — Latest

**Updated:** 2026-08-15
**Phase:** 4 of 9 complete — Remote links, kiosk, voice
**Status:** green (307 tests passing · ruff clean · eslint 0 · builds · smoke test end-to-end)

---

## Where things stand

Stories can now come in from other people's phones. All three ways of
collecting a story work, and they all run through the same wizard.

- **QR links.** Open a link against a question set, give it a label like
  "Hangar noticeboard", and print its QR poster. Someone scans it, the wizard
  opens on their phone, and their story arrives stamped as having come from that
  link. The poster prints black-on-white with the address written underneath for
  anyone whose camera will not cooperate.
- **Closing a link really closes it.** Take the poster down, close the link, and
  anyone who scans the old code is told plainly that it has closed and who to
  ask for a current one. Closing is permanent by design — a link that could
  reopen would be a poster that starts working again by accident. The stories it
  already collected stay exactly where they are.
- **Kiosk mode** runs the same wizard full-screen on a machine left out at a
  workshop, and loops back to a fresh welcome a few seconds after each story so
  nobody sees the last person's answers.
- **Voice sits beside typing, never instead of it.** Dictated words are added to
  whatever is already in the box, so someone can type a paragraph and then speak
  a sentence and keep both. When the microphone is blocked or the browser cannot
  listen, a plain sentence says so and points at the keyboard, which is still
  right there.
- **The app now serves its own front end**, so a phone on your Tailscale network
  reaches the wizard at the same address as everything else. That closes the gap
  noted after the earlier phases.

**The anonymity guarantee now covers the network, not just the database.** Until
this phase every story was typed on your own laptop. Now they arrive from
strangers' phones, which send identifying headers with every request. There is a
test suite that fires a full set of those headers at the public endpoints and
then sweeps every column of every table looking for them. Two further tests go
beyond behaviour to structure: no public handler is allowed to accept a request
object at all, and the module may not even mention header access — so a future
edit cannot quietly start reading them.

**Checked in a real browser:** a link created, its QR poster rendered from a real
generated image, that link opened on a 375px screen with no admin navigation
anywhere, a story driven end to end, the link revoked, and the closed message
confirmed on the phone. Kiosk driven end to end and confirmed looping back.
The voice fallback fired for real.

**Still not verified:** the `.bat` launcher has never run on Windows, because
this build runs on Linux. It also does not yet build the frontend — you need to
run `npm run build` in `frontend/` once before the app can serve it.

## Next step

**Phase 5 — Ingestion + Stage A (mock-first).** See `PROGRESS.md` for the gate.
It adds the file parsers (docx, txt, md, pdf, pptx, xlsx, csv, vtt), the staged
import machine with its 409 stage gate, and the column-mapping screen with exact
row reconciliation. Its gate is the full suite green with `NL_MOCK_AI=1` — no
network at all.

## How to resume

1. Read `CLAUDE.md`, `PRD_Narrative-Lens_v1.3_20260814.md`, `PROGRESS.md`, and
   this file.
2. Run `./run_checks.sh` to confirm the base is green **before** changing
   anything. If it is red, fix that first and say so — never build new work on a
   red base.
3. Build Phase 5 exactly per PRD §6, including its tests and gate.
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
| Print a paper pack | Studio → **Paper pack for version 1**, then Print → Save as PDF |
| Check everything still works | Run `./run_checks.sh` — you want `ALL CHECKS PASSED` |
| Stop the app | Close the small "Narrative Lens server" window |
