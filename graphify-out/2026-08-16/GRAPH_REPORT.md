# Graph Report - TESSA-Sensemaking  (2026-08-16)

## Corpus Check
- 120 files · ~100,082 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1910 nodes · 4628 edges · 102 communities (88 shown, 14 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 432 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4a0c023a`
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
- validate_definition
- NormalisedDocument
- test_stage_gate.py
- parsers.py
- _run_node
- NarrativeSegment
- backend/patterns.py
- CaptureLink
- parse
- What You Must Do When Invoked
- Signification
- test_organise_stage_a.py
- public.py
- TestClient
- PRD: Narrative Lens — Local Narrative Sense-Making App
- Phases
- CaptureError
- App.jsx
- test_capture_draft.py
- Widgets.jsx
- test_schema_absence.py
- paper_pack.py
- ConfirmationView
- Anecdote
- test_patterns.py
- StonesAxis
- ingest_fixtures.py
- build_golden_dataset
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
- SubmittedSignification
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
- export_brief
- Patterns.jsx
- .estimated_minutes
- ai_client.py
- .exceeds_screen_warning
- .signifier_count
- _live_text
- AiError
- env.py
- RateLimiter
- _calls
- xlsx_bytes
- patterns_fixtures.py
- _FakeAnthropic
- field_validator
- chunks
- public_base_url
- .signifier_ids_must_be_unique

## God Nodes (most connected - your core abstractions)
1. `FrameworkDefinition` - 109 edges
2. `Anecdote` - 98 edges
3. `Signification` - 64 edges
4. `Framework` - 60 edges
5. `ImportJob` - 49 edges
6. `parse()` - 41 edges
7. `NormalisedDocument` - 38 edges
8. `_framework()` - 37 edges
9. `get_session()` - 36 edges
10. `make_framework()` - 36 edges

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
- None detected.

## Communities (102 total, 14 thin omitted)

### Community 0 - "BarycentricError"
Cohesion: 0.05
Nodes (47): BarycentricError, from_value_json(), is_inside(), normalise(), ValueError, Triad barycentric maths. A triad answer is a point inside an equilateral…, Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`., Whether the weights describe a point in or on the triangle. (+39 more)

### Community 1 - "TestClient"
Cohesion: 0.08
Nodes (31): qr_png_bytes(), QR codes for capture links (PRD §4, §1.8). A QR is how a phone gets to the…, Return a PNG of ``payload`` as QR, as raw bytes. Error correction is set to M…, _framework(), _link(), TestClient, Capture links and the public capture path (PRD §6 Phase 4). The tests the PRD…, PRD §6 Phase 4: token lifecycle. §7.6: revoked links close. (+23 more)

### Community 2 - "TestClient"
Cohesion: 0.09
Nodes (24): _framework(), TestClient, Local capture (PRD §6 Phase 3). The tests the PRD names for this phase: wizard…, PRD §9 assumption 7: reflection shows one signifier., Skipping every question is allowed; the story is the point., Constraint 3: provenance on every record., PRD §6 Phase 3: batch entry writes paper provenance., Constraint 9, at the moment a story is actually written. (+16 more)

### Community 3 - "Framework"
Cohesion: 0.12
Nodes (38): is_structural_change(), Whether the edit changes the framework's shape rather than its words., Framework, A version of the question set respondents see. ``parent_framework_id`` links…, _anecdote_count(), _apply_meaning_change(), _apply_wording_fix(), create_framework() (+30 more)

### Community 4 - "make_engine"
Cohesion: 0.06
Nodes (46): _connect_args(), make_engine(), SQLite needs ``check_same_thread=False`` to serve requests from a pool., Build an engine, enabling SQLite foreign-key enforcement. SQLite ignores…, Config, Engine, client(), db_path() (+38 more)

### Community 5 - "TestClient"
Cohesion: 0.10
Nodes (23): _create_full(), _pack_html(), TestClient, The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar). Two…, PRD §1.2a: the story card carries respondent-group tick boxes., The pack renders the version's current wording, not a cached copy., Constraint 9: the anonymity statement is printed verbatim on the card., Whatever this version says is what the card prints — no substitution. (+15 more)

### Community 6 - "test_import_pipeline.py"
Cohesion: 0.15
Nodes (46): txt_bytes(), _confirm(), _confirmation_body(), _organise(), parametrize, Session, TestClient, The staged import machine end to end, over HTTP, with zero network. Acceptance… (+38 more)

### Community 7 - "_create"
Cohesion: 0.14
Nodes (23): _add_story(), _create(), _definition(), Session, TestClient, The wording-fix vs meaning-change state machine (PRD §6, constraint 13g). This…, Constraint 7: the operator must be able to act on the message., A wording fix patches in place and appends to the edit log. (+15 more)

