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

### [x] Phase 2 — Studio + widgets + tokens + paper pack — **complete 2026-08-14**
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
- Gate: pytest + ruff + eslint 0. **Shown green: 198 passed · ruff "All checks
  passed" · eslint 0 problems · frontend build · smoke test end-to-end.**
- Commit: `phase-2: studio, tokens, widgets, paper pack`.

Delivered: `backend/framework_schema.py` (validation for every respondent-facing
string), `backend/barycentric.py` + `tests/test_barycentric.py` (golden maths),
`backend/edit_semantics.py`, `backend/routers/frameworks.py` (list/create/fetch
+ the guardrail PUT), `backend/paper_pack.py` + `/paper-pack` endpoint,
`backend/errors.py`, `frontend/` (Vite + React, eslint, `src/tokens.css`,
widgets, Studio with live phone preview, version sidebar, edit-kind dialog).

Verified in a real browser at 1440px and 375px: the Studio renders, the preview
updates, no console errors, no horizontal overflow. Two bugs were found and
fixed that way — see "Fixed" below.

### [x] Phase 3 — Capture wizard (local) + paper batch entry — **complete 2026-08-14**
Wizard per §5a; paper batch entry mode with Enter-to-advance; provenance
stamping incl. `input_method=paper`.
- Tests: wizard round-trip; draft survives reload; batch entry writes paper
  provenance and loops correctly; p95 < 200ms on submit.
- Gate: full regression. **Shown green: 241 passed · ruff "All checks passed" ·
  eslint 0 problems · frontend build · smoke test end-to-end. Regression list
  green: prior suites 111, identifier-absence 20, edit-semantics 26,
  barycentric 41.**
- Commit: `phase-3: capture wizard + paper entry`.

Delivered: `backend/capture_schema.py` (placement validation against the exact
version answered), `backend/routers/capture.py` (`POST /api/capture`, provenance
stamped in one place), `frontend/src/capture/` (draft module, wizard, paper batch
entry, capture tab), interactive widgets in `frontend/src/widgets/Widgets.jsx`.

Verified in a real browser at 375px and 1280px: the whole wizard was driven end
to end — story typed, triad marked by tap, dyad moved by keyboard, MCQ chosen,
story sent, reflection shown — and the draft was checked against a genuine page
reload, not a simulated one. Paper entry was driven through two consecutive
sheets. Data landed with correct provenance and hour-rounded times. One bug was
found this way; see "Fixed".

### [x] Phase 4 — Remote links, kiosk, voice — **complete 2026-08-15**
Identifier-absence test, token lifecycle, 375px snapshot, voice fallback.
- Gate: full regression. **Shown green: 307 passed · ruff "All checks passed" ·
  eslint 0 problems · frontend build · smoke test end-to-end. Regression list
  green: prior suites 154, identifier-absence 31 (schema + remote path),
  edit-semantics 26, barycentric 41.**
- Commit: `phase-4: remote capture + kiosk + voice`.

Delivered: `backend/routers/capture_links.py` (open/list/revoke + QR PNG),
`backend/routers/public.py` (token-gated public path), `backend/rate_limit.py`,
`backend/qr.py`, `backend/settings.py` LAN address resolution, static serving of
the built frontend in `backend/main.py`, `frontend/src/capture/`
(`voice.js`, `VoiceButton.jsx`, `PublicCapture.jsx`, `LinkManager.jsx`, kiosk
mode in `CaptureTab.jsx`).

Verified in a real browser: a link created in the admin UI, its QR poster
rendered from a real generated PNG, that link opened at `/c/{token}` on a
375px viewport with no admin chrome, a story driven end to end and stored with
`entry_mode=link` and the link id; the link then revoked and the closed message
confirmed on the phone. Kiosk mode driven end to end and confirmed looping back
to a fresh welcome, stored with `entry_mode=kiosk`. The voice fallback was
exercised for real — Chromium declares speech support then fails without a
microphone, which produced the plain-English message and left typing working.
A sweep of every table for browser-supplied identifiers found none.

### [x] Phase 5 — Ingestion + Stage A (mock-first) — **complete 2026-08-16**
All parsers, stage machine, Mapping screen, deterministic extraction,
reconciliation arithmetic, stage-gate 409 test.
- Gate: full suite green with `NL_MOCK_AI=1`. **Shown green: 428 passed · ruff
  "All checks passed" · eslint 0 problems · frontend build · smoke test
  end-to-end including a CSV driven through the whole machine over HTTP.
  Regression list green: prior suites 212, identifier-absence 31,
  edit-semantics 26, stage gate 17, barycentric 38, ingestion + Stage A 104.**
- Commit: `phase-5: multi-format ingestion + organise stage`.

Delivered: `backend/parsers.py` (all nine extensions into one normalised
document with locators), `backend/ai_client.py` (the one client — mocks, strict
JSON, one repair-retry, plain-English failure), `backend/stage_machine.py` (the
six-stage table and its 409 gate), `backend/organise.py` (Stage A per file
class, with the proposal checked against the file), `backend/extraction.py`
(confirmation, deterministic post-confirmation extraction, exact
reconciliation), `backend/routers/imports.py`, `frontend/src/import/`
(staged pipeline, Mapping screen, passage checklist, reconciliation table),
`tests/ingest_fixtures.py` (a real file per format, built in memory).

Verified in a real browser at 1280px and 375px: an unreadable file refused with
a plain sentence, a two-sheet workbook uploaded, organised, its mapping screen
driven — column pickers, sample rows, ignored sheet — confirmed, and its
reconciliation read on screen (3 + 1 + 2 = 6). A text file organised, one
passage unticked, and the narrative tally read (2 + 1 = 3). The low-confidence
passage carried its amber flag. No horizontal overflow at either width after one
fix; see "Fixed".

### [x] Phase 6 — Stage B + validation queue (mock-first) — **complete 2026-08-16**
Includes the no-bypass test.
- Gate: full suite, `NL_MOCK_AI=1`. **Shown green: 493 passed · ruff "All checks
  passed" · eslint 0 problems · frontend build · smoke test end-to-end including
  Stage B and a queue decision over HTTP. Regression list green: prior suites
  316, identifier-absence 31, edit-semantics 26, stage gate + no-bypass 29,
  barycentric 38, Stage B + queue 53.**
- Commit: `phase-6: proposals + validation queue`.

Delivered: `backend/propose.py` (Stage B chunked at twenty, every proposal held
to the framework by the same validator a respondent's submission passes
through), `backend/dataset.py` (the single definition of what counts as data),
`POST /api/import/{id}/propose` with its 409 gate, `backend/routers/queue.py`
(`GET /api/queue`, `PUT /api/queue/{anecdote_id}` — accept · correct · reject),
`frontend/src/import/ValidationQueue.jsx`, `frontend/src/capture/placements.js`,
`tests/test_no_bypass.py`, `tests/test_stage_b.py`, `tests/test_queue.py`,
`tests/test_placement_shape_parity.py`, `tests/queue_fixtures.py`.

Verified in a real browser at 1280px and 950px and at 375px: a workbook driven
from upload through organise, mapping, and mark-up into the queue; the AI's
placements read off real widgets with their confidence figures; one story
corrected on the interactive widgets, one accepted, one set aside; the progress
line following each decision; and the file reaching "finished" as the queue
emptied. A sweep of the database afterwards confirmed the corrected placement
stored as `analyst` with no confidence, and the untouched ones still `ai` with
theirs. Three bugs were found this way — see "Fixed".

