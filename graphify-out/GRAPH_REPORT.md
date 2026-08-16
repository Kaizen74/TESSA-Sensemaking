# Graph Report - TESSA-Sensemaking  (2026-08-16)

## Corpus Check
- 133 files · ~115,818 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2133 nodes · 5222 edges · 97 communities (87 shown, 10 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 460 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d023d74a`
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
- ImportJob
- package.json
- validate_definition
- organise
- build_golden_dataset
- parsers.py
- _run_node
- imports.py
- backend/patterns.py
- CaptureLink
- parse
- What You Must Do When Invoked
- _framework
- TriadChart
- capture.py
- TestClient
- PRD: Narrative Lens — Local Narrative Sense-Making App
- Decisions
- test_explorer_clusters.py
- App.jsx
- test_capture_draft.py
- Widgets.jsx
- test_schema_absence.py
- render_paper_pack
- test_terrain_maths.py
- Anecdote
- test_patterns.py
- StonesAxis
- test_capture_links.py
- test_exports.py
- voice.js
- ImportTab.jsx
- models.py
- Wizard.jsx
- Studio.jsx
- test_queue.py
- The session loop (every session, no exceptions)
- Data Visualization Reference — 2026
- FrameworkDefinition
- make_framework
- graphify reference: extra exports and benchmark
- Web Design & Data Visualization
- queue.py
- backend/exports.py
- regenerate_golden.py
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
- README.md
- tests/__init__.py
- narrative-lens
- test_placement_shape_parity.py
- edit_semantics.py
- ValidationQueue.jsx
- propose.py
- routers/landscape.py
- Patterns.jsx
- _story
- conftest.py
- test_landscape_golden.py
- TestTokenDecidesEverything
- TestLinkProvenance
- _backend_modules
- env.py
- RateLimiter
- patterns_fixtures.py
- field_validator
- db.py

## God Nodes (most connected - your core abstractions)
1. `FrameworkDefinition` - 123 edges
2. `Anecdote` - 111 edges
3. `Signification` - 77 edges
4. `build_golden_dataset()` - 71 edges
5. `Framework` - 60 edges
6. `make_framework()` - 50 edges
7. `ImportJob` - 49 edges
8. `parse()` - 41 edges
9. `get_session()` - 40 edges
10. `NormalisedDocument` - 38 edges

## Surprising Connections (you probably didn't know these)
- `Shape` --uses--> `AiError`  [INFERRED]
  tests/test_ai_client.py → backend/ai_client.py
- `TestAnonymityStatementIsTrueOfTheCode` --uses--> `FrameworkDefinition`  [INFERRED]
  tests/test_framework_schema.py → backend/framework_schema.py
- `TestDefaults` --uses--> `FrameworkDefinition`  [INFERRED]
  tests/test_framework_schema.py → backend/framework_schema.py
- `TestDyadValidation` --uses--> `FrameworkDefinition`  [INFERRED]
  tests/test_framework_schema.py → backend/framework_schema.py
- `TestIdRules` --uses--> `FrameworkDefinition`  [INFERRED]
  tests/test_framework_schema.py → backend/framework_schema.py

## Import Cycles
- None detected.

## Communities (97 total, 10 thin omitted)

### Community 0 - "BarycentricError"
Cohesion: 0.05
Nodes (47): BarycentricError, from_value_json(), is_inside(), normalise(), ValueError, Triad barycentric maths. A triad answer is a point inside an equilateral…, Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`., Whether the weights describe a point in or on the triangle. (+39 more)

### Community 1 - "TestClient"
Cohesion: 0.16
Nodes (10): _framework(), _link(), TestClient, PRD §6 Phase 4: token lifecycle. §7.6: revoked links close., The heart of §7.6: a taken-down QR poster cannot keep collecting., Hiding the link would hide where its stories came from., A respondent's browser is told the questions and nothing more., A QR pointing at 127.0.0.1 works on the laptop and fails on a phone. (+2 more)

### Community 2 - "TestClient"
Cohesion: 0.09
Nodes (24): _framework(), TestClient, Local capture (PRD §6 Phase 3). The tests the PRD names for this phase: wizard…, PRD §9 assumption 7: reflection shows one signifier., Skipping every question is allowed; the story is the point., Constraint 3: provenance on every record., PRD §6 Phase 3: batch entry writes paper provenance., Constraint 9, at the moment a story is actually written. (+16 more)

### Community 3 - "Framework"
Cohesion: 0.12
Nodes (41): get_session(), Session, FastAPI dependency yielding a session that always closes., is_structural_change(), Whether the edit changes the framework's shape rather than its words., Framework, A version of the question set respondents see. ``parent_framework_id`` links…, _anecdote_count() (+33 more)

### Community 4 - "make_engine"
Cohesion: 0.18
Nodes (18): make_engine(), Build an engine, enabling SQLite foreign-key enforcement. SQLite ignores…, Config, Engine, alembic_config(), fixture, Alembic migration 001 — up, down, and agreement with the models. Constraint 5…, The two columns v1.3 added to frameworks reach the database. (+10 more)

### Community 5 - "TestClient"
Cohesion: 0.10
Nodes (23): _create_full(), _pack_html(), TestClient, The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar). Two…, PRD §1.2a: the story card carries respondent-group tick boxes., The pack renders the version's current wording, not a cached copy., Constraint 9: the anonymity statement is printed verbatim on the card., Whatever this version says is what the card prints — no substitution. (+15 more)

