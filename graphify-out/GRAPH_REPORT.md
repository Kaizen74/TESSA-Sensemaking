# Graph Report - TESSA-Sensemaking  (2026-08-16)

## Corpus Check
- 97 files · ~76,191 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1447 nodes · 3221 edges · 80 communities (71 shown, 9 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 239 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `75289c86`
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
- test_ai_client.py
- test_public_identifier_absence.py
- imports.py
- package.json
- validate_definition
- NormalisedDocument
- test_stage_gate.py
- parsers.py
- _run_node
- NarrativeSegment
- paper_pack.py
- capture_links.py
- parse
- What You Must Do When Invoked
- Signification
- organise
- public.py
- TestClient
- PRD: Narrative Lens — Local Narrative Sense-Making App
- Phases
- capture_schema.py
- CaptureTab.jsx
- test_capture_draft.py
- Widgets.jsx
- test_schema_absence.py
- FrameworkDefinition
- AiError
- Anecdote
- store_capture
- framework_schema.py
- ingest_fixtures.py
- models.py
- voice.js
- ImportTab.jsx
- capture.py
- Wizard.jsx
- Studio.jsx
- errors.py
- The session loop (every session, no exceptions)
- Data Visualization Reference — 2026
- TestScreenCountAndEstimate
- TestAnonymityStatementIsTrueOfTheCode
- graphify reference: extra exports and benchmark
- Web Design & Data Visualization
- default_definition
- App.jsx
- TestThePathCannotReachForAnIdentifier
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

## God Nodes (most connected - your core abstractions)
1. `Anecdote` - 61 edges
2. `FrameworkDefinition` - 47 edges
3. `Framework` - 40 edges
4. `parse()` - 39 edges
5. `NormalisedDocument` - 37 edges
6. `_framework()` - 37 edges
7. `_framework()` - 36 edges
8. `_submit()` - 36 edges
9. `ImportJob` - 33 edges
10. `_link()` - 33 edges

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

## Communities (80 total, 9 thin omitted)

### Community 0 - "BarycentricError"
Cohesion: 0.05
Nodes (47): BarycentricError, from_value_json(), is_inside(), normalise(), ValueError, Triad barycentric maths. A triad answer is a point inside an equilateral…, Whether three weights sum to 1.0 within :data:`SUM_TOLERANCE`., Whether the weights describe a point in or on the triangle. (+39 more)

### Community 1 - "TestClient"
Cohesion: 0.08
Nodes (30): qr_png_bytes(), Return a PNG of ``payload`` as QR, as raw bytes. Error correction is set to M…, _framework(), _link(), TestClient, Capture links and the public capture path (PRD §6 Phase 4). The tests the PRD…, PRD §6 Phase 4: token lifecycle. §7.6: revoked links close., The heart of §7.6: a taken-down QR poster cannot keep collecting. (+22 more)

### Community 2 - "TestClient"
Cohesion: 0.09
Nodes (24): _framework(), TestClient, Local capture (PRD §6 Phase 3). The tests the PRD names for this phase: wizard…, PRD §9 assumption 7: reflection shows one signifier., Skipping every question is allowed; the story is the point., Constraint 3: provenance on every record., PRD §6 Phase 3: batch entry writes paper provenance., Constraint 9, at the moment a story is actually written. (+16 more)

### Community 3 - "Framework"
Cohesion: 0.08
Nodes (52): get_session(), Session, FastAPI dependency yielding a session that always closes., build_edit_log_entries(), diff_text_fields(), is_structural_change(), Any, datetime (+44 more)

### Community 4 - "make_engine"
Cohesion: 0.06
Nodes (47): Alembic environment. The database URL comes from…, Emit SQL to a script without a live connection., Run migrations against a live connection., _run(), run_migrations_offline(), run_migrations_online(), _url(), _connect_args() (+39 more)

### Community 5 - "TestClient"
Cohesion: 0.10
Nodes (23): _create_full(), _pack_html(), TestClient, The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar). Two…, PRD §1.2a: the story card carries respondent-group tick boxes., The pack renders the version's current wording, not a cached copy., Constraint 9: the anonymity statement is printed verbatim on the card., Whatever this version says is what the card prints — no substitution. (+15 more)