### [x] Phase 7 — Live AI + supporting charts + exports — **complete 2026-08-16**
Real Claude for both stages; supporting charts built to §5b grammar (sorted
horizontal bars, direct labels, quiet weight); filters; version-chip behaviour;
CSV + Pattern Brief with finding-style headlines.
- Tests: repair path; offline degradation; version mixing requires explicit
  flag; 2D aggregation vs golden `patterns_20_anecdotes.json` (byte-identical
  thereafter); a chart-grammar test asserting categorical endpoints return
  value-sorted data.
- Gate: full suite + golden, ruff + eslint 0. **Shown green: 552 passed · ruff
  "All checks passed" · eslint 0 problems · frontend build · smoke test
  end-to-end including patterns, CSV and brief over HTTP. Regression list green:
  prior suites 369, identifier-absence 31, edit-semantics 26, stage gate +
  no-bypass 29, barycentric 38, golden 5, patterns + exports + live AI 54.**
- Commit: `phase-7: live AI + supporting charts`.

Delivered: `backend/patterns.py` (deterministic local aggregation),
`backend/routers/patterns.py` (`GET /api/patterns/{id}` with filters and the
version-mixing guard), `backend/exports.py` + `backend/routers/exports.py`
(`/api/export/csv`, `/api/export/brief`), `frontend/src/patterns/` (the Patterns
tab, the §5b supporting charts, the filter rail, the version chip, the export
links), `tests/golden/patterns_20_anecdotes.json` with
`tests/patterns_fixtures.py` and `tests/regenerate_golden.py`,
`tests/test_live_ai.py` (the real SDK call shape and offline degradation).

Verified in a real browser at 1280px and 375px, on both framework versions: the
charts render from twenty stories, every categorical view arrives sorted by
value, a filter narrows all of them together, clearing it restores them, the
version chip stays hidden until mixing is ticked and then names both versions
with their counts, and both export links carry the current filters. Three
chart-clipping bugs were found this way — see "Fixed".

### [x] Phase 8 — Landscape suite (primary view) — **complete 2026-08-16**
KDE endpoint serving surface + contour twin; landscape as the Patterns default
with the §5b hero layout; directly-labelled peaks; region→stories drill; filter
split; 3D Explorer; k-means overlay; analyst notes; snapshot (contour default).
- Tests: KDE determinism; landscape peaks on golden set stable ±0.02; region
  query exact; contour twin derives from the identical grid as the surface
  (single-source test); default route lands on Landscape; cluster determinism;
  interactive at 1,000 points.
- Gate: full regression incl. both goldens. **Shown green: 617 passed · ruff
  "All checks passed" · eslint 0 problems · frontend build · smoke test
  end-to-end including the landscape's single-source grid and the cluster
  caveat. Regression list green: prior suites 423, identifier-absence 31,
  edit-semantics 26, stage gate + no-bypass 29, barycentric 38, golden 1
  (byte-identical) 5, golden 2 (peaks ±0.02) 4, landscape suite 58, whole-app
  integration 3.**
- Commit: `phase-8: landscape-first patterns`.

Delivered: `backend/landscape.py` (scipy gaussian_kde, Scott bandwidth, 64×64
grid, peaks with their stories, per-cell ids, contour levels off the same grid),
`backend/clusters.py` (the Explorer's dimensions and deterministic k-means at
seed 42), `backend/routers/landscape.py` (`/api/landscape/{id}/{triad}`,
`/api/explorer/{id}`, `/api/clusters/{id}`, filter split on a shared density
scale), `frontend/src/patterns/terrain.js` (projection, marching-squares
contours, the cividis ramp), `Landscape.jsx`, `Explorer.jsx`, `snapshot.js`, the
restructured landscape-first `Patterns.jsx` with sub-navigation, region drawer
and analyst notes, `tests/golden/landscape_peaks.json`,
`tests/test_landscape.py`, `tests/test_landscape_golden.py`,
`tests/test_explorer_clusters.py`, `tests/test_terrain_maths.py`, and
`tests/test_whole_app.py`.

Verified in a real browser at 1440px and 375px: Patterns opens on the Landscape;
the terrain paints and turns under the mouse and the arrow keys; the camera
resets; peaks are labelled directly (4 near Speed · 4 near Care · 4 near Cost)
and clicking one lists exactly its four stories; the contour twin draws 557
isolines and all twenty dots from the same grid; a split by respondent group
gives three panels on one scale; the second triad redraws; the Explorer plots
three chosen axes with the cluster overlay and its caveat; and the snapshot
downloads as `hangar-v1-…-contour-stories-cluster-near-my-team.png`. Three
label-clipping and layout bugs were found this way — see "Fixed".

### [x] Phase 9 — Closing the loop + operator hardening + critique pass — **complete 2026-08-17**
"What We Heard" with <5 suppression; plain-English error pass; empty states;
README-for-Eric (incl. "printing a paper pack" and "reading a landscape"
one-pagers); critique pass per the design skill: remove one element per view,
verify the landscape is the single boldest thing, grayscale screenshot check.
- Gate: full regression; manual smoke incl. one phone over Tailscale, one xlsx
  through the pipeline, and one paper pack printed to PDF.
- Commit: `phase-9: v1.3`.

Delivered: `exports.what_we_heard` with `SUPPRESSION_FLOOR = 5` applied per
slice and after any filter, plus `GET /api/export/heard` and its download in the
Patterns rail; four exception handlers in `backend/main.py` so a mistyped
address, a malformed request and a fault in the app itself all leave by the same
door in the same shape; the whole error surface read out of the source and held
to the rule by `tests/test_error_surface.py`; empty states audited across every
screen and guarded by `tests/test_empty_states.py`; `README.md` rewritten for the
operator with both one-pagers and the single attribution PRD §15 permits, with
`tests/test_original_names.py` holding constraint 8; `frontend/src/studio/
editLog.js` turning schema paths into English, tested through Node by
`tests/test_edit_log_wording.py`; and the critique-pass edits listed under
"Decisions".

- **Gate shown green:** 1030 passed · ruff "All checks passed" · eslint 0
  problems · frontend build · smoke test end-to-end, now including the
  suppression floor and the plain-English 404. Regression list green in one
  run: identifier-absence, edit-semantics, stage gate + no-bypass, barycentric,
  both goldens, the landscape suite and the whole-app integration — 172 tests
  in the named subset.
- **Manual smoke:** a real two-sheet `workshop.xlsx` driven over HTTP through
  upload → stage gate (409) → Organise → mapping → reconciliation (5 rows: 4
  with a story, 1 empty, balanced) → Stage B → four queued → accept, accept,
  correct, reject → patterns, CSV and "What We Heard" all agreeing on the five
  stories that exist. A second end-to-end run — a one-triangle set, eight
  stories, and a wording fix that renamed a corner — found the one real bug of
  this phase, listed first under "Fixed". The paper pack was printed to a real
  A4 PDF from Chromium
  (33 KB, 28 sheets): story card with the verbatim anonymity line, one sheet per
  signifier, facilitator sheet with the reconciliation grid, and every computed
  colour on the page is `rgb(0,0,0)` on white.
- **Not verified:** a phone over Tailscale. This build has one machine and no
  second device, so the wizard was exercised at 375px in Chromium rather than on
  a handset, and the `.bat` launcher still has never run on Windows.

Checked in a real browser at 1440px and 375px, and again with every view forced
to grayscale: the landscape is the single boldest element on the Patterns page
at both widths; the contour, the supporting charts and the Explorer all survive
grayscale because length, position and direct labels carry the meaning; corner
labels on the terrain now hold their size on a phone.

---

### [x] Completeness pass — **complete 2026-08-17**

Not a phase. A review of the build against PRD **§1** rather than against PRD
§6, prompted by the question "is this actually finished?" — and the answer was
no. All nine phases were green while three items of §1's scope had no phase at
all, so nothing was failing and nothing was looking.

