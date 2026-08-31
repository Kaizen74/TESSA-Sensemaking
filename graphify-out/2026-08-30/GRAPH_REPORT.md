# Graph Report - TESSA-Sensemaking  (2026-08-30)

## Corpus Check
- 144 files · ~132,896 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2383 nodes · 5704 edges · 115 communities (104 shown, 11 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 446 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9e589b89`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BarycentricError
- TestClient
- TestClient
- Framework
- make_engine
- TestClient
- test_import_pipeline.py
- TestClient
- request_json
- test_public_identifier_absence.py
- imports.py
- package.json
- validate_definition
- test_story_browser.py
- test_landscape.py
- parsers.py
- _run_node
- NormalisedDocument
- backend/patterns.py
- capture_links.py
- parse
- What You Must Do When Invoked
- Signification
- TriadChart
- get_session
- TestClient
- PRD: Narrative Lens — Local Narrative Sense-Making App
- Decisions
- test_explorer_clusters.py
- api.js
- test_capture_draft.py
- Widgets.jsx
- test_schema_absence.py
- test_error_surface.py
- test_terrain_maths.py
- clusters.py
- test_patterns.py
- StonesAxis
- aggregate
- build_golden_dataset
- voice.js
- ImportTab.jsx
- _FakeAnthropic
- Wizard.jsx
- Studio.jsx
- test_queue.py
- The session loop (every session, no exceptions)
- Data Visualization Reference — 2026
- FrameworkDefinition
- make_framework
- graphify reference: extra exports and benchmark
- Web Design & Data Visualization
- Anecdote
- backend/exports.py
- export_csv
- Design System Reference — 2026
- test_health.py
- MonkeyPatch
- Narrative Lens — binding project instructions
- graphify reference: query, path, explain
- State File Templates
- Narrative Lens — Latest
- Judgment Protocols — Anti-Drift & Anti-Hallucination
- Testing Protocol
- run_checks.sh
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- backend/__init__.py
- routers/__init__.py
- .claude/CLAUDE.md
- extraction-spec.md
- Narrative Lens
- tests/__init__.py
- narrative-lens
- test_placement_shape_parity.py
- plain_http_error
- ValidationQueue.jsx
- SubmittedSignification
- browse_stories
- Patterns.jsx
- paper_pack.py
- test_empty_states.py
- test_landscape_golden.py
- AiError
- mock_enabled
- test_stage_a_repairs_one_bad_reply_and_carries_on
- test_stage_gate.py
- routers/patterns.py
- test_original_names.py
- organise.py
- test_live_ai.py
- create_public_capture
- propose.py
- .estimated_minutes
- health
- regenerate_golden.py
- edit_semantics.py
- .exceeds_screen_warning
- test_scope_completeness.py
- test_edit_log_wording.py
- ImportJob
- conftest.py
- backend/stories.py
- env.py
- App.jsx
- TestFramework
- CaptureError
- patterns_fixtures.py
- field_validator

## God Nodes (most connected - your core abstractions)
1. `FrameworkDefinition` - 126 edges
2. `Anecdote` - 92 edges
3. `build_golden_dataset()` - 90 edges
4. `Signification` - 66 edges
5. `Framework` - 65 edges
6. `make_framework()` - 60 edges
7. `ImportJob` - 49 edges
8. `get_session()` - 44 edges
9. `parse()` - 41 edges
10. `NormalisedDocument` - 38 edges

## Surprising Connections (you probably didn't know these)
- `Shape` --uses--> `AiError`  [INFERRED]
  tests/test_ai_client.py → backend/ai_client.py
- `APIConnectionError` --uses--> `AiError`  [INFERRED]
  tests/test_live_ai.py → backend/ai_client.py
- `APIStatusError` --uses--> `AiError`  [INFERRED]
  tests/test_live_ai.py → backend/ai_client.py
- `_Block` --uses--> `AiError`  [INFERRED]
  tests/test_live_ai.py → backend/ai_client.py
- `_FakeAnthropic` --uses--> `AiError`  [INFERRED]
  tests/test_live_ai.py → backend/ai_client.py

## Import Cycles
- None detected.

## Communities (115 total, 11 thin omitted)

### Community 0 - "BarycentricError"
Cohesion: 0.05
Nodes (49): BarycentricError, from_value_json(), is_inside(), normalise(), _placed(), ValueError, Triad barycentric maths. A triad answer is a point inside an equilateral…, Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`. (+41 more)

### Community 1 - "TestClient"
Cohesion: 0.06
Nodes (39): RateLimiter, Rate limiting for the public capture endpoints (PRD §4). The public endpoints…, A sliding-window counter keyed by an opaque string. Deliberately simple and in-…, Record a hit and report whether it is within the limit., Forget counters. Used by tests and when a link is revoked., How many hits are still allowed in the current window., Clear every counter. Tests call this between cases., reset_all() (+31 more)

### Community 2 - "TestClient"
Cohesion: 0.09
Nodes (24): _framework(), TestClient, Local capture (PRD §6 Phase 3). The tests the PRD names for this phase: wizard…, PRD §9 assumption 7: reflection shows one signifier., Skipping every question is allowed; the story is the point., Constraint 3: provenance on every record., PRD §6 Phase 3: batch entry writes paper provenance., Constraint 9, at the moment a story is actually written. (+16 more)

### Community 3 - "Framework"
Cohesion: 0.12
Nodes (38): label_renames(), ``{signifier_id: {old_label: new_label}}`` for every renamed label. Only labels…, Framework, A version of the question set respondents see. ``parent_framework_id`` links…, _anecdote_count(), _apply_meaning_change(), _apply_wording_fix(), create_framework() (+30 more)

### Community 4 - "make_engine"
Cohesion: 0.16
Nodes (20): _connect_args(), make_engine(), SQLite needs ``check_same_thread=False`` to serve requests from a pool., Build an engine, enabling SQLite foreign-key enforcement. SQLite ignores…, Config, Engine, alembic_config(), fixture (+12 more)

### Community 5 - "TestClient"
Cohesion: 0.10
Nodes (23): _create_full(), _pack_html(), TestClient, The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar). Two…, PRD §1.2a: the story card carries respondent-group tick boxes., The pack renders the version's current wording, not a cached copy., Constraint 9: the anonymity statement is printed verbatim on the card., Whatever this version says is what the card prints — no substitution. (+15 more)

