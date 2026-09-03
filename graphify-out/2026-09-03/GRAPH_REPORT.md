# Graph Report - TESSA-Sensemaking  (2026-09-03)

## Corpus Check
- 168 files · ~177,060 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2976 nodes · 7109 edges · 139 communities (130 shown, 9 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 486 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `87b76682`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- build_golden_dataset
- TestClient
- Signification
- test_edit_log_wording.py
- test_migrations.py
- TestClient
- test_import_pipeline.py
- TestClient
- request_json
- test_public_identifier_absence.py
- test_stage_gate.py
- package.json
- validate_definition
- test_story_browser.py
- test_landscape.py
- parsers.py
- _run_node
- NormalisedDocument
- backend/patterns.py
- test_signification_provenance.py
- parse
- What You Must Do When Invoked
- test_translation_readtime.py
- backend/landscape.py
- export_brief
- TestClient
- PRD: Narrative Lens — Local Narrative Sense-Making App
- Decisions
- test_explorer_clusters.py
- api.js
- test_capture_draft.py
- Widgets.jsx
- Landscape.jsx
- test_error_surface.py
- test_terrain_maths.py
- clusters.py
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
- test_schema_absence.py
- graphify reference: extra exports and benchmark
- Web Design & Data Visualization
- Anecdote
- backend/exports.py
- edit_semantics.py
- Design System Reference — 2026
- test_health.py
- _FakeAnthropic
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
- models.py
- propose.py
- browse_stories
- Patterns.jsx
- render_paper_pack
- test_empty_states.py
- patterns_fixtures.py
- proposed_import
- Framework
- lint.py
- conftest.py
- routers/landscape.py
- test_original_names.py
- organise.py
- ai_client.py
- make_framework
- test_quality_signals.py
- MonkeyPatch
- backend/quality.py
- test_patterns_golden.py
- translate.py
- test_api_alignment.py
- test_scope_completeness.py
- Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6
- _story
- test_live_ai.py
- imports.py
- make_engine
- backend/stories.py
- CaptureLink
- BarycentricError
- FrameworkCreate
- to_barycentric
- routers/stories.py
- test_capture_links.py
- test_the_list_shows_the_context_a_reader_needs
- quality_css
- session_source
- _Strict
- to_cartesian
- barycentric.py
- normalise
- framework_schema.py
- lint_framework
- errors.py
- from_value_json
- RateLimiter
- TestTokenDecidesEverything
- display_name
- TestKioskMode
- translate
- TestGoldenCentroid
- health

## God Nodes (most connected - your core abstractions)
1. `make_framework()` - 142 edges
2. `FrameworkDefinition` - 140 edges
3. `build_golden_dataset()` - 120 edges
4. `Anecdote` - 102 edges
5. `Signification` - 72 edges
6. `Framework` - 69 edges
7. `get_session()` - 51 edges
8. `ImportJob` - 49 edges
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
- 3-file cycle: `frontend/src/patterns/Landscape.jsx -> frontend/src/patterns/Patterns.jsx -> frontend/src/patterns/SessionMode.jsx -> frontend/src/patterns/Landscape.jsx`

## Communities (139 total, 9 thin omitted)

### Community 0 - "build_golden_dataset"
Cohesion: 0.09
Nodes (54): build_golden_dataset(), TestClient, Create the framework and its twenty stories. Returns the framework., brief(), landscape(), listed(), Session, TestClient (+46 more)

### Community 1 - "TestClient"
Cohesion: 0.19
Nodes (9): _framework(), _link(), TestClient, PRD §6 Phase 4: token lifecycle. §7.6: revoked links close., The heart of §7.6: a taken-down QR poster cannot keep collecting., Hiding the link would hide where its stories came from., A QR pointing at 127.0.0.1 works on the laptop and fails on a phone., TestLinkCreation (+1 more)

### Community 2 - "Signification"
Cohesion: 0.05
Nodes (44): One respondent (or validated AI) placement on one signifier. ``value_json``…, A free-text tag the analyst attaches to a story., Signification, Tag, _framework(), TestClient, Local capture (PRD §6 Phase 3). The tests the PRD names for this phase: wizard…, PRD §9 assumption 7: reflection shows one signifier. (+36 more)

### Community 3 - "test_edit_log_wording.py"
Cohesion: 0.16
Nodes (13): _describe(), described(), fixture, The edit log reads as English, not as a schema path (constraint 7). The log…, A log entry nobody planned for is still a record of a change., The full fixture with one string changed in every kind of place., Every path a real wording fix produces, with what the Studio shows., Nothing falls through to the raw path — the whole surface is covered. (+5 more)

### Community 4 - "test_migrations.py"
Cohesion: 0.20
Nodes (15): Config, alembic_config(), fixture, Alembic migration 001 — up, down, and agreement with the models. Constraint 5…, The CHECK constraint reaches the migrated database, not just the models., The two columns v1.3 added to frameworks reach the database., A migration that only works once is a migration that will strand the app., No drift between the migration chain and ``backend/models.py``. (+7 more)

### Community 5 - "TestClient"
Cohesion: 0.10
Nodes (23): _create_full(), _pack_html(), TestClient, The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar). Two…, PRD §1.2a: the story card carries respondent-group tick boxes., The pack renders the version's current wording, not a cached copy., Constraint 9: the anonymity statement is printed verbatim on the card., Whatever this version says is what the card prints — no substitution. (+15 more)

