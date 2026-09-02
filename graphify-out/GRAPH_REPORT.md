# Graph Report - TESSA-Sensemaking  (2026-09-02)

## Corpus Check
- 156 files · ~160,983 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2706 nodes · 6459 edges · 128 communities (117 shown, 11 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 473 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ec1bb9ac`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- from_value_json
- TestClient
- TestClient
- edit_semantics.py
- Base
- TestClient
- test_import_pipeline.py
- TestClient
- ai_client.py
- test_public_identifier_absence.py
- imports.py
- package.json
- validate_definition
- test_story_browser.py
- test_landscape.py
- parsers.py
- _run_node
- ImportJobSummary
- backend/patterns.py
- test_signification_provenance.py
- test_parsers.py
- What You Must Do When Invoked
- CaptureLink
- backend/landscape.py
- get_landscape
- TestClient
- PRD: Narrative Lens — Local Narrative Sense-Making App
- Decisions
- build_golden_dataset
- Wizard.jsx
- test_capture_draft.py
- Widgets.jsx
- test_schema_absence.py
- test_error_surface.py
- test_terrain_maths.py
- clusters.py
- test_patterns.py
- framework_schema.py
- TriadChart
- test_exports.py
- voice.js
- ImportTab.jsx
- test_design_linter.py
- Wizard
- Studio.jsx
- test_queue.py
- The session loop (every session, no exceptions)
- Data Visualization Reference — 2026
- FrameworkDefinition
- parse
- graphify reference: extra exports and benchmark
- Web Design & Data Visualization
- Anecdote
- backend/exports.py
- get_session
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
- ValidationQueue.jsx
- propose.py
- browse_stories
- Patterns.jsx
- Mcq
- test_empty_states.py
- patterns_fixtures.py
- proposed_import
- Framework
- lint.py
- test_stage_gate.py
- routers/patterns.py
- test_original_names.py
- NormalisedDocument
- lint_framework
- make_framework
- test_quality_signals.py
- .estimated_minutes
- BarycentricError
- test_patterns_golden.py
- models.py
- test_api_alignment.py
- test_scope_completeness.py
- Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6
- test_whole_app.py
- TestAnonymityStatementIsTrueOfTheCode
- barycentric.py
- env.py
- normalise
- public.py
- FrameworkCreate
- default_definition
- parametrize
- quality_jsx
- to_barycentric
- to_cartesian
- xlsx_bytes
- quality_css
- SignifiedByCounts
- CategoryChart
- App.jsx
- render_paper_pack
- TestGoldenCentroid
- health
- .signifier_ids_must_be_unique

## God Nodes (most connected - your core abstractions)
1. `FrameworkDefinition` - 139 edges
2. `make_framework()` - 112 edges
3. `Anecdote` - 96 edges
4. `build_golden_dataset()` - 92 edges
5. `Signification` - 70 edges
6. `Framework` - 69 edges
7. `ImportJob` - 49 edges
8. `get_session()` - 47 edges
9. `parse()` - 41 edges
10. `NormalisedDocument` - 38 edges

## Surprising Connections (you probably didn't know these)
- `Shape` --uses--> `AiError`  [INFERRED]
  tests/test_ai_client.py → backend/ai_client.py
- `TestFromValueJson` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py
- `TestGoldenAsymmetricPlacements` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py
- `TestGoldenCentroid` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py
- `TestGoldenCorners` --uses--> `BarycentricError`  [INFERRED]
  tests/test_barycentric.py → backend/barycentric.py

## Import Cycles
- None detected.

## Communities (128 total, 11 thin omitted)

### Community 0 - "from_value_json"
Cohesion: 0.19
Nodes (9): from_value_json(), _placed(), point_from_value_json(), Read a stored ``significations.value_json`` into ordered weights., A stored answer straight to its point in the triangle. Exactly…, The conversion itself, on weights already known to be usable. Kept apart from…, Reading a stored signification back into ordered weights., Dict ordering must never decide which corner is which. (+1 more)

### Community 1 - "TestClient"
Cohesion: 0.08
Nodes (30): qr_png_bytes(), Return a PNG of ``payload`` as QR, as raw bytes. Error correction is set to M…, _framework(), _link(), TestClient, Capture links and the public capture path (PRD §6 Phase 4). The tests the PRD…, PRD §6 Phase 4: token lifecycle. §7.6: revoked links close., The heart of §7.6: a taken-down QR poster cannot keep collecting. (+22 more)

### Community 2 - "TestClient"
Cohesion: 0.10
Nodes (22): _framework(), TestClient, Local capture (PRD §6 Phase 3). The tests the PRD names for this phase: wizard…, PRD §9 assumption 7: reflection shows one signifier., Skipping every question is allowed; the story is the point., Constraint 3: provenance on every record., PRD §6 Phase 3: batch entry writes paper provenance., Constraint 9, at the moment a story is actually written. (+14 more)

### Community 3 - "edit_semantics.py"
Cohesion: 0.09
Nodes (28): build_edit_log_entries(), diff_text_fields(), is_structural_change(), Any, datetime, The wording-fix vs meaning-change guardrail (PRD §1.1, constraint 13g). While a…, One stored answer with its labels brought up to date, or unchanged. Shape-…, The shape of a framework, ignoring every word in it. Two definitions with the… (+20 more)

### Community 4 - "Base"
Cohesion: 0.08
Nodes (39): _connect_args(), make_engine(), SQLite needs ``check_same_thread=False`` to serve requests from a pool., Build an engine, enabling SQLite foreign-key enforcement. SQLite ignores…, Base, Declarative base carrying the shared naming convention., Config, DeclarativeBase (+31 more)

### Community 5 - "TestClient"
Cohesion: 0.10
Nodes (23): _create_full(), _pack_html(), TestClient, The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar). Two…, PRD §1.2a: the story card carries respondent-group tick boxes., The pack renders the version's current wording, not a cached copy., Constraint 9: the anonymity statement is printed verbatim on the card., Whatever this version says is what the card prints — no substitution. (+15 more)

### Community 6 - "test_import_pipeline.py"
Cohesion: 0.15
Nodes (45): txt_bytes(), _confirm(), _confirmation_body(), _organise(), parametrize, Session, TestClient, The staged import machine end to end, over HTTP, with zero network. Acceptance… (+37 more)

### Community 7 - "TestClient"
Cohesion: 0.11
Nodes (27): _add_story(), _create(), _definition(), Session, TestClient, The wording-fix vs meaning-change state machine (PRD §6, constraint 13g). This…, Constraint 7: the operator must be able to act on the message., A wording fix patches in place and appends to the edit log. (+19 more)

### Community 8 - "ai_client.py"
Cohesion: 0.08
Nodes (37): _fenced_json(), _live_text(), mock_enabled(), _parse(), Any, The one AI client (constraint 6). Every call Narrative Lens makes to a language…, Parse one reply strictly, or raise the reason it could not be parsed., One live call to api.anthropic.com. The only network in the app. Imported… (+29 more)

### Community 9 - "test_public_identifier_absence.py"
Cohesion: 0.08
Nodes (28): RateLimiter, Rate limiting for the public capture endpoints (PRD §4). The public endpoints…, A sliding-window counter keyed by an opaque string. Deliberately simple and in-…, Record a hit and report whether it is within the limit., Forget counters. Used by tests and when a link is revoked., How many hits are still allowed in the current window., Clear every counter. Tests call this between cases., reset_all() (+20 more)

### Community 10 - "imports.py"
Cohesion: 0.13
Nodes (39): conflict(), Something outside the app misbehaved — currently only the AI service., upstream(), ImportJob, One uploaded file moving through the two-stage ingestion machine., confirm_mapping(), create_import(), _detail() (+31 more)

### Community 11 - "package.json"
Cohesion: 0.06
Nodes (30): eslint, @eslint/js, eslint-plugin-react, eslint-plugin-react-hooks, dependencies, react, react-dom, description (+22 more)

### Community 12 - "validate_definition"
Cohesion: 0.09
Nodes (13): Parse and validate a raw ``definition_json`` payload., validate_definition(), Validation of ``definition_json`` and the anonymity statement it carries., Significations key on the id alone, so one namespace covers all kinds., A typo in the Studio should fail loudly, not vanish silently., Constraint 10: ≤4 minutes typical., PRD §1.1: warn past roughly six signifier screens., TestDyadValidation (+5 more)

### Community 13 - "test_story_browser.py"
Cohesion: 0.15
Nodes (30): _browse(), _mark(), TestClient, The story browser (PRD §1.6, §5.4). The last item of §1's scope, and the one…, Constraint 1, on the reading side. The queue is where pending lives., Constraint 3 shown, constraint 9 absent — the same as every other view., They share a table, so this is the join worth testing., It is stored as one, which is exactly why this is worth asserting. (+22 more)

### Community 14 - "test_landscape.py"
Cohesion: 0.09
Nodes (49): Every story inside a rectangle of grid cells, and no others. The region drill…, stories_in_region(), _capture(), _landscape(), _panel(), Session, TestClient, The landscape suite: the terrain, its contour twin, the drill, the clusters.… (+41 more)

### Community 15 - "parsers.py"
Cohesion: 0.11
Nodes (28): Block, _blocks_from_text(), classify(), _clean_row(), _decode(), _parse_captions(), _parse_csv(), _parse_docx() (+20 more)

### Community 16 - "_run_node"
Cohesion: 0.11
Nodes (14): parametrize, Voice fallback (PRD §6 Phase 4, §7.12, constraint 10). Constraint 10 says voice…, The UI calls stop() on unmount whether or not voice ever started., Stopping on purpose is not a failure and must not show a warning., Constraint 10: voice always paired with typing., Interim results would rewrite a respondent's words as they speak., §7.12: voice fails plain-English with a working fallback., Constraint 7: no jargon a respondent cannot act on. (+6 more)

### Community 17 - "ImportJobSummary"
Cohesion: 0.17
Nodes (28): _balance(), Candidate, confirm(), confirm_narrative(), confirm_tabular(), ConfirmedExtraction, ExtractionError, BaseModel (+20 more)

### Community 18 - "backend/patterns.py"
Cohesion: 0.19
Nodes (25): Dyad, A 2D canvas on which the respondent places named chips., A slider between two opposing poles; answers are 0–1., Stones, Bar, _dyad_chart(), DyadChart, DyadPoint (+17 more)

### Community 19 - "test_signification_provenance.py"
Cohesion: 0.12
Nodes (37): expert_validated_ids(), mixed_dataset(), patterns(), placed(), plotted(), parametrize, TestClient, Whose interpretation a figure is made of (delta §6, constraint 14). Constraint… (+29 more)

### Community 20 - "test_parsers.py"
Cohesion: 0.08
Nodes (27): docx_bytes(), pdf_bytes(), _pdf_escape(), pptx_bytes(), Real files, in memory, one per format Narrative Lens claims to read. Acceptance…, A one-page PDF with each paragraph as its own text run. Written by hand:…, vtt_bytes(), parametrize (+19 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "CaptureLink"
Cohesion: 0.06
Nodes (43): CaptureLink, A token-gated capture URL pointing at one exact framework version., A free-text tag the analyst attaches to a story., Tag, QR codes for capture links (PRD §4, §1.8). A QR is how a phone gets to the…, capture_link_qr(), capture_url(), CaptureLinkCreate (+35 more)

### Community 23 - "backend/landscape.py"
Cohesion: 0.15
Nodes (24): _axes(), Cell, _cell_index(), compute(), Landscape, LandscapePoint, _local_maxima(), _nearest_corner() (+16 more)

### Community 24 - "get_landscape"
Cohesion: 0.21
Nodes (16): get_clusters(), get_explorer(), get_landscape(), Depends, ge, get, le, Query (+8 more)

### Community 25 - "TestClient"
Cohesion: 0.14
Nodes (9): TestClient, List, create and fetch frameworks (PRD §4)., A new framework starts valid and empty, ready to fill in., The Studio shows these live while the operator edits., Constraint 7: plain English, with something to do about it., PRD §5.1: version history sidebar shows versions with story counts., TestCreate, TestFetch (+1 more)

### Community 26 - "PRD: Narrative Lens — Local Narrative Sense-Making App"
Cohesion: 0.10
Nodes (19): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 11. Changelog v1.2 → v1.3, 1. Scope, 2. Binding constraints (restate these in every session), 3. Data model (SQLite, via SQLAlchemy + Alembic), 4. API contract (FastAPI, all JSON), 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages). (+11 more)

### Community 27 - "Decisions"
Cohesion: 0.07
Nodes (29): Completeness pass, Decisions, Delta phase A, Delta phase B, Delta phase C, Fixed, Narrative Lens — Progress, Phase 1 (+21 more)

### Community 28 - "build_golden_dataset"
Cohesion: 0.16
Nodes (31): median_ms(), How long a call takes, measured as a median rather than a single sample. PRD §4…, build_golden_dataset(), TestClient, Create the framework and its twenty stories. Returns the framework., _clusters(), _explorer(), TestClient (+23 more)

### Community 29 - "Wizard.jsx"
Cohesion: 0.17
Nodes (12): ApiError, CaptureTab(), MODES, LinkManager(), PaperBatch(), buildSteps(), MAX_RESPONDENT_TITLE_CHARS, ReflectionPanel() (+4 more)

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
Cohesion: 0.20
Nodes (9): CaptureSettings, BaseModel, Validation for ``frameworks.definition_json`` (PRD §3 and §5). Every…, Every non-signifier string the respondent reads, plus capture toggles., Reject unknown keys so a typo in the Studio surfaces as an error., One axis of the stones canvas, named at both ends., StonesAxis, _Strict (+1 more)

### Community 38 - "TriadChart"
Cohesion: 0.24
Nodes (13): aggregate(), one_triad(), placements_by_signifier(), AnswerRow, StoryRow, Placements inside one triangle, as points on the unit triangle., Placements grouped by the question they answer, for the stories given., Just one triangle's points, without computing every other chart. The landscape… (+5 more)

### Community 39 - "test_exports.py"
Cohesion: 0.09
Nodes (49): _brief(), _csv(), _heard(), TestClient, The CSV and the Pattern Brief. The CSV is tested as a file a person will open…, The case the provenance column exists for., Constraint 13f, the whole point of the brief., A brief that did not say what it excluded would be misleading. (+41 more)

### Community 40 - "voice.js"
Cohesion: 0.28
Nodes (11): appendDictation(), getRecognitionClass(), isVoiceSupported(), startDictation(), VOICE_DENIED, VOICE_FAILED, VOICE_NETWORK, VOICE_NO_SPEECH (+3 more)

### Community 41 - "ImportTab.jsx"
Cohesion: 0.18
Nodes (4): ImportTab(), MarkUpStep(), storyCount(), MappingScreen()

### Community 42 - "test_design_linter.py"
Cohesion: 0.06
Nodes (58): check(), lint_css(), panel_source(), MonkeyPatch, Session, TestClient, The framework design linter (delta §6, phase C). This is the one AI call in…, The shape is enforced on the mock exactly as on a live reply. ``request_json``… (+50 more)

### Community 43 - "Wizard"
Cohesion: 0.40
Nodes (8): clearDraft(), draftHasContent(), draftKey(), loadDraft(), safeStorage(), saveDraft(), browserStorage(), Wizard()

### Community 44 - "Studio.jsx"
Cohesion: 0.13
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
Cohesion: 0.10
Nodes (38): FrameworkDefinition, The whole respondent-facing definition of one framework version., How many signifier screens the respondent will see., PRD §1.1: warn past roughly six signifier screens., chunks(), propose(), Split the stories into calls of at most ``size`` (PRD §4a)., Run Stage B over a file's stories and return checked proposals. Nothing is… (+30 more)

### Community 49 - "parse"
Cohesion: 0.16
Nodes (24): parse(), Read one uploaded file into the normalised shape, or refuse it. Refusals are…, csv_bytes(), Any, MonkeyPatch, TestClient, Stage A: what it proposes, and what it is not allowed to get away with. Stage A…, Constraint 4 and 7: offline is a normal state, not a broken one. The file stays… (+16 more)

### Community 50 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 51 - "Web Design & Data Visualization"
Cohesion: 0.22
Nodes (8): Data visualization, Output, Step 1: Frame the brief, Step 2: Design plan before code, Step 3: B2B or B2C playbook, Step 4: Build to the quality floor (non-negotiable, never announced), Step 5: Critique pass, Web Design & Data Visualization

### Community 52 - "Anecdote"
Cohesion: 0.11
Nodes (34): Anecdote, One story, bound to the exact framework version it was told against.…, One respondent (or validated AI) placement on one signifier. ``value_json``…, Signification, counts(), decide(), _finish_job_if_empty(), _low() (+26 more)

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

### Community 57 - "AiError"
Cohesion: 0.08
Nodes (42): AiError, Exception, An AI call that failed in a way the operator needs told about. Carries the PRD…, ModuleType, APIConnectionError, APIStatusError, _Block, _calls() (+34 more)

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
Cohesion: 0.20
Nodes (9): How to resume, Narrative Lens — Latest, Next step, Running it yourself, The completeness pass, after Phase 9, The meaningfulness delta — phase A is done, The meaningfulness delta — phase B is done, The meaningfulness delta — phase C is done (+1 more)

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

### Community 83 - "propose.py"
Cohesion: 0.10
Nodes (31): CaptureError, BaseModel, ValueError, A submitted capture that cannot be stored as given., One placement as it arrives from the wizard or paper batch entry., SubmittedSignification, _check_batch(), describe_signifiers() (+23 more)

### Community 84 - "browse_stories"
Cohesion: 0.07
Nodes (39): bad_request(), browse_stories(), MarksIn, BaseModel, Depends, ge, get, put (+31 more)

### Community 85 - "Patterns.jsx"
Cohesion: 0.06
Nodes (39): BarChart(), DyadChart(), StonesChart(), CLUSTER_TOKENS, ExplorerView(), Scatter(), VIEW, ContourTwin() (+31 more)

### Community 86 - "Mcq"
Cohesion: 0.13
Nodes (17): Mcq, A multiple-choice question., Every signifier with its kind, in the order the respondent meets them., A triangle with three named corners; answers are barycentric., Triad, _mcq_options(), The printable paper pack (PRD §1.2, §5b print grammar). One HTML page the…, A square canvas with both axes named at each end. (+9 more)

### Community 87 - "test_empty_states.py"
Cohesion: 0.21
Nodes (13): _copy(), parametrize, Path, Every screen tells the operator what to do next (PRD §6, Phase 9). A fresh…, The Studio is the tab the app opens on, so it carries the first word., One name for the thing, in every place the operator can read it. The code calls…, The text of every empty-state paragraph in one screen, tags stripped., No data" is a fact about the database, not help for the person reading. (+5 more)

### Community 88 - "patterns_fixtures.py"
Cohesion: 0.15
Nodes (17): The twenty-story fixture behind the pattern golden (PRD §6, Phase 7). Twenty…, One story, entirely determined by its position in the run., story_payload(), _tenths(), peaks_of(), produce_peaks(), TestClient, The landscape golden — peaks stable to ±0.02 (PRD §6, Phase 8). The second of… (+9 more)

### Community 89 - "proposed_import"
Cohesion: 0.13
Nodes (30): confirmed_import(), proposed_import(), TestClient, Shared helpers for the Stage B and validation-queue suites. One framework…, Drive a file as far as ``mapping_confirmed``, accepting Stage A as-is., Drive a file all the way to ``proposed`` — stories in the queue., _backend_modules(), Path (+22 more)

### Community 90 - "Framework"
Cohesion: 0.19
Nodes (25): label_renames(), ``{signifier_id: {old_label: new_label}}`` for every renamed label. Only labels…, Framework, A version of the question set respondents see. ``parent_framework_id`` links…, _anecdote_count(), _apply_meaning_change(), _apply_wording_fix(), create_framework() (+17 more)

### Community 91 - "lint.py"
Cohesion: 0.19
Nodes (11): lint(), lint_prompt(), LintReport, _mock_reply(), Any, BaseModel, The framework design linter (delta §4a, item 3). The one AI call in this app…, Everything the model had to say about one question set's design. (+3 more)

### Community 92 - "test_stage_gate.py"
Cohesion: 0.11
Nodes (20): can_advance(), Whether the machine permits ``current → target``., Whether ``target`` can be reached from ``start`` by any number of steps. Used…, reachable(), _job(), parametrize, The stage machine and its 409 gate (constraints 1 and 12). Two levels are…, Constraint 7: a refusal the operator can act on, with no jargon in it. (+12 more)

### Community 93 - "routers/patterns.py"
Cohesion: 0.07
Nodes (55): only_validated(), Narrow a query to the stories a person has actually approved. Every read that…, Database engine and session plumbing (constraint 4: SQLite + local files)., The error shape from PRD §4. ``{"error": {"code": ..., "message": plain-English…, mount_frontend(), FastAPI application. Endpoints arrive with the phase that needs them, per PRD…, Serve ``frontend/dist`` if it has been built. Returns whether anything was…, Export endpoints (PRD §4, §1.7). Both exports read through the same scope as… (+47 more)

### Community 94 - "test_original_names.py"
Cohesion: 0.25
Nodes (7): _files(), parametrize, Path, Original names and materials only (constraint 8, acceptance criterion 15). The…, Criterion 15 allows one attribution. One, not none — it is owed. Counted in…, test_no_reserved_name_appears_in_the_app(), test_the_readme_carries_exactly_one_attribution()

### Community 95 - "NormalisedDocument"
Cohesion: 0.09
Nodes (41): _check_narrative(), _check_tabular(), _hinted_column(), _mock_narrative(), _mock_tabular(), _narrative_prompt(), NarrativeOrganisation, organise() (+33 more)

### Community 96 - "lint_framework"
Cohesion: 0.22
Nodes (10): get_paper_pack(), lint_framework(), list_frameworks(), Depends, get, post, Every framework, newest first. The Studio groups these into lineages., The print-ready paper pack for this exact framework version (PRD §1.2). Returns… (+2 more)

### Community 97 - "make_framework"
Cohesion: 0.14
Nodes (33): make_framework(), capture(), link_for(), parametrize, TestClient, The name a storyteller gives their own story (delta §6, items 2 and 5). A…, No name given is the ordinary case, and it must read as a story anyway., A skipped field submits as blank; blank is no name, not a name of "". Otherwise… (+25 more)

### Community 98 - "test_quality_signals.py"
Cohesion: 0.10
Nodes (47): capture(), MonkeyPatch, Session, TestClient, quality(), Data-quality signals: centre-parking and skip rate (delta §6, phase B). The…, Ten stories, all parked. The proportion must be exactly 1.0., Three parked out of four is 0.75, and nothing about the code decides that. (+39 more)

### Community 100 - "BarycentricError"
Cohesion: 0.18
Nodes (15): BarycentricError, ValueError, Raised when a placement cannot be read as a triad answer., centre_parked_count(), BaseModel, QualityReport, _rate(), Data-quality signals: centre-parking and skip rate (delta §1 item 4, §5). Two… (+7 more)

### Community 101 - "test_patterns_golden.py"
Cohesion: 0.12
Nodes (21): produce(), TestClient, The pattern golden — byte-identical from Phase 7 onward (PRD §6). Twenty…, Determinism, checked against itself rather than against the file. If…, A golden that missed a kind would pin three quarters of the maths., Twenty stories, every one of them answered on every question., The new default, pinned the same way the old view has always been., The delta changed which placements are counted, not how they are counted. On… (+13 more)

### Community 102 - "models.py"
Cohesion: 0.08
Nodes (38): CaptureSubmission, _check_dyad(), _check_mcq(), _check_stones(), LocalCaptureSubmission, Validating a submitted capture against the framework it answers (PRD §4). A…, Dyad value: a single number from 0 to 1., Stones value: a placement per chip, each inside the square. (+30 more)

### Community 103 - "test_api_alignment.py"
Cohesion: 0.31
Nodes (9): _frontend_paths(), The frontend and the backend agree about what exists (contract alignment).…, Every ``/api/...`` address api.js can build, with its parameters blanked., An endpoint nothing calls is either dead or half-finished., A guard on the guard: an empty comparison would pass both tests above., _server_paths(), test_every_address_the_frontend_calls_exists_on_the_server(), test_every_endpoint_is_reached_by_something() (+1 more)

### Community 104 - "test_scope_completeness.py"
Cohesion: 0.16
Nodes (13): TestClient, Every item of PRD §1's scope is actually reachable in the app. This file exists…, One assertion per numbered item of §1 that the API is responsible for., §5.4: "Landscape (default) · Supporting charts · 3D Explorer · Story browser"., The four verbs §1.6 lists, each with something in the code doing it., Dataset CSV · contour PNG · supporting-charts PNG · brief · what we heard., Acceptance criterion 1 ends "QR on home", and the home screen is the Studio., _source() (+5 more)

### Community 105 - "Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6"
Cohesion: 0.11
Nodes (17): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 1. Scope, 2. Binding constraints restated, 3. Data model changes, 4. API contract, 4a. New AI calls — both through `ai_client.request_json`, both mocked, 5. Frontend changes (+9 more)

### Community 106 - "test_whole_app.py"
Cohesion: 0.28
Nodes (8): Session, TestClient, One run through the whole app, in the order an operator would use it. Every…, The guardrail, followed all the way to the landscape and the exports., Day one: a question set, no stories, and nothing that throws., test_a_meaning_change_keeps_the_two_versions_apart_everywhere(), test_an_empty_app_answers_every_endpoint_without_falling_over(), test_the_whole_app_agrees_with_itself()

### Community 107 - "TestAnonymityStatementIsTrueOfTheCode"
Cohesion: 0.27
Nodes (3): Constraint 9: the statement must be literally true of the schema. Each clause…, Story, placements, and chosen group — and that is the whole list., TestAnonymityStatementIsTrueOfTheCode

### Community 108 - "barycentric.py"
Cohesion: 0.27
Nodes (8): is_inside(), Triad barycentric maths. A triad answer is a point inside an equilateral…, Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`., Whether the weights describe a point in or on the triangle., Reject anything that is not a usable triad answer., sums_to_one(), _validated(), Golden maths for triad placements. These values are the contract between the…

### Community 109 - "env.py"
Cohesion: 0.17
Nodes (14): Alembic environment. The database URL comes from…, Emit SQL to a script without a live connection., Run migrations against a live connection., _run(), run_migrations_offline(), run_migrations_online(), _url(), database_url() (+6 more)

### Community 110 - "normalise"
Cohesion: 0.20
Nodes (8): normalise(), Clamp to the triangle and rescale so the three weights sum to exactly 1.0. A…, _check_triad(), Triad weights: one per corner, non-negative, summing to 1.0., PRD §3: triad barycentric sums to 1.0., Even awkward thirds land on a sum of exactly 1.0 after rounding., An imported point a hair outside the triangle is pulled to its edge., TestSumsToOne

### Community 112 - "public.py"
Cohesion: 0.13
Nodes (23): PublicCaptureSubmission, A capture arriving through a capture link. ``framework_id`` is not accepted:…, AppError, not_found(), An error the operator is meant to read and act on., create_public_capture(), _framework_or_refuse(), get_public_framework() (+15 more)

### Community 113 - "FrameworkCreate"
Cohesion: 0.28
Nodes (9): LintFinding, One thing worth a second look, and what to try instead., FrameworkCreate, FrameworkUpdate, LintOut, BaseModel, A design critique of one framework version, and nothing about its data., Body for creating a framework. Version 1 of a fresh lineage. (+1 more)

### Community 114 - "default_definition"
Cohesion: 0.32
Nodes (5): default_definition(), A minimal, valid definition — what a brand-new framework starts from., The operator starts from something valid and fills it in., Constraint 10: reflection on by default; voice paired with typing., TestDefaults

### Community 115 - "parametrize"
Cohesion: 0.20
Nodes (7): parametrize, Each corner weight of 1.0 lands exactly on that corner., Two-way ties sit halfway along an edge, with the third corner at zero., Fixed off-centre answers — the ones a real respondent actually gives., TestGoldenAsymmetricPlacements, TestGoldenCorners, TestGoldenEdgeMidpoints

### Community 116 - "quality_jsx"
Cohesion: 0.22
Nodes (9): patterns_jsx(), quality_jsx(), The panel component, with its comments stripped, for the same reason., Collapsed by default (delta §5). A ``details`` with no ``open``., Below them, not beside them — it is a check read after the answers., Constraint 11: it reports, and offers no reading of this data. The one…, test_the_panel_is_closed_until_it_is_asked_for(), test_the_panel_sits_below_the_supporting_charts() (+1 more)

### Community 117 - "to_barycentric"
Cohesion: 0.17
Nodes (13): Convert a point in the triangle into three corner weights summing to 1.0. The…, to_barycentric(), Weights survive a there-and-back trip without drifting., Ten trips land where one trip landed — no accumulating drift., TestRoundTrip, The widget's triad maths must agree with the server's, exactly.…, The same weights must land on the same point in both languages., The same point must read back as the same weights in both languages. (+5 more)

### Community 118 - "to_cartesian"
Cohesion: 0.22
Nodes (8): distance_from_centre(), How far a placement sits from the middle of the triangle. Plain Euclidean…, Convert three corner weights into a point inside the triangle. >>>…, to_cartesian(), TestRejections, The centroid and "no lean at all" have to be the same point. To the precision…, test_a_corner_is_not_near_the_centre(), test_the_centre_is_where_equal_weights_land()

### Community 119 - "xlsx_bytes"
Cohesion: 0.25
Nodes (8): A two-sheet workbook: one of responses, one lookup table to ignore. The…, xlsx_bytes(), PRD §4: AI endpoints are exempt; reading a job's status is not., test_confirming_a_mapping_before_organising_is_refused(), test_job_status_is_inside_the_200ms_budget(), Assumption 10: a mixed-role workbook is mapped sheet by sheet., test_workbook_keeps_every_sheet_separately(), test_workbook_rows_are_numbered_as_the_spreadsheet_numbers_them()

### Community 120 - "quality_css"
Cohesion: 0.25
Nodes (8): quality_css(), Just the panel's own declarations, with the prose taken out. Comments are…, Constraint 13c, and the reason this panel can be read in greyscale. Every…, Quiet weight (13a). The landscape is the one bold element on this tab. Nothing…, Constraint 10: a phone at 375px must not be pushed sideways by a table., test_the_panel_encodes_nothing_in_colour(), test_the_panel_never_shouts(), test_the_wide_table_scrolls_inside_itself()

### Community 121 - "SignifiedByCounts"
Cohesion: 0.33
Nodes (5): How many placements each provenance holds, before the filter is applied.…, SignifiedByCounts, LandscapeSet, BaseModel, One triad's landscape, or several panels of it side by side.

### Community 122 - "CategoryChart"
Cohesion: 0.43
Nodes (7): _bars(), CategoryChart, _demographics(), _mcq_chart(), A categorical breakdown: horizontal bars sorted by value (§5b)., Bars in drawn order: biggest first, ties broken alphabetically. §5b requires…, Counter

### Community 123 - "App.jsx"
Cohesion: 0.48
Nodes (4): App(), TABS, captureTokenFromPath(), PublicCapture()

### Community 124 - "render_paper_pack"
Cohesion: 0.33
Nodes (6): _facilitator_sheet(), The A4 story card: prompt, ruled space, groups, anonymity line., Running instructions, materials, and the reconciliation grid., Render the whole pack as one self-contained, printable HTML page., render_paper_pack(), _story_card()

### Community 126 - "health"
Cohesion: 0.67
Nodes (3): health(), get, Liveness probe. The launcher opens this while the app is starting.

## Knowledge Gaps
- **196 isolated node(s):** `name`, `version`, `description`, `dev`, `build` (+191 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Anecdote` connect `Anecdote` to `TestClient`, `TestClient`, `Base`, `TestClient`, `test_import_pipeline.py`, `TestClient`, `test_public_identifier_absence.py`, `imports.py`, `test_landscape.py`, `ImportJobSummary`, `CaptureLink`, `test_schema_absence.py`, `test_queue.py`, `browse_stories`, `proposed_import`, `Framework`, `routers/patterns.py`, `NormalisedDocument`, `test_quality_signals.py`, `models.py`, `test_whole_app.py`, `FrameworkCreate`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `FrameworkDefinition` connect `FrameworkDefinition` to `edit_semantics.py`, `imports.py`, `validate_definition`, `ImportJobSummary`, `backend/patterns.py`, `get_landscape`, `clusters.py`, `framework_schema.py`, `TriadChart`, `test_design_linter.py`, `Anecdote`, `backend/exports.py`, `test_placement_shape_parity.py`, `propose.py`, `Mcq`, `Framework`, `lint.py`, `routers/patterns.py`, `NormalisedDocument`, `.estimated_minutes`, `BarycentricError`, `models.py`, `TestAnonymityStatementIsTrueOfTheCode`, `public.py`, `FrameworkCreate`, `default_definition`, `SignifiedByCounts`, `CategoryChart`, `render_paper_pack`, `.signifier_ids_must_be_unique`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `make_framework()` connect `make_framework` to `test_quality_signals.py`, `test_patterns.py`, `test_exports.py`, `test_design_linter.py`, `test_queue.py`, `test_landscape.py`, `test_story_browser.py`, `test_signification_provenance.py`, `proposed_import`, `build_golden_dataset`, `AiError`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 59 inferred relationships involving `FrameworkDefinition` (e.g. with `CaptureError` and `CaptureSubmission`) actually correct?**
  _`FrameworkDefinition` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 57 inferred relationships involving `Anecdote` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Anecdote` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `Signification` (e.g. with `CaptureResult` and `FrameworkCreate`) actually correct?**
  _`Signification` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _196 weakly-connected nodes found - possible documentation gaps or missing edges._