- **The story browser (§1.6, §5.4).** Search, star, tag, export selected, as the
  fourth Patterns sub-view. `backend/stories.py`, `backend/routers/stories.py`,
  `frontend/src/patterns/StoryBrowser.jsx`, `tests/test_story_browser.py`.
- **The QR of the active link on the admin home (§1.8, criterion 1).**
  `frontend/src/studio/ActiveLinkQr.jsx`.
- **The supporting-charts PNG (§1.7).** `saveChartsSnapshot` in
  `frontend/src/patterns/snapshot.js`.
- **The 200ms budget at the scale §4 names.** The suite tested 1,000 stories;
  the PRD says 5,000. Every read endpoint was over. See "Fixed".
- **Two new standing tests**: `tests/test_scope_completeness.py` walks §1's
  scope against the code, and `tests/test_api_alignment.py` compares every
  address `api.js` can build against every route the server exposes, in both
  directions.
- **Gate shown green:** 1081 passed · ruff clean · eslint 0 · frontend build ·
  smoke test end-to-end including the browser and the selected export. Checked
  in a real browser across every view at 1440px and 375px.

---

## The meaningfulness delta

Six phases from `SPEC_DELTA_meaningfulness_20260902.md`, which adds to the PRD
rather than replacing it: the PRD stands for everything the delta does not name.
Each phase is one session and ends with `./run_checks.sh` green plus the delta's
own regression list.

- [x] **Phase A — Provenance made visible + respondent title.** (delta items 1, 2)
  — **complete 2026-09-02**
  Migration 002 adds `anecdotes.respondent_title`. `signified_by` accepted by
  patterns, landscape, explorer, clusters and all three exports, defaulting to
  participant-signified placements only; `signified_by_applied` and
  `counts_by_signified_by` on the patterns and landscape responses. The
  respondent's own title runs through all four capture paths, the story browser,
  the region drill, the paper story card and the CSV. Constraints 14–16 appended
  to `CLAUDE.md`. New: `tests/test_signification_provenance.py` (19),
  `tests/test_respondent_title.py` (16). Goldens per the delta's baseline block:
  `patterns_20_anecdotes.json` and `landscape_peaks.json` untouched and byte-
  identical, their tests now passing `signified_by=all` explicitly, and a new
  `patterns_20_anecdotes_participant.json` beside them. The frontend gains the
  segmented provenance control in the filter rail, the persistent label above
  the figures when the view is not the default, and the optional story-name field
  on the capture wizard and paper entry. Gate green: ruff clean, eslint clean,
  1127 passed, frontend built, smoke test through every path.
- [x] **Phase B — Data-quality signals.** (item 4) — **complete 2026-09-02**
  `backend/quality.py` and `/api/quality/{framework_id}`, both free of any route
  to a language model. Two signals per signifier: the share of triad placements
  inside a circle at the centre of the triangle, and the share of stories that
  left the question blank. No schema change — a skip is an absent signification
  row. The circle is derived from an area share rather than a hard-coded radius,
  so the panel can state what an even spread would look like. The quiet panel
  sits collapsed below the supporting charts. New: `tests/test_quality_signals.py`
  (30), including the frontend visual-grammar assertions and a budget test
  measured against the patterns endpoint in the same run. Gate green: ruff clean,
  eslint clean, 1160 passed, frontend built, smoke test end-to-end.
- [ ] **Phase C — Framework design linter.** (item 3) The lint call in
  `ai_client.py` with its mock fixture, `/api/frameworks/{id}/lint`, and the
  Studio panel. Advisory only: it can never block publishing, never edits the
  framework, and never receives story text. Test: `test_design_linter.py`.
  Commit: `delta-C: framework design linter`.
- [ ] **Phase D — Collective sense-making mode.** (item 5) Migration 005.
  `/api/interpretations` GET/POST, the projector view, the interpretation list,
  and the brief's interpretations section. Test: `test_interpretations.py`,
  including the constraint-16 guard that a recorded interpretation leaves the
  landscape byte-identical. Commit: `delta-D: collective sense-making mode`.
- [ ] **Phase E — Language of record.** (item 6, part 1) Migration 003.
  Per-framework language list, language on capture and on every story display,
  language in the CSV and the filters. Test: `test_language_capture.py`.
  Commit: `delta-E: original language of record`.
- [ ] **Phase F — Read-time translation.** (item 6, part 2) Migration 004. The
  translation endpoint with its mock, the display-only cache, and the permanent
  translation label. Test: `test_translation_readtime.py`, including the
  cache-deletion equivalence guard. Commit: `delta-F: read-time translation`.

---

## Regression list

Green in every phase from introduction onward:

- all prior suites
- schema / identifier-absence *(live since Phase 1 — `tests/test_schema_absence.py`;
  extended in Phase 4 by `tests/test_public_identifier_absence.py`, which covers
  the remote request path rather than only the schema)*
- edit-semantics state machine *(live since Phase 2 — `tests/test_edit_semantics.py`)*
- stage-gate + no-bypass *(both live — `tests/test_stage_gate.py` since Phase 5
  for the transition table and its HTTP 409; `tests/test_no_bypass.py` since
  Phase 6, testing the promise behaviourally and structurally)*
- barycentric maths *(live since Phase 2 — `tests/test_barycentric.py`, plus
  `tests/test_widget_backend_parity.py` holding the JS widget to the same goldens)*
- `patterns_20_anecdotes.json` byte-identical *(live since Phase 7 —
  `tests/test_patterns_golden.py`; regenerate deliberately with
  `python -m tests.regenerate_golden`, never automatically)*
- landscape peaks ±0.02 *(live since Phase 8 — `tests/test_landscape_golden.py`)*
- surface / contour single-source *(live since Phase 8 —
  `tests/test_landscape.py`)*
- whole-app integration *(added Phase 8 — `tests/test_whole_app.py`, one run
  through every feature in the order an operator uses them)*
- the error surface *(added Phase 9 — `tests/test_error_surface.py`, every
  operator-facing sentence in the backend read out of the source and held to
  the plain-English rule, plus the paths nobody wrote a message for)*
- original names *(added Phase 9 — `tests/test_original_names.py`, constraint 8
  and acceptance criterion 15 as a test rather than a promise)*
- scope completeness *(added in the completeness pass —
  `tests/test_scope_completeness.py`, every numbered item of PRD §1 checked
  against the code, because a phase plan cannot notice what it never scheduled)*
- frontend/backend alignment *(added in the completeness pass —
  `tests/test_api_alignment.py`, every address the browser can build against
  every route the server answers, in both directions)*

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

### Phase 2

12. **The anonymity statement is editable, with a canonical default.** PRD §1.1
    lists anonymity text as editable in the Studio, while constraint 9 demands it
    be literally true of the code. Resolved both ways: `CANONICAL_ANONYMITY_TEXT`
    in `backend/framework_schema.py` is the default for every new framework and
    every clause of it is asserted against the live schema in
    `tests/test_framework_schema.py`; the paper pack prints whatever the version
    actually says, verbatim. The Studio field carries a hint that only true
    claims belong there. PRD §9 assumption 12 already puts this class of
    judgement with the operator.
13. **A wording fix may not change structure.** Adding, removing or reshaping a
    signifier would strand significations pointing at the old shape, so
    `wording_fix` on a live framework refuses a structural change with a 409 that
    points at "Change meaning" instead. Assumption 12 asks the operator to judge
    *meaning*; structure is something the app can check, so it does.
14. **A meaning change leaves the parent untouched.** The PRD does not say what
    happens to the old version's `is_active`. Simpler option taken: the parent
    keeps its flag and its stories, and the newest version of a lineage is simply
    the highest `version`. This avoids inventing `is_active` semantics that
    Phases 3–4 would then have to honour.