### Community 6 - "test_import_pipeline.py"
Cohesion: 0.09
Nodes (64): pdf_bytes(), _pdf_escape(), Real files, in memory, one per format Narrative Lens claims to read. Acceptance…, A one-page PDF with each paragraph as its own text run. Written by hand:…, A two-sheet workbook: one of responses, one lookup table to ignore. The…, txt_bytes(), vtt_bytes(), xlsx_bytes() (+56 more)

### Community 7 - "TestClient"
Cohesion: 0.11
Nodes (27): _add_story(), _create(), _definition(), Session, TestClient, The wording-fix vs meaning-change state machine (PRD §6, constraint 13g). This…, Constraint 7: the operator must be able to act on the message., A wording fix patches in place and appends to the edit log. (+19 more)

### Community 8 - "request_json"
Cohesion: 0.11
Nodes (25): Any, Ask for one JSON object of the given shape, or fail in plain English. In mock…, request_json(), live(), BaseModel, fixture, MonkeyPatch, The one AI client, and the four promises constraint 6 makes about it. (+17 more)

### Community 9 - "test_public_identifier_absence.py"
Cohesion: 0.15
Nodes (17): _clear_limits(), _framework(), _link(), fixture, TestClient, Constraint 9 on the remote path (PRD §6 Phase 4: identifier-absence test).…, Sweep every column of every table, not just the ones we expect., Structural guards: not "it doesn't today", but "it has no way to". (+9 more)

### Community 10 - "test_stage_gate.py"
Cohesion: 0.11
Nodes (20): can_advance(), Whether the machine permits ``current → target``., Whether ``target`` can be reached from ``start`` by any number of steps. Used…, reachable(), _job(), parametrize, The stage machine and its 409 gate (constraints 1 and 12). Two levels are…, Constraint 7: a refusal the operator can act on, with no jargon in it. (+12 more)

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
Nodes (49): Every story inside a rectangle of grid cells, and no others. The region drill…, stories_in_region(), _capture(), _landscape(), _panel(), Session, TestClient, The landscape suite: the terrain, its contour twin, the drill, the clusters.… (+41 more)

### Community 15 - "parsers.py"
Cohesion: 0.11
Nodes (29): Block, _blocks_from_text(), _clean_row(), _decode(), _parse_captions(), _parse_csv(), _parse_docx(), _parse_pdf() (+21 more)

### Community 16 - "_run_node"
Cohesion: 0.11
Nodes (14): parametrize, Voice fallback (PRD §6 Phase 4, §7.12, constraint 10). Constraint 10 says voice…, The UI calls stop() on unmount whether or not voice ever started., Stopping on purpose is not a failure and must not show a warning., Constraint 10: voice always paired with typing., Interim results would rewrite a respondent's words as they speak., §7.12: voice fails plain-English with a working fallback., Constraint 7: no jargon a respondent cannot act on. (+6 more)

### Community 17 - "NormalisedDocument"
Cohesion: 0.12
Nodes (46): _balance(), Candidate, confirm(), confirm_narrative(), confirm_tabular(), ConfirmedExtraction, ExtractionError, BaseModel (+38 more)

