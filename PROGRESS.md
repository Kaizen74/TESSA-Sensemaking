# Narrative Lens — Progress

Phase checklist from PRD §6. One phase = one session. A phase is complete only
when its gate has been run and shown green.

Legend: `[ ]` not started · `[~]` in progress · `[x]` complete (gate shown green)

---

## Phases

### [x] Phase 1 — Skeleton + data layer — **complete 2026-08-14**
The §3 schema including `edit_log_json`, `parent_framework_id`, and the
four-value `input_method`.
- Tests: CRUD, migration up/down, schema-absence (constraint 9).
- Gate: pytest green · ruff 0. **Shown green: 61 passed, ruff "All checks
  passed", smoke test answered.**
- Commit: `phase-1: skeleton, schema, launcher`.

Delivered: `backend/` (FastAPI app with `/api/health`, SQLAlchemy models,
engine/session plumbing, settings), `backend/alembic/versions/001_initial_schema.py`,
`tests/` (61 tests across health, CRUD, migrations, schema-absence),
`pyproject.toml` with ruff config, `Start Narrative Lens.bat`, `run_checks.sh`.

Not verified: the `.bat` has been reviewed but not executed — this build ran on
Linux. First Windows run belongs to the operator.

### [ ] Phase 2 — Studio + widgets + tokens + paper pack
Studio editing surface with live preview; `tokens.css` per §5b; shared widget
components; framework JSON validation; edit-semantics flow (free edit at zero
stories; wording-fix vs meaning-change dialog once stories exist; version
history sidebar); paper-pack print page with print CSS.
- Tests: barycentric golden maths; edit-semantics state machine (PUT without
  `edit_kind` on live framework → 409; `wording_fix` logs and patches;
  `meaning_change` spawns version with parent link and leaves old anecdotes
  bound); paper-pack page contains every signifier of the version with its exact
  labels and the verbatim anonymity line; print CSS produces one sheet per page
  (assert page-break rules present).
- Gate: pytest + ruff + eslint 0.
- Commit: `phase-2: studio, tokens, widgets, paper pack`.

### [ ] Phase 3 — Capture wizard (local) + paper batch entry
Wizard per §5a; paper batch entry mode with Enter-to-advance; provenance
stamping incl. `input_method=paper`.
- Tests: wizard round-trip; draft survives reload; batch entry writes paper
  provenance and loops correctly; p95 < 200ms on submit.
- Gate: full regression.
- Commit: `phase-3: capture wizard + paper entry`.

### [ ] Phase 4 — Remote links, kiosk, voice
Identifier-absence test, token lifecycle, 375px snapshot, voice fallback.
- Gate: full regression.
- Commit: `phase-4: remote capture + kiosk + voice`.

### [ ] Phase 5 — Ingestion + Stage A (mock-first)
All parsers, stage machine, Mapping screen, deterministic extraction,
reconciliation arithmetic, stage-gate 409 test.
- Gate: full suite green with `NL_MOCK_AI=1`.
- Commit: `phase-5: multi-format ingestion + organise stage`.

### [ ] Phase 6 — Stage B + validation queue (mock-first)
Includes the no-bypass test.
- Gate: full suite, `NL_MOCK_AI=1`.
- Commit: `phase-6: proposals + validation queue`.

### [ ] Phase 7 — Live AI + supporting charts + exports
Real Claude for both stages; supporting charts built to §5b grammar (sorted
horizontal bars, direct labels, quiet weight); filters; version-chip behaviour;
CSV + Pattern Brief with finding-style headlines.
- Tests: repair path; offline degradation; version mixing requires explicit
  flag; 2D aggregation vs golden `patterns_20_anecdotes.json` (byte-identical
  thereafter); a chart-grammar test asserting categorical endpoints return
  value-sorted data.
- Gate: full suite + golden, ruff + eslint 0.
- Commit: `phase-7: live AI + supporting charts`.

### [ ] Phase 8 — Landscape suite (primary view)
KDE endpoint serving surface + contour twin; landscape as the Patterns default
with the §5b hero layout; directly-labelled peaks; region→stories drill; filter
split; 3D Explorer; k-means overlay; analyst notes; snapshot (contour default).
- Tests: KDE determinism; landscape peaks on golden set stable ±0.02; region
  query exact; contour twin derives from the identical grid as the surface
  (single-source test); default route lands on Landscape; cluster determinism;
  interactive at 1,000 points.
- Gate: full regression incl. both goldens.
- Commit: `phase-8: landscape-first patterns`.

