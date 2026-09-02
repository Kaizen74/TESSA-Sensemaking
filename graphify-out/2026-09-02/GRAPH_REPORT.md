# Graph Report - TESSA-Sensemaking  (2026-09-02)

## Corpus Check
- 153 files · ~155,917 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2625 nodes · 6274 edges · 129 communities (116 shown, 13 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 458 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9fe2d7d5`
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
- build_golden_dataset
- parsers.py
- _run_node
- NormalisedDocument
- backend/patterns.py
- test_signification_provenance.py
- parse
- What You Must Do When Invoked
- CaptureLink
- backend/landscape.py
- routers/landscape.py
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
- framework_schema.py
- aggregate
- test_exports.py
- voice.js
- ImportTab.jsx
- _FakeAnthropic
- Wizard.jsx
- Studio.jsx
- test_queue.py
- The session loop (every session, no exceptions)
- Data Visualization Reference — 2026
- FrameworkDefinition
- organise
- graphify reference: extra exports and benchmark
- Web Design & Data Visualization
- Anecdote
- backend/exports.py
- get_session
- Design System Reference — 2026
- test_health.py
- test_live_ai.py
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
- main.py
- ValidationQueue.jsx
- propose.py
- models.py
- Patterns.jsx
- paper_pack.py
- test_empty_states.py
- test_landscape_golden.py
- AiError
- ai_client.py
- _calls
- errors.py
- routers/patterns.py
- test_original_names.py
- organise.py
- _live_text
- make_framework
- test_quality_signals.py
- .estimated_minutes
- routers/quality.py
- test_patterns_golden.py
- CaptureError
- test_api_alignment.py
- test_scope_completeness.py
- Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6
- ingest_fixtures.py
- conftest.py
- barycentric.py
- env.py
- normalise
- public.py
- to_barycentric
- field_validator
- parametrize
- quality_jsx
- test_widget_backend_parity.py
- to_cartesian
- db.py
- quality_css
- SignifiedByCounts
- distance_from_centre
- TriadChart
- patterns_fixtures.py
- TestGoldenCentroid
- test_five_thousand_stories_cost_less_than_the_charts_beside_them
- test_the_quality_modules_import_nothing_ai_shaped
- test_the_whole_circle_fits_inside_the_triangle

## God Nodes (most connected - your core abstractions)
1. `FrameworkDefinition` - 132 edges
2. `make_framework()` - 97 edges
3. `Anecdote` - 95 edges
4. `build_golden_dataset()` - 92 edges
5. `Signification` - 69 edges
6. `Framework` - 67 edges
7. `ImportJob` - 49 edges
8. `get_session()` - 46 edges
9. `parse()` - 41 edges
10. `NormalisedDocument` - 38 edges

## Surprising Connections (you probably didn't know these)
- `Shape` --uses--> `AiError`  [INFERRED]
  tests/test_ai_client.py → backend/ai_client.py
- `_FakeAnthropic` --uses--> `AiError`  [INFERRED]
  tests/test_live_ai.py → backend/ai_client.py
- `_FakeMessages` --uses--> `AiError`  [INFERRED]
  tests/test_live_ai.py → backend/ai_client.py
- `_Response` --uses--> `AiError`  [INFERRED]
  tests/test_live_ai.py → backend/ai_client.py
- `TestGoldenAsymmetricPlacements` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py

## Import Cycles
- None detected.

## Communities (129 total, 13 thin omitted)

### Community 0 - "BarycentricError"
Cohesion: 0.20
Nodes (10): BarycentricError, from_value_json(), ValueError, Reject anything that is not a usable triad answer., Read a stored ``significations.value_json`` into ordered weights., Raised when a placement cannot be read as a triad answer., _validated(), Reading a stored signification back into ordered weights. (+2 more)

### Community 1 - "TestClient"
Cohesion: 0.08
Nodes (30): qr_png_bytes(), Return a PNG of ``payload`` as QR, as raw bytes. Error correction is set to M…, _framework(), _link(), TestClient, Capture links and the public capture path (PRD §6 Phase 4). The tests the PRD…, PRD §6 Phase 4: token lifecycle. §7.6: revoked links close., The heart of §7.6: a taken-down QR poster cannot keep collecting. (+22 more)

### Community 2 - "TestClient"
Cohesion: 0.09
Nodes (24): _framework(), TestClient, Local capture (PRD §6 Phase 3). The tests the PRD names for this phase: wizard…, PRD §9 assumption 7: reflection shows one signifier., Skipping every question is allowed; the story is the point., Constraint 3: provenance on every record., PRD §6 Phase 3: batch entry writes paper provenance., Constraint 9, at the moment a story is actually written. (+16 more)

### Community 3 - "Framework"
Cohesion: 0.05
Nodes (72): build_edit_log_entries(), diff_text_fields(), is_structural_change(), label_renames(), Any, datetime, The wording-fix vs meaning-change guardrail (PRD §1.1, constraint 13g). While a…, ``{signifier_id: {old_label: new_label}}`` for every renamed label. Only labels… (+64 more)

### Community 4 - "make_engine"
Cohesion: 0.16
Nodes (20): _connect_args(), make_engine(), SQLite needs ``check_same_thread=False`` to serve requests from a pool., Build an engine, enabling SQLite foreign-key enforcement. SQLite ignores…, Config, Engine, alembic_config(), fixture (+12 more)

### Community 5 - "TestClient"
Cohesion: 0.10
Nodes (23): _create_full(), _pack_html(), TestClient, The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar). Two…, PRD §1.2a: the story card carries respondent-group tick boxes., The pack renders the version's current wording, not a cached copy., Constraint 9: the anonymity statement is printed verbatim on the card., Whatever this version says is what the card prints — no substitution. (+15 more)

### Community 6 - "test_import_pipeline.py"
Cohesion: 0.14
Nodes (50): A two-sheet workbook: one of responses, one lookup table to ignore. The…, txt_bytes(), xlsx_bytes(), _confirm(), _confirmation_body(), _organise(), parametrize, Session (+42 more)

### Community 7 - "TestClient"
Cohesion: 0.11
Nodes (27): _add_story(), _create(), _definition(), Session, TestClient, The wording-fix vs meaning-change state machine (PRD §6, constraint 13g). This…, Constraint 7: the operator must be able to act on the message., A wording fix patches in place and appends to the edit log. (+19 more)

### Community 8 - "request_json"
Cohesion: 0.11
Nodes (25): Any, Ask for one JSON object of the given shape, or fail in plain English. In mock…, request_json(), live(), BaseModel, fixture, MonkeyPatch, The one AI client, and the four promises constraint 6 makes about it. (+17 more)

### Community 9 - "test_public_identifier_absence.py"
Cohesion: 0.08
Nodes (28): RateLimiter, Rate limiting for the public capture endpoints (PRD §4). The public endpoints…, A sliding-window counter keyed by an opaque string. Deliberately simple and in-…, Record a hit and report whether it is within the limit., Forget counters. Used by tests and when a link is revoked., How many hits are still allowed in the current window., Clear every counter. Tests call this between cases., reset_all() (+20 more)

### Community 10 - "imports.py"
Cohesion: 0.13
Nodes (34): ImportJob, One uploaded file moving through the two-stage ingestion machine., classify(), Return ``(file_type, file_class)`` for a filename, or refuse it., confirm_mapping(), create_import(), _detail(), get_import() (+26 more)

### Community 11 - "package.json"
Cohesion: 0.06
Nodes (30): eslint, @eslint/js, eslint-plugin-react, eslint-plugin-react-hooks, dependencies, react, react-dom, description (+22 more)

### Community 12 - "validate_definition"
Cohesion: 0.06
Nodes (24): default_definition(), Parse and validate a raw ``definition_json`` payload., A minimal, valid definition — what a brand-new framework starts from., validate_definition(), Base, Declarative base carrying the shared naming convention., DeclarativeBase, Validation of ``definition_json`` and the anonymity statement it carries. (+16 more)

### Community 13 - "test_story_browser.py"
Cohesion: 0.15
Nodes (30): _browse(), _mark(), TestClient, The story browser (PRD §1.6, §5.4). The last item of §1's scope, and the one…, Constraint 1, on the reading side. The queue is where pending lives., Constraint 3 shown, constraint 9 absent — the same as every other view., They share a table, so this is the join worth testing., It is stored as one, which is exactly why this is worth asserting. (+22 more)

### Community 14 - "build_golden_dataset"
Cohesion: 0.09
Nodes (54): Every story inside a rectangle of grid cells, and no others. The region drill…, stories_in_region(), hour_rounded_now(), Naive UTC now truncated to the hour (constraint 9). Minutes, seconds and…, build_golden_dataset(), TestClient, Create the framework and its twenty stories. Returns the framework., _capture() (+46 more)

### Community 15 - "parsers.py"
Cohesion: 0.14
Nodes (23): Block, _blocks_from_text(), _clean_row(), _decode(), _parse_captions(), _parse_csv(), _parse_docx(), _parse_pdf() (+15 more)

### Community 16 - "_run_node"
Cohesion: 0.11
Nodes (14): parametrize, Voice fallback (PRD §6 Phase 4, §7.12, constraint 10). Constraint 10 says voice…, The UI calls stop() on unmount whether or not voice ever started., Stopping on purpose is not a failure and must not show a warning., Constraint 10: voice always paired with typing., Interim results would rewrite a respondent's words as they speak., §7.12: voice fails plain-English with a working fallback., Constraint 7: no jargon a respondent cannot act on. (+6 more)

### Community 17 - "NormalisedDocument"
Cohesion: 0.12
Nodes (43): _balance(), Candidate, confirm(), confirm_narrative(), confirm_tabular(), ConfirmedExtraction, ExtractionError, BaseModel (+35 more)

### Community 18 - "backend/patterns.py"
Cohesion: 0.17
Nodes (31): Dyad, Mcq, A 2D canvas on which the respondent places named chips., A multiple-choice question., Every signifier with its kind, in the order the respondent meets them., A triangle with three named corners; answers are barycentric., A slider between two opposing poles; answers are 0–1., Stones (+23 more)

### Community 19 - "test_signification_provenance.py"
Cohesion: 0.12
Nodes (37): expert_validated_ids(), mixed_dataset(), patterns(), placed(), plotted(), parametrize, TestClient, Whose interpretation a figure is made of (delta §6, constraint 14). Constraint… (+29 more)

### Community 20 - "parse"
Cohesion: 0.11
Nodes (27): parse(), Read one uploaded file into the normalised shape, or refuse it. Refusals are…, docx_bytes(), parametrize, Every format PRD §1.3 promises, read from a real file of that format., PRD §1.3 lists nine extensions. All nine are readable, nothing else is., The reverse map the API uses for jobs whose extension is long gone., The empty paragraph between the two stories is skipped, not renumbered.… (+19 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "CaptureLink"
Cohesion: 0.07
Nodes (42): CaptureLink, A token-gated capture URL pointing at one exact framework version., A free-text tag the analyst attaches to a story., Tag, QR codes for capture links (PRD §4, §1.8). A QR is how a phone gets to the…, capture_link_qr(), capture_url(), CaptureLinkCreate (+34 more)

### Community 23 - "backend/landscape.py"
Cohesion: 0.15
Nodes (24): _axes(), Cell, _cell_index(), compute(), Landscape, LandscapePoint, _local_maxima(), _nearest_corner() (+16 more)

### Community 24 - "routers/landscape.py"
Cohesion: 0.18
Nodes (20): get_clusters(), get_explorer(), get_landscape(), Depends, ge, get, le, Query (+12 more)

### Community 25 - "TestClient"
Cohesion: 0.14
Nodes (9): TestClient, List, create and fetch frameworks (PRD §4)., A new framework starts valid and empty, ready to fill in., The Studio shows these live while the operator edits., Constraint 7: plain English, with something to do about it., PRD §5.1: version history sidebar shows versions with story counts., TestCreate, TestFetch (+1 more)

### Community 26 - "PRD: Narrative Lens — Local Narrative Sense-Making App"
Cohesion: 0.10
Nodes (19): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 11. Changelog v1.2 → v1.3, 1. Scope, 2. Binding constraints (restate these in every session), 3. Data model (SQLite, via SQLAlchemy + Alembic), 4. API contract (FastAPI, all JSON), 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages). (+11 more)

### Community 27 - "Decisions"
Cohesion: 0.07
Nodes (28): Completeness pass, Decisions, Delta phase A, Delta phase B, Fixed, Narrative Lens — Progress, Phase 1, Phase 2 (+20 more)

### Community 28 - "test_explorer_clusters.py"
Cohesion: 0.16
Nodes (28): median_ms(), How long a call takes, measured as a median rather than a single sample. PRD §4…, _clusters(), _explorer(), TestClient, The 3D Explorer and the k-means overlay. Acceptance criterion 11: the Explorer…, PRD §9 assumption 8 pins the seed; the same stories always group the same., Acceptance criterion 11: always labelled "descriptive only". (+20 more)

### Community 29 - "api.js"
Cohesion: 0.15
Nodes (10): api, ApiError, App(), TABS, CaptureTab(), MODES, LinkManager(), captureTokenFromPath() (+2 more)

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

### Community 37 - "framework_schema.py"
Cohesion: 0.16
Nodes (10): CaptureSettings, BaseModel, Validation for ``frameworks.definition_json`` (PRD §3 and §5). Every…, Every non-signifier string the respondent reads, plus capture toggles., One id namespace across all signifier kinds — significations key on it., Reject unknown keys so a typo in the Studio surfaces as an error., One axis of the stones canvas, named at both ends., StonesAxis (+2 more)

### Community 38 - "aggregate"
Cohesion: 0.23
Nodes (14): aggregate(), _bars(), _demographics(), _mcq_chart(), one_triad(), placements_by_signifier(), AnswerRow, StoryRow (+6 more)

### Community 39 - "test_exports.py"
Cohesion: 0.09
Nodes (49): _brief(), _csv(), _heard(), TestClient, The CSV and the Pattern Brief. The CSV is tested as a file a person will open…, The case the provenance column exists for., Constraint 13f, the whole point of the brief., A brief that did not say what it excluded would be misleading. (+41 more)

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
Cohesion: 0.22
Nodes (16): clearDraft(), draftHasContent(), draftKey(), loadDraft(), safeStorage(), saveDraft(), PaperBatch(), browserStorage() (+8 more)

### Community 44 - "Studio.jsx"
Cohesion: 0.16
Nodes (11): EditKindDialog(), describePath(), GROUPS, isIndex(), LEAVES, SILENT, Field(), SignifierEditor() (+3 more)

### Community 45 - "test_queue.py"
Cohesion: 0.07
Nodes (72): confirmed_import(), proposed_import(), TestClient, Shared helpers for the Stage B and validation-queue suites. One framework…, Drive a file as far as ``mapping_confirmed``, accepting Stage A as-is., Drive a file all the way to ``proposed`` — stories in the queue., _backend_modules(), Path (+64 more)

### Community 46 - "The session loop (every session, no exceptions)"
Cohesion: 0.20
Nodes (9): 1. SESSION START — recover state before touching anything, 2. PLAN — small increments, 3. BUILD — one increment at a time, 4. TEST — after every increment, before calling it done, 5. CHECKPOINT — commit + state update, every increment, 6. SESSION END (or when the user says "wrap up"), Communication rules (owner is non-technical), Resilient Build (+1 more)

### Community 47 - "Data Visualization Reference — 2026"
Cohesion: 0.20
Nodes (9): Accessibility floor, Chart selection, Color encoding, Dashboard hierarchy, Data Visualization Reference — 2026, First principle, Integrity rules (non-negotiable), Interactivity discipline (+1 more)

### Community 48 - "FrameworkDefinition"
Cohesion: 0.10
Nodes (38): FrameworkDefinition, The whole respondent-facing definition of one framework version., How many signifier screens the respondent will see., PRD §1.1: warn past roughly six signifier screens., chunks(), propose(), Split the stories into calls of at most ``size`` (PRD §4a)., Run Stage B over a file's stories and return checked proposals. Nothing is… (+30 more)

### Community 49 - "organise"
Cohesion: 0.17
Nodes (23): organise(), Run Stage A over a parsed file and return its proposal. Nothing is written to…, csv_bytes(), Any, MonkeyPatch, TestClient, Stage A: what it proposes, and what it is not allowed to get away with. Stage A…, Constraint 4 and 7: offline is a normal state, not a broken one. The file stays… (+15 more)

### Community 50 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 51 - "Web Design & Data Visualization"
Cohesion: 0.22
Nodes (8): Data visualization, Output, Step 1: Frame the brief, Step 2: Design plan before code, Step 3: B2B or B2C playbook, Step 4: Build to the quality floor (non-negotiable, never announced), Step 5: Critique pass, Web Design & Data Visualization

### Community 52 - "Anecdote"
Cohesion: 0.10
Nodes (37): Anecdote, One story, bound to the exact framework version it was told against.…, One respondent (or validated AI) placement on one signifier. ``value_json``…, Signification, counts(), decide(), _finish_job_if_empty(), _low() (+29 more)

### Community 53 - "backend/exports.py"
Cohesion: 0.10
Nodes (32): _category_finding(), dataset_csv(), _dyad_finding(), findings(), headline(), _headlines(), _heard_category(), _join() (+24 more)

### Community 54 - "get_session"
Cohesion: 0.23
Nodes (16): get_session(), Session, FastAPI dependency yielding a session that always closes., export_brief(), export_csv(), export_heard(), Depends, get (+8 more)

### Community 55 - "Design System Reference — 2026"
Cohesion: 0.29
Nodes (6): 2026 trend catalog — pick deliberately, one direction per project, Banned defaults (the "AI look"), Copy rules, Design System Reference — 2026, Layout heuristics, Tokens

### Community 56 - "test_health.py"
Cohesion: 0.29
Nodes (5): The one endpoint Phase 1 ships., PRD §4 budgets 200ms for non-AI endpoints; health should be far under., Guard against building ahead of the phase plan (PRD §6). Enumerated from the…, test_health_is_fast_enough_for_the_200ms_budget(), test_no_routes_beyond_the_current_phase()

### Community 57 - "test_live_ai.py"
Cohesion: 0.21
Nodes (16): _last(), MonkeyPatch, TestClient, The live path to api.anthropic.com — the one Phase 7 switches on. Everything…, Answer each successive request with the next reply in the list., PRD §6 Phase 7: the repair path, exercised through Stage A itself., Acceptance criterion 12: offline is a working state, not a broken one., The operator loses the click, not the file. (+8 more)

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
Cohesion: 0.22
Nodes (8): How to resume, Narrative Lens — Latest, Next step, Running it yourself, The completeness pass, after Phase 9, The meaningfulness delta — phase A is done, The meaningfulness delta — phase B is done, Where things stand

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

### Community 81 - "main.py"
Cohesion: 0.14
Nodes (21): _envelope(), health(), mount_frontend(), plain_http_error(), plain_unexpected_error(), plain_validation_error(), Exception, get (+13 more)

### Community 82 - "ValidationQueue.jsx"
Cohesion: 0.29
Nodes (6): fromStored(), orderedSignifiers(), toSubmission(), signifiersInOrder(), ValidationQueue(), widgetValues()

### Community 83 - "propose.py"
Cohesion: 0.11
Nodes (28): BaseModel, One placement as it arrives from the wizard or paper batch entry., SubmittedSignification, _check_batch(), describe_signifiers(), _mock_batch(), _mock_confidence(), _mock_value() (+20 more)

### Community 84 - "models.py"
Cohesion: 0.06
Nodes (45): only_pending(), Select, What counts as data, in one place (constraint 1). An anecdote exists in three…, Narrow a query to the stories still waiting on a person., _in_clause(), datetime, The six-table schema from PRD §3. Two constraints shape this module directly: *…, Render a SQL ``IN`` predicate for a CHECK constraint. (+37 more)

### Community 85 - "Patterns.jsx"
Cohesion: 0.06
Nodes (39): BarChart(), DyadChart(), StonesChart(), CLUSTER_TOKENS, ExplorerView(), Scatter(), VIEW, ContourTwin() (+31 more)

### Community 86 - "paper_pack.py"
Cohesion: 0.23
Nodes (11): _mcq_options(), The printable paper pack (PRD §1.2, §5b print grammar). One HTML page the…, A square canvas with both axes named at each end., Tick boxes, one per option, big enough to mark with a pen., One A4 landscape sheet for one signifier., A large equilateral triangle with its three corners labelled. Drawn from the…, A long line between two named poles, with tick marks to aim at., _signifier_sheet() (+3 more)

### Community 87 - "test_empty_states.py"
Cohesion: 0.21
Nodes (13): _copy(), parametrize, Path, Every screen tells the operator what to do next (PRD §6, Phase 9). A fresh…, The Studio is the tab the app opens on, so it carries the first word., One name for the thing, in every place the operator can read it. The code calls…, The text of every empty-state paragraph in one screen, tags stripped., No data" is a fact about the database, not help for the person reading. (+5 more)

### Community 88 - "test_landscape_golden.py"
Cohesion: 0.21
Nodes (13): peaks_of(), produce_peaks(), TestClient, The landscape golden — peaks stable to ±0.02 (PRD §6, Phase 8). The second of…, The delta changed which placements are drawn, not where they land. Every story…, Determinism against itself, not only against the stored file., The peaks of one triangle, under a stated provenance choice. ``all`` by…, The headline guarantee: the terrain does not drift under anyone's feet. (+5 more)

### Community 89 - "AiError"
Cohesion: 0.24
Nodes (8): AiError, Exception, An AI call that failed in a way the operator needs told about. Carries the PRD…, APIConnectionError, APIStatusError, _Block, Exception, RateLimitError

### Community 90 - "ai_client.py"
Cohesion: 0.20
Nodes (10): _fenced_json(), mock_enabled(), _parse(), The one AI client (constraint 6). Every call Narrative Lens makes to a language…, Parse one reply strictly, or raise the reason it could not be parsed., Whether this process runs with mocks instead of the network. Read on every call…, Return *raw* with one surrounding markdown fence removed, if present. Strict…, Payload (+2 more)

### Community 91 - "_calls"
Cohesion: 0.29
Nodes (6): _calls(), Any, Strict JSON is asked for on every call, not only where it is convenient., Every request made, across every client. ``_live_text`` builds a fresh…, _Response, test_the_json_instruction_is_appended_to_every_system_prompt()

### Community 92 - "errors.py"
Cohesion: 0.07
Nodes (34): AppError, bad_request(), conflict(), not_found(), The error shape from PRD §4. ``{"error": {"code": ..., "message": plain-English…, An error the operator is meant to read and act on., Something outside the app misbehaved — currently only the AI service., upstream() (+26 more)

### Community 93 - "routers/patterns.py"
Cohesion: 0.13
Nodes (27): only_validated(), Narrow a query to the stories a person has actually approved. Every read that…, distinct_values(), get_patterns(), load_answers(), load_rows(), load_view(), AnswerRow (+19 more)

### Community 94 - "test_original_names.py"
Cohesion: 0.25
Nodes (7): _files(), parametrize, Path, Original names and materials only (constraint 8, acceptance criterion 15). The…, Criterion 15 allows one attribution. One, not none — it is owed. Counted in…, test_no_reserved_name_appears_in_the_app(), test_the_readme_carries_exactly_one_attribution()

### Community 95 - "organise.py"
Cohesion: 0.11
Nodes (27): _check_narrative(), _check_tabular(), _hinted_column(), _mock_narrative(), _mock_tabular(), _narrative_prompt(), NarrativeOrganisation, OrganiseError (+19 more)

### Community 96 - "_live_text"
Cohesion: 0.22
Nodes (11): _live_text(), One live call to api.anthropic.com. The only network in the app. Imported…, ModuleType, fake_anthropic(), fixture, parametrize, A reply may carry blocks that are not text; they are not the answer., Install a fake ``anthropic`` package and turn mock mode off. (+3 more)

### Community 97 - "make_framework"
Cohesion: 0.14
Nodes (33): make_framework(), capture(), link_for(), parametrize, TestClient, The name a storyteller gives their own story (delta §6, items 2 and 5). A…, No name given is the ordinary case, and it must read as a story anyway., A skipped field submits as blank; blank is no name, not a name of "". Otherwise… (+25 more)

### Community 98 - "test_quality_signals.py"
Cohesion: 0.12
Nodes (40): capture(), MonkeyPatch, TestClient, quality(), Data-quality signals: centre-parking and skip rate (delta §6, phase B). The…, Ten stories, all parked. The proportion must be exactly 1.0., Three parked out of four is 0.75, and nothing about the code decides that., A placement just inside the circle counts; one just outside does not. Built by… (+32 more)

### Community 100 - "routers/quality.py"
Cohesion: 0.10
Nodes (28): centre_parked_count(), BaseModel, QualityReport, _rate(), Data-quality signals: centre-parking and skip rate (delta §1 item 4, §5). Two…, A proportion, rounded, with the empty case answered rather than raised., How many of one triad's placements sit inside the centre circle. Reads each…, Assemble the report from counts the caller has already read. Takes numbers… (+20 more)

### Community 101 - "test_patterns_golden.py"
Cohesion: 0.11
Nodes (25): main(), Rewrite the goldens. Run deliberately, never automatically. python -m…, produce(), produce_participant(), TestClient, The pattern golden — byte-identical from Phase 7 onward (PRD §6). Twenty…, Determinism, checked against itself rather than against the file. If…, A golden that missed a kind would pin three quarters of the maths. (+17 more)

### Community 102 - "CaptureError"
Cohesion: 0.10
Nodes (31): CaptureError, CaptureSubmission, _check_dyad(), _check_mcq(), _check_stones(), _check_triad(), LocalCaptureSubmission, ValueError (+23 more)

### Community 103 - "test_api_alignment.py"
Cohesion: 0.31
Nodes (9): _frontend_paths(), The frontend and the backend agree about what exists (contract alignment).…, Every ``/api/...`` address api.js can build, with its parameters blanked., An endpoint nothing calls is either dead or half-finished., A guard on the guard: an empty comparison would pass both tests above., _server_paths(), test_every_address_the_frontend_calls_exists_on_the_server(), test_every_endpoint_is_reached_by_something() (+1 more)

### Community 104 - "test_scope_completeness.py"
Cohesion: 0.16
Nodes (13): TestClient, Every item of PRD §1's scope is actually reachable in the app. This file exists…, One assertion per numbered item of §1 that the API is responsible for., §5.4: "Landscape (default) · Supporting charts · 3D Explorer · Story browser"., The four verbs §1.6 lists, each with something in the code doing it., Dataset CSV · contour PNG · supporting-charts PNG · brief · what we heard., Acceptance criterion 1 ends "QR on home", and the home screen is the Studio., _source() (+5 more)

### Community 105 - "Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6"
Cohesion: 0.11
Nodes (17): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 1. Scope, 2. Binding constraints restated, 3. Data model changes, 4. API contract, 4a. New AI calls — both through `ai_client.request_json`, both mocked, 5. Frontend changes (+9 more)

### Community 106 - "ingest_fixtures.py"
Cohesion: 0.13
Nodes (14): pdf_bytes(), _pdf_escape(), pptx_bytes(), Real files, in memory, one per format Narrative Lens claims to read. Acceptance…, A one-page PDF with each paragraph as its own text run. Written by hand:…, vtt_bytes(), Session, TestClient (+6 more)

### Community 107 - "conftest.py"
Cohesion: 0.24
Nodes (12): client(), db_path(), db_url(), engine(), fixture, Path, TestClient, Shared fixtures. Every test runs against a throwaway SQLite file, never the… (+4 more)

### Community 108 - "barycentric.py"
Cohesion: 0.22
Nodes (10): is_inside(), _placed(), point_from_value_json(), Triad barycentric maths. A triad answer is a point inside an equilateral…, Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`., Whether the weights describe a point in or on the triangle., A stored answer straight to its point in the triangle. Exactly…, The conversion itself, on weights already known to be usable. Kept apart from… (+2 more)

### Community 109 - "env.py"
Cohesion: 0.27
Nodes (9): Alembic environment. The database URL comes from…, Emit SQL to a script without a live connection., Run migrations against a live connection., _run(), run_migrations_offline(), run_migrations_online(), _url(), database_url() (+1 more)

### Community 110 - "normalise"
Cohesion: 0.24
Nodes (6): normalise(), Clamp to the triangle and rescale so the three weights sum to exactly 1.0. A…, PRD §3: triad barycentric sums to 1.0., Even awkward thirds land on a sum of exactly 1.0 after rounding., An imported point a hair outside the triangle is pulled to its edge., TestSumsToOne

### Community 112 - "public.py"
Cohesion: 0.17
Nodes (19): PublicCaptureSubmission, A capture arriving through a capture link. ``framework_id`` is not accepted:…, create_public_capture(), _framework_or_refuse(), get_public_framework(), _link_or_refuse(), PublicFrameworkOut, BaseModel (+11 more)

### Community 113 - "to_barycentric"
Cohesion: 0.22
Nodes (7): Convert a point in the triangle into three corner weights summing to 1.0. The…, to_barycentric(), Weights survive a there-and-back trip without drifting., Ten trips land where one trip landed — no accumulating drift., Two-way ties sit halfway along an edge, with the third corner at zero., TestGoldenEdgeMidpoints, TestRoundTrip

### Community 115 - "parametrize"
Cohesion: 0.28
Nodes (5): parametrize, Each corner weight of 1.0 lands exactly on that corner., Fixed off-centre answers — the ones a real respondent actually gives., TestGoldenAsymmetricPlacements, TestGoldenCorners

### Community 116 - "quality_jsx"
Cohesion: 0.22
Nodes (9): patterns_jsx(), quality_jsx(), The panel component, with its comments stripped, for the same reason., Collapsed by default (delta §5). A ``details`` with no ``open``., Below them, not beside them — it is a check read after the answers., Constraint 11: it reports, and offers no reading of this data. The one…, test_the_panel_is_closed_until_it_is_asked_for(), test_the_panel_sits_below_the_supporting_charts() (+1 more)

### Community 117 - "test_widget_backend_parity.py"
Cohesion: 0.31
Nodes (8): The widget's triad maths must agree with the server's, exactly.…, The same weights must land on the same point in both languages., The same point must read back as the same weights in both languages., PRD §3: triad barycentric sums to 1.0 — in the widget too., _run_node(), test_javascript_and_python_agree_on_to_barycentric(), test_javascript_and_python_agree_on_to_cartesian(), test_javascript_normalise_sums_to_one()

### Community 118 - "to_cartesian"
Cohesion: 0.39
Nodes (3): Convert three corner weights into a point inside the triangle. >>>…, to_cartesian(), TestRejections

### Community 119 - "db.py"
Cohesion: 0.29
Nodes (6): Database engine and session plumbing (constraint 4: SQLite + local files)., lan_host(), public_base_url(), Runtime settings. Constraint 7 (non-technical operator) forbids config editing,…, The address other devices on the mesh can reach this machine at. A QR pointing…, Base URL a capture link should carry.

### Community 120 - "quality_css"
Cohesion: 0.25
Nodes (8): quality_css(), Just the panel's own declarations, with the prose taken out. Comments are…, Constraint 13c, and the reason this panel can be read in greyscale. Every…, Quiet weight (13a). The landscape is the one bold element on this tab. Nothing…, Constraint 10: a phone at 375px must not be pushed sideways by a table., test_the_panel_encodes_nothing_in_colour(), test_the_panel_never_shouts(), test_the_wide_table_scrolls_inside_itself()

### Community 121 - "SignifiedByCounts"
Cohesion: 0.33
Nodes (5): How many placements each provenance holds, before the filter is applied.…, SignifiedByCounts, LandscapeSet, BaseModel, One triad's landscape, or several panels of it side by side.

### Community 122 - "distance_from_centre"
Cohesion: 0.40
Nodes (5): distance_from_centre(), How far a placement sits from the middle of the triangle. Plain Euclidean…, The centroid and "no lean at all" have to be the same point. To the precision…, test_a_corner_is_not_near_the_centre(), test_the_centre_is_where_equal_weights_land()

### Community 123 - "TriadChart"
Cohesion: 0.50
Nodes (5): Placements inside one triangle, as points on the unit triangle., The same chart as :func:`one_triad`, from rows rather than from objects.…, _triad_chart(), triad_from_answers(), TriadChart

### Community 124 - "patterns_fixtures.py"
Cohesion: 0.50
Nodes (4): The twenty-story fixture behind the pattern golden (PRD §6, Phase 7). Twenty…, One story, entirely determined by its position in the run., story_payload(), _tenths()

### Community 126 - "test_five_thousand_stories_cost_less_than_the_charts_beside_them"
Cohesion: 0.67
Nodes (3): Session, Measured against the patterns endpoint in the same run, not in milliseconds.…, test_five_thousand_stories_cost_less_than_the_charts_beside_them()

## Knowledge Gaps
- **194 isolated node(s):** `name`, `version`, `description`, `dev`, `build` (+189 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Anecdote` connect `Anecdote` to `TestClient`, `TestClient`, `Framework`, `TestClient`, `test_import_pipeline.py`, `TestClient`, `test_public_identifier_absence.py`, `imports.py`, `validate_definition`, `build_golden_dataset`, `NormalisedDocument`, `CaptureLink`, `test_schema_absence.py`, `test_queue.py`, `models.py`, `routers/patterns.py`, `test_quality_signals.py`, `CaptureError`, `ingest_fixtures.py`, `test_five_thousand_stories_cost_less_than_the_charts_beside_them`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `FrameworkDefinition` connect `FrameworkDefinition` to `Framework`, `imports.py`, `validate_definition`, `NormalisedDocument`, `backend/patterns.py`, `routers/landscape.py`, `clusters.py`, `framework_schema.py`, `aggregate`, `Anecdote`, `backend/exports.py`, `test_placement_shape_parity.py`, `propose.py`, `models.py`, `paper_pack.py`, `routers/patterns.py`, `.estimated_minutes`, `routers/quality.py`, `CaptureError`, `public.py`, `SignifiedByCounts`, `TriadChart`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `make_framework()` connect `make_framework` to `test_quality_signals.py`, `test_patterns.py`, `test_exports.py`, `test_queue.py`, `build_golden_dataset`, `test_story_browser.py`, `test_signification_provenance.py`, `test_live_ai.py`, `test_explorer_clusters.py`, `test_five_thousand_stories_cost_less_than_the_charts_beside_them`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 56 inferred relationships involving `FrameworkDefinition` (e.g. with `CaptureError` and `CaptureSubmission`) actually correct?**
  _`FrameworkDefinition` has 56 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `Anecdote` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Anecdote` has 56 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Signification` (e.g. with `CaptureResult` and `FrameworkCreate`) actually correct?**
  _`Signification` has 40 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _194 weakly-connected nodes found - possible documentation gaps or missing edges._