### Community 6 - "test_import_pipeline.py"
Cohesion: 0.08
Nodes (65): csv_bytes(), pdf_bytes(), _pdf_escape(), Real files, in memory, one per format Narrative Lens claims to read. Acceptance…, A one-page PDF with each paragraph as its own text run. Written by hand:…, A two-sheet workbook: one of responses, one lookup table to ignore. The…, txt_bytes(), vtt_bytes() (+57 more)

### Community 7 - "_create"
Cohesion: 0.14
Nodes (23): _add_story(), _create(), _definition(), Session, TestClient, The wording-fix vs meaning-change state machine (PRD §6, constraint 13g). This…, Constraint 7: the operator must be able to act on the message., A wording fix patches in place and appends to the edit log. (+15 more)

### Community 8 - "request_json"
Cohesion: 0.08
Nodes (34): _fenced_json(), mock_enabled(), _parse(), Any, Parse one reply strictly, or raise the reason it could not be parsed., Ask for one JSON object of the given shape, or fail in plain English. In mock…, Whether this process runs with mocks instead of the network. Read on every call…, Return *raw* with one surrounding markdown fence removed, if present. Strict… (+26 more)

### Community 9 - "test_public_identifier_absence.py"
Cohesion: 0.17
Nodes (15): _framework(), _link(), TestClient, Constraint 9 on the remote path (PRD §6 Phase 4: identifier-absence test).…, Sweep every column of every table, not just the ones we expect., Structural guards: not "it doesn't today", but "it has no way to"., Taking a ``Request`` would put every header within arm's reach., A grep-level guard against a future edit reaching for client data. (+7 more)

### Community 10 - "ImportJob"
Cohesion: 0.07
Nodes (55): conflict(), ImportJob, One uploaded file moving through the two-stage ingestion machine., confirm_mapping(), create_import(), _detail(), get_import(), list_imports() (+47 more)

### Community 11 - "package.json"
Cohesion: 0.06
Nodes (30): eslint, @eslint/js, eslint-plugin-react, eslint-plugin-react-hooks, dependencies, react, react-dom, description (+22 more)

### Community 12 - "validate_definition"
Cohesion: 0.06
Nodes (24): default_definition(), Parse and validate a raw ``definition_json`` payload., A minimal, valid definition — what a brand-new framework starts from., validate_definition(), Base, Declarative base carrying the shared naming convention., DeclarativeBase, Validation of ``definition_json`` and the anonymity statement it carries. (+16 more)

### Community 13 - "organise"
Cohesion: 0.09
Nodes (41): _check_narrative(), _check_tabular(), _hinted_column(), _mock_narrative(), _mock_tabular(), _narrative_prompt(), NarrativeOrganisation, organise() (+33 more)