### Community 18 - "backend/patterns.py"
Cohesion: 0.09
Nodes (59): Dyad, Mcq, A 2D canvas on which the respondent places named chips., A multiple-choice question., Every signifier with its kind, in the order the respondent meets them., A triangle with three named corners; answers are barycentric., A slider between two opposing poles; answers are 0–1., Stones (+51 more)

### Community 19 - "test_signification_provenance.py"
Cohesion: 0.12
Nodes (37): expert_validated_ids(), mixed_dataset(), patterns(), placed(), plotted(), parametrize, TestClient, Whose interpretation a figure is made of (delta §6, constraint 14). Constraint… (+29 more)

### Community 20 - "parse"
Cohesion: 0.07
Nodes (53): AiError, Exception, An AI call that failed in a way the operator needs told about. Carries the PRD…, organise(), Run Stage A over a parsed file and return its proposal. Nothing is written to…, parse(), Read one uploaded file into the normalised shape, or refuse it. Refusals are…, csv_bytes() (+45 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "test_translation_readtime.py"
Cohesion: 0.06
Nodes (60): capture(), code_of(), MonkeyPatch, parametrize, Path, Session, TestClient, Read-time translation, display-only (delta §6, constraint 15). The second half… (+52 more)

### Community 23 - "backend/landscape.py"
Cohesion: 0.14
Nodes (22): _axes(), Cell, _cell_index(), Landscape, LandscapePoint, _local_maxima(), _nearest_corner(), Peak (+14 more)

### Community 24 - "export_brief"
Cohesion: 0.11
Nodes (31): only_validated(), Narrow a query to the stories a person has actually approved. Every read that…, export_brief(), export_csv(), export_heard(), Depends, get, Query (+23 more)

### Community 25 - "TestClient"
Cohesion: 0.14
Nodes (9): TestClient, List, create and fetch frameworks (PRD §4)., A new framework starts valid and empty, ready to fill in., The Studio shows these live while the operator edits., Constraint 7: plain English, with something to do about it., PRD §5.1: version history sidebar shows versions with story counts., TestCreate, TestFetch (+1 more)

### Community 26 - "PRD: Narrative Lens — Local Narrative Sense-Making App"
Cohesion: 0.10
Nodes (19): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 11. Changelog v1.2 → v1.3, 1. Scope, 2. Binding constraints (restate these in every session), 3. Data model (SQLite, via SQLAlchemy + Alembic), 4. API contract (FastAPI, all JSON), 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages). (+11 more)

### Community 27 - "Decisions"
Cohesion: 0.06
Nodes (31): Completeness pass, Decisions, Delta phase A, Delta phase B, Delta phase C, Delta phase D, Delta phase E, Fixed (+23 more)

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
Cohesion: 0.19
Nodes (18): Cluster, ClusterAssignment, ClusterSet, Dimension, dimensions_of(), explorer(), ExplorerPoint, ExplorerSet (+10 more)

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
Nodes (58): check(), lint_css(), panel_source(), MonkeyPatch, Session, TestClient, The framework design linter (delta §6, phase C). This is the one AI call in…, The shape is enforced on the mock exactly as on a live reply. ``request_json``… (+50 more)

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

### Community 49 - "test_schema_absence.py"
Cohesion: 0.11
Nodes (23): _columns(), parametrize, Constraint 9 — respondent anonymity is engineered, not promised. These tests…, No IP, user agent, fingerprint, device/session id or email anywhere., No name-family column on a table whose rows are linked to a respondent., Catch identifiers this test did not anticipate, e.g. ``manager_name``.…, Constraint 9: respondent time is hour-rounded, so no exact clock exists.…, The only writer of ``created_at_hour`` carries no sub-hour information. (+15 more)

### Community 50 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 51 - "Web Design & Data Visualization"
Cohesion: 0.22
Nodes (8): Data visualization, Output, Step 1: Frame the brief, Step 2: Design plan before code, Step 3: B2B or B2C playbook, Step 4: Build to the quality floor (non-negotiable, never announced), Step 5: Critique pass, Web Design & Data Visualization

