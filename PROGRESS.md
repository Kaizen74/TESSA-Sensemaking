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

---

## Fixed

Bugs found and fixed, newest first.

1. **The landscape was buried under the filter rail on a phone** *(Phase 8,
   found in a real browser)*. The rail comes first in source order, which is
   right for a screen reader and for the keyboard — but stacked on a 375px
   screen it put the terrain 1,264px down the page. Constraint 13a makes the
   landscape the visual anchor, and an anchor nobody sees without scrolling past
   a column of dropdowns is not one. Fixed with `order: -1` on the main column
   under 60rem, so the picture leads visually while the rail still leads for
   assistive technology. `frontend/src/patterns/patterns.css`.
2. **Corner labels were clipped off both landscape views** *(Phase 8, found in a
   real browser)*. On the terrain, "Cost" ran past the canvas edge and was cut
   to "ost" — and which side each corner lands on changes as the view rotates,
   so a fixed alignment cannot be right. On the contour, "Speed" arrived as
   "peed" because the base labels were anchored outwards from their corners.
   Fixed by aligning terrain labels from where they actually landed and clamping
   them inside the canvas, and by anchoring the contour's base labels inwards.
   Confirmed by asserting no ink touches the canvas border and no text box
   escapes its SVG, at both widths and after a large rotation.
   `frontend/src/patterns/Landscape.jsx`.
3. **Chart labels were clipped away wherever they ran long** *(Phase 7, found in
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
7. **The reconciliation table pushed the phone sideways** *(Phase 5, found in a
   real browser)*. `.nl-tally` had a `min-width` of 22rem, which with the page's
   own padding came to 384px — 9px past constraint 10's clean-375px bar. Fixed
   with `min-width: min(22rem, 100%)`, so the figures still get their own column
   on a laptop and the phone still does not scroll sideways.
   `frontend/src/import/import-tab.css`.
8. **"Patterns— coming soon" ran together in the nav** *(Phase 2, found in a real
   browser while checking Phase 5)*. The leading space of an inline element is
   collapsed, so the label ran straight into the dash. Fixed with a
   non-breaking space. `frontend/src/App.jsx`.
9. **A submitted story left its draft behind** *(Phase 3, found in a real
   browser)*. `submit()` cleared the draft, then navigated — and navigation
   re-saved it. The next visitor would be offered "pick up where I left off" for
   a story already sent, and could submit it twice. Fixed with a ref checked
   inside the save path: React state would not have updated within the same
   handler that does the submitting. `frontend/src/capture/Wizard.jsx`.
10. **Nav tabs overflowed the screen at 375px** *(Phase 2, found in a real
   browser)*. Four tab labels plus their "coming soon" notes did not fit on one
   line, pushing the page 36px wider than the viewport and breaking constraint
   10's clean-375px bar. Fixed by letting `.nl-nav__list` wrap.
   `frontend/src/app.css`.
11. **A 404 on every page load** *(Phase 2, found in a real browser)*. No favicon
   was declared, so the browser requested `/favicon.ico` and logged a console
   error. Fixed with an inline SVG data-URI icon, which also keeps the app off
   the network entirely (constraint 4). `frontend/index.html`.