### Community 8 - "request_json"
Cohesion: 0.11
Nodes (25): Any, Ask for one JSON object of the given shape, or fail in plain English. In mock…, request_json(), live(), BaseModel, fixture, MonkeyPatch, The one AI client, and the four promises constraint 6 makes about it. (+17 more)

### Community 9 - "test_public_identifier_absence.py"
Cohesion: 0.12
Nodes (22): Clear every counter. Tests call this between cases., reset_all(), _clear_limits(), fixture, Rate limiters are process-wide; keep cases independent., _clear_limits(), _framework(), _link() (+14 more)

### Community 10 - "imports.py"
Cohesion: 0.11
Nodes (42): Something outside the app misbehaved — currently only the AI service., upstream(), ImportJob, One uploaded file moving through the two-stage ingestion machine., confirm_mapping(), create_import(), _detail(), get_import() (+34 more)

### Community 11 - "package.json"
Cohesion: 0.06
Nodes (30): eslint, @eslint/js, eslint-plugin-react, eslint-plugin-react-hooks, dependencies, react, react-dom, description (+22 more)

### Community 12 - "validate_definition"
Cohesion: 0.06
Nodes (21): default_definition(), Parse and validate a raw ``definition_json`` payload., A minimal, valid definition — what a brand-new framework starts from., validate_definition(), Validation of ``definition_json`` and the anonymity statement it carries., Significations key on the id alone, so one namespace covers all kinds., A typo in the Studio should fail loudly, not vanish silently., Constraint 10: ≤4 minutes typical. (+13 more)

### Community 13 - "NormalisedDocument"
Cohesion: 0.12
Nodes (31): _check_narrative(), _check_tabular(), _hinted_column(), _mock_narrative(), _mock_tabular(), _narrative_prompt(), NarrativeOrganisation, organise() (+23 more)

### Community 14 - "test_stage_gate.py"
Cohesion: 0.12
Nodes (18): Whether ``target`` can be reached from ``start`` by any number of steps. Used…, reachable(), _job(), parametrize, The stage machine and its 409 gate (constraints 1 and 12). Two levels are…, Constraint 7: a refusal the operator can act on, with no jargon in it., ``failed`` is terminal, so a blinking network must not land there., A stage with no row would be a dead end nothing could describe. (+10 more)

### Community 15 - "parsers.py"
Cohesion: 0.14
Nodes (23): Block, _blocks_from_text(), _clean_row(), _decode(), _parse_captions(), _parse_csv(), _parse_docx(), _parse_pdf() (+15 more)

### Community 16 - "_run_node"
Cohesion: 0.11
Nodes (14): parametrize, Voice fallback (PRD §6 Phase 4, §7.12, constraint 10). Constraint 10 says voice…, The UI calls stop() on unmount whether or not voice ever started., Stopping on purpose is not a failure and must not show a warning., Constraint 10: voice always paired with typing., Interim results would rewrite a respondent's words as they speak., §7.12: voice fails plain-English with a working fallback., Constraint 7: no jargon a respondent cannot act on. (+6 more)

### Community 17 - "NarrativeSegment"
Cohesion: 0.19
Nodes (25): _balance(), Candidate, confirm(), confirm_narrative(), confirm_tabular(), ConfirmedExtraction, ExtractionError, BaseModel (+17 more)

### Community 18 - "backend/patterns.py"
Cohesion: 0.13
Nodes (39): CaptureSettings, Dyad, Mcq, BaseModel, Validation for ``frameworks.definition_json`` (PRD §3 and §5). Every…, A 2D canvas on which the respondent places named chips., A multiple-choice question., Every non-signifier string the respondent reads, plus capture toggles. (+31 more)

### Community 19 - "CaptureLink"
Cohesion: 0.16
Nodes (25): CaptureLink, A token-gated capture URL pointing at one exact framework version., Rate limiting for the public capture endpoints (PRD §4). The public endpoints…, capture_link_qr(), capture_url(), CaptureLinkCreate, CaptureLinkOut, create_capture_link() (+17 more)