### Community 52 - "Anecdote"
Cohesion: 0.09
Nodes (43): CaptureError, _check_dyad(), _check_mcq(), _check_stones(), _check_triad(), ValueError, Validating a submitted capture against the framework it answers (PRD §4). A…, Triad weights: one per corner, non-negative, summing to 1.0. (+35 more)

### Community 53 - "backend/exports.py"
Cohesion: 0.10
Nodes (34): _category_finding(), dataset_csv(), _dyad_finding(), findings(), headline(), _headlines(), _heard_category(), _interpretation_section() (+26 more)

### Community 54 - "edit_semantics.py"
Cohesion: 0.15
Nodes (17): build_edit_log_entries(), diff_text_fields(), is_structural_change(), label_renames(), Any, datetime, The wording-fix vs meaning-change guardrail (PRD §1.1, constraint 13g). While a…, ``{signifier_id: {old_label: new_label}}`` for every renamed label. Only labels… (+9 more)

### Community 55 - "Design System Reference — 2026"
Cohesion: 0.29
Nodes (6): 2026 trend catalog — pick deliberately, one direction per project, Banned defaults (the "AI look"), Copy rules, Design System Reference — 2026, Layout heuristics, Tokens

### Community 56 - "test_health.py"
Cohesion: 0.29
Nodes (5): The one endpoint Phase 1 ships., PRD §4 budgets 200ms for non-AI endpoints; health should be far under., Guard against building ahead of the phase plan (PRD §6). Enumerated from the…, test_health_is_fast_enough_for_the_200ms_budget(), test_no_routes_beyond_the_current_phase()

### Community 57 - "_FakeAnthropic"
Cohesion: 0.22
Nodes (6): _Block, _FakeAnthropic, _FakeMessages, Any, Stands in for ``anthropic.Anthropic`` and records what it was asked., _Response

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
Cohesion: 0.17
Nodes (11): How to resume, Narrative Lens — Latest, Next step, Running it yourself, The completeness pass, after Phase 9, The meaningfulness delta — phase A is done, The meaningfulness delta — phase B is done, The meaningfulness delta — phase C is done (+3 more)

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

### Community 82 - "models.py"
Cohesion: 0.07
Nodes (49): CaptureSubmission, LocalCaptureSubmission, PublicCaptureSubmission, BaseModel, A capture arriving through a capture link. ``framework_id`` is not accepted:…, A whole capture: one story plus its placements. Note what is *not* here: no id,…, A capture from the operator's own machine: admin, paper entry, or kiosk. Only…, only_pending() (+41 more)

### Community 83 - "propose.py"
Cohesion: 0.11
Nodes (25): _check_batch(), describe_signifiers(), _mock_batch(), _mock_confidence(), _mock_value(), Placement, _prompt(), ProposalBatch (+17 more)

### Community 84 - "browse_stories"
Cohesion: 0.13
Nodes (22): browse_stories(), get_translation(), Depends, ge, get, put, Query, Session (+14 more)

### Community 85 - "Patterns.jsx"
Cohesion: 0.10
Nodes (19): BarChart(), DyadChart(), StonesChart(), LandscapeView(), FILTERS, lineageOf(), optionsFrom(), PatternsTab() (+11 more)

### Community 86 - "render_paper_pack"
Cohesion: 0.33
Nodes (6): _facilitator_sheet(), The A4 story card: prompt, ruled space, groups, anonymity line., Running instructions, materials, and the reconciliation grid., Render the whole pack as one self-contained, printable HTML page., render_paper_pack(), _story_card()

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
Cohesion: 0.21
Nodes (23): Framework, A version of the question set respondents see. ``parent_framework_id`` links…, _anecdote_count(), _apply_meaning_change(), _apply_wording_fix(), create_framework(), FrameworkOut, get_framework() (+15 more)

### Community 91 - "lint.py"
Cohesion: 0.19
Nodes (11): lint(), lint_prompt(), LintReport, _mock_reply(), Any, BaseModel, The framework design linter (delta §4a, item 3). The one AI call in this app…, Everything the model had to say about one question set's design. (+3 more)

### Community 92 - "conftest.py"
Cohesion: 0.22
Nodes (13): client(), db_path(), db_url(), engine(), fixture, Path, TestClient, Shared fixtures. Every test runs against a throwaway SQLite file, never the… (+5 more)