15. **Version numbers come from the lineage, not the parent.** `_next_version`
    takes one past the highest version anywhere in the chain, so two meaning
    changes from the same parent get 2 and 3 rather than colliding on 2.
16. **`react/prop-types` is off.** React 19 removed runtime `propTypes`
    entirely, so the rule checks for something the framework ignores. Component
    contracts are documented in each module header instead. This was the only
    eslint rule firing across the whole frontend.
17. **The route guard reads the OpenAPI schema.** `tests/test_health.py`
    enumerated `app.routes`, but this FastAPI version represents an included
    router as one object with no `path` — so the Phase 1 guard silently stopped
    seeing routed endpoints. It now pins the exact allowed path set, and must be
    widened deliberately by whichever phase adds an endpoint.
18. **Widget/server maths parity is tested across languages.**
    `frontend/src/widgets/barycentric.js` mirrors `backend/barycentric.py` so the
    widget can place a marker without a round trip. Drift would silently corrupt
    placements, so `tests/test_widget_backend_parity.py` runs both against the
    same goldens via Node. It skips cleanly where Node is absent.
19. **Cartesian points carry more precision than weights.** Rounding points to
    the weights' own 6 decimals capped round-trip accuracy at exactly the
    precision the weights claim, so a there-and-back trip drifted by 1e-6.
    Points now keep 9 decimals; the round trip is lossless at 6.
20. **Playwright is not a project dependency.** It was installed briefly to
    verify the Studio renders, then removed. The Phase 2 gate is pytest + ruff +
    eslint; browser tooling belongs with the Phase 9 critique pass and its
    grayscale screenshot check.

### Phase 3

21. **A directly-captured story is stored `validated`, not queued.** Constraint 1
    gates *AI-organised* anecdotes and *AI-proposed* significations. A respondent
    who writes their own story and places their own markers is first-hand
    testimony with no machine in the loop, so queueing it would ask the operator
    to approve something no AI ever touched — and would stop the story reaching
    the live picture §0 promises the respondent. The no-bypass test in Phase 6
    covers the AI path, which is what that test is for. Significations from
    capture carry `signified_by=respondent`, `ai_confidence=NULL`, and a
    `validated_at` stamp.
22. **`source_type` is `capture` for both the wizard and paper entry.** The PRD
    does not enumerate the column. Ingestion will use its own value from Phase 5;
    `entry_mode` and `input_method` already carry the finer distinctions.
23. **Paper transcription is still `signified_by=respondent`.** The operator
    types it in, but the interpretation is the respondent's pen mark.
    `input_method=paper` is what records how it arrived.
24. **A skipped question stores nothing.** Forcing an answer would put a number
    in the dataset that nobody meant, and constraint 11 wants patterns computed
    from what people actually said. The wizard's button reads "Skip" until a
    placement is made.
25. **A triad that arrives not summing to 1.0 is normalised, not rejected.** It
    goes through the same `backend/barycentric.py` clamp the goldens pin down.
    A placement *outside* the shape — a negative weight, a dyad past its end, a
    chip off the square — is refused in plain English, because that is a broken
    submission rather than a rounding artefact.
26. **Enter saves in paper entry; Ctrl/Cmd+Enter saves from inside the story
    box.** PRD §1.2 says "Enter advances", but the story field needs real
    newlines for multi-paragraph transcription. The screen says so in its
    instructions.
27. **The respondent group is kept between paper entries.** A pile of returned
    sheets is usually one group, and re-picking it 30 times is exactly the
    friction §7.5's four-minute bar is measuring. The story and the placements
    clear; the group does not.
28. **Draft persistence takes its storage as an argument.**
    `frontend/src/capture/draft.js` never reaches for `window.localStorage`
    itself, so `tests/test_capture_draft.py` exercises the real module in Node.
    Constraint 9 reaches into the browser too: the storage key names the
    framework version, never the person, and a test asserts it.
29. **Voice is deliberately absent.** Constraint 10 requires voice always paired
    with typing, and PRD §6 puts voice in Phase 4. The typing path is built first
    so voice can be added beside it rather than instead of it.

### Phase 4

30. **Rate limiting is keyed by capture-link token, never by requester.** PRD §4
    asks for public endpoints that are both "rate-limited" and "identifier-free",
    and the usual key for a rate limit is the client IP — which constraint 9
    forbids this app from ever knowing. Keying on the token bounds abuse of an
    open LAN endpoint without singling out any respondent. Counters are in
    memory only and never persisted.
31. **The token decides the version, the entry mode and the link id.** The public
    submission model does not accept `entry_mode` at all and ignores any
    `framework_id` sent with it, so a respondent's browser cannot retarget its
    story or claim to have arrived another way. The *local* endpoint does accept
    `entry_mode`, limited to `admin | kiosk`, because there the caller is the
    operator's own machine.
32. **`imported` cannot be claimed by a live capture.** That value belongs to the
    ingestion pipeline; accepting it from a browser would let AI-derived content
    pose as first-hand testimony (constraint 1).
33. **Revoking is one-way.** A link that could be reopened would mean a QR poster
    taken down from a wall might start working again without anyone intending
    it. Closed links stay listed rather than disappearing, because hiding one
    would hide where its stories came from.
34. **Capture URLs use the machine's LAN/Tailscale address, not loopback.** A QR
    encoding `127.0.0.1` scans perfectly and then fails on every phone. The
    address is found by asking the OS which local interface it would route from;
    no packet is sent and nothing is looked up over the network. A test asserts
    the URL is not loopback.
35. **The app now serves the built frontend.** A capture link is only a capture
    link if a scanned QR reaches the wizard, so `backend/main.py` mounts
    `frontend/dist` when it exists. Unknown paths fall through to `index.html`
    so `/c/{token}` survives a reload; unmatched `/api` paths still return the
    PRD §4 JSON error rather than being handed HTML. This also closes the
    "launcher starts only the server" gap noted after Phases 1–3.
36. **A story that used voice at all is stamped `voice`.** Constraint 3 wants the
    input method recorded; when someone dictates and then edits by hand, the
    dictation is the part a later reader would want flagged.
37. **The voice button hides itself where speech is unsupported**, rather than
    sitting there dead. An offer that cannot be accepted is worse than no offer,
    and typing is already the working path. Where the browser *claims* support
    and then fails — which is what headless Chromium does — the §7.12 fallback
    fires with a plain-English message.
38. **`qrcode` and `pillow` added.** Pure-Python QR generation plus PNG output.
    Pillow ships self-contained wheels, so this is not the class of native
    dependency PRD §9 assumption 11 ruled out when it chose browser printing
    over a PDF library — and PRD §1.7 needs PNG chart export from Phase 7
    regardless.
39. **Kiosk resets after six seconds.** Long enough to read the thank-you, short
    enough that the next person at the table does not see the last person's
    answers. The exit control is deliberately small and cornered: whoever is at
    the keyboard in kiosk mode is a respondent, not the operator.

### Phase 5

40. **`/propose` is Phase 6; its gate is enforced from Phase 5.** PRD §6 puts
    the stage machine and the 409 stage-gate test in Phase 5 but Stage B in
    Phase 6, and acceptance criterion 7's "`/propose` is impossible before
    confirmation" is a whole-project criterion. Building a `/propose` endpoint
    now with nothing behind it would be a stub, and the session rule forbids
    building ahead. So the *transition table* is complete now — including the
    `mapping_confirmed → proposed` edge Phase 6 will hang Stage B on — and
    `tests/test_stage_gate.py` states the guarantee as a property of the table:
    with `mapping_confirmed` removed, `proposed` is unreachable from every
    earlier stage. The HTTP route arrives with the handler that needs it.
