# Graph Report - TESSA-Sensemaking  (2026-09-02)

## Corpus Check
- 161 files · ~167,217 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2809 nodes · 6706 edges · 124 communities (115 shown, 9 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 475 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b2b7da97`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_interpretations.py
- TestClient
- TestClient
- edit_semantics.py
- make_engine
- Anecdote
- test_import_pipeline.py
- TestClient
- request_json
- test_public_identifier_absence.py
- propose_import
- package.json
- validate_definition
- test_story_browser.py
- test_landscape.py
- parsers.py
- _run_node
- extraction.py
- backend/patterns.py
- test_signification_provenance.py
- parse
- What You Must Do When Invoked
- Signification
- TriadChart
- imports.py
- TestClient
- PRD: Narrative Lens — Local Narrative Sense-Making App
- Decisions
- build_golden_dataset
- api.js
- test_capture_draft.py
- Widgets.jsx
- Landscape.jsx
- test_error_surface.py
- test_terrain_maths.py
- clusters.py
- test_patterns.py
- StonesAxis
- backend/interpretations.py
- test_exports.py
- voice.js
- ValidationQueue.jsx
- test_design_linter.py
- Wizard.jsx
- Studio.jsx
- test_queue.py
- The session loop (every session, no exceptions)
- Data Visualization Reference — 2026
- FrameworkDefinition
- test_capture.py
- graphify reference: extra exports and benchmark
- Web Design & Data Visualization
- queue.py
- backend/exports.py
- export_brief
- Design System Reference — 2026
- test_health.py
- AiError
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
- CaptureResult
- propose.py
- browse_stories
- Patterns.jsx
- framework_schema.py
- test_empty_states.py
- test_landscape_golden.py
- proposed_import
- Framework
- get_quality
- conftest.py
- routers/landscape.py
- test_original_names.py
- NormalisedDocument
- ai_client.py
- make_framework
- test_quality_signals.py
- _live_text
- barycentric.py
- test_patterns_golden.py
- models.py
- test_api_alignment.py
- test_scope_completeness.py
- Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6
- test_stage_a_repairs_one_bad_reply_and_carries_on
- MonkeyPatch
- AppError
- env.py
- Story
- get_session
- patterns_fixtures.py
- TestVersionBinding
- BarycentricError
- quality_jsx
- to_cartesian
- test_the_list_shows_the_context_a_reader_needs
- quality_css
- Shape
- render_paper_pack
- routers/patterns.py

## God Nodes (most connected - your core abstractions)
1. `FrameworkDefinition` - 140 edges
2. `build_golden_dataset()` - 115 edges
3. `make_framework()` - 112 edges
4. `Anecdote` - 96 edges
5. `Signification` - 71 edges
6. `Framework` - 69 edges
7. `get_session()` - 50 edges
8. `ImportJob` - 49 edges
9. `parse()` - 41 edges
10. `NormalisedDocument` - 38 edges

## Surprising Connections (you probably didn't know these)
- `Shape` --uses--> `AiError`  [INFERRED]
  tests/test_ai_client.py → backend/ai_client.py
- `_Response` --uses--> `AiError`  [INFERRED]
  tests/test_live_ai.py → backend/ai_client.py
- `TestGoldenCentroid` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py
- `TestRejections` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py
- `TestAnonymityStatementIsTrueOfTheCode` --uses--> `FrameworkDefinition`  [INFERRED]
  tests/test_framework_schema.py → backend/framework_schema.py

## Import Cycles
- 3-file cycle: `frontend/src/patterns/Landscape.jsx -> frontend/src/patterns/Patterns.jsx -> frontend/src/patterns/SessionMode.jsx -> frontend/src/patterns/Landscape.jsx`

## Communities (124 total, 9 thin omitted)

### Community 0 - "test_interpretations.py"
Cohesion: 0.07
Nodes (60): brief(), landscape(), listed(), Session, TestClient, Collective interpretation as an artefact, not data (delta §6, constraint 16).…, One interpretation might round away. Ten cannot., The landscape is the named guard; it is not the only surface that matters.… (+52 more)

### Community 1 - "TestClient"
Cohesion: 0.06
Nodes (42): qr_png_bytes(), QR codes for capture links (PRD §4, §1.8). A QR is how a phone gets to the…, Return a PNG of ``payload`` as QR, as raw bytes. Error correction is set to M…, RateLimiter, Rate limiting for the public capture endpoints (PRD §4). The public endpoints…, A sliding-window counter keyed by an opaque string. Deliberately simple and in-…, Record a hit and report whether it is within the limit., Forget counters. Used by tests and when a link is revoked. (+34 more)

### Community 2 - "TestClient"
Cohesion: 0.15
Nodes (10): _framework(), TestClient, PRD §9 assumption 7: reflection shows one signifier., Skipping every question is allowed; the story is the point., A slightly-off placement is repaired, not thrown away., Constraint 7: a respondent must be able to act on the message., A story goes in through the wizard and comes back out intact., _submit() (+2 more)

### Community 3 - "edit_semantics.py"
Cohesion: 0.10
Nodes (24): build_edit_log_entries(), diff_text_fields(), Any, datetime, The wording-fix vs meaning-change guardrail (PRD §1.1, constraint 13g). While a…, The shape of a framework, ignoring every word in it. Two definitions with the…, Flatten a definition into ``{field_path: text}`` for every string leaf., Every changed string, as ``(field_path, old_text, new_text)``. Field paths read… (+16 more)

### Community 4 - "make_engine"
Cohesion: 0.16
Nodes (20): _connect_args(), make_engine(), SQLite needs ``check_same_thread=False`` to serve requests from a pool., Build an engine, enabling SQLite foreign-key enforcement. SQLite ignores…, Config, Engine, alembic_config(), fixture (+12 more)

### Community 5 - "Anecdote"
Cohesion: 0.06
Nodes (48): Anecdote, One story, bound to the exact framework version it was told against.…, _create_full(), _pack_html(), TestClient, The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar). Two…, PRD §1.2a: the story card carries respondent-group tick boxes., The pack renders the version's current wording, not a cached copy. (+40 more)

### Community 6 - "test_import_pipeline.py"
Cohesion: 0.11
Nodes (58): A two-sheet workbook: one of responses, one lookup table to ignore. The…, txt_bytes(), xlsx_bytes(), _confirm(), _confirmation_body(), _organise(), parametrize, Session (+50 more)

### Community 7 - "TestClient"
Cohesion: 0.11
Nodes (27): _add_story(), _create(), _definition(), Session, TestClient, The wording-fix vs meaning-change state machine (PRD §6, constraint 13g). This…, Constraint 7: the operator must be able to act on the message., A wording fix patches in place and appends to the edit log. (+19 more)

### Community 8 - "request_json"
Cohesion: 0.12
Nodes (23): Any, Ask for one JSON object of the given shape, or fail in plain English. In mock…, request_json(), live(), fixture, MonkeyPatch, The one AI client, and the four promises constraint 6 makes about it., Valid JSON of the wrong shape is just as unusable as invalid JSON. (+15 more)

### Community 9 - "test_public_identifier_absence.py"
Cohesion: 0.15
Nodes (17): _clear_limits(), _framework(), _link(), fixture, TestClient, Constraint 9 on the remote path (PRD §6 Phase 4: identifier-absence test).…, Sweep every column of every table, not just the ones we expect., Structural guards: not "it doesn't today", but "it has no way to". (+9 more)

### Community 10 - "propose_import"
Cohesion: 0.06
Nodes (48): confirm_mapping(), create_import(), get_import(), list_imports(), _load(), organise_import(), propose_import(), Depends (+40 more)

### Community 11 - "package.json"
Cohesion: 0.06
Nodes (30): eslint, @eslint/js, eslint-plugin-react, eslint-plugin-react-hooks, dependencies, react, react-dom, description (+22 more)

### Community 12 - "validate_definition"
Cohesion: 0.06
Nodes (24): default_definition(), Parse and validate a raw ``definition_json`` payload., A minimal, valid definition — what a brand-new framework starts from., validate_definition(), Base, Declarative base carrying the shared naming convention., DeclarativeBase, Validation of ``definition_json`` and the anonymity statement it carries. (+16 more)

### Community 13 - "test_story_browser.py"
Cohesion: 0.15
Nodes (30): _browse(), _mark(), TestClient, The story browser (PRD §1.6, §5.4). The last item of §1's scope, and the one…, Constraint 1, on the reading side. The queue is where pending lives., Constraint 3 shown, constraint 9 absent — the same as every other view., They share a table, so this is the join worth testing., It is stored as one, which is exactly why this is worth asserting. (+22 more)

### Community 14 - "test_landscape.py"
Cohesion: 0.09
Nodes (47): _capture(), _landscape(), _panel(), Session, TestClient, The landscape suite: the terrain, its contour twin, the drill, the clusters.…, PRD §9 assumption 8 pins it; a different rule is a different terrain., The single-source test PRD §6 asks for. The surface and the contour are not two… (+39 more)

### Community 15 - "parsers.py"
Cohesion: 0.11
Nodes (31): Block, _blocks_from_text(), classify(), _clean_row(), _decode(), _parse_captions(), _parse_csv(), _parse_docx() (+23 more)

### Community 16 - "_run_node"
Cohesion: 0.11
Nodes (14): parametrize, Voice fallback (PRD §6 Phase 4, §7.12, constraint 10). Constraint 10 says voice…, The UI calls stop() on unmount whether or not voice ever started., Stopping on purpose is not a failure and must not show a warning., Constraint 10: voice always paired with typing., Interim results would rewrite a respondent's words as they speak., §7.12: voice fails plain-English with a working fallback., Constraint 7: no jargon a respondent cannot act on. (+6 more)

### Community 17 - "extraction.py"
Cohesion: 0.20
Nodes (18): _balance(), Candidate, confirm(), confirm_narrative(), confirm_tabular(), ExtractionError, BaseModel, Exception (+10 more)

### Community 18 - "backend/patterns.py"
Cohesion: 0.14
Nodes (28): aggregate(), Bar, _bars(), CategoryChart, _demographics(), _dyad_chart(), _histogram(), _mcq_chart() (+20 more)

### Community 19 - "test_signification_provenance.py"
Cohesion: 0.12
Nodes (37): expert_validated_ids(), mixed_dataset(), patterns(), placed(), plotted(), parametrize, TestClient, Whose interpretation a figure is made of (delta §6, constraint 14). Constraint… (+29 more)

### Community 20 - "parse"
Cohesion: 0.06
Nodes (54): parse(), Read one uploaded file into the normalised shape, or refuse it. Refusals are…, csv_bytes(), docx_bytes(), pdf_bytes(), _pdf_escape(), pptx_bytes(), Real files, in memory, one per format Narrative Lens claims to read. Acceptance… (+46 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "Signification"
Cohesion: 0.11
Nodes (20): One respondent (or validated AI) placement on one signifier. ``value_json``…, A free-text tag the analyst attaches to a story., Signification, Tag, _anecdote(), _framework(), parametrize, CRUD across the six tables of PRD §3, plus the vocabularies they enforce. (+12 more)

### Community 23 - "TriadChart"
Cohesion: 0.13
Nodes (28): _axes(), Cell, _cell_index(), compute(), Landscape, LandscapePoint, _local_maxima(), _nearest_corner() (+20 more)

### Community 24 - "imports.py"
Cohesion: 0.17
Nodes (36): ConfirmedExtraction, The arithmetic the Mapping screen shows, and that has to add up., The operator's confirmed mapping for one sheet., Reconciliation, SheetMapping, ImportJob, One uploaded file moving through the two-stage ingestion machine., NarrativeSegment (+28 more)

### Community 25 - "TestClient"
Cohesion: 0.14
Nodes (9): TestClient, List, create and fetch frameworks (PRD §4)., A new framework starts valid and empty, ready to fill in., The Studio shows these live while the operator edits., Constraint 7: plain English, with something to do about it., PRD §5.1: version history sidebar shows versions with story counts., TestCreate, TestFetch (+1 more)

### Community 26 - "PRD: Narrative Lens — Local Narrative Sense-Making App"
Cohesion: 0.10
Nodes (19): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 11. Changelog v1.2 → v1.3, 1. Scope, 2. Binding constraints (restate these in every session), 3. Data model (SQLite, via SQLAlchemy + Alembic), 4. API contract (FastAPI, all JSON), 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages). (+11 more)

### Community 27 - "Decisions"
Cohesion: 0.06
Nodes (30): Completeness pass, Decisions, Delta phase A, Delta phase B, Delta phase C, Delta phase D, Fixed, Narrative Lens — Progress (+22 more)

### Community 28 - "build_golden_dataset"
Cohesion: 0.17
Nodes (29): build_golden_dataset(), TestClient, Create the framework and its twenty stories. Returns the framework., _clusters(), _explorer(), TestClient, The 3D Explorer and the k-means overlay. Acceptance criterion 11: the Explorer…, PRD §9 assumption 8 pins the seed; the same stories always group the same. (+21 more)

### Community 29 - "api.js"
Cohesion: 0.14
Nodes (11): api, ApiError, App(), TABS, CaptureTab(), MODES, LinkManager(), PaperBatch() (+3 more)

### Community 30 - "test_capture_draft.py"
Cohesion: 0.15
Nodes (18): Drafts survive a reload (PRD §6 Phase 3, §7.6). The draft lives in the browser,…, Nothing lingers once the story has been sent., Starting fresh is recoverable; crashing on load is not., A draft from an older shape must not crash the wizard., Private browsing must not stop someone telling their story., Constraint 9 reaches into the browser, not just the database., Offering to restore an empty draft would be noise., The whole point: a half-written story survives the page going away. (+10 more)

### Community 31 - "Widgets.jsx"
Cohesion: 0.24
Nodes (15): CORNER_0, CORNER_1, CORNER_2, normalise(), roundTo(), toBarycentric(), toCartesian(), TRIANGLE_HEIGHT (+7 more)

### Community 32 - "Landscape.jsx"
Cohesion: 0.13
Nodes (21): CLUSTER_TOKENS, ExplorerView(), Scatter(), VIEW, ContourTwin(), Terrain(), terrainStops(), VIEW (+13 more)

### Community 33 - "test_error_surface.py"
Cohesion: 0.11
Nodes (28): AST, _error(), _messages(), parametrize, TestClient, The plain-English error pass, held as a test (constraint 7, PRD §4). Individual…, The literal text of a string argument, with ``{}`` for what is filled in., Every written error triple in the backend: (file, line, message, action). Non-… (+20 more)

### Community 34 - "test_terrain_maths.py"
Cohesion: 0.14
Nodes (22): The landscape's geometry, held to fixed answers in Node. The terrain is drawn…, Rotation moves the terrain, it does not grow or shrink it., Nothing crosses a level the whole grid is already above., The answer known by hand: one peak, one loop, and it encircles the peak., Contours nest. If they did not, the terrain would be unreadable., What makes the terrain survive a grayscale screenshot (§5b)., Two equal heights project to the same rise, wherever they sit. A perspective…, Elevation is the camera's angle above the horizon, as it sounds. From the… (+14 more)

### Community 35 - "clusters.py"
Cohesion: 0.16
Nodes (21): Cluster, ClusterAssignment, ClusterSet, Dimension, dimensions_of(), explorer(), ExplorerPoint, ExplorerSet (+13 more)

### Community 36 - "test_patterns.py"
Cohesion: 0.11
Nodes (40): median_ms(), How long a call takes, measured as a median rather than a single sample. PRD §4…, _capture(), _patterns(), TestClient, The patterns endpoint: what it counts, what it sorts, what it refuses. Three…, The no-bypass promise, applied to what the operator actually sees., A meaning change: version n+1, old stories left on the old wording. (+32 more)

### Community 37 - "StonesAxis"
Cohesion: 0.40
Nodes (3): One axis of the stones canvas, named at both ends., StonesAxis, model_validator

### Community 38 - "backend/interpretations.py"
Cohesion: 0.14
Nodes (24): for_framework(), InterpretationIn, InterpretationOut, BaseModel, Session, Collective interpretation: what a room concluded, kept as an artefact.…, Store one conclusion exactly as the room gave it. The text goes in unchanged.…, Every conclusion recorded against these framework versions, newest first. Takes… (+16 more)

### Community 39 - "test_exports.py"
Cohesion: 0.09
Nodes (49): _brief(), _csv(), _heard(), TestClient, The CSV and the Pattern Brief. The CSV is tested as a file a person will open…, The case the provenance column exists for., Constraint 13f, the whole point of the brief., A brief that did not say what it excluded would be misleading. (+41 more)

### Community 40 - "voice.js"
Cohesion: 0.28
Nodes (11): appendDictation(), getRecognitionClass(), isVoiceSupported(), startDictation(), VOICE_DENIED, VOICE_FAILED, VOICE_NETWORK, VOICE_NO_SPEECH (+3 more)

### Community 41 - "ValidationQueue.jsx"
Cohesion: 0.12
Nodes (8): fromStored(), ImportTab(), MarkUpStep(), storyCount(), MappingScreen(), signifiersInOrder(), ValidationQueue(), widgetValues()

### Community 42 - "test_design_linter.py"
Cohesion: 0.05
Nodes (60): lint_prompt(), What the model is asked about: the question set, and nothing else.…, check(), lint_css(), panel_source(), MonkeyPatch, Session, TestClient (+52 more)

### Community 43 - "Wizard.jsx"
Cohesion: 0.21
Nodes (17): clearDraft(), draftHasContent(), draftKey(), loadDraft(), safeStorage(), saveDraft(), orderedSignifiers(), toSubmission() (+9 more)

### Community 44 - "Studio.jsx"
Cohesion: 0.15
Nodes (11): EditKindDialog(), describePath(), GROUPS, isIndex(), LEAVES, SILENT, Field(), SignifierEditor() (+3 more)

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
Cohesion: 0.08
Nodes (41): FrameworkDefinition, The whole respondent-facing definition of one framework version., One id namespace across all signifier kinds — significations key on it., How many signifier screens the respondent will see., PRD §1.1: warn past roughly six signifier screens., Coarse 'respondent minutes' estimate shown live in the Studio., Estimated respondent time, rounded to one decimal., chunks() (+33 more)

### Community 49 - "test_capture.py"
Cohesion: 0.14
Nodes (11): Local capture (PRD §6 Phase 3). The tests the PRD names for this phase: wizard…, Constraint 3: provenance on every record., PRD §6 Phase 3: batch entry writes paper provenance., Constraint 9, at the moment a story is actually written., Nothing may smuggle an identifier in alongside the story., Constraint 1 gates AI output; first-hand testimony is not AI output., PRD §6 Phase 3: p95 < 200ms on submit., TestAnonymityAtCapture (+3 more)

### Community 50 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 51 - "Web Design & Data Visualization"
Cohesion: 0.22
Nodes (8): Data visualization, Output, Step 1: Frame the brief, Step 2: Design plan before code, Step 3: B2B or B2C playbook, Step 4: Build to the quality floor (non-negotiable, never announced), Step 5: Critique pass, Web Design & Data Visualization

### Community 52 - "queue.py"
Cohesion: 0.07
Nodes (54): CaptureError, _check_dyad(), _check_mcq(), _check_stones(), _check_triad(), ValueError, Validating a submitted capture against the framework it answers (PRD §4). A…, Triad weights: one per corner, non-negative, summing to 1.0. (+46 more)

### Community 53 - "backend/exports.py"
Cohesion: 0.09
Nodes (36): Convert a point in the triangle into three corner weights summing to 1.0. The…, to_barycentric(), _category_finding(), dataset_csv(), _dyad_finding(), findings(), headline(), _headlines() (+28 more)

### Community 54 - "export_brief"
Cohesion: 0.28
Nodes (13): export_brief(), export_csv(), export_heard(), Depends, get, Query, Session, The Pattern Brief: findings in markdown, generated from the figures. (+5 more)

### Community 55 - "Design System Reference — 2026"
Cohesion: 0.29
Nodes (6): 2026 trend catalog — pick deliberately, one direction per project, Banned defaults (the "AI look"), Copy rules, Design System Reference — 2026, Layout heuristics, Tokens

### Community 56 - "test_health.py"
Cohesion: 0.29
Nodes (5): The one endpoint Phase 1 ships., PRD §4 budgets 200ms for non-AI endpoints; health should be far under., Guard against building ahead of the phase plan (PRD §6). Enumerated from the…, test_health_is_fast_enough_for_the_200ms_budget(), test_no_routes_beyond_the_current_phase()

### Community 57 - "AiError"
Cohesion: 0.16
Nodes (16): AiError, Exception, An AI call that failed in a way the operator needs told about. Carries the PRD…, APIConnectionError, APIStatusError, _Block, _FakeAnthropic, _FakeMessages (+8 more)

### Community 58 - "Narrative Lens — binding project instructions"
Cohesion: 0.29
Nodes (6): Added by `SPEC_DELTA_meaningfulness_20260902.md` (delta §2), Binding constraints (restate these in every session), graphify, Narrative Lens — binding project instructions, Project skills, Session protocol

### Community 59 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 60 - "State File Templates"
Cohesion: 0.33
Nodes (5): API_CONTRACT.md (only for projects with a backend + frontend), DECISIONS.md (why things are the way they are), GUIDE.md (the owner's manual — plain language only), PROJECT_STATE.md (the resume file — most important), State File Templates

### Community 61 - "Narrative Lens — Latest"
Cohesion: 0.18
Nodes (10): How to resume, Narrative Lens — Latest, Next step, Running it yourself, The completeness pass, after Phase 9, The meaningfulness delta — phase A is done, The meaningfulness delta — phase B is done, The meaningfulness delta — phase C is done (+2 more)

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

### Community 82 - "CaptureResult"
Cohesion: 0.18
Nodes (13): CaptureSubmission, LocalCaptureSubmission, PublicCaptureSubmission, BaseModel, A capture arriving through a capture link. ``framework_id`` is not accepted:…, A whole capture: one story plus its placements. Note what is *not* here: no id,…, A capture from the operator's own machine: admin, paper entry, or kiosk. Only…, CaptureResult (+5 more)

### Community 83 - "propose.py"
Cohesion: 0.24
Nodes (12): describe_signifiers(), _mock_batch(), _mock_confidence(), _mock_value(), _prompt(), Any, Stage B — Propose (PRD §4a, constraint 1). Stage B reads a story and *suggests*…, The questions, with the exact answer shape each one takes. Written out in full… (+4 more)

### Community 84 - "browse_stories"
Cohesion: 0.08
Nodes (30): browse_stories(), MarksIn, BaseModel, Depends, ge, get, put, Query (+22 more)

### Community 85 - "Patterns.jsx"
Cohesion: 0.09
Nodes (19): BarChart(), DyadChart(), StonesChart(), LandscapeView(), FILTERS, lineageOf(), optionsFrom(), PatternsTab() (+11 more)

### Community 86 - "framework_schema.py"
Cohesion: 0.10
Nodes (38): CaptureSettings, Dyad, Mcq, BaseModel, Validation for ``frameworks.definition_json`` (PRD §3 and §5). Every…, A 2D canvas on which the respondent places named chips., A multiple-choice question., Every non-signifier string the respondent reads, plus capture toggles. (+30 more)

### Community 87 - "test_empty_states.py"
Cohesion: 0.21
Nodes (13): _copy(), parametrize, Path, Every screen tells the operator what to do next (PRD §6, Phase 9). A fresh…, The Studio is the tab the app opens on, so it carries the first word., One name for the thing, in every place the operator can read it. The code calls…, The text of every empty-state paragraph in one screen, tags stripped., No data" is a fact about the database, not help for the person reading. (+5 more)

### Community 88 - "test_landscape_golden.py"
Cohesion: 0.21
Nodes (13): peaks_of(), produce_peaks(), TestClient, The landscape golden — peaks stable to ±0.02 (PRD §6, Phase 8). The second of…, The delta changed which placements are drawn, not where they land. Every story…, Determinism against itself, not only against the stored file., The peaks of one triangle, under a stated provenance choice. ``all`` by…, The headline guarantee: the terrain does not drift under anyone's feet. (+5 more)

### Community 89 - "proposed_import"
Cohesion: 0.13
Nodes (30): confirmed_import(), proposed_import(), TestClient, Shared helpers for the Stage B and validation-queue suites. One framework…, Drive a file as far as ``mapping_confirmed``, accepting Stage A as-is., Drive a file all the way to ``proposed`` — stories in the queue., _backend_modules(), Path (+22 more)

### Community 90 - "Framework"
Cohesion: 0.07
Nodes (58): is_structural_change(), label_renames(), ``{signifier_id: {old_label: new_label}}`` for every renamed label. Only labels…, One stored answer with its labels brought up to date, or unchanged. Shape-…, Whether the edit changes the framework's shape rather than its words., rename_in_value(), conflict(), lint() (+50 more)

### Community 91 - "get_quality"
Cohesion: 0.19
Nodes (13): Select, Narrow a signification query to the chosen provenance (constraint 14). The one…, signified_by_clause(), answered_by_signifier(), get_quality(), Depends, get, Query (+5 more)

### Community 92 - "conftest.py"
Cohesion: 0.24
Nodes (12): client(), db_path(), db_url(), engine(), fixture, Path, TestClient, Shared fixtures. Every test runs against a throwaway SQLite file, never the… (+4 more)

### Community 93 - "routers/landscape.py"
Cohesion: 0.08
Nodes (48): only_validated(), Narrow a query to the stories a person has actually approved. Every read that…, bad_request(), get_clusters(), get_explorer(), get_landscape(), Depends, ge (+40 more)

### Community 94 - "test_original_names.py"
Cohesion: 0.25
Nodes (7): _files(), parametrize, Path, Original names and materials only (constraint 8, acceptance criterion 15). The…, Criterion 15 allows one attribution. One, not none — it is owed. Counted in…, test_no_reserved_name_appears_in_the_app(), test_the_readme_carries_exactly_one_attribution()

### Community 95 - "NormalisedDocument"
Cohesion: 0.15
Nodes (23): _check_narrative(), _check_tabular(), _hinted_column(), _mock_narrative(), _mock_tabular(), _narrative_prompt(), NarrativeOrganisation, organise() (+15 more)

### Community 96 - "ai_client.py"
Cohesion: 0.20
Nodes (10): _fenced_json(), mock_enabled(), _parse(), The one AI client (constraint 6). Every call Narrative Lens makes to a language…, Parse one reply strictly, or raise the reason it could not be parsed., Whether this process runs with mocks instead of the network. Read on every call…, Return *raw* with one surrounding markdown fence removed, if present. Strict…, Payload (+2 more)

### Community 97 - "make_framework"
Cohesion: 0.14
Nodes (33): make_framework(), capture(), link_for(), parametrize, TestClient, The name a storyteller gives their own story (delta §6, items 2 and 5). A…, No name given is the ordinary case, and it must read as a story anyway., A skipped field submits as blank; blank is no name, not a name of "". Otherwise… (+25 more)

### Community 98 - "test_quality_signals.py"
Cohesion: 0.10
Nodes (47): capture(), MonkeyPatch, Session, TestClient, quality(), Data-quality signals: centre-parking and skip rate (delta §6, phase B). The…, Ten stories, all parked. The proportion must be exactly 1.0., Three parked out of four is 0.75, and nothing about the code decides that. (+39 more)

### Community 99 - "_live_text"
Cohesion: 0.20
Nodes (11): _live_text(), One live call to api.anthropic.com. The only network in the app. Imported…, ModuleType, fake_anthropic(), fixture, A reply may carry blocks that are not text; they are not the answer., Strict JSON is asked for on every call, not only where it is convenient., Install a fake ``anthropic`` package and turn mock mode off. (+3 more)

### Community 100 - "barycentric.py"
Cohesion: 0.13
Nodes (21): distance_from_centre(), _placed(), point_from_value_json(), Triad barycentric maths. A triad answer is a point inside an equilateral…, How far a placement sits from the middle of the triangle. Plain Euclidean…, A stored answer straight to its point in the triangle. Exactly…, The conversion itself, on weights already known to be usable. Kept apart from…, How many placements each provenance holds, before the filter is applied.… (+13 more)

### Community 101 - "test_patterns_golden.py"
Cohesion: 0.11
Nodes (25): main(), Rewrite the goldens. Run deliberately, never automatically. python -m…, produce(), produce_participant(), TestClient, The pattern golden — byte-identical from Phase 7 onward (PRD §6). Twenty…, Determinism, checked against itself rather than against the file. If…, A golden that missed a kind would pin three quarters of the maths. (+17 more)

### Community 102 - "models.py"
Cohesion: 0.15
Nodes (18): hour_rounded_now(), _in_clause(), datetime, The six-table schema from PRD §3. Two constraints shape this module directly: *…, Render a SQL ``IN`` predicate for a CHECK constraint., Naive UTC now, for operator-side records that carry no respondent link., Naive UTC now truncated to the hour (constraint 9). Minutes, seconds and…, utcnow() (+10 more)

### Community 103 - "test_api_alignment.py"
Cohesion: 0.31
Nodes (9): _frontend_paths(), The frontend and the backend agree about what exists (contract alignment).…, Every ``/api/...`` address api.js can build, with its parameters blanked., An endpoint nothing calls is either dead or half-finished., A guard on the guard: an empty comparison would pass both tests above., _server_paths(), test_every_address_the_frontend_calls_exists_on_the_server(), test_every_endpoint_is_reached_by_something() (+1 more)

### Community 104 - "test_scope_completeness.py"
Cohesion: 0.16
Nodes (13): TestClient, Every item of PRD §1's scope is actually reachable in the app. This file exists…, One assertion per numbered item of §1 that the API is responsible for., §5.4: "Landscape (default) · Supporting charts · 3D Explorer · Story browser"., The four verbs §1.6 lists, each with something in the code doing it., Dataset CSV · contour PNG · supporting-charts PNG · brief · what we heard., Acceptance criterion 1 ends "QR on home", and the home screen is the Studio., _source() (+5 more)

### Community 105 - "Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6"
Cohesion: 0.11
Nodes (17): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 1. Scope, 2. Binding constraints restated, 3. Data model changes, 4. API contract, 4a. New AI calls — both through `ai_client.request_json`, both mocked, 5. Frontend changes (+9 more)

### Community 106 - "test_stage_a_repairs_one_bad_reply_and_carries_on"
Cohesion: 0.24
Nodes (9): _calls(), Any, Answer each successive request with the next reply in the list., PRD §6 Phase 7: the repair path, exercised through Stage A itself., Every request made, across every client. ``_live_text`` builds a fresh…, _replies(), _Response, test_stage_a_repairs_one_bad_reply_and_carries_on() (+1 more)

### Community 107 - "MonkeyPatch"
Cohesion: 0.36
Nodes (8): MonkeyPatch, TestClient, Acceptance criterion 12: offline is a working state, not a broken one., The operator loses the click, not the file., test_a_file_waiting_to_be_analysed_survives_the_outage(), test_analyse_fails_in_a_sentence_when_there_is_no_key(), test_everything_that_is_not_analyse_still_works_offline(), test_stage_b_also_degrades_gracefully()

### Community 108 - "AppError"
Cohesion: 0.33
Nodes (5): AppError, An error the operator is meant to read and act on., Something outside the app misbehaved — currently only the AI service., upstream(), HTTPException

### Community 109 - "env.py"
Cohesion: 0.27
Nodes (9): Alembic environment. The database URL comes from…, Emit SQL to a script without a live connection., Run migrations against a live connection., _run(), run_migrations_offline(), run_migrations_online(), _url(), database_url() (+1 more)

### Community 110 - "Story"
Cohesion: 0.40
Nodes (5): BaseModel, One story as the browser lists it., A page of the browser, and everything the screen needs around it., Story, StoryPage

### Community 112 - "get_session"
Cohesion: 0.10
Nodes (42): get_session(), Session, FastAPI dependency yielding a session that always closes., not_found(), CaptureLink, A token-gated capture URL pointing at one exact framework version., capture_link_qr(), capture_url() (+34 more)

### Community 113 - "patterns_fixtures.py"
Cohesion: 0.50
Nodes (4): The twenty-story fixture behind the pattern golden (PRD §6, Phase 7). Twenty…, One story, entirely determined by its position in the run., story_payload(), _tenths()

### Community 114 - "TestVersionBinding"
Cohesion: 0.40
Nodes (3): A meaning change after capture must not move existing stories., Answering v1's question against v2 must not silently succeed., TestVersionBinding

### Community 115 - "BarycentricError"
Cohesion: 0.07
Nodes (31): BarycentricError, from_value_json(), is_inside(), normalise(), ValueError, Clamp to the triangle and rescale so the three weights sum to exactly 1.0. A…, Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`., Whether the weights describe a point in or on the triangle. (+23 more)

### Community 116 - "quality_jsx"
Cohesion: 0.22
Nodes (9): patterns_jsx(), quality_jsx(), The panel component, with its comments stripped, for the same reason., Collapsed by default (delta §5). A ``details`` with no ``open``., Below them, not beside them — it is a check read after the answers., Constraint 11: it reports, and offers no reading of this data. The one…, test_the_panel_is_closed_until_it_is_asked_for(), test_the_panel_sits_below_the_supporting_charts() (+1 more)

### Community 118 - "to_cartesian"
Cohesion: 0.12
Nodes (16): Convert three corner weights into a point inside the triangle. >>>…, to_cartesian(), The dead centre is the equal-weight answer — the most-read position., TestGoldenCentroid, TestRejections, The centroid and "no lean at all" have to be the same point. To the precision…, test_a_corner_is_not_near_the_centre(), test_the_centre_is_where_equal_weights_land() (+8 more)

### Community 119 - "test_the_list_shows_the_context_a_reader_needs"
Cohesion: 0.67
Nodes (3): parametrize, A sentence about "this landscape" is worthless without the landscape., test_the_list_shows_the_context_a_reader_needs()

### Community 120 - "quality_css"
Cohesion: 0.25
Nodes (8): quality_css(), Just the panel's own declarations, with the prose taken out. Comments are…, Constraint 13c, and the reason this panel can be read in greyscale. Every…, Quiet weight (13a). The landscape is the one bold element on this tab. Nothing…, Constraint 10: a phone at 375px must not be pushed sideways by a table., test_the_panel_encodes_nothing_in_colour(), test_the_panel_never_shouts(), test_the_wide_table_scrolls_inside_itself()

### Community 124 - "render_paper_pack"
Cohesion: 0.33
Nodes (6): _facilitator_sheet(), The A4 story card: prompt, ruled space, groups, anonymity line., Running instructions, materials, and the reconciliation grid., Render the whole pack as one self-contained, printable HTML page., render_paper_pack(), _story_card()

### Community 126 - "routers/patterns.py"
Cohesion: 0.09
Nodes (27): only_pending(), Select, What counts as data, in one place (constraint 1). An anecdote exists in three…, Narrow a query to the stories still waiting on a person., Database engine and session plumbing (constraint 4: SQLite + local files)., The error shape from PRD §4. ``{"error": {"code": ..., "message": plain-English…, health(), mount_frontend() (+19 more)

## Knowledge Gaps
- **198 isolated node(s):** `name`, `version`, `description`, `dev`, `build` (+193 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Anecdote` connect `Anecdote` to `TestClient`, `TestClient`, `test_import_pipeline.py`, `TestClient`, `test_public_identifier_absence.py`, `propose_import`, `validate_definition`, `test_landscape.py`, `Signification`, `imports.py`, `test_queue.py`, `test_capture.py`, `queue.py`, `CaptureResult`, `browse_stories`, `proposed_import`, `Framework`, `test_quality_signals.py`, `models.py`, `Story`, `get_session`, `TestVersionBinding`, `routers/patterns.py`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `FrameworkDefinition` connect `FrameworkDefinition` to `edit_semantics.py`, `validate_definition`, `backend/patterns.py`, `TriadChart`, `imports.py`, `clusters.py`, `test_design_linter.py`, `queue.py`, `backend/exports.py`, `test_placement_shape_parity.py`, `CaptureResult`, `propose.py`, `framework_schema.py`, `Framework`, `routers/landscape.py`, `barycentric.py`, `models.py`, `get_session`, `render_paper_pack`, `routers/patterns.py`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `make_framework()` connect `make_framework` to `test_quality_signals.py`, `test_patterns.py`, `test_exports.py`, `test_design_linter.py`, `MonkeyPatch`, `test_queue.py`, `test_landscape.py`, `test_story_browser.py`, `test_signification_provenance.py`, `proposed_import`, `build_golden_dataset`, `AiError`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 59 inferred relationships involving `FrameworkDefinition` (e.g. with `CaptureError` and `CaptureSubmission`) actually correct?**
  _`FrameworkDefinition` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 57 inferred relationships involving `Anecdote` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Anecdote` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `Signification` (e.g. with `CaptureResult` and `FrameworkCreate`) actually correct?**
  _`Signification` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _198 weakly-connected nodes found - possible documentation gaps or missing edges._