### Community 93 - "routers/landscape.py"
Cohesion: 0.11
Nodes (30): compute(), One triad's landscape, grid and all. Takes the already-aggregated triad chart…, Placements inside one triangle, as points on the unit triangle., The same chart as :func:`one_triad`, from rows rather than from objects.…, triad_from_answers(), TriadChart, get_clusters(), get_explorer() (+22 more)

### Community 94 - "test_original_names.py"
Cohesion: 0.25
Nodes (7): _files(), parametrize, Path, Original names and materials only (constraint 8, acceptance criterion 15). The…, Criterion 15 allows one attribution. One, not none — it is owed. Counted in…, test_no_reserved_name_appears_in_the_app(), test_the_readme_carries_exactly_one_attribution()

### Community 95 - "organise.py"
Cohesion: 0.13
Nodes (19): _check_narrative(), _check_tabular(), _hinted_column(), _mock_narrative(), _mock_tabular(), _narrative_prompt(), NarrativeOrganisation, OrganiseError (+11 more)

### Community 96 - "ai_client.py"
Cohesion: 0.20
Nodes (10): _fenced_json(), mock_enabled(), _parse(), The one AI client (constraint 6). Every call Narrative Lens makes to a language…, Parse one reply strictly, or raise the reason it could not be parsed., Whether this process runs with mocks instead of the network. Read on every call…, Return *raw* with one surrounding markdown fence removed, if present. Strict…, Payload (+2 more)

### Community 97 - "make_framework"
Cohesion: 0.14
Nodes (33): make_framework(), capture(), link_for(), parametrize, TestClient, The name a storyteller gives their own story (delta §6, items 2 and 5). A…, No name given is the ordinary case, and it must read as a story anyway., A skipped field submits as blank; blank is no name, not a name of "". Otherwise… (+25 more)

### Community 98 - "test_quality_signals.py"
Cohesion: 0.08
Nodes (56): capture(), patterns_jsx(), MonkeyPatch, Session, TestClient, quality(), quality_jsx(), Data-quality signals: centre-parking and skip rate (delta §6, phase B). The… (+48 more)

### Community 99 - "MonkeyPatch"
Cohesion: 0.24
Nodes (11): fake_anthropic(), fixture, MonkeyPatch, TestClient, Acceptance criterion 12: offline is a working state, not a broken one., The operator loses the click, not the file., Install a fake ``anthropic`` package and turn mock mode off., test_a_file_waiting_to_be_analysed_survives_the_outage() (+3 more)

### Community 100 - "backend/quality.py"
Cohesion: 0.16
Nodes (17): distance_from_centre(), point_from_value_json(), How far a placement sits from the middle of the triangle. Plain Euclidean…, A stored answer straight to its point in the triangle. Exactly…, centre_parked_count(), BaseModel, QualityReport, _rate() (+9 more)

### Community 101 - "test_patterns_golden.py"
Cohesion: 0.12
Nodes (23): produce(), produce_participant(), TestClient, The pattern golden — byte-identical from Phase 7 onward (PRD §6). Twenty…, Determinism, checked against itself rather than against the file. If…, A golden that missed a kind would pin three quarters of the maths., Twenty stories, every one of them answered on every question., The new default, pinned the same way the old view has always been. (+15 more)

### Community 102 - "translate.py"
Cohesion: 0.20
Nodes (15): A cached read-time translation of one story into one language. Constraint 15 in…, Translation, cached(), BaseModel, Session, Read-time translation, display-only (delta §4a, constraint 15). The second half…, The cached translation, if this story has been read in this language., Cache one translation, replacing any earlier one for the same pair. Replaced… (+7 more)

### Community 103 - "test_api_alignment.py"
Cohesion: 0.31
Nodes (9): _frontend_paths(), The frontend and the backend agree about what exists (contract alignment).…, Every ``/api/...`` address api.js can build, with its parameters blanked., An endpoint nothing calls is either dead or half-finished., A guard on the guard: an empty comparison would pass both tests above., _server_paths(), test_every_address_the_frontend_calls_exists_on_the_server(), test_every_endpoint_is_reached_by_something() (+1 more)