### Community 14 - "build_golden_dataset"
Cohesion: 0.10
Nodes (49): Every story inside a rectangle of grid cells, and no others. The region drill…, stories_in_region(), build_golden_dataset(), TestClient, Create the framework and its twenty stories. Returns the framework., _capture(), _landscape(), _panel() (+41 more)

### Community 15 - "parsers.py"
Cohesion: 0.11
Nodes (31): Block, _blocks_from_text(), classify(), _clean_row(), _decode(), _parse_captions(), _parse_csv(), _parse_docx() (+23 more)

### Community 16 - "_run_node"
Cohesion: 0.11
Nodes (14): parametrize, Voice fallback (PRD §6 Phase 4, §7.12, constraint 10). Constraint 10 says voice…, The UI calls stop() on unmount whether or not voice ever started., Stopping on purpose is not a failure and must not show a warning., Constraint 10: voice always paired with typing., Interim results would rewrite a respondent's words as they speak., §7.12: voice fails plain-English with a working fallback., Constraint 7: no jargon a respondent cannot act on. (+6 more)

### Community 17 - "imports.py"
Cohesion: 0.12
Nodes (50): _balance(), Candidate, confirm(), confirm_narrative(), confirm_tabular(), ConfirmedExtraction, ExtractionError, BaseModel (+42 more)

### Community 18 - "backend/patterns.py"
Cohesion: 0.09
Nodes (57): CaptureSettings, Dyad, Mcq, BaseModel, Validation for ``frameworks.definition_json`` (PRD §3 and §5). Every…, A 2D canvas on which the respondent places named chips., A multiple-choice question., Every non-signifier string the respondent reads, plus capture toggles. (+49 more)

### Community 19 - "CaptureLink"
Cohesion: 0.18
Nodes (24): CaptureLink, A token-gated capture URL pointing at one exact framework version., capture_link_qr(), capture_url(), CaptureLinkCreate, CaptureLinkOut, create_capture_link(), _get_or_404() (+16 more)

### Community 20 - "parse"
Cohesion: 0.11
Nodes (27): parse(), Read one uploaded file into the normalised shape, or refuse it. Refusals are…, docx_bytes(), pptx_bytes(), parametrize, Every format PRD §1.3 promises, read from a real file of that format., PRD §1.3 lists nine extensions. All nine are readable, nothing else is., The reverse map the API uses for jobs whose extension is long gone. (+19 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "_framework"
Cohesion: 0.10
Nodes (18): A free-text tag the analyst attaches to a story., Tag, _anecdote(), _framework(), parametrize, CRUD across the six tables of PRD §3, plus the vocabularies they enforce., Constraint 3: provenance on every record., PRD §3: input_method is typed | voice | paper | imported. (+10 more)

### Community 23 - "TriadChart"
Cohesion: 0.13
Nodes (29): _axes(), Cell, _cell_index(), compute(), Landscape, LandscapePoint, _local_maxima(), _nearest_corner() (+21 more)

### Community 24 - "capture.py"
Cohesion: 0.06
Nodes (52): CaptureSubmission, LocalCaptureSubmission, PublicCaptureSubmission, BaseModel, A whole capture: one story plus its placements. Note what is *not* here: no id,…, A capture from the operator's own machine: admin, paper entry, or kiosk. Only…, A capture arriving through a capture link. ``framework_id`` is not accepted:…, AppError (+44 more)

### Community 25 - "TestClient"
Cohesion: 0.14
Nodes (9): TestClient, List, create and fetch frameworks (PRD §4)., A new framework starts valid and empty, ready to fill in., The Studio shows these live while the operator edits., Constraint 7: plain English, with something to do about it., PRD §5.1: version history sidebar shows versions with story counts., TestCreate, TestFetch (+1 more)

### Community 26 - "PRD: Narrative Lens — Local Narrative Sense-Making App"
Cohesion: 0.10
Nodes (19): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 11. Changelog v1.2 → v1.3, 1. Scope, 2. Binding constraints (restate these in every session), 3. Data model (SQLite, via SQLAlchemy + Alembic), 4. API contract (FastAPI, all JSON), 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages). (+11 more)

