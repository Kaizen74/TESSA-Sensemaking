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
- schema / identifier-absence *(live since Phase 1 — `tests/test_schema_absence.py`;
  extended in Phase 4 by `tests/test_public_identifier_absence.py`, which covers
  the remote request path rather than only the schema)*
- edit-semantics state machine *(live since Phase 2 — `tests/test_edit_semantics.py`)*
- stage-gate + no-bypass *(arrives Phase 5–6)*
- barycentric maths *(live since Phase 2 — `tests/test_barycentric.py`, plus
  `tests/test_widget_backend_parity.py` holding the JS widget to the same goldens)*
- `patterns_20_anecdotes.json` byte-identical *(arrives Phase 7)*
- landscape peaks ±0.02 *(arrives Phase 8)*
- surface / contour single-source *(arrives Phase 8)*

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

---

## Fixed

Bugs found and fixed, newest first.

1. **A submitted story left its draft behind** *(Phase 3, found in a real
   browser)*. `submit()` cleared the draft, then navigated — and navigation
   re-saved it. The next visitor would be offered "pick up where I left off" for
   a story already sent, and could submit it twice. Fixed with a ref checked
   inside the save path: React state would not have updated within the same
   handler that does the submitting. `frontend/src/capture/Wizard.jsx`.
2. **Nav tabs overflowed the screen at 375px** *(Phase 2, found in a real
   browser)*. Four tab labels plus their "coming soon" notes did not fit on one
   line, pushing the page 36px wider than the viewport and breaking constraint
   10's clean-375px bar. Fixed by letting `.nl-nav__list` wrap.
   `frontend/src/app.css`.
3. **A 404 on every page load** *(Phase 2, found in a real browser)*. No favicon
   was declared, so the browser requested `/favicon.ico` and logged a console
   error. Fixed with an inline SVG data-URI icon, which also keeps the app off
   the network entirely (constraint 4). `frontend/index.html`.