### Community 104 - "test_scope_completeness.py"
Cohesion: 0.16
Nodes (13): TestClient, Every item of PRD §1's scope is actually reachable in the app. This file exists…, One assertion per numbered item of §1 that the API is responsible for., §5.4: "Landscape (default) · Supporting charts · 3D Explorer · Story browser"., The four verbs §1.6 lists, each with something in the code doing it., Dataset CSV · contour PNG · supporting-charts PNG · brief · what we heard., Acceptance criterion 1 ends "QR on home", and the home screen is the Studio., _source() (+5 more)

### Community 105 - "Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6"
Cohesion: 0.11
Nodes (17): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 1. Scope, 2. Binding constraints restated, 3. Data model changes, 4. API contract, 4a. New AI calls — both through `ai_client.request_json`, both mocked, 5. Frontend changes (+9 more)

### Community 106 - "_story"
Cohesion: 0.18
Nodes (7): Constraint 3: provenance on every record, whatever route it came by., Constraint 3: input_method distinguishes voice from typing., PRD §4: public endpoints are rate-limited — per token, never per person., The limit is per link, so one workshop cannot shut down another., _story(), TestLinkProvenance, TestRateLimiting

### Community 107 - "test_live_ai.py"
Cohesion: 0.14
Nodes (24): _live_text(), One live call to api.anthropic.com. The only network in the app. Imported…, ModuleType, APIConnectionError, APIStatusError, _calls(), _last(), Exception (+16 more)

### Community 108 - "imports.py"
Cohesion: 0.10
Nodes (46): get_session(), Session, FastAPI dependency yielding a session that always closes., conflict(), Something outside the app misbehaved — currently only the AI service., upstream(), ImportJob, One uploaded file moving through the two-stage ingestion machine. (+38 more)

### Community 109 - "make_engine"
Cohesion: 0.18
Nodes (14): Alembic environment. The database URL comes from…, Emit SQL to a script without a live connection., Run migrations against a live connection., _run(), run_migrations_offline(), run_migrations_online(), _url(), _connect_args() (+6 more)

### Community 110 - "backend/stories.py"
Cohesion: 0.18
Nodes (14): answer_counts(), known_tags(), marks_for(), Session, The story browser's read model (PRD §1.6). The landscape says where stories…, Star and tags per story, in one query rather than one per row., How many questions each story answered., The full-text rule: every word must appear, in the story or either title.… (+6 more)

### Community 112 - "CaptureLink"
Cohesion: 0.15
Nodes (27): CaptureLink, A token-gated capture URL pointing at one exact framework version., qr_png_bytes(), QR codes for capture links (PRD §4, §1.8). A QR is how a phone gets to the…, Return a PNG of ``payload`` as QR, as raw bytes. Error correction is set to M…, capture_link_qr(), capture_url(), CaptureLinkCreate (+19 more)

### Community 113 - "BarycentricError"
Cohesion: 0.17
Nodes (10): BarycentricError, ValueError, Raised when a placement cannot be read as a triad answer., parametrize, Each corner weight of 1.0 lands exactly on that corner., Two-way ties sit halfway along an edge, with the third corner at zero., Fixed off-centre answers — the ones a real respondent actually gives., TestGoldenAsymmetricPlacements (+2 more)

### Community 114 - "FrameworkCreate"
Cohesion: 0.23
Nodes (12): Language, BaseModel, One language a framework may offer, named twice., LintFinding, One thing worth a second look, and what to try instead., FrameworkCreate, FrameworkUpdate, LintOut (+4 more)

### Community 115 - "to_barycentric"
Cohesion: 0.17
Nodes (13): Convert a point in the triangle into three corner weights summing to 1.0. The…, to_barycentric(), Weights survive a there-and-back trip without drifting., Ten trips land where one trip landed — no accumulating drift., TestRoundTrip, The widget's triad maths must agree with the server's, exactly.…, The same weights must land on the same point in both languages., The same point must read back as the same weights in both languages. (+5 more)

### Community 116 - "routers/stories.py"
Cohesion: 0.14
Nodes (13): offered(), The language a story was told in (delta §3, constraint 15). Constraint 15 says…, Whether a tag is shaped like a language tag at all., The languages a framework offers, in the order it lists them. An unknown but…, well_formed(), MarksIn, BaseModel, The story browser (PRD §1.6, §5.4). Two endpoints. One lists the stories in the… (+5 more)