### Community 27 - "Decisions"
Cohesion: 0.09
Nodes (21): Decisions, Fixed, Narrative Lens — Progress, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5 (+13 more)

### Community 28 - "test_explorer_clusters.py"
Cohesion: 0.16
Nodes (28): median_ms(), How long a call takes, measured as a median rather than a single sample. PRD §4…, _clusters(), _explorer(), TestClient, The 3D Explorer and the k-means overlay. Acceptance criterion 11: the Explorer…, PRD §9 assumption 8 pins the seed; the same stories always group the same., Acceptance criterion 11: always labelled "descriptive only". (+20 more)

### Community 29 - "App.jsx"
Cohesion: 0.17
Nodes (9): api, ApiError, App(), TABS, CaptureTab(), MODES, LinkManager(), captureTokenFromPath() (+1 more)

### Community 30 - "test_capture_draft.py"
Cohesion: 0.15
Nodes (18): Drafts survive a reload (PRD §6 Phase 3, §7.6). The draft lives in the browser,…, Nothing lingers once the story has been sent., Starting fresh is recoverable; crashing on load is not., A draft from an older shape must not crash the wizard., Private browsing must not stop someone telling their story., Constraint 9 reaches into the browser, not just the database., Offering to restore an empty draft would be noise., The whole point: a half-written story survives the page going away. (+10 more)

### Community 31 - "Widgets.jsx"
Cohesion: 0.24
Nodes (15): CORNER_0, CORNER_1, CORNER_2, normalise(), roundTo(), toBarycentric(), toCartesian(), TRIANGLE_HEIGHT (+7 more)

### Community 32 - "test_schema_absence.py"
Cohesion: 0.15
Nodes (17): _columns(), parametrize, Constraint 9 — respondent anonymity is engineered, not promised. These tests…, Constraint 9: respondent time is hour-rounded, so no exact clock exists.…, A row written through the ORM gets an hour-rounded stamp automatically., The rules hold against the real database, not just the model metadata., PRD §3: migration 001 creates all six tables and no others., No IP, user agent, fingerprint, device/session id or email anywhere. (+9 more)

### Community 33 - "render_paper_pack"
Cohesion: 0.33
Nodes (6): _facilitator_sheet(), The A4 story card: prompt, ruled space, groups, anonymity line., Running instructions, materials, and the reconciliation grid., Render the whole pack as one self-contained, printable HTML page., render_paper_pack(), _story_card()

### Community 34 - "test_terrain_maths.py"
Cohesion: 0.14
Nodes (22): The landscape's geometry, held to fixed answers in Node. The terrain is drawn…, Rotation moves the terrain, it does not grow or shrink it., Nothing crosses a level the whole grid is already above., The answer known by hand: one peak, one loop, and it encircles the peak., Contours nest. If they did not, the terrain would be unreadable., What makes the terrain survive a grayscale screenshot (§5b)., Two equal heights project to the same rise, wherever they sit. A perspective…, Elevation is the camera's angle above the horizon, as it sounds. From the… (+14 more)

### Community 35 - "Anecdote"
Cohesion: 0.18
Nodes (24): Cluster, ClusterAssignment, ClusterSet, Dimension, dimensions_of(), explorer(), ExplorerPoint, ExplorerSet (+16 more)

### Community 36 - "test_patterns.py"
Cohesion: 0.12
Nodes (38): _capture(), _patterns(), TestClient, The patterns endpoint: what it counts, what it sorts, what it refuses. Three…, The no-bypass promise, applied to what the operator actually sees., A meaning change: version n+1, old stories left on the old wording., PRD §4: no silent mixing. A v1 answer is not an answer to v2., §5.4: any view spanning versions must be able to say so on screen. (+30 more)

### Community 37 - "StonesAxis"
Cohesion: 0.40
Nodes (3): One axis of the stones canvas, named at both ends., StonesAxis, model_validator