### Community 6 - "test_import_pipeline.py"
Cohesion: 0.11
Nodes (57): A two-sheet workbook: one of responses, one lookup table to ignore. The…, txt_bytes(), xlsx_bytes(), _confirm(), _confirmation_body(), _organise(), parametrize, Session (+49 more)

### Community 7 - "TestClient"
Cohesion: 0.11
Nodes (27): _add_story(), _create(), _definition(), Session, TestClient, The wording-fix vs meaning-change state machine (PRD §6, constraint 13g). This…, Constraint 7: the operator must be able to act on the message., A wording fix patches in place and appends to the edit log. (+19 more)

### Community 8 - "request_json"
Cohesion: 0.09
Nodes (30): _fenced_json(), _parse(), Any, Parse one reply strictly, or raise the reason it could not be parsed., Ask for one JSON object of the given shape, or fail in plain English. In mock…, Return *raw* with one surrounding markdown fence removed, if present. Strict…, request_json(), Payload (+22 more)

### Community 9 - "test_public_identifier_absence.py"
Cohesion: 0.15
Nodes (17): _clear_limits(), _framework(), _link(), fixture, TestClient, Constraint 9 on the remote path (PRD §6 Phase 4: identifier-absence test).…, Sweep every column of every table, not just the ones we expect., Structural guards: not "it doesn't today", but "it has no way to". (+9 more)