### Community 118 - "test_capture_links.py"
Cohesion: 0.18
Nodes (9): Rate limiting for the public capture endpoints (PRD §4). The public endpoints…, Clear every counter. Tests call this between cases., reset_all(), _clear_limits(), fixture, Capture links and the public capture path (PRD §6 Phase 4). The tests the PRD…, Rate limiters are process-wide; keep cases independent., A QR nobody can scan is a poster with a picture on it. (+1 more)

### Community 119 - "test_the_list_shows_the_context_a_reader_needs"
Cohesion: 0.67
Nodes (3): parametrize, A sentence about "this landscape" is worthless without the landscape., test_the_list_shows_the_context_a_reader_needs()

### Community 120 - "quality_css"
Cohesion: 0.25
Nodes (8): quality_css(), Just the panel's own declarations, with the prose taken out. Comments are…, Constraint 13c, and the reason this panel can be read in greyscale. Every…, Quiet weight (13a). The landscape is the one bold element on this tab. Nothing…, Constraint 10: a phone at 375px must not be pushed sideways by a table., test_the_panel_encodes_nothing_in_colour(), test_the_panel_never_shouts(), test_the_wide_table_scrolls_inside_itself()

### Community 121 - "session_source"
Cohesion: 0.22
Nodes (9): Delta §5: "the landscape at full screen with controls hidden". Checked by…, Delta §6 names this. A view you cannot leave strands the facilitator., The question a facilitator will silently be asking, answered on screen., The filters come from the screen, not from a field somebody fills in., session_source(), test_the_projector_view_hides_the_controls(), test_the_projector_view_is_keyboard_escapable(), test_the_projector_view_says_recording_changes_nothing() (+1 more)

### Community 122 - "_Strict"
Cohesion: 0.11
Nodes (11): CaptureSettings, BaseModel, Every non-signifier string the respondent reads, plus capture toggles., Well-formed BCP-47, and each offered once. Shape only — no registry lookup. An…, What the welcome screen offers: the configured list, or English., Reject unknown keys so a typo in the Studio surfaces as an error., One axis of the stones canvas, named at both ends., StonesAxis (+3 more)

### Community 123 - "to_cartesian"
Cohesion: 0.23
Nodes (7): _placed(), The conversion itself, on weights already known to be usable. Kept apart from…, Convert three corner weights into a point inside the triangle. >>>…, to_cartesian(), TestRejections, The centroid and "no lean at all" have to be the same point. To the precision…, test_the_centre_is_where_equal_weights_land()