41. **Parsing happens at upload, Stage A at Organise.** The PRD names an
    `uploaded` stage before `organised`; the simplest thing that distinguishes
    them is that reading the file is deterministic and offline while organising
    it is not. So an unreadable file is refused while the operator is still
    looking at the file picker, no copy of the original has to be kept, and the
    AI is only ever shown the parsed text — never the document.
42. **Stage A's proposal is checked against the file before it is shown.** A
    locator, sheet, or column the file does not have stops the import with a
    plain-English message rather than being silently dropped or offered to the
    operator. The confirmation endpoint re-checks the operator's own mapping
    against the file independently, so the guarantee does not rest on Stage A
    behaving.
43. **Stage A output lives on the import job, not in `anecdotes`.** Constraint 1
    says no AI-organised anecdote enters the dataset without validation, so
    nothing in Phase 5 writes to `anecdotes` at all. `normalised_json` holds
    `{document, stage_a}` and `column_mapping_json` holds
    `{sheets|accepted, reconciliation, candidates}` — both existing columns, no
    schema change (constraint 5).
44. **A recoverable AI failure leaves the job where it was.** `failed` is
    terminal in the transition table, so parking a job there because the network
    blinked would force a re-upload. The reason is written to `error_message`
    and the stage is untouched, so Organise can simply be clicked again.
45. **`/mapping` is the one confirmation door for both file classes.** Tables
    send a column mapping; prose sends the list of passages the operator kept.
    Sending the wrong shape is refused rather than treated as "accept
    everything" — one endpoint, one human yes, whatever the file was.
46. **Spreadsheet candidates carry no confidence.** No model read those cells;
    Stage A only named the column. An empty confidence is honest where a
    fabricated 1.0 would not be, and constraint 2's amber rule then applies only
    where a model actually made a judgement.
47. **The reconciliation is a display object that must balance.** Constraint 12
    asks for exact row reconciliation, shown — so it is computed as labelled
    lines plus a total, and a tally whose lines do not sum to the file's own row
    count stops the import instead of being displayed.
48. **A docx is prose; its tables are not read.** A table of responses belongs in
    the tabular path, where it gets a confirmed column mapping and exact row
    reconciliation. Reading Word tables as loose paragraphs would smuggle table
    data past constraint 12.
49. **Five parser dependencies added** — `python-docx`, `pypdf`, `python-pptx`,
    `openpyxl`, `python-multipart` — plus `anthropic` for the live path. All
    self-contained wheels, none of the native class §9 assumption 11 ruled out.
    The test suite writes its own PDF by hand rather than adding a PDF *writer*.
50. **`tests/` is now a package.** One `__init__.py`, so the shared file fixtures
    can be imported by name rather than by sys.path luck.
51. **The gate exports `NL_MOCK_AI=1`, and so does `conftest.py`.** Constraint 6
    wants zero network in the suite; setting it in both places means neither a
    bare `pytest` nor `./run_checks.sh` can reach out. A structural test asserts
    `ai_client.py` is the only module in `backend/` that so much as names the
    service.

### Phase 6

52. **`backend/dataset.py` is the single definition of "in the data".** The
    no-bypass promise cannot be tested if it is spread across a dozen `.where()`
    clauses, so `only_validated()` states it once and everything downstream reads
    through it. `tests/test_no_bypass.py` then tests the promise structurally as
    well as behaviourally: exactly two modules may write `validated` — capture,
    where no AI was involved, and the queue, where a person just said yes.
53. **Accepting keeps `signified_by="ai"`.** The honest record is that a model
    placed the marker and a person agreed with it; restamping it as the
    analyst's would read, later, as though a human had made the judgement from
    scratch. What accepting adds is `validated_at`.
54. **Correcting restamps per placement, not per story.** A placement the
    operator left exactly as proposed keeps `ai` and its confidence; one they
    moved becomes `analyst` with no confidence. Restamping the whole story would
    overstate their involvement in the parts they agreed with.
55. **A rejected story keeps its placements and never gets `validated_at`.** It
    stays on disk so the import remains auditable, and `only_validated` excludes
    it — "not data" and "deleted" are different things.
56. **Stage B names the framework in the request; the operator picks it.** A file
    of stories carries no idea which triads it should be read through, and
    guessing would bind stories to wording nobody chose. The anecdote is then
    bound to that exact version, as a captured story is.
57. **Imported stories are `entry_mode=admin`, `source_type=import`.** The three
    entry modes are about how a *respondent* met the wizard; a file was brought
    in by the operator at their own machine. `source_type` is what distinguishes
    a file from first-hand testimony, and `input_method=imported` says the rest.
58. **A file reaches `done` when its queue empties, not when Stage B ends.** The
    last transition of the stage machine is therefore reachable only by a person
    working through the queue — which is the same guarantee as constraint 1,
    stated as the shape of the machine.
59. **There is no "accept all".** A bulk approve is the operator not looking, and
    constraint 1 asks for explicit human validation rather than a fast way past
    it. Three buttons per story, and no fourth.
60. **The two placement converters live in `capture/placements.js`, not in
    `Wizard.jsx`.** Plain JavaScript with no JSX, so Node can load them and
    `tests/test_placement_shape_parity.py` can take a value the Python side
    actually produced all the way to the widget shape and back. That test exists
    because the trip home was missing and the queue crashed on it; see "Fixed".

### Phase 7

61. **The §5b sort is served, not drawn.** Every categorical view returns its
    bars already ordered by value, with ties broken alphabetically so the order
    cannot wobble between runs. A chart therefore cannot be drawn unsorted by
    forgetting to sort it, and the grammar rule is testable against the API
    rather than only against a screenshot.
62. **An option nobody chose still gets a bar.** A zero is a finding; dropping
    it would quietly redraw the question the operator asked.
63. **Shares are of the stories that answered, not of the view.** A skipped
    question is not a zero — nobody said nothing on purpose — so each chart
    carries its own `answered` count as the denominator.
64. **One version by default; `mixed=true` to span the lineage.** PRD §4 forbids
    *silent* mixing rather than mixing, so the endpoint answers for exactly one
    framework version unless asked, and a mixed answer carries the per-version
    counts the chip needs. The questions drawn are always the version the
    operator is looking at.
65. **`load_rows` is shared by patterns and both exports.** A downloaded CSV is
    exactly the rows the charts were drawn from — same version scope, same
    filters. An export covering a different set than the screen above it would
    be worse than no export.
66. **The CSV is one row per story.** `signified_by` lists every distinct value
    across that story's placements — `ai|analyst` after a partial correction,
    which is the case the column exists for — and `lowest_ai_confidence` carries
    the weakest thing anyone agreed to. One row per placement would repeat every
    story text; per-placement columns would double the width for a rare case.
67. **Brief headlines are written separately from brief bullets.** A bullet
    starts by naming the question, which is right in a list and wrong as a
    title: "On *What drove this?*, stories pull towards Speed" reads as a topic
    with a finding attached. The headline templates lead with what was found
    (constraint 13f).
68. **The brief refuses to find a pattern in fewer than three stories**, and says
    so instead. It also records the filters it was taken under and warns when a
    view mixes versions — a brief that did not say what it excluded would
    mislead.
69. **The golden is regenerated by a separate command.** `python -m
    tests.regenerate_golden`, never automatically on failure: a golden that
    rewrites itself when it disagrees is a comment, not a test.
70. **The golden fixture cycles its provenance fields at different periods.**
    Cycling group, input method and entry mode together made them perfectly
    correlated, so every filter was really the same filter and combining two
    narrowed nothing. Caught by the first test that combined two filters.