### Community 10 - "imports.py"
Cohesion: 0.11
Nodes (40): AppError, bad_request(), conflict(), not_found(), The error shape from PRD §4. ``{"error": {"code": ..., "message": plain-English…, An error the operator is meant to read and act on., Something outside the app misbehaved — currently only the AI service., upstream() (+32 more)

### Community 11 - "package.json"
Cohesion: 0.06
Nodes (30): eslint, @eslint/js, eslint-plugin-react, eslint-plugin-react-hooks, dependencies, react, react-dom, description (+22 more)

### Community 12 - "validate_definition"
Cohesion: 0.06
Nodes (21): default_definition(), Parse and validate a raw ``definition_json`` payload., A minimal, valid definition — what a brand-new framework starts from., validate_definition(), Validation of ``definition_json`` and the anonymity statement it carries., Significations key on the id alone, so one namespace covers all kinds., A typo in the Studio should fail loudly, not vanish silently., Constraint 10: ≤4 minutes typical. (+13 more)

### Community 13 - "test_story_browser.py"
Cohesion: 0.16
Nodes (28): _browse(), _mark(), TestClient, The story browser (PRD §1.6, §5.4). The last item of §1's scope, and the one…, Constraint 1, on the reading side. The queue is where pending lives., Constraint 3 shown, constraint 9 absent — the same as every other view., They share a table, so this is the join worth testing., It is stored as one, which is exactly why this is worth asserting. (+20 more)

### Community 14 - "test_landscape.py"
Cohesion: 0.09
Nodes (49): Every story inside a rectangle of grid cells, and no others. The region drill…, stories_in_region(), _capture(), _landscape(), _panel(), Session, TestClient, The landscape suite: the terrain, its contour twin, the drill, the clusters.… (+41 more)

### Community 15 - "parsers.py"
Cohesion: 0.12
Nodes (27): Block, _blocks_from_text(), _clean_row(), _decode(), _parse_captions(), _parse_csv(), _parse_docx(), _parse_pdf() (+19 more)

### Community 16 - "_run_node"
Cohesion: 0.11
Nodes (14): parametrize, Voice fallback (PRD §6 Phase 4, §7.12, constraint 10). Constraint 10 says voice…, The UI calls stop() on unmount whether or not voice ever started., Stopping on purpose is not a failure and must not show a warning., Constraint 10: voice always paired with typing., Interim results would rewrite a respondent's words as they speak., §7.12: voice fails plain-English with a working fallback., Constraint 7: no jargon a respondent cannot act on. (+6 more)

### Community 17 - "NormalisedDocument"
Cohesion: 0.12
Nodes (44): _balance(), Candidate, confirm(), confirm_narrative(), confirm_tabular(), ConfirmedExtraction, ExtractionError, BaseModel (+36 more)

### Community 18 - "backend/patterns.py"
Cohesion: 0.13
Nodes (39): point_from_value_json(), A stored answer straight to its point in the triangle. Exactly…, CaptureSettings, Dyad, Mcq, BaseModel, Validation for ``frameworks.definition_json`` (PRD §3 and §5). Every…, A 2D canvas on which the respondent places named chips. (+31 more)

### Community 19 - "capture_links.py"
Cohesion: 0.11
Nodes (30): qr_png_bytes(), QR codes for capture links (PRD §4, §1.8). A QR is how a phone gets to the…, Return a PNG of ``payload`` as QR, as raw bytes. Error correction is set to M…, capture_link_qr(), capture_url(), CaptureLinkCreate, CaptureLinkOut, create_capture_link() (+22 more)

### Community 20 - "parse"
Cohesion: 0.06
Nodes (56): organise(), Run Stage A over a parsed file and return its proposal. Nothing is written to…, parse(), Read one uploaded file into the normalised shape, or refuse it. Refusals are…, csv_bytes(), docx_bytes(), pdf_bytes(), _pdf_escape() (+48 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "Signification"
Cohesion: 0.21
Nodes (11): One respondent (or validated AI) placement on one signifier. ``value_json``…, Signification, _anecdote(), _framework(), parametrize, Constraint 3: provenance on every record., PRD §3: input_method is typed | voice | paper | imported., An old story stays on v1 when v2 appears (PRD §3). (+3 more)

### Community 23 - "TriadChart"
Cohesion: 0.10
Nodes (35): _axes(), Cell, _cell_index(), compute(), Landscape, LandscapePoint, _local_maxima(), _nearest_corner() (+27 more)

### Community 24 - "get_session"
Cohesion: 0.10
Nodes (29): get_session(), Session, Database engine and session plumbing (constraint 4: SQLite + local files)., FastAPI dependency yielding a session that always closes., mount_frontend(), FastAPI application. Endpoints arrive with the phase that needs them, per PRD…, Serve ``frontend/dist`` if it has been built. Returns whether anything was…, hour_rounded_now() (+21 more)

### Community 25 - "TestClient"
Cohesion: 0.14
Nodes (9): TestClient, List, create and fetch frameworks (PRD §4)., A new framework starts valid and empty, ready to fill in., The Studio shows these live while the operator edits., Constraint 7: plain English, with something to do about it., PRD §5.1: version history sidebar shows versions with story counts., TestCreate, TestFetch (+1 more)

### Community 26 - "PRD: Narrative Lens — Local Narrative Sense-Making App"
Cohesion: 0.10
Nodes (19): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 11. Changelog v1.2 → v1.3, 1. Scope, 2. Binding constraints (restate these in every session), 3. Data model (SQLite, via SQLAlchemy + Alembic), 4. API contract (FastAPI, all JSON), 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages). (+11 more)

### Community 27 - "Decisions"
Cohesion: 0.08
Nodes (23): Decisions, Fixed, Narrative Lens — Progress, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5 (+15 more)

### Community 28 - "test_explorer_clusters.py"
Cohesion: 0.16
Nodes (28): median_ms(), How long a call takes, measured as a median rather than a single sample. PRD §4…, _clusters(), _explorer(), TestClient, The 3D Explorer and the k-means overlay. Acceptance criterion 11: the Explorer…, PRD §9 assumption 8 pins the seed; the same stories always group the same., Acceptance criterion 11: always labelled "descriptive only". (+20 more)

### Community 29 - "api.js"
Cohesion: 0.16
Nodes (9): ApiError, CaptureTab(), MODES, LinkManager(), PaperBatch(), ReflectionPanel(), orderedSignifiers(), PhonePreview() (+1 more)

### Community 30 - "test_capture_draft.py"
Cohesion: 0.15
Nodes (18): Drafts survive a reload (PRD §6 Phase 3, §7.6). The draft lives in the browser,…, Nothing lingers once the story has been sent., Starting fresh is recoverable; crashing on load is not., A draft from an older shape must not crash the wizard., Private browsing must not stop someone telling their story., Constraint 9 reaches into the browser, not just the database., Offering to restore an empty draft would be noise., The whole point: a half-written story survives the page going away. (+10 more)

### Community 31 - "Widgets.jsx"
Cohesion: 0.24
Nodes (15): CORNER_0, CORNER_1, CORNER_2, normalise(), roundTo(), toBarycentric(), toCartesian(), TRIANGLE_HEIGHT (+7 more)

### Community 32 - "test_schema_absence.py"
Cohesion: 0.12
Nodes (21): _columns(), parametrize, Constraint 9 — respondent anonymity is engineered, not promised. These tests…, Constraint 9: respondent time is hour-rounded, so no exact clock exists.…, The only writer of ``created_at_hour`` carries no sub-hour information., 13:59 must land on 13:00, never 14:00 — truncation, not rounding., A row written through the ORM gets an hour-rounded stamp automatically., The rules hold against the real database, not just the model metadata. (+13 more)

### Community 33 - "test_error_surface.py"
Cohesion: 0.11
Nodes (28): AST, _error(), _messages(), parametrize, TestClient, The plain-English error pass, held as a test (constraint 7, PRD §4). Individual…, The literal text of a string argument, with ``{}`` for what is filled in., Every written error triple in the backend: (file, line, message, action). Non-… (+20 more)

### Community 34 - "test_terrain_maths.py"
Cohesion: 0.14
Nodes (22): The landscape's geometry, held to fixed answers in Node. The terrain is drawn…, Rotation moves the terrain, it does not grow or shrink it., Nothing crosses a level the whole grid is already above., The answer known by hand: one peak, one loop, and it encircles the peak., Contours nest. If they did not, the terrain would be unreadable., What makes the terrain survive a grayscale screenshot (§5b)., Two equal heights project to the same rise, wherever they sit. A perspective…, Elevation is the camera's angle above the horizon, as it sounds. From the… (+14 more)

### Community 35 - "clusters.py"
Cohesion: 0.19
Nodes (18): Cluster, ClusterAssignment, ClusterSet, Dimension, dimensions_of(), explorer(), ExplorerPoint, ExplorerSet (+10 more)

### Community 36 - "test_patterns.py"
Cohesion: 0.12
Nodes (38): _capture(), _patterns(), TestClient, The patterns endpoint: what it counts, what it sorts, what it refuses. Three…, The no-bypass promise, applied to what the operator actually sees., A meaning change: version n+1, old stories left on the old wording., PRD §4: no silent mixing. A v1 answer is not an answer to v2., §5.4: any view spanning versions must be able to say so on screen. (+30 more)

### Community 37 - "StonesAxis"
Cohesion: 0.29
Nodes (4): One id namespace across all signifier kinds — significations key on it., One axis of the stones canvas, named at both ends., StonesAxis, model_validator

### Community 38 - "aggregate"
Cohesion: 0.22
Nodes (15): aggregate(), _bars(), CategoryChart, _demographics(), _mcq_chart(), one_triad(), placements_by_signifier(), AnswerRow (+7 more)

### Community 39 - "build_golden_dataset"
Cohesion: 0.09
Nodes (52): build_golden_dataset(), TestClient, Create the framework and its twenty stories. Returns the framework., _brief(), _csv(), _heard(), TestClient, The CSV and the Pattern Brief. The CSV is tested as a file a person will open… (+44 more)

### Community 40 - "voice.js"
Cohesion: 0.28
Nodes (11): appendDictation(), getRecognitionClass(), isVoiceSupported(), startDictation(), VOICE_DENIED, VOICE_FAILED, VOICE_NETWORK, VOICE_NO_SPEECH (+3 more)

### Community 41 - "ImportTab.jsx"
Cohesion: 0.18
Nodes (4): ImportTab(), MarkUpStep(), storyCount(), MappingScreen()

### Community 42 - "_FakeAnthropic"
Cohesion: 0.50
Nodes (3): _FakeAnthropic, _FakeMessages, Stands in for ``anthropic.Anthropic`` and records what it was asked.

### Community 43 - "Wizard.jsx"
Cohesion: 0.41
Nodes (9): clearDraft(), draftHasContent(), draftKey(), loadDraft(), safeStorage(), saveDraft(), browserStorage(), buildSteps() (+1 more)

### Community 44 - "Studio.jsx"
Cohesion: 0.14
Nodes (13): api, ActiveLinkQr(), EditKindDialog(), describePath(), GROUPS, isIndex(), LEAVES, SILENT (+5 more)

### Community 45 - "test_queue.py"
Cohesion: 0.13
Nodes (42): Session, TestClient, _queue(), The validation queue over HTTP — accept, correct, reject. Everything here is…, Constraint 2 — a colour, not a different queue., Nothing AI touched it, so there is nothing for the operator to approve., The AI read something into a story that is not there — so remove it., The operator is held to the same shapes as the AI and the respondent. (+34 more)

### Community 46 - "The session loop (every session, no exceptions)"
Cohesion: 0.20
Nodes (9): 1. SESSION START — recover state before touching anything, 2. PLAN — small increments, 3. BUILD — one increment at a time, 4. TEST — after every increment, before calling it done, 5. CHECKPOINT — commit + state update, every increment, 6. SESSION END (or when the user says "wrap up"), Communication rules (owner is non-technical), Resilient Build (+1 more)

### Community 47 - "Data Visualization Reference — 2026"
Cohesion: 0.20
Nodes (9): Accessibility floor, Chart selection, Color encoding, Dashboard hierarchy, Data Visualization Reference — 2026, First principle, Integrity rules (non-negotiable), Interactivity discipline (+1 more)

### Community 48 - "FrameworkDefinition"
Cohesion: 0.11
Nodes (35): FrameworkDefinition, The whole respondent-facing definition of one framework version., How many signifier screens the respondent will see., chunks(), propose(), Split the stories into calls of at most ``size`` (PRD §4a)., Run Stage B over a file's stories and return checked proposals. Nothing is…, definition() (+27 more)

### Community 49 - "make_framework"
Cohesion: 0.14
Nodes (31): confirmed_import(), make_framework(), proposed_import(), TestClient, Shared helpers for the Stage B and validation-queue suites. One framework…, Drive a file as far as ``mapping_confirmed``, accepting Stage A as-is., Drive a file all the way to ``proposed`` — stories in the queue., _backend_modules() (+23 more)

### Community 50 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 51 - "Web Design & Data Visualization"
Cohesion: 0.22
Nodes (8): Data visualization, Output, Step 1: Frame the brief, Step 2: Design plan before code, Step 3: B2B or B2C playbook, Step 4: Build to the quality floor (non-negotiable, never announced), Step 5: Critique pass, Web Design & Data Visualization

### Community 52 - "Anecdote"
Cohesion: 0.10
Nodes (31): only_pending(), What counts as data, in one place (constraint 1). An anecdote exists in three…, Narrow a query to the stories still waiting on a person., Anecdote, One story, bound to the exact framework version it was told against.…, decide(), _finish_job_if_empty(), _low() (+23 more)

### Community 53 - "backend/exports.py"
Cohesion: 0.10
Nodes (32): _category_finding(), dataset_csv(), _dyad_finding(), findings(), headline(), _headlines(), _heard_category(), _join() (+24 more)

### Community 54 - "export_csv"
Cohesion: 0.23
Nodes (15): export_brief(), export_csv(), export_heard(), Depends, get, Query, Session, The Pattern Brief: findings in markdown, generated from the figures. (+7 more)

### Community 55 - "Design System Reference — 2026"
Cohesion: 0.29
Nodes (6): 2026 trend catalog — pick deliberately, one direction per project, Banned defaults (the "AI look"), Copy rules, Design System Reference — 2026, Layout heuristics, Tokens

### Community 56 - "test_health.py"
Cohesion: 0.29
Nodes (5): The one endpoint Phase 1 ships., PRD §4 budgets 200ms for non-AI endpoints; health should be far under., Guard against building ahead of the phase plan (PRD §6). Enumerated from the…, test_health_is_fast_enough_for_the_200ms_budget(), test_no_routes_beyond_the_current_phase()

### Community 57 - "MonkeyPatch"
Cohesion: 0.24
Nodes (11): fake_anthropic(), fixture, MonkeyPatch, TestClient, Acceptance criterion 12: offline is a working state, not a broken one., The operator loses the click, not the file., Install a fake ``anthropic`` package and turn mock mode off., test_a_file_waiting_to_be_analysed_survives_the_outage() (+3 more)

### Community 58 - "Narrative Lens — binding project instructions"
Cohesion: 0.33
Nodes (5): Binding constraints (restate these in every session), graphify, Narrative Lens — binding project instructions, Project skills, Session protocol

### Community 59 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 60 - "State File Templates"
Cohesion: 0.33
Nodes (5): API_CONTRACT.md (only for projects with a backend + frontend), DECISIONS.md (why things are the way they are), GUIDE.md (the owner's manual — plain language only), PROJECT_STATE.md (the resume file — most important), State File Templates

### Community 61 - "Narrative Lens — Latest"
Cohesion: 0.33
Nodes (5): How to resume, Narrative Lens — Latest, Next step, Running it yourself, Where things stand

### Community 62 - "Judgment Protocols — Anti-Drift & Anti-Hallucination"
Cohesion: 0.40
Nodes (4): Anti-drift, Anti-hallucination, Escalation honesty, Judgment Protocols — Anti-Drift & Anti-Hallucination

### Community 63 - "Testing Protocol"
Cohesion: 0.40
Nodes (4): Rules, Testing Protocol, The check script (create in session 1, grow it forever), When checks fail at session start

### Community 64 - "run_checks.sh"
Cohesion: 0.40
Nodes (3): NL_DATABASE_URL, NL_MOCK_AI, run_checks.sh script

### Community 65 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 66 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 67 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 75 - "Narrative Lens"
Cohesion: 0.15
Nodes (12): 1. Studio — write the questions, 2. Capture & Links — collect the stories, 3. Import & Validate — bring in stories you already have, 4. Patterns — read what you have, For whoever maintains this, Keeping your data, Narrative Lens, One-pager: printing a paper pack (+4 more)

### Community 80 - "test_placement_shape_parity.py"
Cohesion: 0.15
Nodes (13): fixture, A stored placement must survive the round trip to a widget and back. The server…, server shape → widget shape → server shape, unchanged., The shape the widget's own maths destructures, in corner order., The one kind whose two dialects happen to agree., Run one ES module through Node and read its JSON back., Exactly what Stage B writes to the database, for every signifier kind., round_trip() (+5 more)

### Community 81 - "plain_http_error"
Cohesion: 0.22
Nodes (14): _envelope(), plain_http_error(), plain_unexpected_error(), plain_validation_error(), Exception, Our own refusals pass straight through; the framework's get translated., A body or query the page built wrongly. The operator cannot fix a validator's…, A fault in the app itself. Logged in full, reported in one sentence. (+6 more)

### Community 82 - "ValidationQueue.jsx"
Cohesion: 0.29
Nodes (6): fromStored(), orderedSignifiers(), toSubmission(), signifiersInOrder(), ValidationQueue(), widgetValues()

### Community 83 - "SubmittedSignification"
Cohesion: 0.18
Nodes (15): One placement as it arrives from the wizard or paper batch entry., SubmittedSignification, _check_batch(), Placement, ProposalBatch, ProposedPlacement, ProposedStory, BaseModel (+7 more)

### Community 84 - "browse_stories"
Cohesion: 0.10
Nodes (24): browse_stories(), MarksIn, BaseModel, Depends, ge, get, put, Query (+16 more)

### Community 85 - "Patterns.jsx"
Cohesion: 0.07
Nodes (35): BarChart(), DyadChart(), StonesChart(), CLUSTER_TOKENS, ExplorerView(), Scatter(), VIEW, ContourTwin() (+27 more)

### Community 86 - "paper_pack.py"
Cohesion: 0.16
Nodes (17): _facilitator_sheet(), _mcq_options(), The printable paper pack (PRD §1.2, §5b print grammar). One HTML page the…, A square canvas with both axes named at each end., Tick boxes, one per option, big enough to mark with a pen., One A4 landscape sheet for one signifier., The A4 story card: prompt, ruled space, groups, anonymity line., Running instructions, materials, and the reconciliation grid. (+9 more)

### Community 87 - "test_empty_states.py"
Cohesion: 0.21
Nodes (13): _copy(), parametrize, Path, Every screen tells the operator what to do next (PRD §6, Phase 9). A fresh…, The Studio is the tab the app opens on, so it carries the first word., One name for the thing, in every place the operator can read it. The code calls…, The text of every empty-state paragraph in one screen, tags stripped., No data" is a fact about the database, not help for the person reading. (+5 more)

### Community 88 - "test_landscape_golden.py"
Cohesion: 0.26
Nodes (10): peaks_of(), produce_peaks(), TestClient, The landscape golden — peaks stable to ±0.02 (PRD §6, Phase 8). The second of…, The headline guarantee: the terrain does not drift under anyone's feet., A golden of empty lists would pass the tolerance test forever., Determinism against itself, not only against the stored file., test_peaks_are_stable_within_tolerance() (+2 more)

### Community 89 - "AiError"
Cohesion: 0.33
Nodes (4): AiError, Exception, The one AI client (constraint 6). Every call Narrative Lens makes to a language…, An AI call that failed in a way the operator needs told about. Carries the PRD…

### Community 90 - "mock_enabled"
Cohesion: 0.50
Nodes (4): mock_enabled(), Whether this process runs with mocks instead of the network. Read on every call…, Constraint 6: NL_MOCK_AI=1 runs everything with zero network., test_the_suite_runs_in_mock_mode_by_default()

### Community 91 - "test_stage_a_repairs_one_bad_reply_and_carries_on"
Cohesion: 0.19
Nodes (10): _Block, _calls(), Any, Answer each successive request with the next reply in the list., PRD §6 Phase 7: the repair path, exercised through Stage A itself., Every request made, across every client. ``_live_text`` builds a fresh…, _replies(), _Response (+2 more)

### Community 92 - "test_stage_gate.py"
Cohesion: 0.09
Nodes (27): advance(), can_advance(), The ingestion stage machine and its gate (PRD §3, §4; constraints 1 and 12). An…, Move the job on, or refuse the move with the same 409 the gate uses., Note why a step did not work, without moving the job. A failed AI call is worth…, Whether the machine permits ``current → target``., Whether ``target`` can be reached from ``start`` by any number of steps. Used…, Refuse, with 409 and an explanation, unless the job is at ``expected``. This is… (+19 more)

### Community 93 - "routers/patterns.py"
Cohesion: 0.10
Nodes (39): only_validated(), Narrow a query to the stories a person has actually approved. Every read that…, get_clusters(), get_explorer(), get_landscape(), Depends, ge, get (+31 more)

### Community 94 - "test_original_names.py"
Cohesion: 0.25
Nodes (7): _files(), parametrize, Path, Original names and materials only (constraint 8, acceptance criterion 15). The…, Criterion 15 allows one attribution. One, not none — it is owed. Counted in…, test_no_reserved_name_appears_in_the_app(), test_the_readme_carries_exactly_one_attribution()

### Community 95 - "organise.py"
Cohesion: 0.13
Nodes (23): _check_narrative(), _check_tabular(), _hinted_column(), _mock_narrative(), _mock_tabular(), _narrative_prompt(), NarrativeOrganisation, OrganiseError (+15 more)

### Community 96 - "test_live_ai.py"
Cohesion: 0.18
Nodes (17): _live_text(), One live call to api.anthropic.com. The only network in the app. Imported…, ModuleType, APIConnectionError, APIStatusError, _last(), Exception, parametrize (+9 more)

### Community 97 - "create_public_capture"
Cohesion: 0.17
Nodes (16): create_public_capture(), _framework_or_refuse(), get_public_framework(), _link_or_refuse(), PublicFrameworkOut, BaseModel, Depends, get (+8 more)

### Community 98 - "propose.py"
Cohesion: 0.20
Nodes (14): describe_signifiers(), _mock_batch(), _mock_confidence(), _mock_value(), _prompt(), Any, Stage B — Propose (PRD §4a, constraint 1). Stage B reads a story and *suggests*…, The questions, with the exact answer shape each one takes. Written out in full… (+6 more)

### Community 100 - "health"
Cohesion: 0.67
Nodes (3): health(), get, Liveness probe. The launcher opens this while the app is starting.

### Community 101 - "regenerate_golden.py"
Cohesion: 0.16
Nodes (16): main(), Rewrite both goldens. Run deliberately, never automatically. python -m…, produce(), TestClient, The pattern golden — byte-identical from Phase 7 onward (PRD §6). Twenty…, The one way this project writes a golden file. Sorted keys and a fixed indent,…, A missing golden would make every other test here silently vacuous., Determinism, checked against itself rather than against the file. If… (+8 more)

### Community 102 - "edit_semantics.py"
Cohesion: 0.17
Nodes (15): build_edit_log_entries(), diff_text_fields(), is_structural_change(), Any, datetime, The wording-fix vs meaning-change guardrail (PRD §1.1, constraint 13g). While a…, One stored answer with its labels brought up to date, or unchanged. Shape-…, The shape of a framework, ignoring every word in it. Two definitions with the… (+7 more)

### Community 104 - "test_scope_completeness.py"
Cohesion: 0.16
Nodes (13): TestClient, Every item of PRD §1's scope is actually reachable in the app. This file exists…, One assertion per numbered item of §1 that the API is responsible for., §5.4: "Landscape (default) · Supporting charts · 3D Explorer · Story browser"., The four verbs §1.6 lists, each with something in the code doing it., Dataset CSV · contour PNG · supporting-charts PNG · brief · what we heard., Acceptance criterion 1 ends "QR on home", and the home screen is the Studio., _source() (+5 more)

### Community 105 - "test_edit_log_wording.py"
Cohesion: 0.16
Nodes (13): _describe(), described(), fixture, The edit log reads as English, not as a schema path (constraint 7). The log…, A log entry nobody planned for is still a record of a change., The full fixture with one string changed in every kind of place., Every path a real wording fix produces, with what the Studio shows., Nothing falls through to the raw path — the whole surface is covered. (+5 more)

### Community 106 - "ImportJob"
Cohesion: 0.15
Nodes (17): Base, CaptureLink, ImportJob, _in_clause(), The six-table schema from PRD §3. Two constraints shape this module directly: *…, A token-gated capture URL pointing at one exact framework version., One uploaded file moving through the two-stage ingestion machine., A free-text tag the analyst attaches to a story. (+9 more)

### Community 107 - "conftest.py"
Cohesion: 0.24
Nodes (12): client(), db_path(), db_url(), engine(), fixture, Path, TestClient, Shared fixtures. Every test runs against a throwaway SQLite file, never the… (+4 more)

### Community 108 - "backend/stories.py"
Cohesion: 0.20
Nodes (10): BaseModel, The story browser's read model (PRD §1.6). The landscape says where stories…, The full-text rule: every word must appear, in the story or its title.…, Set a story's star and tags, and return what it now carries. Both are…, One story as the browser lists it., A page of the browser, and everything the screen needs around it., search_clause(), set_marks() (+2 more)

### Community 109 - "env.py"
Cohesion: 0.27
Nodes (9): Alembic environment. The database URL comes from…, Emit SQL to a script without a live connection., Run migrations against a live connection., _run(), run_migrations_offline(), run_migrations_online(), _url(), database_url() (+1 more)

### Community 110 - "App.jsx"
Cohesion: 0.48
Nodes (4): App(), TABS, captureTokenFromPath(), PublicCapture()

### Community 111 - "TestFramework"
Cohesion: 0.29
Nodes (3): A wording fix appends to the log in place (PRD §3)., A meaning change creates a new row pointing back at its parent., TestFramework

### Community 112 - "CaptureError"
Cohesion: 0.13
Nodes (21): CaptureError, CaptureSubmission, _check_dyad(), _check_mcq(), _check_stones(), _check_triad(), LocalCaptureSubmission, PublicCaptureSubmission (+13 more)

### Community 113 - "patterns_fixtures.py"
Cohesion: 0.50
Nodes (4): The twenty-story fixture behind the pattern golden (PRD §6, Phase 7). Twenty…, One story, entirely determined by its position in the run., story_payload(), _tenths()

## Knowledge Gaps
- **172 isolated node(s):** `name`, `version`, `description`, `dev`, `build` (+167 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Anecdote` connect `Anecdote` to `TestClient`, `TestClient`, `Framework`, `TestClient`, `test_import_pipeline.py`, `TestClient`, `test_public_identifier_absence.py`, `imports.py`, `test_landscape.py`, `NormalisedDocument`, `capture_links.py`, `Signification`, `get_session`, `test_schema_absence.py`, `test_queue.py`, `make_framework`, `browse_stories`, `routers/patterns.py`, `ImportJob`, `backend/stories.py`, `TestFramework`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `FrameworkDefinition` connect `FrameworkDefinition` to `Framework`, `imports.py`, `validate_definition`, `NormalisedDocument`, `backend/patterns.py`, `TriadChart`, `get_session`, `clusters.py`, `StonesAxis`, `aggregate`, `Anecdote`, `backend/exports.py`, `test_placement_shape_parity.py`, `SubmittedSignification`, `paper_pack.py`, `routers/patterns.py`, `create_public_capture`, `propose.py`, `.estimated_minutes`, `edit_semantics.py`, `.exceeds_screen_warning`, `test_edit_log_wording.py`, `CaptureError`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `Signification` connect `Signification` to `TestClient`, `Framework`, `test_import_pipeline.py`, `TestClient`, `test_public_identifier_absence.py`, `imports.py`, `ImportJob`, `backend/stories.py`, `test_queue.py`, `test_landscape.py`, `TestFramework`, `NormalisedDocument`, `make_framework`, `Anecdote`, `get_session`, `routers/patterns.py`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 53 inferred relationships involving `FrameworkDefinition` (e.g. with `CaptureError` and `CaptureSubmission`) actually correct?**
  _`FrameworkDefinition` has 53 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `Anecdote` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Anecdote` has 56 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Signification` (e.g. with `CaptureResult` and `FrameworkCreate`) actually correct?**
  _`Signification` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `Framework` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Framework` has 32 INFERRED edges - model-reasoned connections that need verification._