### Community 38 - "test_capture_links.py"
Cohesion: 0.12
Nodes (14): qr_png_bytes(), QR codes for capture links (PRD §4, §1.8). A QR is how a phone gets to the…, Return a PNG of ``payload`` as QR, as raw bytes. Error correction is set to M…, Rate limiting for the public capture endpoints (PRD §4). The public endpoints…, Clear every counter. Tests call this between cases., reset_all(), _clear_limits(), fixture (+6 more)

### Community 39 - "test_exports.py"
Cohesion: 0.13
Nodes (32): _brief(), _csv(), TestClient, The CSV and the Pattern Brief. The CSV is tested as a file a person will open…, The case the provenance column exists for., Constraint 13f, the whole point of the brief., A brief that did not say what it excluded would be misleading., Constraint 12: exploratory and abductive, never causal. (+24 more)

### Community 40 - "voice.js"
Cohesion: 0.28
Nodes (11): appendDictation(), getRecognitionClass(), isVoiceSupported(), startDictation(), VOICE_DENIED, VOICE_FAILED, VOICE_NETWORK, VOICE_NO_SPEECH (+3 more)

### Community 41 - "ImportTab.jsx"
Cohesion: 0.18
Nodes (4): ImportTab(), MarkUpStep(), storyCount(), MappingScreen()

### Community 42 - "models.py"
Cohesion: 0.19
Nodes (12): hour_rounded_now(), _in_clause(), datetime, The six-table schema from PRD §3. Two constraints shape this module directly: *…, Render a SQL ``IN`` predicate for a CHECK constraint., Naive UTC now, for operator-side records that carry no respondent link., Naive UTC now truncated to the hour (constraint 9). Minutes, seconds and…, utcnow() (+4 more)

### Community 43 - "Wizard.jsx"
Cohesion: 0.41
Nodes (9): clearDraft(), draftHasContent(), draftKey(), loadDraft(), safeStorage(), saveDraft(), browserStorage(), buildSteps() (+1 more)

### Community 44 - "Studio.jsx"
Cohesion: 0.18
Nodes (11): PaperBatch(), ReflectionPanel(), EditKindDialog(), Field(), SignifierEditor(), TextArea(), orderedSignifiers(), PhonePreview() (+3 more)

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
Cohesion: 0.07
Nodes (46): FrameworkDefinition, The whole respondent-facing definition of one framework version., One id namespace across all signifier kinds — significations key on it., How many signifier screens the respondent will see., PRD §1.1: warn past roughly six signifier screens., Coarse 'respondent minutes' estimate shown live in the Studio., Estimated respondent time, rounded to one decimal., _check_batch() (+38 more)

### Community 49 - "make_framework"
Cohesion: 0.17
Nodes (26): confirmed_import(), make_framework(), proposed_import(), TestClient, Shared helpers for the Stage B and validation-queue suites. One framework…, Drive a file as far as ``mapping_confirmed``, accepting Stage A as-is., Drive a file all the way to ``proposed`` — stories in the queue., Session (+18 more)

### Community 50 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 51 - "Web Design & Data Visualization"
Cohesion: 0.22
Nodes (8): Data visualization, Output, Step 1: Frame the brief, Step 2: Design plan before code, Step 3: B2B or B2C playbook, Step 4: Build to the quality floor (non-negotiable, never announced), Step 5: Critique pass, Web Design & Data Visualization

### Community 52 - "queue.py"
Cohesion: 0.09
Nodes (41): CaptureError, _check_dyad(), _check_mcq(), _check_stones(), _check_triad(), ValueError, Validating a submitted capture against the framework it answers (PRD §4). A…, Triad weights: one per corner, non-negative, summing to 1.0. (+33 more)

### Community 53 - "backend/exports.py"
Cohesion: 0.13
Nodes (26): _category_finding(), dataset_csv(), _dyad_finding(), findings(), headline(), _headlines(), _join(), _nearest_corner() (+18 more)