71. **The live path is tested against a fake `anthropic` module.** Injected into
    `sys.modules`, so the suite still runs with zero network while checking the
    request that actually goes out: the pinned model, temperature 0, the system
    prompt, and the repair turn's message list.
72. **Triads are not drawn in Phase 7.** PRD §1.5 lists the supporting charts as
    demographics and MCQ bars, dyads as strip + histogram, and stones as a 2D
    scatter; triads belong to the Landscape, which is Phase 8. The endpoint
    returns triad points — they are 2D aggregation and part of the golden — but
    the screen leaves that space to the phase that owns it.

### Phase 8

73. **No 3D library.** The terrain is 4,096 quads projected by hand onto a
    canvas and sorted back to front. A WebGL engine would be hundreds of
    kilobytes for a workload this size, and one driver away from a blank
    rectangle on the single laptop that matters (constraint 4, constraint 7).
    The projection lives in plain JS so Node can test it.
74. **One grid, handed out once.** `compute()` produces a single density array;
    the surface reads it, the contour's levels are shares of its own maximum,
    and both travel in one response. The twin is not a second calculation that
    agrees — it is the first calculation seen from above (constraint 13b).
75. **Split panels share a density scale.** Two terrains drawn to their own
    maxima look equally tall however many stories each holds, which defeats the
    comparison a split exists for. Each panel keeps its own `max_density`
    alongside the shared `scale_density`.
76. **A hill with no stories under it is not a peak.** Smoothing invents ridges
    between clusters; a peak has to have marks beneath it or it is an artefact.
    Peak counts are stories near the peak, not density values — "nine stories
    sit here" is checkable, "0.83" is not.
77. **Too few or too alike gives no surface, and says so.** Fewer than three
    distinct placements has no area for a density estimate, so the view shows
    the marks as they are rather than a smooth hill over four points.
78. **k-means uses only dimensions every story answered.** Filling a gap with a
    mean would invent an answer; dropping the story would silently shrink the
    picture. Centres are returned in the reader's own units.
79. **MCQs are not Explorer axes.** Plotting a category on an axis would invent
    an order the operator never wrote.
80. **The landscape uses `one_triad`, not the whole aggregate.** Building every
    bar and histogram to draw one triangle was the difference between meeting
    and missing PRD §4's 200ms at a thousand stories.
81. **Budgets are measured as a median of repeated calls.** A single sample on a
    shared machine measures the neighbours, not the app; a first call also pays
    for caches it never pays for again. `tests/conftest.py::median_ms` is now
    the one way this suite times an endpoint. Two flaky budget assertions were
    converted to it after one failed at 268ms against a true median of 122ms.
82. **The story browser is not in Phase 8.** PRD §6's Phase 8 list ends at the
    region drill, and §1 scope item 6 (full-text search, tag, star) is never
    assigned a phase. The region drawer covers "the stories beneath it"; the
    browser is left for Phase 9 or a v2 decision rather than smuggled in here.

### Phase 9

83. **The floor is per slice, and it is applied after the filter.** Five is the
    total below which "What We Heard" shows nothing at all; it is also the
    minimum any single answer needs before it is named. A filtered view is a
    smaller room, so the ten kiosk stories can be over the floor as a set while
    not one of their answers is — and then the page says so rather than
    disappearing.
84. **Suppression is stated, never silent.** A question whose every answer is
    too thin keeps its heading and says that nothing under it can be shown. A
    reader who cannot see that something is missing reads the remainder as the
    whole, which is a worse failure than showing less.
85. **The headline obeys the floor too.** `_headlines` takes the floor as an
    argument: `MIN_FOR_FINDING` (3) for the analyst's brief, `SUPPRESSION_FLOOR`
    (5) for the summary that goes back to the room. Without it "Deck told most
    of the stories (3 of 8)" would have walked a slice of three past the
    suppression the bullets below it apply.
86. **One error shape, everywhere, as PRD §4 states it.** FastAPI nests an
    `HTTPException` detail under `detail`, so the app was emitting
    `{"detail": {"error": …}}` from its own refusals and `{"error": …}` from the
    catch-all. A handler now unwraps it, and every failure — ours, the
    framework's 404 and 405, a malformed request, and an unhandled fault — leaves
    as `{"error": {code, message, action}}`. The tests were updated to read the
    one shape.
87. **A validator's rejection keeps its status code and loses its body.** The
    422 stays (it is what the anonymity tests assert on, and the operator never
    sees a number); the field dump is replaced by a sentence that names the part
    that could not be read.
88. **"Question set" is the operator's word for a framework.** The code, the
    schema and the PRD all say framework; the Studio said both. Every visible
    string now says question set, and `tests/test_empty_states.py` holds it.
89. **The critique pass removed one element per view.** The shell: the dead
    "coming soon" branch and its CSS, with the brand promoted to the page's only
    `h1`. The Studio: the schema field path in the edit log, replaced by the
    Studio's own words for the same field. The Landscape: the row of triangle
    buttons when there is only one triangle, which becomes the caption it always
    was. The supporting charts: any categorical chart with a single answer at
    100%, which is a fact rather than a comparison and lives in the CSV. Import:
    a duplicated CSS rule under a name left over from "coming soon".
90. **Corner labels are sized in screen pixels, not canvas units.** The terrain
    draws in a fixed 640-unit space stretched to whatever width it is given, so
    a 13-unit label landed at about 7px on a 375px phone — half §5b's floor. The
    font is now scaled by how much the canvas was squeezed, and a resize
    redraws.
91. **Empty states are checked by reading the source.** There is no DOM test
    harness in this project, and adding one to assert on eleven sentences would
    be heavier apparatus than the thing it guards. The test asserts what a
    reader can confirm by eye: every screen has empty-state copy, and that copy
    names a next step.
92. **The trademark scan excludes the PRD and CLAUDE.md.** They are the
    specification and the standing instructions, and they *state* constraint 8.
    A rule that forbade quoting itself would be a strange rule. Everything that
    ships is scanned, and the README carries exactly one attribution paragraph,
    counted as a paragraph rather than a line — where a sentence wraps is a fact
    about the editor, not about how many times the app names somebody else's
    product.
93. **A wording fix carries the answers, not just the words.** Renaming a triad
    corner, a stones chip or an MCQ option rewrites the stored answers in the
    same transaction, positionally. The alternative — making every reader
    tolerant of a label it no longer recognises — would have spread the problem
    across patterns, the landscape, the exports and the queue, and left the
    database holding words the framework does not contain. One invariant is
    better than four kindnesses: a stored answer always uses its own version's
    current labels.
94. **The launcher opens the app, not its health check.** `Start Narrative
    Lens.bat` pointed the browser at `/api/health`, so a successful start looked
    like a page of JSON. It now polls health for up to fifteen seconds — the
    ceiling acceptance criterion 1 sets — and opens the app itself, and it
    refuses to start with a plain sentence if the frontend has not been built.
    Still never executed on Windows.

### Completeness pass

95. **Stars are a reserved tag, not a new column.** PRD §3 ends with "no further
    schema in v1", and the tags table is already there. ``__starred__`` is
    refused as a typed tag so the two can never be confused.
96. **The browser reads validated stories only**, like every other view. What is
    still waiting belongs to the validation queue, which is a different screen
    with a different job.
97. **"Export selected" is the CSV endpoint with an ``ids`` parameter**, not a
    fourth export. One code path means a selection cannot quietly become a
    thinner kind of export than the whole dataset (constraint 3).
98. **Search is plain ``LIKE`` with the wildcards escaped.** A search index
    would be a seventh table; at this app's scale the difference is not
    something an operator could feel, and "50%" is a thing people write.