### Community 20 - "parse"
Cohesion: 0.11
Nodes (28): parse(), Read one uploaded file into the normalised shape, or refuse it. Refusals are…, pptx_bytes(), test_prose_segments_carry_the_locator_they_came_from(), parametrize, Every format PRD §1.3 promises, read from a real file of that format., PRD §1.3 lists nine extensions. All nine are readable, nothing else is., The reverse map the API uses for jobs whose extension is long gone. (+20 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "Signification"
Cohesion: 0.12
Nodes (19): One respondent (or validated AI) placement on one signifier. ``value_json``…, A free-text tag the analyst attaches to a story., Signification, Tag, _anecdote(), _framework(), parametrize, CRUD across the six tables of PRD §3, plus the vocabularies they enforce. (+11 more)

### Community 23 - "test_organise_stage_a.py"
Cohesion: 0.23
Nodes (16): csv_bytes(), Any, MonkeyPatch, TestClient, Stage A: what it proposes, and what it is not allowed to get away with. Stage A…, Constraint 4 and 7: offline is a normal state, not a broken one. The file stays…, Make Stage A's next answer whatever the test says it is., _reply() (+8 more)

### Community 24 - "public.py"
Cohesion: 0.09
Nodes (36): AppError, bad_request(), conflict(), not_found(), The error shape from PRD §4. ``{"error": {"code": ..., "message": plain-English…, An error the operator is meant to read and act on., _auto_title(), CaptureResult (+28 more)

### Community 25 - "TestClient"
Cohesion: 0.14
Nodes (9): TestClient, List, create and fetch frameworks (PRD §4)., A new framework starts valid and empty, ready to fill in., The Studio shows these live while the operator edits., Constraint 7: plain English, with something to do about it., PRD §5.1: version history sidebar shows versions with story counts., TestCreate, TestFetch (+1 more)

### Community 26 - "PRD: Narrative Lens — Local Narrative Sense-Making App"
Cohesion: 0.10
Nodes (19): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 11. Changelog v1.2 → v1.3, 1. Scope, 2. Binding constraints (restate these in every session), 3. Data model (SQLite, via SQLAlchemy + Alembic), 4. API contract (FastAPI, all JSON), 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages). (+11 more)

### Community 27 - "Phases"
Cohesion: 0.09
Nodes (21): Decisions, Fixed, Narrative Lens — Progress, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5 (+13 more)

### Community 28 - "CaptureError"
Cohesion: 0.12
Nodes (23): CaptureError, CaptureSubmission, _check_dyad(), _check_mcq(), _check_stones(), _check_triad(), LocalCaptureSubmission, PublicCaptureSubmission (+15 more)

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
Cohesion: 0.12
Nodes (21): _columns(), parametrize, Constraint 9 — respondent anonymity is engineered, not promised. These tests…, Constraint 9: respondent time is hour-rounded, so no exact clock exists.…, The only writer of ``created_at_hour`` carries no sub-hour information., 13:59 must land on 13:00, never 14:00 — truncation, not rounding., A row written through the ORM gets an hour-rounded stamp automatically., The rules hold against the real database, not just the model metadata. (+13 more)

### Community 33 - "paper_pack.py"
Cohesion: 0.16
Nodes (17): _facilitator_sheet(), _mcq_options(), The printable paper pack (PRD §1.2, §5b print grammar). One HTML page the…, A square canvas with both axes named at each end., Tick boxes, one per option, big enough to mark with a pen., One A4 landscape sheet for one signifier., The A4 story card: prompt, ruled space, groups, anonymity line., Running instructions, materials, and the reconciliation grid. (+9 more)

### Community 34 - "ConfirmationView"
Cohesion: 0.13
Nodes (20): classify(), ParseError, Exception, Return ``(file_type, file_class)`` for a filename, or refuse it., A file that could not be read, phrased for the operator., ProposeError, Exception, Stage B produced something that does not fit the framework. (+12 more)

### Community 35 - "Anecdote"
Cohesion: 0.26
Nodes (11): Anecdote, One story, bound to the exact framework version it was told against.…, aggregate(), _bars(), CategoryChart, _demographics(), _mcq_chart(), Bars in drawn order: biggest first, ties broken alphabetically. §5b requires… (+3 more)

### Community 36 - "test_patterns.py"
Cohesion: 0.12
Nodes (38): _capture(), _patterns(), TestClient, The patterns endpoint: what it counts, what it sorts, what it refuses. Three…, The no-bypass promise, applied to what the operator actually sees., A meaning change: version n+1, old stories left on the old wording., PRD §4: no silent mixing. A v1 answer is not an answer to v2., §5.4: any view spanning versions must be able to say so on screen. (+30 more)

### Community 37 - "StonesAxis"
Cohesion: 0.40
Nodes (3): One axis of the stones canvas, named at both ends., StonesAxis, model_validator

### Community 38 - "ingest_fixtures.py"
Cohesion: 0.22
Nodes (7): docx_bytes(), pdf_bytes(), _pdf_escape(), Real files, in memory, one per format Narrative Lens claims to read. Acceptance…, A one-page PDF with each paragraph as its own text run. Written by hand:…, vtt_bytes(), test_segments_found_counts_what_stage_a_believes_it_found()

### Community 39 - "build_golden_dataset"
Cohesion: 0.14
Nodes (35): build_golden_dataset(), TestClient, Create the framework and its twenty stories. Returns the framework., _brief(), _csv(), TestClient, The CSV and the Pattern Brief. The CSV is tested as a file a person will open…, The case the provenance column exists for. (+27 more)

### Community 40 - "voice.js"
Cohesion: 0.28
Nodes (11): appendDictation(), getRecognitionClass(), isVoiceSupported(), startDictation(), VOICE_DENIED, VOICE_FAILED, VOICE_NETWORK, VOICE_NO_SPEECH (+3 more)

### Community 41 - "ImportTab.jsx"
Cohesion: 0.18
Nodes (4): ImportTab(), MarkUpStep(), storyCount(), MappingScreen()

### Community 42 - "models.py"
Cohesion: 0.09
Nodes (31): What counts as data, in one place (constraint 1). An anecdote exists in three…, get_session(), Session, Database engine and session plumbing (constraint 4: SQLite + local files)., FastAPI dependency yielding a session that always closes., health(), mount_frontend(), get (+23 more)

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
Cohesion: 0.14
Nodes (30): FrameworkDefinition, The whole respondent-facing definition of one framework version., propose(), Run Stage B over a file's stories and return checked proposals. Nothing is…, definition(), Any, fixture, MonkeyPatch (+22 more)

### Community 49 - "make_framework"
Cohesion: 0.14
Nodes (31): confirmed_import(), make_framework(), proposed_import(), TestClient, Shared helpers for the Stage B and validation-queue suites. One framework…, Drive a file as far as ``mapping_confirmed``, accepting Stage A as-is., Drive a file all the way to ``proposed`` — stories in the queue., _backend_modules() (+23 more)

### Community 50 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 51 - "Web Design & Data Visualization"
Cohesion: 0.22
Nodes (8): Data visualization, Output, Step 1: Frame the brief, Step 2: Design plan before code, Step 3: B2B or B2C playbook, Step 4: Build to the quality floor (non-negotiable, never announced), Step 5: Critique pass, Web Design & Data Visualization

### Community 52 - "queue.py"
Cohesion: 0.13
Nodes (22): decide(), _finish_job_if_empty(), _low(), BaseModel, Depends, get, put, Query (+14 more)

### Community 53 - "backend/exports.py"
Cohesion: 0.13
Nodes (26): _category_finding(), dataset_csv(), _dyad_finding(), findings(), headline(), _headlines(), _join(), _nearest_corner() (+18 more)

### Community 54 - "SubmittedSignification"
Cohesion: 0.17
Nodes (16): One placement as it arrives from the wizard or paper batch entry., SubmittedSignification, _check_batch(), Placement, ProposalBatch, ProposedPlacement, ProposedStory, BaseModel (+8 more)

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
Cohesion: 0.20
Nodes (14): describe_signifiers(), _mock_batch(), _mock_confidence(), _mock_value(), _prompt(), Any, Stage B — Propose (PRD §4a, constraint 1). Stage B reads a story and *suggests*…, The questions, with the exact answer shape each one takes. Written out in full… (+6 more)

### Community 84 - "export_brief"
Cohesion: 0.10
Nodes (31): only_pending(), only_validated(), Narrow a query to the stories a person has actually approved. Every read that…, Narrow a query to the stories still waiting on a person., export_brief(), export_csv(), Depends, get (+23 more)

### Community 85 - "Patterns.jsx"
Cohesion: 0.24
Nodes (7): BarChart(), DyadChart(), StonesChart(), FILTERS, lineageOf(), optionsFrom(), PatternsTab()

### Community 87 - "ai_client.py"
Cohesion: 0.20
Nodes (10): _fenced_json(), mock_enabled(), _parse(), The one AI client (constraint 6). Every call Narrative Lens makes to a language…, Parse one reply strictly, or raise the reason it could not be parsed., Whether this process runs with mocks instead of the network. Read on every call…, Return *raw* with one surrounding markdown fence removed, if present. Strict…, Payload (+2 more)

### Community 90 - "_live_text"
Cohesion: 0.22
Nodes (11): _live_text(), One live call to api.anthropic.com. The only network in the app. Imported…, ModuleType, fake_anthropic(), fixture, parametrize, A reply may carry blocks that are not text; they are not the answer., Install a fake ``anthropic`` package and turn mock mode off. (+3 more)

### Community 91 - "AiError"
Cohesion: 0.24
Nodes (8): AiError, Exception, An AI call that failed in a way the operator needs told about. Carries the PRD…, APIConnectionError, APIStatusError, _Block, Exception, RateLimitError

### Community 92 - "env.py"
Cohesion: 0.27
Nodes (9): Alembic environment. The database URL comes from…, Emit SQL to a script without a live connection., Run migrations against a live connection., _run(), run_migrations_offline(), run_migrations_online(), _url(), database_url() (+1 more)

### Community 93 - "RateLimiter"
Cohesion: 0.22
Nodes (5): RateLimiter, A sliding-window counter keyed by an opaque string. Deliberately simple and in-…, Record a hit and report whether it is within the limit., Forget counters. Used by tests and when a link is revoked., How many hits are still allowed in the current window.

### Community 94 - "_calls"
Cohesion: 0.29
Nodes (6): _calls(), Any, Strict JSON is asked for on every call, not only where it is convenient., Every request made, across every client. ``_live_text`` builds a fresh…, _Response, test_the_json_instruction_is_appended_to_every_system_prompt()

### Community 95 - "xlsx_bytes"
Cohesion: 0.29
Nodes (7): A two-sheet workbook: one of responses, one lookup table to ignore. The…, xlsx_bytes(), PRD §4: AI endpoints are exempt; reading a job's status is not., test_job_status_is_inside_the_200ms_budget(), A lookup table is not a set of responses, and saying so is the answer., test_a_sheet_with_nothing_story_like_is_proposed_as_ignore(), test_the_mock_reads_a_named_story_column()

### Community 96 - "patterns_fixtures.py"
Cohesion: 0.50
Nodes (4): The twenty-story fixture behind the pattern golden (PRD §6, Phase 7). Twenty…, One story, entirely determined by its position in the run., story_payload(), _tenths()

### Community 97 - "_FakeAnthropic"
Cohesion: 0.50
Nodes (3): _FakeAnthropic, _FakeMessages, Stands in for ``anthropic.Anthropic`` and records what it was asked.

### Community 99 - "chunks"
Cohesion: 0.50
Nodes (4): chunks(), Split the stories into calls of at most ``size`` (PRD §4a)., test_a_long_file_is_split_into_calls_of_twenty(), test_a_short_file_is_one_call()

### Community 100 - "public_base_url"
Cohesion: 0.50
Nodes (4): lan_host(), public_base_url(), The address other devices on the mesh can reach this machine at. A QR pointing…, Base URL a capture link should carry.

## Knowledge Gaps
- **151 isolated node(s):** `name`, `version`, `description`, `dev`, `build` (+146 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Anecdote` connect `Anecdote` to `TestClient`, `TestClient`, `Framework`, `TestClient`, `test_import_pipeline.py`, `_create`, `test_public_identifier_absence.py`, `imports.py`, `backend/patterns.py`, `CaptureLink`, `Signification`, `public.py`, `CaptureError`, `test_schema_absence.py`, `ConfirmationView`, `models.py`, `test_queue.py`, `make_framework`, `queue.py`, `backend/exports.py`, `SubmittedSignification`, `export_brief`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does `FrameworkDefinition` connect `FrameworkDefinition` to `Framework`, `imports.py`, `validate_definition`, `backend/patterns.py`, `public.py`, `CaptureError`, `paper_pack.py`, `ConfirmationView`, `Anecdote`, `models.py`, `queue.py`, `backend/exports.py`, `SubmittedSignification`, `test_placement_shape_parity.py`, `edit_semantics.py`, `propose.py`, `.estimated_minutes`, `.exceeds_screen_warning`, `.signifier_count`, `.signifier_ids_must_be_unique`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `Signification` connect `Signification` to `ConfirmationView`, `Anecdote`, `TestClient`, `test_import_pipeline.py`, `test_public_identifier_absence.py`, `models.py`, `imports.py`, `test_queue.py`, `make_framework`, `backend/patterns.py`, `export_brief`, `backend/exports.py`, `queue.py`, `SubmittedSignification`, `public.py`, `CaptureError`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `FrameworkDefinition` (e.g. with `CaptureError` and `CaptureSubmission`) actually correct?**
  _`FrameworkDefinition` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 63 inferred relationships involving `Anecdote` (e.g. with `Bar` and `CategoryChart`) actually correct?**
  _`Anecdote` has 63 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `Signification` (e.g. with `Bar` and `CategoryChart`) actually correct?**
  _`Signification` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `Framework` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Framework` has 30 INFERRED edges - model-reasoned connections that need verification._