### Community 54 - "regenerate_golden.py"
Cohesion: 0.16
Nodes (16): main(), Rewrite both goldens. Run deliberately, never automatically. python -m…, produce(), TestClient, The pattern golden — byte-identical from Phase 7 onward (PRD §6). Twenty…, The one way this project writes a golden file. Sorted keys and a fixed indent,…, A missing golden would make every other test here silently vacuous., Determinism, checked against itself rather than against the file. If… (+8 more)

### Community 55 - "Design System Reference — 2026"
Cohesion: 0.29
Nodes (6): 2026 trend catalog — pick deliberately, one direction per project, Banned defaults (the "AI look"), Copy rules, Design System Reference — 2026, Layout heuristics, Tokens

### Community 56 - "test_health.py"
Cohesion: 0.29
Nodes (5): The one endpoint Phase 1 ships., PRD §4 budgets 200ms for non-AI endpoints; health should be far under., Guard against building ahead of the phase plan (PRD §6). Enumerated from the…, test_health_is_fast_enough_for_the_200ms_budget(), test_no_routes_beyond_the_current_phase()

### Community 57 - "test_live_ai.py"
Cohesion: 0.08
Nodes (45): AiError, _live_text(), Exception, The one AI client (constraint 6). Every call Narrative Lens makes to a language…, One live call to api.anthropic.com. The only network in the app. Imported…, An AI call that failed in a way the operator needs told about. Carries the PRD…, ModuleType, APIConnectionError (+37 more)

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
Cohesion: 0.23
Nodes (11): build_edit_log_entries(), diff_text_fields(), Any, datetime, The wording-fix vs meaning-change guardrail (PRD §1.1, constraint 13g). While a…, The shape of a framework, ignoring every word in it. Two definitions with the…, Flatten a definition into ``{field_path: text}`` for every string leaf., Every changed string, as ``(field_path, old_text, new_text)``. Field paths read… (+3 more)

### Community 82 - "ValidationQueue.jsx"
Cohesion: 0.29
Nodes (6): fromStored(), orderedSignifiers(), toSubmission(), signifiersInOrder(), ValidationQueue(), widgetValues()

### Community 83 - "propose.py"
Cohesion: 0.14
Nodes (20): describe_signifiers(), _mock_batch(), _mock_confidence(), _mock_value(), Placement, _prompt(), ProposalBatch, ProposedPlacement (+12 more)

### Community 84 - "routers/landscape.py"
Cohesion: 0.07
Nodes (53): only_pending(), only_validated(), What counts as data, in one place (constraint 1). An anecdote exists in three…, Narrow a query to the stories a person has actually approved. Every read that…, Narrow a query to the stories still waiting on a person., export_brief(), export_csv(), Depends (+45 more)

### Community 85 - "Patterns.jsx"
Cohesion: 0.08
Nodes (32): BarChart(), DyadChart(), StonesChart(), CLUSTER_TOKENS, ExplorerView(), Scatter(), VIEW, ContourTwin() (+24 more)

### Community 86 - "_story"
Cohesion: 0.18
Nodes (8): PRD §1.2: three entry modes share one wizard., Only a real token may produce a ``link`` record., Constraint 1: AI-derived content must not pose as first-hand., PRD §4: public endpoints are rate-limited — per token, never per person., The limit is per link, so one workshop cannot shut down another., _story(), TestKioskMode, TestRateLimiting

### Community 87 - "conftest.py"
Cohesion: 0.24
Nodes (12): client(), db_path(), db_url(), engine(), fixture, Path, TestClient, Shared fixtures. Every test runs against a throwaway SQLite file, never the… (+4 more)

### Community 88 - "test_landscape_golden.py"
Cohesion: 0.26
Nodes (10): peaks_of(), produce_peaks(), TestClient, The landscape golden — peaks stable to ±0.02 (PRD §6, Phase 8). The second of…, The headline guarantee: the terrain does not drift under anyone's feet., A golden of empty lists would pass the tolerance test forever., Determinism against itself, not only against the stored file., test_peaks_are_stable_within_tolerance() (+2 more)

