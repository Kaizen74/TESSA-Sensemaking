# Narrative Lens — Latest

**Updated:** 2026-08-14
**Phase:** 1 of 9 complete — Skeleton + data layer
**Status:** green (61 tests passing, ruff clean, smoke test answering)

---

## Where things stand

The foundation is in and verified. There is no user interface yet — this phase
built the parts underneath one.

- A local web server runs and answers a health check at
  `http://127.0.0.1:8756/api/health`.
- The database has all six tables from PRD §3, created by Alembic migration 001:
  `frameworks` (with `edit_log_json` and `parent_framework_id`), `capture_links`,
  `anecdotes` (with the four-value `input_method`), `significations`,
  `import_jobs`, `tags`.
- The anonymity guarantee is enforced by tests, not by intention: no IP, user
  agent, fingerprint, email, or personal-name column can be added to a
  respondent table without the suite going red, and story timestamps are rounded
  to the hour by the only function permitted to write them.
- `Start Narrative Lens.bat` prepares the database, starts the server, and opens
  the browser.
- `./run_checks.sh` runs everything in one command.

**One thing not verified:** the `.bat` launcher was written and reviewed but
never executed, because this build ran on Linux and it is a Windows file. Its
first real run is on the operator's laptop.

## Next step

**Phase 2 — Studio + widgets + tokens + paper pack.** See `PROGRESS.md` for the
full specification and its gate. It adds the first frontend (`React + Vite`),
`frontend/src/tokens.css` per PRD §5b, the framework editing surface with live
preview, the wording-fix vs meaning-change guardrail, and the printable paper
pack. Its gate adds `eslint 0` to pytest and ruff.

## How to resume

1. Read `CLAUDE.md`, `PRD_Narrative-Lens_v1.3_20260814.md`, `PROGRESS.md`, and
   this file.
2. Run `./run_checks.sh` to confirm the base is green **before** changing
   anything. If it is red, fix that first and say so — never build new work on a
   red base.
3. Build Phase 2 exactly per PRD §6, including its tests and gate.
4. Show the gate output, commit with the phase's commit message, and update
   `PROGRESS.md` and `LATEST.md`.

## Running it yourself

| What you want | What to do |
|---|---|
| Start the app | Double-click `Start Narrative Lens.bat` |
| Check everything still works | Run `./run_checks.sh` — you want to see `ALL CHECKS PASSED` |
| Stop the app | Close the small "Narrative Lens server" window |