### Community 124 - "barycentric.py"
Cohesion: 0.27
Nodes (8): is_inside(), Triad barycentric maths. A triad answer is a point inside an equilateral…, Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`., Whether the weights describe a point in or on the triangle., Reject anything that is not a usable triad answer., sums_to_one(), _validated(), Golden maths for triad placements. These values are the contract between the…

### Community 125 - "normalise"
Cohesion: 0.24
Nodes (6): normalise(), Clamp to the triangle and rescale so the three weights sum to exactly 1.0. A…, PRD §3: triad barycentric sums to 1.0., Even awkward thirds land on a sum of exactly 1.0 after rounding., An imported point a hair outside the triangle is pulled to its edge., TestSumsToOne

### Community 126 - "framework_schema.py"
Cohesion: 0.07
Nodes (42): Database engine and session plumbing (constraint 4: SQLite + local files)., Validation for ``frameworks.definition_json`` (PRD §3 and §5). Every…, mount_frontend(), FastAPI application. Endpoints arrive with the phase that needs them, per PRD…, Serve ``frontend/dist`` if it has been built. Returns whether anything was…, Export endpoints (PRD §4, §1.7). Both exports read through the same scope as…, list_interpretations(), get (+34 more)

### Community 127 - "lint_framework"
Cohesion: 0.18
Nodes (12): get_paper_pack(), known_languages(), lint_framework(), list_frameworks(), Depends, get, post, The languages the Studio offers, named in English and in their own script. A… (+4 more)

### Community 128 - "errors.py"
Cohesion: 0.24
Nodes (8): AppError, bad_request(), not_found(), The error shape from PRD §4. ``{"error": {"code": ..., "message": plain-English…, An error the operator is meant to read and act on., The story ids a caller asked for by name, or None for all of them. One parser…, selected_ids(), HTTPException

### Community 129 - "from_value_json"
Cohesion: 0.31
Nodes (5): from_value_json(), Read a stored ``significations.value_json`` into ordered weights., Reading a stored signification back into ordered weights., Dict ordering must never decide which corner is which., TestFromValueJson

### Community 130 - "RateLimiter"
Cohesion: 0.22
Nodes (5): RateLimiter, A sliding-window counter keyed by an opaque string. Deliberately simple and in-…, Record a hit and report whether it is within the limit., Forget counters. Used by tests and when a link is revoked., How many hits are still allowed in the current window.

### Community 132 - "TestTokenDecidesEverything"
Cohesion: 0.22
Nodes (5): The token, not the body, chooses the version and the entry mode., A later meaning change must not retarget an existing link., The browser may not choose which question set it answered., A respondent's browser is told the questions and nothing more., TestTokenDecidesEverything

### Community 133 - "display_name"
Cohesion: 0.25
Nodes (8): display_name(), What to show for a story's language. A code we know gets its English name. A…, language_label(), The language written the way a reader reads it (constraint 15). One definition,…, The named guarantee of delta §6, at the one place it is decided., More use to a reader than nothing, and better than a wrong guess., test_a_tag_the_app_does_not_know_shows_itself(), test_an_unrecorded_language_reads_as_unknown_not_as_english()

### Community 134 - "TestKioskMode"
Cohesion: 0.25
Nodes (4): PRD §1.2: three entry modes share one wizard., Only a real token may produce a ``link`` record., Constraint 1: AI-derived content must not pose as first-hand., TestKioskMode

### Community 135 - "translate"
Cohesion: 0.29
Nodes (7): _mock_reply(), Any, The practice reply, read once from the file that holds it., What the model is given: the story as told, and where to carry it to. The…, Ask for one translation. Raises :class:`~backend.ai_client.AiError`.…, translate(), translate_prompt()

### Community 138 - "health"
Cohesion: 0.67
Nodes (3): health(), get, Liveness probe. The launcher opens this while the app is starting.

## Knowledge Gaps
- **200 isolated node(s):** `name`, `version`, `description`, `dev`, `build` (+195 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Anecdote` connect `Anecdote` to `TestClient`, `Signification`, `TestTokenDecidesEverything`, `TestClient`, `TestKioskMode`, `TestClient`, `test_import_pipeline.py`, `test_public_identifier_absence.py`, `validate_definition`, `test_landscape.py`, `NormalisedDocument`, `test_translation_readtime.py`, `test_language_capture.py`, `test_queue.py`, `test_schema_absence.py`, `models.py`, `browse_stories`, `proposed_import`, `Framework`, `test_quality_signals.py`, `translate.py`, `_story`, `imports.py`, `backend/stories.py`, `CaptureLink`, `FrameworkCreate`, `routers/stories.py`, `test_capture_links.py`, `framework_schema.py`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Why does `FrameworkDefinition` connect `FrameworkDefinition` to `test_edit_log_wording.py`, `validate_definition`, `NormalisedDocument`, `backend/patterns.py`, `clusters.py`, `test_design_linter.py`, `Anecdote`, `backend/exports.py`, `edit_semantics.py`, `test_placement_shape_parity.py`, `models.py`, `propose.py`, `render_paper_pack`, `Framework`, `lint.py`, `routers/landscape.py`, `backend/quality.py`, `imports.py`, `FrameworkCreate`, `_Strict`, `framework_schema.py`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `make_framework()` connect `make_framework` to `test_quality_signals.py`, `MonkeyPatch`, `test_patterns.py`, `test_language_capture.py`, `test_exports.py`, `test_design_linter.py`, `test_live_ai.py`, `test_queue.py`, `test_landscape.py`, `test_story_browser.py`, `test_signification_provenance.py`, `test_translation_readtime.py`, `proposed_import`, `test_explorer_clusters.py`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 59 inferred relationships involving `FrameworkDefinition` (e.g. with `CaptureError` and `CaptureSubmission`) actually correct?**
  _`FrameworkDefinition` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `Anecdote` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Anecdote` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `Signification` (e.g. with `CaptureResult` and `FrameworkCreate`) actually correct?**
  _`Signification` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _200 weakly-connected nodes found - possible documentation gaps or missing edges._