### Community 89 - "TestTokenDecidesEverything"
Cohesion: 0.29
Nodes (4): The token, not the body, chooses the version and the entry mode., A later meaning change must not retarget an existing link., The browser may not choose which question set it answered., TestTokenDecidesEverything

### Community 90 - "TestLinkProvenance"
Cohesion: 0.40
Nodes (3): Constraint 3: provenance on every record, whatever route it came by., Constraint 3: input_method distinguishes voice from typing., TestLinkProvenance

### Community 91 - "_backend_modules"
Cohesion: 0.40
Nodes (5): _backend_modules(), Path, One symbol, so the test above cannot be sidestepped by a literal., test_nobody_writes_the_status_as_a_bare_string(), test_only_two_modules_write_validated()

### Community 92 - "env.py"
Cohesion: 0.36
Nodes (7): Alembic environment. The database URL comes from…, Emit SQL to a script without a live connection., Run migrations against a live connection., _run(), run_migrations_offline(), run_migrations_online(), _url()

### Community 93 - "RateLimiter"
Cohesion: 0.22
Nodes (5): RateLimiter, A sliding-window counter keyed by an opaque string. Deliberately simple and in-…, Record a hit and report whether it is within the limit., Forget counters. Used by tests and when a link is revoked., How many hits are still allowed in the current window.

### Community 96 - "patterns_fixtures.py"
Cohesion: 0.50
Nodes (4): The twenty-story fixture behind the pattern golden (PRD §6, Phase 7). Twenty…, One story, entirely determined by its position in the run., story_payload(), _tenths()

### Community 100 - "db.py"
Cohesion: 0.18
Nodes (10): _connect_args(), Database engine and session plumbing (constraint 4: SQLite + local files)., SQLite needs ``check_same_thread=False`` to serve requests from a pool., database_url(), lan_host(), public_base_url(), Runtime settings. Constraint 7 (non-technical operator) forbids config editing,…, Return the SQLAlchemy URL for the local SQLite database. (+2 more)

## Knowledge Gaps
- **158 isolated node(s):** `name`, `version`, `description`, `dev`, `build` (+153 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Anecdote` connect `Anecdote` to `TestClient`, `TestClient`, `Framework`, `TestClient`, `test_import_pipeline.py`, `_create`, `test_public_identifier_absence.py`, `ImportJob`, `validate_definition`, `build_golden_dataset`, `imports.py`, `backend/patterns.py`, `CaptureLink`, `_framework`, `TriadChart`, `capture.py`, `test_schema_absence.py`, `test_capture_links.py`, `models.py`, `test_queue.py`, `make_framework`, `queue.py`, `backend/exports.py`, `routers/landscape.py`, `_story`, `TestTokenDecidesEverything`, `TestLinkProvenance`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **Why does `FrameworkDefinition` connect `FrameworkDefinition` to `render_paper_pack`, `Anecdote`, `Framework`, `validate_definition`, `test_placement_shape_parity.py`, `edit_semantics.py`, `backend/patterns.py`, `propose.py`, `queue.py`, `backend/exports.py`, `imports.py`, `TriadChart`, `capture.py`, `routers/landscape.py`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `Signification` connect `Anecdote` to `TestClient`, `test_import_pipeline.py`, `test_public_identifier_absence.py`, `models.py`, `ImportJob`, `validate_definition`, `test_queue.py`, `build_golden_dataset`, `imports.py`, `backend/patterns.py`, `make_framework`, `routers/landscape.py`, `backend/exports.py`, `queue.py`, `TriadChart`, `capture.py`, `_framework`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 53 inferred relationships involving `FrameworkDefinition` (e.g. with `CaptureError` and `CaptureSubmission`) actually correct?**
  _`FrameworkDefinition` has 53 INFERRED edges - model-reasoned connections that need verification._
- **Are the 69 inferred relationships involving `Anecdote` (e.g. with `Cluster` and `ClusterAssignment`) actually correct?**
  _`Anecdote` has 69 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Signification` (e.g. with `Cluster` and `ClusterAssignment`) actually correct?**
  _`Signification` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `Framework` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Framework` has 30 INFERRED edges - model-reasoned connections that need verification._