99. **The read path carries rows, not mapped objects.** ``load_rows`` selects
    columns, and every reader downstream works unchanged because attribute
    access is identical. Writers still use the mapped classes; this is the read
    side only.
100. **The budget test asserts our share, not scipy's.** At five thousand
     stories the density estimate is 165ms of the request and the PRD pins the
     library that does it. A test that asserted the total would fail on a slow
     machine and pass on a fast one while the app got worse; a test that
     subtracts the estimate catches the thing we can actually control.
101. **Three switchers, one pattern.** The capture modes and import views gave
     up their ``role="tablist"`` rather than grow the arrow-key navigation and
     tabpanels that pattern promises. The simpler option, and now the app
     announces every switcher the same way.

### Delta phase A

102. **`signified_by` does not go into `FILTERABLE`.** The delta says to add it
     there, but `FILTERABLE` holds *anecdote* columns, and three things read it
     that way: the demographic charts, the landscape's split, and
     `distinct_values`, which does `getattr(Anecdote, field)`. A signification
     column in that tuple would offer "split the landscape by signified_by" and
     then fail on the attribute. The vocabulary lives beside `FILTERABLE` in the
     same module instead, and `signified_by_clause` is the one place it becomes
     SQL. The behaviour the delta asks for — the filter and its default on every
     read — is unchanged; only where the constant sits differs.
103. **The filter narrows placements, never stories.** A story whose markers an
     analyst placed still exists and was still told by somebody. So `total` is
     the same under all three choices and only the placements move. Dropping the
     story would be a stronger claim than constraint 14 makes.
104. **`counts_by_signified_by` counts placements, not stories.** A single story
     can hold both kinds at once — that is exactly what a corrected import looks
     like — so a per-story count would have to pick one and lie about the other.
105. **The counts are deliberately not narrowed by the choice in force.** Both
     halves come back under every view, because a screen has to be able to name
     what it is *not* showing as well as what it is.
106. **The old golden is compared with the delta's two envelope fields stripped.**
     `patterns_20_anecdotes.json` pins the aggregate — every count, share, point
     and sort order — and it cannot also pin fields that did not exist when it
     was written, which the delta forbids regenerating. `DELTA_ENVELOPE_FIELDS`
     is lifted out before the comparison, and those two fields are pinned instead
     by the new participant golden, which is free to hold them.
107. **`regenerate_golden.py` takes a selector.** `python -m tests.regenerate_golden
     participant` writes the one new file without touching the two baselines the
     delta protects. The whole-file behaviour is unchanged when no name is given.
108. **The CSV gains a column rather than changing one.** `title` still means
     what it has always meant — the machine's first eighty characters — and
     `respondent_title` sits beside it. Both are exported, as delta §3 requires,
     and no existing column silently changes meaning in a spreadsheet somebody
     already has.
109. **The region drill reads titles through the story browser's `ids`
     parameter**, the same idiom "export selected" already uses, rather than a
     new endpoint. It is a filter on the same scope as everything else, so a
     drill can never surface a story the version or validated rule excludes.
110. **The story name is searchable.** The browser already searched the story and
     its machine title; leaving the one title a person chose out of the search
     box would have made it the only title the operator could not find by.

### Delta phase B

111. **Centre-parking is measured on triads only.** The delta names the triad
     centroid, and the signal means something precise there: a three-way
     trade-off is what people duck when a question does not fit. A dyad's
     midpoint and a stones grid's middle are real places, but "parked" would be
     a different claim about each. The other kinds report `null` rather than
     `0` — "does not apply", not "nobody parked", which would be false.
112. **The radius comes from an area share, not from a number somebody liked.**
     "A small radius" is not a measurement. The circle is fixed at a tenth of
     the triangle's area and the radius derived from it (≈0.117 of a side), so
     the panel can say the one thing that makes a proportion readable: an even
     spread would put about 10% in this circle, and this is more. A test checks
     the circle really is a tenth, and that it fits inside the triangle so the
     share is not clipped.
113. **`/api/quality` takes the provenance filter, though delta §4 does not list
     it there.** Constraint 14 governs "every view that aggregates
     significations", and this one does. A skip rate pooled across the
     storytellers' own readings and somebody else's would be exactly the silent
     mixture the constraint forbids, so the endpoint takes the same choice with
     the same default and reports `signified_by_applied` like the others.
114. **"Answered" counts stories, not rows.** The stones signifier stores one
     row per chip, so counting rows would report three answers from one story —
     and then a negative skip count. Counted with `COUNT(DISTINCT anecdote_id)`,
     with a test that places three chips and expects one answer.
115. **The budget test is a ratio against the patterns endpoint in the same
     run.** Carrying forward what phase A learned the hard way: an absolute
     millisecond ceiling is not machine-independent, and these containers differ
     by a factor of three on Python work. Patterns is the right yardstick —
     same scope query, same filter, same rows, already budgeted at 200ms by the
     PRD — and this endpoint does strictly less, so it must come in under it. It
     measured 246ms against patterns' 670ms here, about a third.

---

## Fixed

Bugs found and fixed, newest first.

0. **The 5,000-story budget test failed on a slower machine than the one that
   set it, and its replacement threshold was wrong twice**
   *(delta phase A, found by running the gate before starting work)*.
   `test_five_thousand_stories_cost_almost_nothing_beyond_the_estimate`
   subtracted scipy's density estimate and then asserted our remaining share was
   under an absolute 120ms. Subtracting scipy made the number look
   machine-independent, but it is not: our share scales with the machine exactly
   as scipy's does. Here scipy alone took 224ms against the 165ms the threshold
   was written on, and our share came to 160ms — a slower box, not a regression,
   confirmed because the only backend change since was to `stories.py`, which the
   landscape never calls.

   The first fix — assert our share is under the estimate, a ratio rather than a
   number — was **also wrong**, and only looked green because it sat exactly on
   this container's boundary. Run repeatedly it failed about one time in three.
   The two halves do not scale together: our half is Python and SQLite, scipy's
   is vectorised arithmetic, so the healthy ratio is 0.35 on the container that
   set the original number and about 0.7 here. Two further things came out of
   measuring it properly: cold-start samples were inflating the figure (both
   sides are now warmed once before timing), and phase A's own additions were
   ruled out as the cause — `signified_by_counts` costs 3ms of a 412ms request,
   and the same benchmark on stashed pre-delta code gave 380ms.

   The bound is now `OWN_SHARE_CEILING = 1.5`, with headroom above both measured
   healthy values. **This makes the test coarser than it was meant to be, and
   that is recorded rather than papered over:** re-running the original mutation
   here — reinstating ORM hydration on the landscape path — moves the ratio only
   from ~0.7 to ~1.1, so on this container that mutation now passes. The test
   catches a runaway, not a small regression. The precise form of the budget is
   PRD §4's 200ms, and it can only be checked on the machine the operator runs.
   `tests/test_landscape.py`.

1. **Every read endpoint was over its budget at the size the PRD names**
   *(completeness pass, found by measuring where PRD §4 says to measure)*. The
   suite tested the landscape at 1,000 stories; §4 sizes the budget at 5,000.
   At five thousand the landscape took 455ms and patterns, explorer, clusters
   and the CSV were all over 200ms too. Most of it was work nobody needed:
   SQLAlchemy entities built so they could be written to, on a path that only
   reads; one triangle's answers loaded alongside every other question's; numpy
   called on single scalars; and every placement validated twice, once on the
   way out of the database and once on the way into the maths. Landscape 455 →
   222ms, patterns 321 → 167, explorer 251 → 159, clusters 306 → 200, CSV 303 →
   240, brief 350 → 195. What is left of the landscape is one scipy call the
   PRD pins us to, so the new budget test asserts the share the app controls
   rather than scipy's.
