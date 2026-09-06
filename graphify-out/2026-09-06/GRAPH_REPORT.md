# Graph Report - TESSA-Sensemaking  (2026-09-06)

## Corpus Check
- 170 files · ~188,972 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3088 nodes · 7302 edges · 133 communities (125 shown, 8 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 487 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `04958f4d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- build_golden_dataset
- TestClient
- Signification
- test_edit_log_wording.py
- make_engine
- TestClient
- test_import_pipeline.py
- TestClient
- request_json
- test_public_identifier_absence.py
- errors.py
- package.json
- validate_definition
- test_story_browser.py
- test_landscape.py
- parsers.py
- _run_node
- NormalisedDocument
- backend/patterns.py
- test_signification_provenance.py
- test_parsers.py
- What You Must Do When Invoked
- test_translation_readtime.py
- organise.py
- imports.py
- TestClient
- PRD: Narrative Lens — Local Narrative Sense-Making App
- Decisions
- test_explorer_clusters.py
- api.js
- test_capture_draft.py
- Widgets.jsx
- terrain.js
- test_error_surface.py
- test_terrain_maths.py
- public_base_url
- test_patterns.py
- test_language_capture.py
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
- _columns
- graphify reference: extra exports and benchmark
- Web Design & Data Visualization
- test_launcher.py
- backend/exports.py
- test_placement_shape_parity.py
- Design System Reference — 2026
- test_health.py
- _calls
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
- code_of
- plain_http_error
- Anecdote
- backend/stories.py
- ai_client.py
- Patterns.jsx
- proposed_import
- test_empty_states.py
- test_landscape_golden.py
- _FakeAnthropic
- Framework
- TriadChart
- conftest.py
- AiError
- test_original_names.py
- test_visual_grammar.py
- parse
- make_framework
- test_quality_signals.py
- test_live_ai.py
- barycentric.py
- test_patterns_golden.py
- routers/stories.py
- test_api_alignment.py
- test_scope_completeness.py
- Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6
- CaptureSettings
- _live_text
- StonesAxis
- env.py
- queue.py
- public.py
- BarycentricError
- clusters.py
- edit_semantics.py
- lint.py
- get_landscape
- test_the_list_shows_the_context_a_reader_needs
- quality_css
- session_source
- FrameworkCreate
- propose.py
- get_paper_pack
- read_queue
- routers/patterns.py
- xlsx_bytes
- patterns_fixtures.py
- ProposeError
- health

## God Nodes (most connected - your core abstractions)
1. `make_framework()` - 142 edges
2. `FrameworkDefinition` - 140 edges
3. `build_golden_dataset()` - 120 edges
4. `Anecdote` - 103 edges
5. `Signification` - 72 edges
6. `Framework` - 69 edges
7. `get_session()` - 51 edges
8. `ImportJob` - 49 edges
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
- `TestAnonymityStatementIsTrueOfTheCode` --uses--> `FrameworkDefinition`  [INFERRED]
  tests/test_framework_schema.py → backend/framework_schema.py

## Import Cycles
- 3-file cycle: `frontend/src/patterns/Landscape.jsx -> frontend/src/patterns/Patterns.jsx -> frontend/src/patterns/SessionMode.jsx -> frontend/src/patterns/Landscape.jsx`

## Communities (133 total, 8 thin omitted)

### Community 0 - "build_golden_dataset"
Cohesion: 0.09
Nodes (54): build_golden_dataset(), TestClient, Create the framework and its twenty stories. Returns the framework., brief(), landscape(), listed(), Session, TestClient (+46 more)

### Community 1 - "TestClient"
Cohesion: 0.06
Nodes (55): CaptureLink, A token-gated capture URL pointing at one exact framework version., qr_png_bytes(), QR codes for capture links (PRD §4, §1.8). A QR is how a phone gets to the…, Return a PNG of ``payload`` as QR, as raw bytes. Error correction is set to M…, capture_link_qr(), capture_url(), CaptureLinkCreate (+47 more)

### Community 2 - "Signification"
Cohesion: 0.05
Nodes (44): One respondent (or validated AI) placement on one signifier. ``value_json``…, A free-text tag the analyst attaches to a story., Signification, Tag, _framework(), TestClient, Local capture (PRD §6 Phase 3). The tests the PRD names for this phase: wizard…, PRD §9 assumption 7: reflection shows one signifier. (+36 more)

### Community 3 - "test_edit_log_wording.py"
Cohesion: 0.16
Nodes (13): _describe(), described(), fixture, The edit log reads as English, not as a schema path (constraint 7). The log…, A log entry nobody planned for is still a record of a change., The full fixture with one string changed in every kind of place., Every path a real wording fix produces, with what the Studio shows., Nothing falls through to the raw path — the whole surface is covered. (+5 more)

### Community 4 - "make_engine"
Cohesion: 0.16
Nodes (20): _connect_args(), make_engine(), SQLite needs ``check_same_thread=False`` to serve requests from a pool., Build an engine, enabling SQLite foreign-key enforcement. SQLite ignores…, Config, Engine, alembic_config(), fixture (+12 more)

### Community 5 - "TestClient"
Cohesion: 0.07
Nodes (30): Break a corner name into lines that each fit ``limit`` pixels. Greedy by word.…, wrap_label(), _create_full(), _pack_html(), TestClient, The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar). Two…, PRD §1.2a: the story card carries respondent-group tick boxes., The pack renders the version's current wording, not a cached copy. (+22 more)

### Community 6 - "test_import_pipeline.py"
Cohesion: 0.15
Nodes (46): txt_bytes(), _confirm(), _confirmation_body(), _organise(), parametrize, Session, TestClient, The staged import machine end to end, over HTTP, with zero network. Acceptance… (+38 more)

### Community 7 - "TestClient"
Cohesion: 0.11
Nodes (27): _add_story(), _create(), _definition(), Session, TestClient, The wording-fix vs meaning-change state machine (PRD §6, constraint 13g). This…, Constraint 7: the operator must be able to act on the message., A wording fix patches in place and appends to the edit log. (+19 more)

### Community 8 - "request_json"
Cohesion: 0.11
Nodes (25): Any, Ask for one JSON object of the given shape, or fail in plain English. In mock…, request_json(), live(), BaseModel, fixture, MonkeyPatch, The one AI client, and the four promises constraint 6 makes about it. (+17 more)

### Community 9 - "test_public_identifier_absence.py"
Cohesion: 0.08
Nodes (28): RateLimiter, Rate limiting for the public capture endpoints (PRD §4). The public endpoints…, A sliding-window counter keyed by an opaque string. Deliberately simple and in-…, Record a hit and report whether it is within the limit., Forget counters. Used by tests and when a link is revoked., How many hits are still allowed in the current window., Clear every counter. Tests call this between cases., reset_all() (+20 more)

### Community 10 - "errors.py"
Cohesion: 0.07
Nodes (35): AppError, conflict(), not_found(), The error shape from PRD §4. ``{"error": {"code": ..., "message": plain-English…, An error the operator is meant to read and act on., Something outside the app misbehaved — currently only the AI service., upstream(), advance() (+27 more)

### Community 11 - "package.json"
Cohesion: 0.06
Nodes (30): eslint, @eslint/js, eslint-plugin-react, eslint-plugin-react-hooks, dependencies, react, react-dom, description (+22 more)

### Community 12 - "validate_definition"
Cohesion: 0.06
Nodes (21): default_definition(), Parse and validate a raw ``definition_json`` payload., A minimal, valid definition — what a brand-new framework starts from., validate_definition(), Validation of ``definition_json`` and the anonymity statement it carries., Significations key on the id alone, so one namespace covers all kinds., A typo in the Studio should fail loudly, not vanish silently., Constraint 10: ≤4 minutes typical. (+13 more)

### Community 13 - "test_story_browser.py"
Cohesion: 0.15
Nodes (30): _browse(), _mark(), TestClient, The story browser (PRD §1.6, §5.4). The last item of §1's scope, and the one…, Constraint 1, on the reading side. The queue is where pending lives., Constraint 3 shown, constraint 9 absent — the same as every other view., They share a table, so this is the join worth testing., It is stored as one, which is exactly why this is worth asserting. (+22 more)

### Community 14 - "test_landscape.py"
Cohesion: 0.09
Nodes (49): Every story inside a rectangle of grid cells, and no others. The region drill…, stories_in_region(), _capture(), _landscape(), _panel(), Session, TestClient, The landscape suite: the terrain, its contour twin, the drill, the clusters.… (+41 more)

### Community 15 - "parsers.py"
Cohesion: 0.11
Nodes (31): Block, _blocks_from_text(), classify(), _clean_row(), _decode(), _parse_captions(), _parse_csv(), _parse_docx() (+23 more)

### Community 16 - "_run_node"
Cohesion: 0.11
Nodes (14): parametrize, Voice fallback (PRD §6 Phase 4, §7.12, constraint 10). Constraint 10 says voice…, The UI calls stop() on unmount whether or not voice ever started., Stopping on purpose is not a failure and must not show a warning., Constraint 10: voice always paired with typing., Interim results would rewrite a respondent's words as they speak., §7.12: voice fails plain-English with a working fallback., Constraint 7: no jargon a respondent cannot act on. (+6 more)

### Community 17 - "NormalisedDocument"
Cohesion: 0.14
Nodes (38): _balance(), Candidate, confirm(), confirm_narrative(), confirm_tabular(), ConfirmedExtraction, ExtractionError, BaseModel (+30 more)

### Community 18 - "backend/patterns.py"
Cohesion: 0.08
Nodes (65): Dyad, Mcq, BaseModel, Validation for ``frameworks.definition_json`` (PRD §3 and §5). Every…, A 2D canvas on which the respondent places named chips., A multiple-choice question., Every signifier with its kind, in the order the respondent meets them., Reject unknown keys so a typo in the Studio surfaces as an error. (+57 more)

### Community 19 - "test_signification_provenance.py"
Cohesion: 0.10
Nodes (47): expert_validated_ids(), mixed_dataset(), patterns(), placed(), plotted(), parametrize, TestClient, Whose interpretation a figure is made of (delta §6, constraint 14). Constraint… (+39 more)

### Community 20 - "test_parsers.py"
Cohesion: 0.08
Nodes (27): docx_bytes(), pdf_bytes(), _pdf_escape(), pptx_bytes(), Real files, in memory, one per format Narrative Lens claims to read. Acceptance…, A one-page PDF with each paragraph as its own text run. Written by hand:…, vtt_bytes(), parametrize (+19 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "test_translation_readtime.py"
Cohesion: 0.08
Nodes (50): capture(), MonkeyPatch, Session, TestClient, Read-time translation, display-only (delta §6, constraint 15). The second half…, The browser reads stories; a translation is not one., ``anecdotes.text`` is the record and stays exactly as it was told., Translating into English does not make the story an English story. (+42 more)

### Community 23 - "organise.py"
Cohesion: 0.13
Nodes (20): _check_narrative(), _check_tabular(), _hinted_column(), _mock_narrative(), _mock_tabular(), _narrative_prompt(), NarrativeOrganisation, OrganiseError (+12 more)

### Community 24 - "imports.py"
Cohesion: 0.15
Nodes (36): bad_request(), ImportJob, One uploaded file moving through the two-stage ingestion machine., OrganiseResult, Stage A's whole output, as stored on the job and shown for confirmation., confirm_mapping(), create_import(), _detail() (+28 more)

### Community 25 - "TestClient"
Cohesion: 0.14
Nodes (9): TestClient, List, create and fetch frameworks (PRD §4)., A new framework starts valid and empty, ready to fill in., The Studio shows these live while the operator edits., Constraint 7: plain English, with something to do about it., PRD §5.1: version history sidebar shows versions with story counts., TestCreate, TestFetch (+1 more)

### Community 26 - "PRD: Narrative Lens — Local Narrative Sense-Making App"
Cohesion: 0.10
Nodes (19): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 11. Changelog v1.2 → v1.3, 1. Scope, 2. Binding constraints (restate these in every session), 3. Data model (SQLite, via SQLAlchemy + Alembic), 4. API contract (FastAPI, all JSON), 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages). (+11 more)

### Community 27 - "Decisions"
Cohesion: 0.06
Nodes (33): After the delta — the whole-delta check, Completeness pass, Decisions, Delta phase A, Delta phase B, Delta phase C, Delta phase D, Delta phase E (+25 more)

### Community 28 - "test_explorer_clusters.py"
Cohesion: 0.16
Nodes (28): median_ms(), How long a call takes, measured as a median rather than a single sample. PRD §4…, _clusters(), _explorer(), TestClient, The 3D Explorer and the k-means overlay. Acceptance criterion 11: the Explorer…, PRD §9 assumption 8 pins the seed; the same stories always group the same., Acceptance criterion 11: always labelled "descriptive only". (+20 more)

### Community 29 - "api.js"
Cohesion: 0.13
Nodes (11): api, ApiError, App(), TABS, CaptureTab(), MODES, LinkManager(), captureTokenFromPath() (+3 more)

### Community 30 - "test_capture_draft.py"
Cohesion: 0.15
Nodes (18): Drafts survive a reload (PRD §6 Phase 3, §7.6). The draft lives in the browser,…, Nothing lingers once the story has been sent., Starting fresh is recoverable; crashing on load is not., A draft from an older shape must not crash the wizard., Private browsing must not stop someone telling their story., Constraint 9 reaches into the browser, not just the database., Offering to restore an empty draft would be noise., The whole point: a half-written story survives the page going away. (+10 more)

### Community 31 - "Widgets.jsx"
Cohesion: 0.20
Nodes (18): CORNER_0, CORNER_1, CORNER_2, normalise(), roundTo(), toBarycentric(), toCartesian(), TRIANGLE_HEIGHT (+10 more)

### Community 32 - "terrain.js"
Cohesion: 0.10
Nodes (29): CLUSTER_TOKENS, ExplorerView(), Scatter(), VIEW, ContourTwin(), FindingsPanel(), Terrain(), terrainStops() (+21 more)

### Community 33 - "test_error_surface.py"
Cohesion: 0.11
Nodes (28): AST, _error(), _messages(), parametrize, TestClient, The plain-English error pass, held as a test (constraint 7, PRD §4). Individual…, The literal text of a string argument, with ``{}`` for what is filled in., Every written error triple in the backend: (file, line, message, action). Non-… (+20 more)

### Community 34 - "test_terrain_maths.py"
Cohesion: 0.14
Nodes (22): The landscape's geometry, held to fixed answers in Node. The terrain is drawn…, Rotation moves the terrain, it does not grow or shrink it., Nothing crosses a level the whole grid is already above., The answer known by hand: one peak, one loop, and it encircles the peak., Contours nest. If they did not, the terrain would be unreadable., What makes the terrain survive a grayscale screenshot (§5b)., Two equal heights project to the same rise, wherever they sit. A perspective…, Elevation is the camera's angle above the horizon, as it sounds. From the… (+14 more)

### Community 35 - "public_base_url"
Cohesion: 0.50
Nodes (4): lan_host(), public_base_url(), The address other devices on the mesh can reach this machine at. A QR pointing…, Base URL a capture link should carry.

### Community 36 - "test_patterns.py"
Cohesion: 0.12
Nodes (38): _capture(), _patterns(), TestClient, The patterns endpoint: what it counts, what it sorts, what it refuses. Three…, The no-bypass promise, applied to what the operator actually sees., A meaning change: version n+1, old stories left on the old wording., PRD §4: no silent mixing. A v1 answer is not an answer to v2., §5.4: any view spanning versions must be able to say so on screen. (+30 more)

### Community 37 - "test_language_capture.py"
Cohesion: 0.10
Nodes (40): capture(), csv_rows(), MonkeyPatch, parametrize, Session, TestClient, The original language is the record (delta §6, constraint 15). Constraint 15…, The text is the record. Not transliterated, not normalised, not folded. (+32 more)

### Community 38 - "backend/interpretations.py"
Cohesion: 0.16
Nodes (20): for_framework(), InterpretationIn, InterpretationOut, BaseModel, Session, Collective interpretation: what a room concluded, kept as an artefact.…, Store one conclusion exactly as the room gave it. The text goes in unchanged.…, Every conclusion recorded against these framework versions, newest first. Takes… (+12 more)

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
Cohesion: 0.06
Nodes (54): check(), lint_css(), panel_source(), MonkeyPatch, Session, TestClient, The framework design linter (delta §6, phase C). This is the one AI call in…, The shape is enforced on the mock exactly as on a live reply. ``request_json``… (+46 more)

### Community 43 - "Wizard.jsx"
Cohesion: 0.19
Nodes (19): clearDraft(), draftHasContent(), draftKey(), loadDraft(), safeStorage(), saveDraft(), PaperBatch(), orderedSignifiers() (+11 more)

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

### Community 49 - "_columns"
Cohesion: 0.20
Nodes (12): _columns(), parametrize, No IP, user agent, fingerprint, device/session id or email anywhere., No name-family column on a table whose rows are linked to a respondent., Catch identifiers this test did not anticipate, e.g. ``manager_name``.…, Constraint 9: respondent time is hour-rounded, so no exact clock exists.…, Constraint 16, read off the metadata rather than promised. The guarantee is…, test_an_interpretation_has_no_route_to_a_respondent() (+4 more)

### Community 50 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 51 - "Web Design & Data Visualization"
Cohesion: 0.22
Nodes (8): Data visualization, Output, Step 1: Frame the brief, Step 2: Design plan before code, Step 3: B2B or B2C playbook, Step 4: Build to the quality floor (non-negotiable, never announced), Step 5: Critique pass, Web Design & Data Visualization

### Community 52 - "test_launcher.py"
Cohesion: 0.09
Nodes (39): parametrize, Path, The two files the operator actually double-clicks (constraint 7). Constraint 7…, ``npm`` is a ``.cmd`` on Windows. A batch file that runs another batch file…, Constraint 7: a sentence about what went wrong, and one about what to do., A double-clicked window closes the instant the file ends. Every path that gives…, Constraint 7 again: nothing here may be fixed by typing a command., Windows Explorer hides ``.bat``. A message saying to double-click "Set up… (+31 more)

### Community 53 - "backend/exports.py"
Cohesion: 0.09
Nodes (36): _category_finding(), dataset_csv(), _dyad_finding(), findings(), headline(), _headlines(), _heard_category(), _interpretation_section() (+28 more)

### Community 54 - "test_placement_shape_parity.py"
Cohesion: 0.15
Nodes (13): fixture, A stored placement must survive the round trip to a widget and back. The server…, server shape → widget shape → server shape, unchanged., The shape the widget's own maths destructures, in corner order., The one kind whose two dialects happen to agree., Run one ES module through Node and read its JSON back., Exactly what Stage B writes to the database, for every signifier kind., round_trip() (+5 more)

### Community 55 - "Design System Reference — 2026"
Cohesion: 0.29
Nodes (6): 2026 trend catalog — pick deliberately, one direction per project, Banned defaults (the "AI look"), Copy rules, Design System Reference — 2026, Layout heuristics, Tokens

### Community 56 - "test_health.py"
Cohesion: 0.29
Nodes (5): The one endpoint Phase 1 ships., PRD §4 budgets 200ms for non-AI endpoints; health should be far under., Guard against building ahead of the phase plan (PRD §6). Enumerated from the…, test_health_is_fast_enough_for_the_200ms_budget(), test_no_routes_beyond_the_current_phase()

### Community 57 - "_calls"
Cohesion: 0.29
Nodes (6): _calls(), Any, Strict JSON is asked for on every call, not only where it is convenient., Every request made, across every client. ``_live_text`` builds a fresh…, _Response, test_the_json_instruction_is_appended_to_every_system_prompt()

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
Cohesion: 0.12
Nodes (15): How to resume, Narrative Lens — Latest, Next step, Running it yourself, Starting it: the launcher now sets itself up, The app would not start, and it was our fault, The completeness pass, after Phase 9, The meaningfulness delta — phase A is done (+7 more)

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

### Community 80 - "code_of"
Cohesion: 0.20
Nodes (10): code_of(), parametrize, Path, Structural, not behavioural. The equivalence test above proves no cached row…, A module's code with its docstrings and comments taken out. These assertions…, And the traffic does not flow the other way either., Secondary weight (delta §5), read off the stylesheet., test_no_computing_module_can_reach_the_cache() (+2 more)

### Community 81 - "plain_http_error"
Cohesion: 0.22
Nodes (14): _envelope(), plain_http_error(), plain_unexpected_error(), plain_validation_error(), Exception, Our own refusals pass straight through; the framework's get translated., A body or query the page built wrongly. The operator cannot fix a validator's…, A fault in the app itself. Logged in full, reported in one sentence. (+6 more)

### Community 82 - "Anecdote"
Cohesion: 0.06
Nodes (43): What counts as data, in one place (constraint 1). An anecdote exists in three…, Anecdote, Base, hour_rounded_now(), _in_clause(), datetime, The six-table schema from PRD §3. Two constraints shape this module directly: *…, One story, bound to the exact framework version it was told against.… (+35 more)

### Community 83 - "backend/stories.py"
Cohesion: 0.08
Nodes (37): browse_stories(), Depends, ge, get, put, Query, Session, Star a story, or replace its tags. The analyst's own shorthand. (+29 more)

### Community 84 - "ai_client.py"
Cohesion: 0.20
Nodes (10): _fenced_json(), mock_enabled(), _parse(), The one AI client (constraint 6). Every call Narrative Lens makes to a language…, Parse one reply strictly, or raise the reason it could not be parsed., Whether this process runs with mocks instead of the network. Read on every call…, Return *raw* with one surrounding markdown fence removed, if present. Strict…, Payload (+2 more)

### Community 85 - "Patterns.jsx"
Cohesion: 0.10
Nodes (19): BarChart(), DyadChart(), StonesChart(), LandscapeView(), FILTERS, lineageOf(), optionsFrom(), PatternsTab() (+11 more)

### Community 86 - "proposed_import"
Cohesion: 0.13
Nodes (30): confirmed_import(), proposed_import(), TestClient, Shared helpers for the Stage B and validation-queue suites. One framework…, Drive a file as far as ``mapping_confirmed``, accepting Stage A as-is., Drive a file all the way to ``proposed`` — stories in the queue., _backend_modules(), Path (+22 more)

### Community 87 - "test_empty_states.py"
Cohesion: 0.21
Nodes (13): _copy(), parametrize, Path, Every screen tells the operator what to do next (PRD §6, Phase 9). A fresh…, The Studio is the tab the app opens on, so it carries the first word., One name for the thing, in every place the operator can read it. The code calls…, The text of every empty-state paragraph in one screen, tags stripped., No data" is a fact about the database, not help for the person reading. (+5 more)

### Community 88 - "test_landscape_golden.py"
Cohesion: 0.21
Nodes (13): peaks_of(), produce_peaks(), TestClient, The landscape golden — peaks stable to ±0.02 (PRD §6, Phase 8). The second of…, The delta changed which placements are drawn, not where they land. Every story…, Determinism against itself, not only against the stored file., The peaks of one triangle, under a stated provenance choice. ``all`` by…, The headline guarantee: the terrain does not drift under anyone's feet. (+5 more)

### Community 89 - "_FakeAnthropic"
Cohesion: 0.50
Nodes (3): _FakeAnthropic, _FakeMessages, Stands in for ``anthropic.Anthropic`` and records what it was asked.

### Community 90 - "Framework"
Cohesion: 0.16
Nodes (32): get_session(), Session, FastAPI dependency yielding a session that always closes., Framework, A version of the question set respondents see. ``parent_framework_id`` links…, _anecdote_count(), _apply_meaning_change(), _apply_wording_fix() (+24 more)

### Community 91 - "TriadChart"
Cohesion: 0.13
Nodes (29): _axes(), Cell, _cell_index(), compute(), Landscape, LandscapePoint, _local_maxima(), _nearest_corner() (+21 more)

### Community 92 - "conftest.py"
Cohesion: 0.24
Nodes (12): client(), db_path(), db_url(), engine(), fixture, Path, TestClient, Shared fixtures. Every test runs against a throwaway SQLite file, never the… (+4 more)

### Community 93 - "AiError"
Cohesion: 0.24
Nodes (8): AiError, Exception, An AI call that failed in a way the operator needs told about. Carries the PRD…, APIConnectionError, APIStatusError, _Block, Exception, RateLimitError

### Community 94 - "test_original_names.py"
Cohesion: 0.25
Nodes (7): _files(), parametrize, Path, Original names and materials only (constraint 8, acceptance criterion 15). The…, Criterion 15 allows one attribution. One, not none — it is owed. Counted in…, test_no_reserved_name_appears_in_the_app(), test_the_readme_carries_exactly_one_attribution()

### Community 95 - "test_visual_grammar.py"
Cohesion: 0.09
Nodes (28): frontend_sources(), palette(), patterns_source(), parametrize, Path, The palette, held to §5b, by reading the source rather than trusting it.…, How far a colour is from grey, 0 to 1., §5b says 4–6 named colours; the approved tint is a value, not a hue. This is… (+20 more)

### Community 96 - "parse"
Cohesion: 0.17
Nodes (26): organise(), Run Stage A over a parsed file and return its proposal. Nothing is written to…, parse(), Read one uploaded file into the normalised shape, or refuse it. Refusals are…, csv_bytes(), Any, MonkeyPatch, TestClient (+18 more)

### Community 97 - "make_framework"
Cohesion: 0.14
Nodes (33): make_framework(), capture(), link_for(), parametrize, TestClient, The name a storyteller gives their own story (delta §6, items 2 and 5). A…, No name given is the ordinary case, and it must read as a story anyway., A skipped field submits as blank; blank is no name, not a name of "". Otherwise… (+25 more)

### Community 98 - "test_quality_signals.py"
Cohesion: 0.08
Nodes (56): capture(), patterns_jsx(), MonkeyPatch, Session, TestClient, quality(), quality_jsx(), Data-quality signals: centre-parking and skip rate (delta §6, phase B). The… (+48 more)

### Community 99 - "test_live_ai.py"
Cohesion: 0.21
Nodes (16): _last(), MonkeyPatch, TestClient, The live path to api.anthropic.com — the one Phase 7 switches on. Everything…, Answer each successive request with the next reply in the list., PRD §6 Phase 7: the repair path, exercised through Stage A itself., Acceptance criterion 12: offline is a working state, not a broken one., The operator loses the click, not the file. (+8 more)

### Community 100 - "barycentric.py"
Cohesion: 0.14
Nodes (19): distance_from_centre(), _placed(), point_from_value_json(), Triad barycentric maths. A triad answer is a point inside an equilateral…, How far a placement sits from the middle of the triangle. Plain Euclidean…, A stored answer straight to its point in the triangle. Exactly…, The conversion itself, on weights already known to be usable. Kept apart from…, centre_parked_count() (+11 more)

### Community 101 - "test_patterns_golden.py"
Cohesion: 0.11
Nodes (25): main(), Rewrite the goldens. Run deliberately, never automatically. python -m…, produce(), produce_participant(), TestClient, The pattern golden — byte-identical from Phase 7 onward (PRD §6). Twenty…, Determinism, checked against itself rather than against the file. If…, A golden that missed a kind would pin three quarters of the maths. (+17 more)

### Community 102 - "routers/stories.py"
Cohesion: 0.07
Nodes (42): display_name(), The language a story was told in (delta §3, constraint 15). Constraint 15 says…, Whether a tag is shaped like a language tag at all., What to show for a story's language. A code we know gets its English name. A…, well_formed(), A cached read-time translation of one story into one language. Constraint 15 in…, Translation, get_translation() (+34 more)

### Community 103 - "test_api_alignment.py"
Cohesion: 0.31
Nodes (9): _frontend_paths(), The frontend and the backend agree about what exists (contract alignment).…, Every ``/api/...`` address api.js can build, with its parameters blanked., An endpoint nothing calls is either dead or half-finished., A guard on the guard: an empty comparison would pass both tests above., _server_paths(), test_every_address_the_frontend_calls_exists_on_the_server(), test_every_endpoint_is_reached_by_something() (+1 more)

### Community 104 - "test_scope_completeness.py"
Cohesion: 0.16
Nodes (13): TestClient, Every item of PRD §1's scope is actually reachable in the app. This file exists…, One assertion per numbered item of §1 that the API is responsible for., §5.4: "Landscape (default) · Supporting charts · 3D Explorer · Story browser"., The four verbs §1.6 lists, each with something in the code doing it., Dataset CSV · contour PNG · supporting-charts PNG · brief · what we heard., Acceptance criterion 1 ends "QR on home", and the home screen is the Studio., _source() (+5 more)

### Community 105 - "Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6"
Cohesion: 0.11
Nodes (17): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 1. Scope, 2. Binding constraints restated, 3. Data model changes, 4. API contract, 4a. New AI calls — both through `ai_client.request_json`, both mocked, 5. Frontend changes (+9 more)

### Community 106 - "CaptureSettings"
Cohesion: 0.20
Nodes (5): CaptureSettings, Every non-signifier string the respondent reads, plus capture toggles., Well-formed BCP-47, and each offered once. Shape only — no registry lookup. An…, What the welcome screen offers: the configured list, or English., field_validator

### Community 107 - "_live_text"
Cohesion: 0.22
Nodes (11): _live_text(), One live call to api.anthropic.com. The only network in the app. Imported…, ModuleType, fake_anthropic(), fixture, parametrize, A reply may carry blocks that are not text; they are not the answer., Install a fake ``anthropic`` package and turn mock mode off. (+3 more)

### Community 108 - "StonesAxis"
Cohesion: 0.40
Nodes (3): One axis of the stones canvas, named at both ends., StonesAxis, model_validator

### Community 109 - "env.py"
Cohesion: 0.27
Nodes (9): Alembic environment. The database URL comes from…, Emit SQL to a script without a live connection., Run migrations against a live connection., _run(), run_migrations_offline(), run_migrations_online(), _url(), database_url() (+1 more)

### Community 110 - "queue.py"
Cohesion: 0.08
Nodes (46): CaptureError, _check_dyad(), _check_mcq(), _check_stones(), _check_triad(), ValueError, Validating a submitted capture against the framework it answers (PRD §4). A…, Triad weights: one per corner, non-negative, summing to 1.0. (+38 more)

### Community 112 - "public.py"
Cohesion: 0.12
Nodes (27): CaptureSubmission, LocalCaptureSubmission, PublicCaptureSubmission, BaseModel, A capture arriving through a capture link. ``framework_id`` is not accepted:…, A whole capture: one story plus its placements. Note what is *not* here: no id,…, A capture from the operator's own machine: admin, paper entry, or kiosk. Only…, CaptureResult (+19 more)

### Community 113 - "BarycentricError"
Cohesion: 0.05
Nodes (49): BarycentricError, from_value_json(), is_inside(), normalise(), ValueError, Clamp to the triangle and rescale so the three weights sum to exactly 1.0. A…, Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`., Whether the weights describe a point in or on the triangle. (+41 more)

### Community 114 - "clusters.py"
Cohesion: 0.19
Nodes (18): Cluster, ClusterAssignment, ClusterSet, Dimension, dimensions_of(), explorer(), ExplorerPoint, ExplorerSet (+10 more)

### Community 115 - "edit_semantics.py"
Cohesion: 0.15
Nodes (17): build_edit_log_entries(), diff_text_fields(), is_structural_change(), label_renames(), Any, datetime, The wording-fix vs meaning-change guardrail (PRD §1.1, constraint 13g). While a…, ``{signifier_id: {old_label: new_label}}`` for every renamed label. Only labels… (+9 more)

### Community 116 - "lint.py"
Cohesion: 0.14
Nodes (15): lint(), lint_prompt(), LintReport, _mock_reply(), Any, BaseModel, The framework design linter (delta §4a, item 3). The one AI call in this app…, Everything the model had to say about one question set's design. (+7 more)

### Community 118 - "get_landscape"
Cohesion: 0.21
Nodes (16): get_clusters(), get_explorer(), get_landscape(), Depends, ge, get, le, Query (+8 more)

### Community 119 - "test_the_list_shows_the_context_a_reader_needs"
Cohesion: 0.67
Nodes (3): parametrize, A sentence about "this landscape" is worthless without the landscape., test_the_list_shows_the_context_a_reader_needs()

### Community 120 - "quality_css"
Cohesion: 0.25
Nodes (8): quality_css(), Just the panel's own declarations, with the prose taken out. Comments are…, Constraint 13c, and the reason this panel can be read in greyscale. Every…, Quiet weight (13a). The landscape is the one bold element on this tab. Nothing…, Constraint 10: a phone at 375px must not be pushed sideways by a table., test_the_panel_encodes_nothing_in_colour(), test_the_panel_never_shouts(), test_the_wide_table_scrolls_inside_itself()

### Community 121 - "session_source"
Cohesion: 0.22
Nodes (9): Delta §5: "the landscape at full screen with controls hidden". Checked by…, Delta §6 names this. A view you cannot leave strands the facilitator., The question a facilitator will silently be asking, answered on screen., The filters come from the screen, not from a field somebody fills in., session_source(), test_the_projector_view_hides_the_controls(), test_the_projector_view_is_keyboard_escapable(), test_the_projector_view_says_recording_changes_nothing() (+1 more)

### Community 122 - "FrameworkCreate"
Cohesion: 0.19
Nodes (14): Language, offered(), BaseModel, The languages a framework offers, in the order it lists them. An unknown but…, One language a framework may offer, named twice., LintFinding, One thing worth a second look, and what to try instead., FrameworkCreate (+6 more)

### Community 123 - "propose.py"
Cohesion: 0.24
Nodes (12): describe_signifiers(), _mock_batch(), _mock_confidence(), _mock_value(), _prompt(), Any, Stage B — Propose (PRD §4a, constraint 1). Stage B reads a story and *suggests*…, The questions, with the exact answer shape each one takes. Written out in full… (+4 more)

### Community 124 - "get_paper_pack"
Cohesion: 0.17
Nodes (12): _facilitator_sheet(), The A4 story card: prompt, ruled space, groups, anonymity line., Running instructions, materials, and the reconciliation grid., Render the whole pack as one self-contained, printable HTML page., render_paper_pack(), _story_card(), get_paper_pack(), known_languages() (+4 more)

### Community 125 - "read_queue"
Cohesion: 0.18
Nodes (11): only_pending(), Select, Narrow a query to the stories still waiting on a person., Depends, ge, get, le, Query (+3 more)

### Community 126 - "routers/patterns.py"
Cohesion: 0.06
Nodes (72): only_validated(), Narrow a query to the stories a person has actually approved. Every read that…, Database engine and session plumbing (constraint 4: SQLite + local files)., mount_frontend(), FastAPI application. Endpoints arrive with the phase that needs them, per PRD…, Serve ``frontend/dist`` if it has been built. Returns whether anything was…, export_brief(), export_csv() (+64 more)

### Community 127 - "xlsx_bytes"
Cohesion: 0.29
Nodes (7): A two-sheet workbook: one of responses, one lookup table to ignore. The…, xlsx_bytes(), PRD §4: AI endpoints are exempt; reading a job's status is not., test_job_status_is_inside_the_200ms_budget(), Assumption 10: a mixed-role workbook is mapped sheet by sheet., test_workbook_keeps_every_sheet_separately(), test_workbook_rows_are_numbered_as_the_spreadsheet_numbers_them()

### Community 128 - "patterns_fixtures.py"
Cohesion: 0.50
Nodes (4): The twenty-story fixture behind the pattern golden (PRD §6, Phase 7). Twenty…, One story, entirely determined by its position in the run., story_payload(), _tenths()

### Community 129 - "ProposeError"
Cohesion: 0.50
Nodes (3): ProposeError, Exception, Stage B produced something that does not fit the framework.

### Community 130 - "health"
Cohesion: 0.67
Nodes (3): health(), get, Liveness probe. The launcher opens this while the app is starting.

## Knowledge Gaps
- **210 isolated node(s):** `name`, `version`, `description`, `dev`, `build` (+205 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Anecdote` connect `Anecdote` to `TestClient`, `Signification`, `TestClient`, `test_import_pipeline.py`, `TestClient`, `test_public_identifier_absence.py`, `test_landscape.py`, `NormalisedDocument`, `test_translation_readtime.py`, `imports.py`, `test_language_capture.py`, `test_queue.py`, `backend/stories.py`, `proposed_import`, `Framework`, `test_quality_signals.py`, `routers/stories.py`, `queue.py`, `public.py`, `FrameworkCreate`, `routers/patterns.py`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `FrameworkDefinition` connect `FrameworkDefinition` to `ProposeError`, `test_edit_log_wording.py`, `validate_definition`, `NormalisedDocument`, `backend/patterns.py`, `imports.py`, `test_design_linter.py`, `backend/exports.py`, `test_placement_shape_parity.py`, `Anecdote`, `Framework`, `TriadChart`, `barycentric.py`, `queue.py`, `public.py`, `clusters.py`, `edit_semantics.py`, `lint.py`, `get_landscape`, `FrameworkCreate`, `propose.py`, `get_paper_pack`, `routers/patterns.py`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `make_framework()` connect `make_framework` to `test_quality_signals.py`, `test_live_ai.py`, `test_patterns.py`, `test_language_capture.py`, `test_exports.py`, `test_design_linter.py`, `test_queue.py`, `test_landscape.py`, `test_story_browser.py`, `test_signification_provenance.py`, `proposed_import`, `test_translation_readtime.py`, `test_explorer_clusters.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 59 inferred relationships involving `FrameworkDefinition` (e.g. with `CaptureError` and `CaptureSubmission`) actually correct?**
  _`FrameworkDefinition` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `Anecdote` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Anecdote` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `Signification` (e.g. with `CaptureResult` and `FrameworkCreate`) actually correct?**
  _`Signification` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _210 weakly-connected nodes found - possible documentation gaps or missing edges._