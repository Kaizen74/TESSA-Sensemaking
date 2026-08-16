# Graph Report - TESSA-Sensemaking  (2026-08-16)

## Corpus Check
- 107 files · ~86,715 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1661 nodes · 3880 edges · 90 communities (78 shown, 12 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 337 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `392d6d3f`
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
- _create
- request_json
- test_public_identifier_absence.py
- imports.py
- package.json
- framework_schema.py
- NormalisedDocument
- test_stage_gate.py
- parsers.py
- _run_node
- NarrativeSegment
- paper_pack.py
- CaptureLink
- parse
- What You Must Do When Invoked
- Signification
- test_organise_stage_a.py
- create_public_capture
- TestClient
- PRD: Narrative Lens — Local Narrative Sense-Making App
- Phases
- CaptureError
- App.jsx
- test_capture_draft.py
- Widgets.jsx
- test_schema_absence.py
- get_paper_pack
- ConfirmationView
- Anecdote
- store_capture
- StonesAxis
- ingest_fixtures.py
- models.py
- voice.js
- ImportTab.jsx
- capture.py
- Wizard.jsx
- Studio.jsx
- test_queue.py
- The session loop (every session, no exceptions)
- Data Visualization Reference — 2026
- FrameworkDefinition
- TestAnonymityStatementIsTrueOfTheCode
- graphify reference: extra exports and benchmark
- Web Design & Data Visualization
- queue.py
- to_cartesian
- propose.py
- Design System Reference — 2026
- test_health.py
- TestFramework
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
- README.md
- tests/__init__.py
- narrative-lens
- test_placement_shape_parity.py
- edit_semantics.py
- ValidationQueue.jsx
- parametrize
- dataset.py
- FrameworkCreate
- .estimated_minutes
- test_prose_segments_carry_the_locator_they_came_from
- .exceeds_screen_warning
- .signifier_count

## God Nodes (most connected - your core abstractions)
1. `FrameworkDefinition` - 90 edges
2. `Anecdote` - 80 edges
3. `Framework` - 54 edges
4. `Signification` - 47 edges
5. `ImportJob` - 41 edges
6. `parse()` - 39 edges
7. `NormalisedDocument` - 38 edges
8. `_framework()` - 37 edges
9. `_framework()` - 36 edges
10. `_submit()` - 36 edges

## Surprising Connections (you probably didn't know these)
- `Shape` --uses--> `AiError`  [INFERRED]
  tests/test_ai_client.py → backend/ai_client.py
- `TestGoldenAsymmetricPlacements` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py
- `TestGoldenCentroid` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py
- `TestGoldenCorners` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py
- `TestGoldenEdgeMidpoints` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py

## Import Cycles
- None detected.

## Communities (90 total, 12 thin omitted)

### Community 0 - "BarycentricError"
Cohesion: 0.10
Nodes (22): BarycentricError, from_value_json(), is_inside(), normalise(), ValueError, Triad barycentric maths. A triad answer is a point inside an equilateral…, Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`., Whether the weights describe a point in or on the triangle. (+14 more)

### Community 1 - "TestClient"
Cohesion: 0.06
Nodes (42): qr_png_bytes(), QR codes for capture links (PRD §4, §1.8). A QR is how a phone gets to the…, Return a PNG of ``payload`` as QR, as raw bytes. Error correction is set to M…, RateLimiter, Rate limiting for the public capture endpoints (PRD §4). The public endpoints…, A sliding-window counter keyed by an opaque string. Deliberately simple and in-…, Record a hit and report whether it is within the limit., Forget counters. Used by tests and when a link is revoked. (+34 more)

### Community 2 - "TestClient"
Cohesion: 0.09
Nodes (24): _framework(), TestClient, Local capture (PRD §6 Phase 3). The tests the PRD names for this phase: wizard…, PRD §9 assumption 7: reflection shows one signifier., Skipping every question is allowed; the story is the point., Constraint 3: provenance on every record., PRD §6 Phase 3: batch entry writes paper provenance., Constraint 9, at the moment a story is actually written. (+16 more)

### Community 3 - "Framework"
Cohesion: 0.16
Nodes (30): get_session(), Session, FastAPI dependency yielding a session that always closes., Framework, A version of the question set respondents see. ``parent_framework_id`` links…, _anecdote_count(), _apply_meaning_change(), _apply_wording_fix() (+22 more)

### Community 4 - "make_engine"
Cohesion: 0.07
Nodes (41): Alembic environment. The database URL comes from…, Emit SQL to a script without a live connection., Run migrations against a live connection., _run(), run_migrations_offline(), run_migrations_online(), _url(), _connect_args() (+33 more)

### Community 5 - "TestClient"
Cohesion: 0.10
Nodes (23): _create_full(), _pack_html(), TestClient, The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar). Two…, PRD §1.2a: the story card carries respondent-group tick boxes., The pack renders the version's current wording, not a cached copy., Constraint 9: the anonymity statement is printed verbatim on the card., Whatever this version says is what the card prints — no substitution. (+15 more)

### Community 6 - "test_import_pipeline.py"
Cohesion: 0.14
Nodes (50): A two-sheet workbook: one of responses, one lookup table to ignore. The…, txt_bytes(), xlsx_bytes(), _confirm(), _confirmation_body(), _organise(), parametrize, Session (+42 more)

### Community 7 - "_create"
Cohesion: 0.14
Nodes (23): _add_story(), _create(), _definition(), Session, TestClient, The wording-fix vs meaning-change state machine (PRD §6, constraint 13g). This…, Constraint 7: the operator must be able to act on the message., A wording fix patches in place and appends to the edit log. (+15 more)

### Community 8 - "request_json"
Cohesion: 0.08
Nodes (36): _fenced_json(), _live_text(), mock_enabled(), _parse(), Any, Parse one reply strictly, or raise the reason it could not be parsed., One live call to api.anthropic.com. The only network in the app. Imported…, Ask for one JSON object of the given shape, or fail in plain English. In mock… (+28 more)

### Community 9 - "test_public_identifier_absence.py"
Cohesion: 0.15
Nodes (17): _clear_limits(), _framework(), _link(), fixture, TestClient, Constraint 9 on the remote path (PRD §6 Phase 4: identifier-absence test).…, Sweep every column of every table, not just the ones we expect., Structural guards: not "it doesn't today", but "it has no way to". (+9 more)

### Community 10 - "imports.py"
Cohesion: 0.12
Nodes (41): bad_request(), conflict(), Something outside the app misbehaved — currently only the AI service., upstream(), ImportJob, One uploaded file moving through the two-stage ingestion machine., confirm_mapping(), create_import() (+33 more)

### Community 11 - "package.json"
Cohesion: 0.06
Nodes (30): eslint, @eslint/js, eslint-plugin-react, eslint-plugin-react-hooks, dependencies, react, react-dom, description (+22 more)

### Community 12 - "framework_schema.py"
Cohesion: 0.07
Nodes (19): default_definition(), Validation for ``frameworks.definition_json`` (PRD §3 and §5). Every…, Parse and validate a raw ``definition_json`` payload., A minimal, valid definition — what a brand-new framework starts from., validate_definition(), Validation of ``definition_json`` and the anonymity statement it carries., Significations key on the id alone, so one namespace covers all kinds., A typo in the Studio should fail loudly, not vanish silently. (+11 more)

### Community 13 - "NormalisedDocument"
Cohesion: 0.12
Nodes (31): _check_narrative(), _check_tabular(), _hinted_column(), _mock_narrative(), _mock_tabular(), _narrative_prompt(), NarrativeOrganisation, organise() (+23 more)

### Community 14 - "test_stage_gate.py"
Cohesion: 0.10
Nodes (23): can_advance(), The ingestion stage machine and its gate (PRD §3, §4; constraints 1 and 12). An…, Whether the machine permits ``current → target``., Whether ``target`` can be reached from ``start`` by any number of steps. Used…, Refuse, with 409 and an explanation, unless the job is at ``expected``. This is…, reachable(), require_stage(), _job() (+15 more)

### Community 15 - "parsers.py"
Cohesion: 0.14
Nodes (23): Block, _blocks_from_text(), _clean_row(), _decode(), _parse_captions(), _parse_csv(), _parse_docx(), _parse_pdf() (+15 more)

### Community 16 - "_run_node"
Cohesion: 0.11
Nodes (14): parametrize, Voice fallback (PRD §6 Phase 4, §7.12, constraint 10). Constraint 10 says voice…, The UI calls stop() on unmount whether or not voice ever started., Stopping on purpose is not a failure and must not show a warning., Constraint 10: voice always paired with typing., Interim results would rewrite a respondent's words as they speak., §7.12: voice fails plain-English with a working fallback., Constraint 7: no jargon a respondent cannot act on. (+6 more)

### Community 17 - "NarrativeSegment"
Cohesion: 0.19
Nodes (25): _balance(), Candidate, confirm(), confirm_narrative(), confirm_tabular(), ConfirmedExtraction, ExtractionError, BaseModel (+17 more)

### Community 18 - "paper_pack.py"
Cohesion: 0.11
Nodes (26): CaptureSettings, Dyad, Mcq, BaseModel, A 2D canvas on which the respondent places named chips., A multiple-choice question., Every non-signifier string the respondent reads, plus capture toggles., Every signifier with its kind, in the order the respondent meets them. (+18 more)

### Community 19 - "CaptureLink"
Cohesion: 0.17
Nodes (25): CaptureLink, A token-gated capture URL pointing at one exact framework version., capture_link_qr(), capture_url(), CaptureLinkCreate, CaptureLinkOut, create_capture_link(), _get_or_404() (+17 more)

### Community 20 - "parse"
Cohesion: 0.14
Nodes (22): parse(), Read one uploaded file into the normalised shape, or refuse it. Refusals are…, parametrize, Every format PRD §1.3 promises, read from a real file of that format., PRD §1.3 lists nine extensions. All nine are readable, nothing else is., The reverse map the API uses for jobs whose extension is long gone., Assumption 10: a mixed-role workbook is mapped sheet by sheet., test_a_corrupt_office_file_says_what_to_do_about_it() (+14 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "Signification"
Cohesion: 0.14
Nodes (17): One respondent (or validated AI) placement on one signifier. ``value_json``…, A free-text tag the analyst attaches to a story., Signification, Tag, _anecdote(), _framework(), parametrize, CRUD across the six tables of PRD §3, plus the vocabularies they enforce. (+9 more)

### Community 23 - "test_organise_stage_a.py"
Cohesion: 0.18
Nodes (19): csv_bytes(), Any, MonkeyPatch, TestClient, Stage A: what it proposes, and what it is not allowed to get away with. Stage A…, Constraint 4 and 7: offline is a normal state, not a broken one. The file stays…, Make Stage A's next answer whatever the test says it is., A lookup table is not a set of responses, and saying so is the answer. (+11 more)

### Community 24 - "create_public_capture"
Cohesion: 0.12
Nodes (22): PublicCaptureSubmission, A capture arriving through a capture link. ``framework_id`` is not accepted:…, AppError, not_found(), An error the operator is meant to read and act on., create_public_capture(), _framework_or_refuse(), get_public_framework() (+14 more)

### Community 25 - "TestClient"
Cohesion: 0.14
Nodes (9): TestClient, List, create and fetch frameworks (PRD §4)., A new framework starts valid and empty, ready to fill in., The Studio shows these live while the operator edits., Constraint 7: plain English, with something to do about it., PRD §5.1: version history sidebar shows versions with story counts., TestCreate, TestFetch (+1 more)

### Community 26 - "PRD: Narrative Lens — Local Narrative Sense-Making App"
Cohesion: 0.10
Nodes (19): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 11. Changelog v1.2 → v1.3, 1. Scope, 2. Binding constraints (restate these in every session), 3. Data model (SQLite, via SQLAlchemy + Alembic), 4. API contract (FastAPI, all JSON), 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages). (+11 more)

### Community 27 - "Phases"
Cohesion: 0.10
Nodes (20): Decisions, Fixed, Narrative Lens — Progress, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5 (+12 more)

### Community 28 - "CaptureError"
Cohesion: 0.20
Nodes (14): CaptureError, _check_dyad(), _check_mcq(), _check_stones(), _check_triad(), ValueError, Validating a submitted capture against the framework it answers (PRD §4). A…, Triad weights: one per corner, non-negative, summing to 1.0. (+6 more)

### Community 29 - "App.jsx"
Cohesion: 0.18
Nodes (10): api, ApiError, App(), TABS, CaptureTab(), MODES, LinkManager(), PaperBatch() (+2 more)

### Community 30 - "test_capture_draft.py"
Cohesion: 0.15
Nodes (18): Drafts survive a reload (PRD §6 Phase 3, §7.6). The draft lives in the browser,…, Nothing lingers once the story has been sent., Starting fresh is recoverable; crashing on load is not., A draft from an older shape must not crash the wizard., Private browsing must not stop someone telling their story., Constraint 9 reaches into the browser, not just the database., Offering to restore an empty draft would be noise., The whole point: a half-written story survives the page going away. (+10 more)

### Community 31 - "Widgets.jsx"
Cohesion: 0.24
Nodes (15): CORNER_0, CORNER_1, CORNER_2, normalise(), roundTo(), toBarycentric(), toCartesian(), TRIANGLE_HEIGHT (+7 more)

### Community 32 - "test_schema_absence.py"
Cohesion: 0.17
Nodes (15): _columns(), parametrize, Constraint 9 — respondent anonymity is engineered, not promised. These tests…, Constraint 9: respondent time is hour-rounded, so no exact clock exists.…, The rules hold against the real database, not just the model metadata., PRD §3: migration 001 creates all six tables and no others., No IP, user agent, fingerprint, device/session id or email anywhere., No name-family column on a table whose rows are linked to a respondent. (+7 more)

### Community 33 - "get_paper_pack"
Cohesion: 0.20
Nodes (10): _facilitator_sheet(), The A4 story card: prompt, ruled space, groups, anonymity line., Running instructions, materials, and the reconciliation grid., Render the whole pack as one self-contained, printable HTML page., render_paper_pack(), _story_card(), get_paper_pack(), get (+2 more)

### Community 34 - "ConfirmationView"
Cohesion: 0.14
Nodes (17): AiError, Exception, An AI call that failed in a way the operator needs told about. Carries the PRD…, classify(), ParseError, Exception, Return ``(file_type, file_class)`` for a filename, or refuse it., A file that could not be read, phrased for the operator. (+9 more)

### Community 35 - "Anecdote"
Cohesion: 0.25
Nodes (7): Anecdote, Base, One story, bound to the exact framework version it was told against.…, Declarative base carrying the shared naming convention., DeclarativeBase, A row written through the ORM gets an hour-rounded stamp automatically., test_anecdote_default_stamps_hour_rounded_time()

### Community 36 - "store_capture"
Cohesion: 0.15
Nodes (17): CaptureSubmission, LocalCaptureSubmission, BaseModel, A whole capture: one story plus its placements. Note what is *not* here: no id,…, A capture from the operator's own machine: admin, paper entry, or kiosk. Only…, _auto_title(), CaptureResult, create_capture() (+9 more)

### Community 37 - "StonesAxis"
Cohesion: 0.29
Nodes (4): One id namespace across all signifier kinds — significations key on it., One axis of the stones canvas, named at both ends., StonesAxis, model_validator

### Community 38 - "ingest_fixtures.py"
Cohesion: 0.18
Nodes (9): docx_bytes(), pdf_bytes(), _pdf_escape(), Real files, in memory, one per format Narrative Lens claims to read. Acceptance…, A one-page PDF with each paragraph as its own text run. Written by hand:…, vtt_bytes(), test_segments_found_counts_what_stage_a_believes_it_found(), The empty paragraph between the two stories is skipped, not renumbered.… (+1 more)

### Community 39 - "models.py"
Cohesion: 0.19
Nodes (12): hour_rounded_now(), _in_clause(), datetime, The six-table schema from PRD §3. Two constraints shape this module directly: *…, Render a SQL ``IN`` predicate for a CHECK constraint., Naive UTC now, for operator-side records that carry no respondent link., Naive UTC now truncated to the hour (constraint 9). Minutes, seconds and…, utcnow() (+4 more)

### Community 40 - "voice.js"
Cohesion: 0.28
Nodes (11): appendDictation(), getRecognitionClass(), isVoiceSupported(), startDictation(), VOICE_DENIED, VOICE_FAILED, VOICE_NETWORK, VOICE_NO_SPEECH (+3 more)

### Community 41 - "ImportTab.jsx"
Cohesion: 0.18
Nodes (4): ImportTab(), MarkUpStep(), storyCount(), MappingScreen()

### Community 42 - "capture.py"
Cohesion: 0.13
Nodes (16): Database engine and session plumbing (constraint 4: SQLite + local files)., The error shape from PRD §4. ``{"error": {"code": ..., "message": plain-English…, health(), mount_frontend(), get, FastAPI application. Endpoints arrive with the phase that needs them, per PRD…, Liveness probe. The launcher opens this while the app is starting., Serve ``frontend/dist`` if it has been built. Returns whether anything was… (+8 more)

### Community 43 - "Wizard.jsx"
Cohesion: 0.41
Nodes (9): clearDraft(), draftHasContent(), draftKey(), loadDraft(), safeStorage(), saveDraft(), browserStorage(), buildSteps() (+1 more)

### Community 44 - "Studio.jsx"
Cohesion: 0.20
Nodes (9): ReflectionPanel(), EditKindDialog(), Field(), SignifierEditor(), TextArea(), orderedSignifiers(), PhonePreview(), estimateMinutes() (+1 more)

### Community 45 - "test_queue.py"
Cohesion: 0.07
Nodes (73): confirmed_import(), make_framework(), proposed_import(), TestClient, Shared helpers for the Stage B and validation-queue suites. One framework…, Drive a file as far as ``mapping_confirmed``, accepting Stage A as-is., Drive a file all the way to ``proposed`` — stories in the queue., _backend_modules() (+65 more)

### Community 46 - "The session loop (every session, no exceptions)"
Cohesion: 0.20
Nodes (9): 1. SESSION START — recover state before touching anything, 2. PLAN — small increments, 3. BUILD — one increment at a time, 4. TEST — after every increment, before calling it done, 5. CHECKPOINT — commit + state update, every increment, 6. SESSION END (or when the user says "wrap up"), Communication rules (owner is non-technical), Resilient Build (+1 more)

### Community 47 - "Data Visualization Reference — 2026"
Cohesion: 0.20
Nodes (9): Accessibility floor, Chart selection, Color encoding, Dashboard hierarchy, Data Visualization Reference — 2026, First principle, Integrity rules (non-negotiable), Interactivity discipline (+1 more)

### Community 48 - "FrameworkDefinition"
Cohesion: 0.10
Nodes (39): FrameworkDefinition, The whole respondent-facing definition of one framework version., chunks(), describe_signifiers(), _prompt(), propose(), The questions, with the exact answer shape each one takes. Written out in full…, Split the stories into calls of at most ``size`` (PRD §4a). (+31 more)

### Community 49 - "TestAnonymityStatementIsTrueOfTheCode"
Cohesion: 0.27
Nodes (3): Constraint 9: the statement must be literally true of the schema. Each clause…, Story, placements, and chosen group — and that is the whole list., TestAnonymityStatementIsTrueOfTheCode

### Community 50 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 51 - "Web Design & Data Visualization"
Cohesion: 0.22
Nodes (8): Data visualization, Output, Step 1: Frame the brief, Step 2: Design plan before code, Step 3: B2B or B2C playbook, Step 4: Build to the quality floor (non-negotiable, never announced), Step 5: Critique pass, Web Design & Data Visualization

### Community 52 - "queue.py"
Cohesion: 0.11
Nodes (28): The one AI client (constraint 6). Every call Narrative Lens makes to a language…, One placement as it arrives from the wizard or paper batch entry., SubmittedSignification, decide(), _finish_job_if_empty(), _low(), BaseModel, Depends (+20 more)

### Community 53 - "to_cartesian"
Cohesion: 0.11
Nodes (18): Convert three corner weights into a point inside the triangle. >>>…, Convert a point in the triangle into three corner weights summing to 1.0. The…, to_barycentric(), to_cartesian(), Weights survive a there-and-back trip without drifting., Ten trips land where one trip landed — no accumulating drift., The dead centre is the equal-weight answer — the most-read position., TestGoldenCentroid (+10 more)

### Community 54 - "propose.py"
Cohesion: 0.11
Nodes (25): _check_batch(), _mock_batch(), _mock_confidence(), _mock_value(), Placement, ProposalBatch, ProposedPlacement, ProposedStory (+17 more)

### Community 55 - "Design System Reference — 2026"
Cohesion: 0.29
Nodes (6): 2026 trend catalog — pick deliberately, one direction per project, Banned defaults (the "AI look"), Copy rules, Design System Reference — 2026, Layout heuristics, Tokens

### Community 56 - "test_health.py"
Cohesion: 0.29
Nodes (5): The one endpoint Phase 1 ships., PRD §4 budgets 200ms for non-AI endpoints; health should be far under., Guard against building ahead of the phase plan (PRD §6). Enumerated from the…, test_health_is_fast_enough_for_the_200ms_budget(), test_no_routes_beyond_the_current_phase()

### Community 57 - "TestFramework"
Cohesion: 0.29
Nodes (3): A wording fix appends to the log in place (PRD §3)., A meaning change creates a new row pointing back at its parent., TestFramework

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

### Community 80 - "test_placement_shape_parity.py"
Cohesion: 0.15
Nodes (13): fixture, A stored placement must survive the round trip to a widget and back. The server…, server shape → widget shape → server shape, unchanged., The shape the widget's own maths destructures, in corner order., The one kind whose two dialects happen to agree., Run one ES module through Node and read its JSON back., Exactly what Stage B writes to the database, for every signifier kind., round_trip() (+5 more)

### Community 81 - "edit_semantics.py"
Cohesion: 0.20
Nodes (13): build_edit_log_entries(), diff_text_fields(), is_structural_change(), Any, datetime, The wording-fix vs meaning-change guardrail (PRD §1.1, constraint 13g). While a…, The shape of a framework, ignoring every word in it. Two definitions with the…, Whether the edit changes the framework's shape rather than its words. (+5 more)

### Community 82 - "ValidationQueue.jsx"
Cohesion: 0.26
Nodes (7): fromStored(), orderedSignifiers(), toSubmission(), signifiersInOrder(), ValidationQueue(), widgetValues(), SignifierWidget()

### Community 83 - "parametrize"
Cohesion: 0.20
Nodes (7): parametrize, Each corner weight of 1.0 lands exactly on that corner., Two-way ties sit halfway along an edge, with the third corner at zero., Fixed off-centre answers — the ones a real respondent actually gives., TestGoldenAsymmetricPlacements, TestGoldenCorners, TestGoldenEdgeMidpoints

### Community 84 - "dataset.py"
Cohesion: 0.33
Nodes (6): only_pending(), only_validated(), What counts as data, in one place (constraint 1). An anecdote exists in three…, Narrow a query to the stories a person has actually approved. Every read that…, Narrow a query to the stories still waiting on a person., Select

### Community 85 - "FrameworkCreate"
Cohesion: 0.40
Nodes (5): FrameworkCreate, FrameworkUpdate, BaseModel, Body for creating a framework. Version 1 of a fresh lineage., Body for editing a framework. ``edit_kind`` is required once the framework has…

### Community 87 - "test_prose_segments_carry_the_locator_they_came_from"
Cohesion: 0.50
Nodes (4): pptx_bytes(), test_prose_segments_carry_the_locator_they_came_from(), PRD §9 assumption 9: decks are text-only., test_deck_reads_slide_text_and_notes_and_nothing_else()

## Knowledge Gaps
- **149 isolated node(s):** `name`, `version`, `description`, `dev`, `build` (+144 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Anecdote` connect `Anecdote` to `TestClient`, `TestClient`, `Framework`, `TestClient`, `test_import_pipeline.py`, `_create`, `test_public_identifier_absence.py`, `imports.py`, `CaptureLink`, `Signification`, `test_schema_absence.py`, `ConfirmationView`, `store_capture`, `models.py`, `capture.py`, `test_queue.py`, `queue.py`, `TestFramework`, `dataset.py`, `FrameworkCreate`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Why does `FrameworkDefinition` connect `FrameworkDefinition` to `Framework`, `imports.py`, `framework_schema.py`, `paper_pack.py`, `create_public_capture`, `CaptureError`, `get_paper_pack`, `ConfirmationView`, `store_capture`, `StonesAxis`, `capture.py`, `TestAnonymityStatementIsTrueOfTheCode`, `queue.py`, `propose.py`, `test_placement_shape_parity.py`, `edit_semantics.py`, `FrameworkCreate`, `.estimated_minutes`, `.exceeds_screen_warning`, `.signifier_count`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `BarycentricError` connect `BarycentricError` to `store_capture`, `parametrize`, `queue.py`, `to_cartesian`, `create_public_capture`, `CaptureError`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `FrameworkDefinition` (e.g. with `CaptureError` and `CaptureSubmission`) actually correct?**
  _`FrameworkDefinition` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `Anecdote` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Anecdote` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `Framework` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Framework` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `Signification` (e.g. with `CaptureResult` and `ConfirmationView`) actually correct?**
  _`Signification` has 28 INFERRED edges - model-reasoned connections that need verification._