### Community 6 - "test_import_pipeline.py"
Cohesion: 0.14
Nodes (50): A two-sheet workbook: one of responses, one lookup table to ignore. The…, txt_bytes(), xlsx_bytes(), _confirm(), _confirmation_body(), _organise(), parametrize, Session (+42 more)

### Community 7 - "_create"
Cohesion: 0.14
Nodes (23): _add_story(), _create(), _definition(), Session, TestClient, The wording-fix vs meaning-change state machine (PRD §6, constraint 13g). This…, Constraint 7: the operator must be able to act on the message., A wording fix patches in place and appends to the edit log. (+15 more)

### Community 8 - "test_ai_client.py"
Cohesion: 0.08
Nodes (37): _fenced_json(), _live_text(), mock_enabled(), _parse(), Any, The one AI client (constraint 6). Every call Narrative Lens makes to a language…, Parse one reply strictly, or raise the reason it could not be parsed., One live call to api.anthropic.com. The only network in the app. Imported… (+29 more)

### Community 9 - "test_public_identifier_absence.py"
Cohesion: 0.10
Nodes (23): RateLimiter, Rate limiting for the public capture endpoints (PRD §4). The public endpoints…, A sliding-window counter keyed by an opaque string. Deliberately simple and in-…, Record a hit and report whether it is within the limit., Forget counters. Used by tests and when a link is revoked., How many hits are still allowed in the current window., Clear every counter. Tests call this between cases., reset_all() (+15 more)

### Community 10 - "imports.py"
Cohesion: 0.14
Nodes (32): ImportJob, One uploaded file moving through the two-stage ingestion machine., classify(), Return ``(file_type, file_class)`` for a filename, or refuse it., confirm_mapping(), create_import(), _detail(), get_import() (+24 more)

### Community 11 - "package.json"
Cohesion: 0.06
Nodes (30): eslint, @eslint/js, eslint-plugin-react, eslint-plugin-react-hooks, dependencies, react, react-dom, description (+22 more)

### Community 12 - "validate_definition"
Cohesion: 0.11
Nodes (13): Parse and validate a raw ``definition_json`` payload., validate_definition(), Base, Declarative base carrying the shared naming convention., DeclarativeBase, Validation of ``definition_json`` and the anonymity statement it carries., Significations key on the id alone, so one namespace covers all kinds., A typo in the Studio should fail loudly, not vanish silently. (+5 more)

### Community 13 - "NormalisedDocument"
Cohesion: 0.12
Nodes (27): _check_narrative(), _check_tabular(), _hinted_column(), _mock_narrative(), _mock_tabular(), _narrative_prompt(), NarrativeOrganisation, OrganiseError (+19 more)

### Community 14 - "test_stage_gate.py"
Cohesion: 0.09
Nodes (25): can_advance(), The ingestion stage machine and its gate (PRD §3, §4; constraints 1 and 12). An…, Note why a step did not work, without moving the job. A failed AI call is worth…, Whether the machine permits ``current → target``., Whether ``target`` can be reached from ``start`` by any number of steps. Used…, Refuse, with 409 and an explanation, unless the job is at ``expected``. This is…, reachable(), record_error() (+17 more)

### Community 15 - "parsers.py"
Cohesion: 0.13
Nodes (26): Block, _blocks_from_text(), _clean_row(), _decode(), _parse_captions(), _parse_csv(), _parse_docx(), _parse_pdf() (+18 more)

### Community 16 - "_run_node"
Cohesion: 0.11
Nodes (14): parametrize, Voice fallback (PRD §6 Phase 4, §7.12, constraint 10). Constraint 10 says voice…, The UI calls stop() on unmount whether or not voice ever started., Stopping on purpose is not a failure and must not show a warning., Constraint 10: voice always paired with typing., Interim results would rewrite a respondent's words as they speak., §7.12: voice fails plain-English with a working fallback., Constraint 7: no jargon a respondent cannot act on. (+6 more)

### Community 17 - "NarrativeSegment"
Cohesion: 0.19
Nodes (24): _balance(), Candidate, confirm(), confirm_narrative(), confirm_tabular(), ConfirmedExtraction, ExtractionError, BaseModel (+16 more)

### Community 18 - "paper_pack.py"
Cohesion: 0.13
Nodes (21): Dyad, Mcq, A 2D canvas on which the respondent places named chips., A multiple-choice question., Every signifier with its kind, in the order the respondent meets them., A triangle with three named corners; answers are barycentric., A slider between two opposing poles; answers are 0–1., Stones (+13 more)