2. **The supporting-charts picture painted a black square over the scatter**
   *(completeness pass, found in a real browser)*. The export clones each
   chart's SVG, and a clone leaves the stylesheet behind — so the stones frame,
   which has `fill: none` in CSS and no fill of its own, defaulted to black and
   covered the data. Fixed by copying each element's resolved style onto the
   copy rather than guessing from its class name.
3. **Two switchers claimed an ARIA pattern they did not implement**
   *(completeness pass)*. The capture modes and the import views were marked
   `role="tablist"`/`role="tab"` with no tabpanel to move into and no arrow-key
   navigation — a promise to a screen reader that the app did not keep. They are
   now plain buttons with `aria-current`, the same as the Patterns
   sub-navigation, so all three switchers are announced the same way.
4. **A wildcard typed into the search box was treated as one**
   *(completeness pass)*. "50%" and "shift_notes" are things people write in
   stories; `%` and `_` are now escaped, so a search returns what the operator
   asked for.
5. **A wording fix that renamed a corner stranded every answer under it**
   *(Phase 9, found by the end-to-end mock run — no unit test could have caught
   it, because every piece was behaving exactly as written)*. Three of the four
   signifier kinds store an answer by its label: a triad is `{corner: weight}`,
   stones name their chip, an MCQ lists the options chosen. A wording fix is
   allowed to rewrite those labels — renaming "Care" to "Carefulness" is the
   textbook case the guardrail blesses — and when it did, every stored answer
   was left keyed by a word the framework no longer had. The Patterns tab then
   failed outright on a renamed triad corner, and a renamed option or chip
   quietly stopped being counted, which is worse. A wording fix now carries the
   answers with the words, positionally — sound because the structural check
   has already refused anything that adds, removes or reshapes. Five tests in
   `TestARenameCarriesTheAnswers` hold it; four of them fail if the migration
   is removed.
6. **Five found in the Phase 9 critique pass, four of them in a real browser.**
   (a) *The launcher opened a page of JSON.* `Start Narrative Lens.bat` sent the
   browser to `/api/health`, so a perfectly successful start looked like a
   failure to anyone who is not a developer. It now waits for health and opens
   the app. (b) *Terrain corner labels shrank below the legibility floor on a
   phone* — 13 canvas units in a 640-unit space stretched to 343px is about 7px
   on screen, against §5b's 12px floor. Scaled by the squeeze, and redrawn on
   resize. (c) *"Waiting for you" ran into "before it counts"* on the Import
   tab: JSX drops the line break between an element and the text after it. (d)
   *A chart that could only ever say 100%* — the source-type breakdown with one
   answer — was drawn as a bar chart with nothing to compare. (e) *A duplicated
   CSS rule* for `.nl-import__soon`, under a class name left over from before
   the tab was built.
7. **The landscape was buried under the filter rail on a phone** *(Phase 8,
   found in a real browser)*. The rail comes first in source order, which is
   right for a screen reader and for the keyboard — but stacked on a 375px
   screen it put the terrain 1,264px down the page. Constraint 13a makes the
   landscape the visual anchor, and an anchor nobody sees without scrolling past
   a column of dropdowns is not one. Fixed with `order: -1` on the main column
   under 60rem, so the picture leads visually while the rail still leads for
   assistive technology. `frontend/src/patterns/patterns.css`.
3. **Corner labels were clipped off both landscape views** *(Phase 8, found in a
   real browser)*. On the terrain, "Cost" ran past the canvas edge and was cut
   to "ost" — and which side each corner lands on changes as the view rotates,
   so a fixed alignment cannot be right. On the contour, "Speed" arrived as
   "peed" because the base labels were anchored outwards from their corners.
   Fixed by aligning terrain labels from where they actually landed and clamping
   them inside the canvas, and by anchoring the contour's base labels inwards.
   Confirmed by asserting no ink touches the canvas border and no text box
   escapes its SVG, at both widths and after a large rotation.
   `frontend/src/patterns/Landscape.jsx`.
4. **Chart labels were clipped away wherever they ran long** *(Phase 7, found in
   a real browser)*. Three separate cases of the same mistake: bar values wide
   enough to read "20 · 100%" ran past the viewBox and were cut to "20 · 10";
   a stones axis label like "Fraught" set horizontally beside the square ran off
   the right edge; and a median of exactly 0.00 or 1.00 put its centred label
   outside the plot entirely. SVG clips silently rather than wrapping, so each
   one lost information without any sign that it had. Fixed by measuring the
   value column against its widest case, setting the vertical axis along itself,
   and clamping the median label inside the plot. Confirmed by walking every
   chart on both framework versions at 1280px and 375px and asserting no text
   box escapes its own SVG. `frontend/src/patterns/Charts.jsx`.
4. **The validation queue crashed on every stored triad** *(Phase 6, found in a
   real browser)*. The widgets take a triad as three ordered numbers; the server
   stores it keyed by corner label. The wizard had a converter one way
   (`toSubmission`) and none the other, so the queue handed a widget the database
   shape, its maths tried to destructure an object as an array, and React took
   the whole screen down — a blank page, not an error. Fixed by adding
   `fromStored` beside `toSubmission`, moving both into plain-JS
   `frontend/src/capture/placements.js`, and adding
   `tests/test_placement_shape_parity.py`, which runs a value the Python side
   actually produced through Node to the widget shape and back. Confirmed the
   test fails if the bug is reintroduced.
5. **`.nl-check` was already the Studio's checkbox row** *(Phase 6, found in a
   real browser)*. Global CSS, two files, one class name — the queue card
   inherited `display: flex` from `studio.css` and laid the story, the widgets
   and the buttons out as three columns. Renamed the queue's classes to
   `nl-verify*`. `frontend/src/import/import-tab.css`.
6. **Every question was printed twice in the queue** *(Phase 6, found in a real
   browser)*. The widget draws its own caption, and the queue added a heading
   above it. Removed the heading and left the confidence figure in its place.
   `frontend/src/import/ValidationQueue.jsx`.
8. **The reconciliation table pushed the phone sideways** *(Phase 5, found in a
   real browser)*. `.nl-tally` had a `min-width` of 22rem, which with the page's
   own padding came to 384px — 9px past constraint 10's clean-375px bar. Fixed
   with `min-width: min(22rem, 100%)`, so the figures still get their own column
   on a laptop and the phone still does not scroll sideways.
   `frontend/src/import/import-tab.css`.
9. **"Patterns— coming soon" ran together in the nav** *(Phase 2, found in a real
   browser while checking Phase 5)*. The leading space of an inline element is
   collapsed, so the label ran straight into the dash. Fixed with a
   non-breaking space. `frontend/src/App.jsx`.
10. **A submitted story left its draft behind** *(Phase 3, found in a real
   browser)*. `submit()` cleared the draft, then navigated — and navigation
   re-saved it. The next visitor would be offered "pick up where I left off" for
   a story already sent, and could submit it twice. Fixed with a ref checked
   inside the save path: React state would not have updated within the same
   handler that does the submitting. `frontend/src/capture/Wizard.jsx`.
11. **Nav tabs overflowed the screen at 375px** *(Phase 2, found in a real
   browser)*. Four tab labels plus their "coming soon" notes did not fit on one
   line, pushing the page 36px wider than the viewport and breaking constraint
   10's clean-375px bar. Fixed by letting `.nl-nav__list` wrap.
   `frontend/src/app.css`.
12. **A 404 on every page load** *(Phase 2, found in a real browser)*. No favicon
   was declared, so the browser requested `/favicon.ico` and logged a console
   error. Fixed with an inline SVG data-URI icon, which also keeps the app off
   the network entirely (constraint 4). `frontend/index.html`.