### [ ] Phase 9 — Closing the loop + operator hardening + critique pass
"What We Heard" with <5 suppression; plain-English error pass; empty states;
README-for-Eric (incl. "printing a paper pack" and "reading a landscape"
one-pagers); critique pass per the design skill: remove one element per view,
verify the landscape is the single boldest thing, grayscale screenshot check.
- Gate: full regression; manual smoke incl. one phone over Tailscale, one xlsx
  through the pipeline, and one paper pack printed to PDF.
- Commit: `phase-9: v1.3`.

---

## Regression list

Green in every phase from introduction onward:

- all prior suites
- schema / identifier-absence *(live since Phase 1)*
- edit-semantics state machine
- stage-gate + no-bypass
- barycentric maths
- `patterns_20_anecdotes.json` byte-identical
- landscape peaks ±0.02
- surface / contour single-source

---

## Decisions

Choices made where the PRD was silent or ambiguous. Per the kickoff rule, the
simpler option was taken unless noted.

### Phase 1

1. **Layout: `backend/` package, `tests/` at root.** The PRD names
   `frontend/src/tokens.css` (§5b) and `ai_client.py` (constraint 6) but never
   fixes the backend layout. Chose a single flat `backend/` package with
   `tests/` at the repo root — the smallest structure that leaves room for
   `frontend/` in Phase 2.
2. **Enum columns are `String` + named `CheckConstraint`, not SQLAlchemy
   `Enum`.** Both produce a `VARCHAR` + `CHECK` in SQLite; the explicit
   constraint is easier to read in the migration and easier to extend
   additively later. Constraint names follow the `MetaData` naming convention so
   future Alembic batch operations can address them.
3. **`created_at_hour` stores a full `DateTime` truncated to the hour**, not an
   integer hour or a string. Constraint 9 demands hour-rounded timestamps;
   storing a real datetime with minutes/seconds/microseconds zeroed keeps
   ordering and filtering trivial while carrying no sub-hour information. The
   helper `hour_rounded_now()` in `backend/models.py` is the only writer, and it
   is unit-tested.
4. **Schema-absence test scope.** Constraint 9 bans "name" anywhere, but
   `frameworks.name` (the framework's own title) and `import_jobs.filename` (an
   operator's own uploaded file) are not respondent identifiers. The test
   therefore bans `ip`/`user_agent`/`email`/`fingerprint`/`device_id` on **every**
   table, and additionally bans `name`-family columns on the four
   respondent-bearing tables (`anecdotes`, `significations`, `tags`,
   `capture_links`). It also fails any new `*_name` column on those tables, so
   the guard survives future schema growth.
5. **No error-envelope handler yet.** PRD §4 specifies the
   `{"error": {code, message, action}}` shape, but Phase 9 explicitly schedules
   the "plain-English error pass". Phase 1 ships `/api/health` only and leaves
   FastAPI's default error responses in place. Simpler option taken.
6. **Server port 8756.** The PRD does not name a port. Avoided 8000/8080 because
   a clash on the operator's laptop would surface as a confusing failure, and
   constraint 7 forbids config editing to resolve it.
7. **Launcher scope.** `Start Narrative Lens.bat` starts the server and opens the
   browser, preferring a `.venv` interpreter and falling back to `python` on
   PATH. It does **not** install dependencies — PRD §9 assumption 3 states a
   one-time Python/Node install is acceptable. Because this container is Linux,
   the `.bat` has been reviewed by eye but **not executed on Windows**; first
   real run belongs to the operator.
8. **`run_checks.sh` added** as the single green-or-red command (ruff, pytest,
   and a live smoke test of `/api/health`). Not named in the PRD; adopted from
   the `resilient-build` skill so the non-technical operator has one command
   (constraint 7). It runs the same gate the PRD specifies, nothing more.
9. **`signifier_type` is CHECK-constrained to triad | dyad | stones | mcq.** PRD
   §3 does not enumerate the column, but its `value_json` note names exactly
   these four shapes. Constraining it now costs nothing and a fifth type would
   arrive as an additive migration anyway.
10. **Tests run warnings-as-errors** (`filterwarnings = ["error"]` in
    `pyproject.toml`). This caught two real problems on the first run — an
    Alembic config key that had been renamed, and starlette's `TestClient`
    wanting `httpx2` rather than `httpx`. Dev dependency is therefore `httpx2`,
    not `httpx`.
11. **Autogenerated migrations get `ruff format` applied.** Alembic emits lines
    well past the 100-column limit, so a raw autogenerate fails `ruff check .`.
    Running `ruff format` on the new revision file fixes it without a lint
    carve-out; do this for every future migration.

---

## Fixed

Bugs found and fixed, newest first. *(none yet)*