### Community 19 - "capture_links.py"
Cohesion: 0.15
Nodes (24): QR codes for capture links (PRD §4, §1.8). A QR is how a phone gets to the…, capture_link_qr(), capture_url(), CaptureLinkCreate, CaptureLinkOut, create_capture_link(), _get_or_404(), list_capture_links() (+16 more)

### Community 20 - "parse"
Cohesion: 0.13
Nodes (24): parse(), Read one uploaded file into the normalised shape, or refuse it. Refusals are…, parametrize, Every format PRD §1.3 promises, read from a real file of that format., PRD §1.3 lists nine extensions. All nine are readable, nothing else is., The reverse map the API uses for jobs whose extension is long gone., PRD §9 assumption 9: decks are text-only., Assumption 10: a mixed-role workbook is mapped sheet by sheet. (+16 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "Signification"
Cohesion: 0.21
Nodes (11): One respondent (or validated AI) placement on one signifier. ``value_json``…, Signification, _anecdote(), _framework(), parametrize, Constraint 3: provenance on every record., PRD §3: input_method is typed | voice | paper | imported., An old story stays on v1 when v2 appears (PRD §3). (+3 more)

### Community 23 - "organise"
Cohesion: 0.19
Nodes (21): organise(), Run Stage A over a parsed file and return its proposal. Nothing is written to…, csv_bytes(), Any, MonkeyPatch, TestClient, Stage A: what it proposes, and what it is not allowed to get away with. Stage A…, Constraint 4 and 7: offline is a normal state, not a broken one. The file stays… (+13 more)

### Community 24 - "public.py"
Cohesion: 0.16
Nodes (20): PublicCaptureSubmission, A capture arriving through a capture link. ``framework_id`` is not accepted:…, not_found(), create_public_capture(), _framework_or_refuse(), get_public_framework(), _link_or_refuse(), PublicFrameworkOut (+12 more)

### Community 25 - "TestClient"
Cohesion: 0.14
Nodes (9): TestClient, List, create and fetch frameworks (PRD §4)., A new framework starts valid and empty, ready to fill in., The Studio shows these live while the operator edits., Constraint 7: plain English, with something to do about it., PRD §5.1: version history sidebar shows versions with story counts., TestCreate, TestFetch (+1 more)

### Community 26 - "PRD: Narrative Lens — Local Narrative Sense-Making App"
Cohesion: 0.10
Nodes (19): 0. What you're getting (plain language), 10. Future upgrades — document, do not build, 11. Changelog v1.2 → v1.3, 1. Scope, 2. Binding constraints (restate these in every session), 3. Data model (SQLite, via SQLAlchemy + Alembic), 4. API contract (FastAPI, all JSON), 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages). (+11 more)

### Community 27 - "Phases"
Cohesion: 0.10
Nodes (19): Decisions, Fixed, Narrative Lens — Progress, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5 (+11 more)

### Community 28 - "capture_schema.py"
Cohesion: 0.16
Nodes (17): CaptureError, _check_dyad(), _check_mcq(), _check_stones(), _check_triad(), BaseModel, ValueError, Validating a submitted capture against the framework it answers (PRD §4). A… (+9 more)

### Community 29 - "CaptureTab.jsx"
Cohesion: 0.19
Nodes (10): api, ApiError, MODES, LinkManager(), PaperBatch(), ReflectionPanel(), toSubmission(), orderedSignifiers() (+2 more)

### Community 30 - "test_capture_draft.py"
Cohesion: 0.15
Nodes (18): Drafts survive a reload (PRD §6 Phase 3, §7.6). The draft lives in the browser,…, Nothing lingers once the story has been sent., Starting fresh is recoverable; crashing on load is not., A draft from an older shape must not crash the wizard., Private browsing must not stop someone telling their story., Constraint 9 reaches into the browser, not just the database., Offering to restore an empty draft would be noise., The whole point: a half-written story survives the page going away. (+10 more)

### Community 31 - "Widgets.jsx"
Cohesion: 0.24
Nodes (15): CORNER_0, CORNER_1, CORNER_2, normalise(), roundTo(), toBarycentric(), toCartesian(), TRIANGLE_HEIGHT (+7 more)

### Community 32 - "test_schema_absence.py"
Cohesion: 0.15
Nodes (17): _columns(), parametrize, Constraint 9 — respondent anonymity is engineered, not promised. These tests…, Constraint 9: respondent time is hour-rounded, so no exact clock exists.…, A row written through the ORM gets an hour-rounded stamp automatically., The rules hold against the real database, not just the model metadata., PRD §3: migration 001 creates all six tables and no others., No IP, user agent, fingerprint, device/session id or email anywhere. (+9 more)

### Community 33 - "FrameworkDefinition"
Cohesion: 0.15
Nodes (12): FrameworkDefinition, The whole respondent-facing definition of one framework version., How many signifier screens the respondent will see., PRD §1.1: warn past roughly six signifier screens., Coarse 'respondent minutes' estimate shown live in the Studio., Estimated respondent time, rounded to one decimal., _facilitator_sheet(), The A4 story card: prompt, ruled space, groups, anonymity line. (+4 more)

### Community 34 - "AiError"
Cohesion: 0.17
Nodes (13): AiError, Exception, An AI call that failed in a way the operator needs told about. Carries the PRD…, ParseError, Exception, A file that could not be read, phrased for the operator., ConfirmationView, MappingConfirmation (+5 more)

### Community 35 - "Anecdote"
Cohesion: 0.25
Nodes (10): Anecdote, CaptureLink, A token-gated capture URL pointing at one exact framework version., One story, bound to the exact framework version it was told against.…, A free-text tag the analyst attaches to a story., Tag, CRUD across the six tables of PRD §3, plus the vocabularies they enforce., TestCaptureLink (+2 more)

### Community 36 - "store_capture"
Cohesion: 0.20
Nodes (14): CaptureSubmission, LocalCaptureSubmission, A whole capture: one story plus its placements. Note what is *not* here: no id,…, A capture from the operator's own machine: admin, paper entry, or kiosk. Only…, CaptureResult, create_capture(), BaseModel, Depends (+6 more)

### Community 37 - "framework_schema.py"
Cohesion: 0.16
Nodes (10): CaptureSettings, BaseModel, Validation for ``frameworks.definition_json`` (PRD §3 and §5). Every…, Every non-signifier string the respondent reads, plus capture toggles., One id namespace across all signifier kinds — significations key on it., Reject unknown keys so a typo in the Studio surfaces as an error., One axis of the stones canvas, named at both ends., StonesAxis (+2 more)

### Community 38 - "ingest_fixtures.py"
Cohesion: 0.15
Nodes (11): docx_bytes(), pdf_bytes(), _pdf_escape(), pptx_bytes(), Real files, in memory, one per format Narrative Lens claims to read. Acceptance…, A one-page PDF with each paragraph as its own text run. Written by hand:…, vtt_bytes(), test_prose_segments_carry_the_locator_they_came_from() (+3 more)

### Community 39 - "models.py"
Cohesion: 0.19
Nodes (12): hour_rounded_now(), _in_clause(), datetime, The six-table schema from PRD §3. Two constraints shape this module directly: *…, Render a SQL ``IN`` predicate for a CHECK constraint., Naive UTC now, for operator-side records that carry no respondent link., Naive UTC now truncated to the hour (constraint 9). Minutes, seconds and…, utcnow() (+4 more)

### Community 40 - "voice.js"
Cohesion: 0.28
Nodes (11): appendDictation(), getRecognitionClass(), isVoiceSupported(), startDictation(), VOICE_DENIED, VOICE_FAILED, VOICE_NETWORK, VOICE_NO_SPEECH (+3 more)

### Community 41 - "ImportTab.jsx"
Cohesion: 0.19
Nodes (4): ImportDetail(), ImportTab(), storyCount(), MappingScreen()

### Community 42 - "capture.py"
Cohesion: 0.20
Nodes (10): health(), mount_frontend(), get, FastAPI application. Endpoints arrive with the phase that needs them, per PRD…, Liveness probe. The launcher opens this while the app is starting., Serve ``frontend/dist`` if it has been built. Returns whether anything was…, _auto_title(), Capture endpoints (PRD §4). Phase 3 covers local capture: the admin wizard and… (+2 more)

### Community 43 - "Wizard.jsx"
Cohesion: 0.41
Nodes (9): clearDraft(), draftHasContent(), draftKey(), loadDraft(), safeStorage(), saveDraft(), browserStorage(), buildSteps() (+1 more)

### Community 44 - "Studio.jsx"
Cohesion: 0.24
Nodes (6): EditKindDialog(), Field(), SignifierEditor(), TextArea(), estimateMinutes(), Studio()

### Community 45 - "errors.py"
Cohesion: 0.27
Nodes (8): AppError, bad_request(), conflict(), The error shape from PRD §4. ``{"error": {"code": ..., "message": plain-English…, An error the operator is meant to read and act on., Something outside the app misbehaved — currently only the AI service., upstream(), HTTPException

### Community 46 - "The session loop (every session, no exceptions)"
Cohesion: 0.20
Nodes (9): 1. SESSION START — recover state before touching anything, 2. PLAN — small increments, 3. BUILD — one increment at a time, 4. TEST — after every increment, before calling it done, 5. CHECKPOINT — commit + state update, every increment, 6. SESSION END (or when the user says "wrap up"), Communication rules (owner is non-technical), Resilient Build (+1 more)

### Community 47 - "Data Visualization Reference — 2026"
Cohesion: 0.20
Nodes (9): Accessibility floor, Chart selection, Color encoding, Dashboard hierarchy, Data Visualization Reference — 2026, First principle, Integrity rules (non-negotiable), Interactivity discipline (+1 more)

### Community 48 - "TestScreenCountAndEstimate"
Cohesion: 0.27
Nodes (3): Constraint 10: ≤4 minutes typical., PRD §1.1: warn past roughly six signifier screens., TestScreenCountAndEstimate

### Community 49 - "TestAnonymityStatementIsTrueOfTheCode"
Cohesion: 0.27
Nodes (3): Constraint 9: the statement must be literally true of the schema. Each clause…, Story, placements, and chosen group — and that is the whole list., TestAnonymityStatementIsTrueOfTheCode

### Community 50 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 51 - "Web Design & Data Visualization"
Cohesion: 0.22
Nodes (8): Data visualization, Output, Step 1: Frame the brief, Step 2: Design plan before code, Step 3: B2B or B2C playbook, Step 4: Build to the quality floor (non-negotiable, never announced), Step 5: Critique pass, Web Design & Data Visualization

### Community 52 - "default_definition"
Cohesion: 0.32
Nodes (5): default_definition(), A minimal, valid definition — what a brand-new framework starts from., The operator starts from something valid and fills it in., Constraint 10: reflection on by default; voice paired with typing., TestDefaults

### Community 53 - "App.jsx"
Cohesion: 0.39
Nodes (5): App(), TABS, CaptureTab(), captureTokenFromPath(), PublicCapture()

### Community 54 - "TestThePathCannotReachForAnIdentifier"
Cohesion: 0.25
Nodes (5): Structural guards: not "it doesn't today", but "it has no way to"., Taking a ``Request`` would put every header within arm's reach., A grep-level guard against a future edit reaching for client data., The one place a naive implementation would reach for a client IP., TestThePathCannotReachForAnIdentifier

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

## Knowledge Gaps
- **148 isolated node(s):** `name`, `version`, `description`, `dev`, `build` (+143 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Anecdote` connect `Anecdote` to `test_schema_absence.py`, `TestClient`, `TestClient`, `Framework`, `store_capture`, `TestClient`, `test_import_pipeline.py`, `models.py`, `_create`, `test_public_identifier_absence.py`, `capture.py`, `validate_definition`, `capture_links.py`, `Signification`, `TestThePathCannotReachForAnIdentifier`, `TestFramework`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Why does `FrameworkDefinition` connect `FrameworkDefinition` to `Framework`, `store_capture`, `framework_schema.py`, `capture.py`, `validate_definition`, `TestScreenCountAndEstimate`, `TestAnonymityStatementIsTrueOfTheCode`, `paper_pack.py`, `default_definition`, `public.py`, `capture_schema.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `ImportJob` connect `imports.py` to `AiError`, `Anecdote`, `test_import_pipeline.py`, `models.py`, `validate_definition`, `test_stage_gate.py`, `Signification`, `organise`, `TestFramework`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `Anecdote` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Anecdote` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `FrameworkDefinition` (e.g. with `CaptureError` and `CaptureSubmission`) actually correct?**
  _`FrameworkDefinition` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `Framework` (e.g. with `CaptureResult` and `CaptureLinkCreate`) actually correct?**
  _`Framework` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _148 weakly-connected nodes found - possible documentation gaps or missing edges._