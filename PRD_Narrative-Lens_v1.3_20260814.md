# PRD: Narrative Lens — Local Narrative Sense-Making App
Status: DRAFT v1.3 | Date: 2026-08-14 | Owner: Eric Yim | Greenfield build (no existing repo)
Supersedes: v1.2 (2026-08-14). Changelog in §11. Sections NOT listed in the changelog are unchanged from v1.2.

---

## 0. What you're getting (plain language)

A private app on your laptop where people share short real-work anecdotes and interpret their own stories on visual scales — triangles, sliders, and a 2D canvas. The app overlays everyone's interpretations into pattern maps, so disconnects between "work as designed" and "work as done" become visible.

The respondent experience: stories from their phones via QR over Tailscale, voice or typing, one friendly screen at a time, anonymous, ending with their story landing on the live pattern. Kiosk mode for workshops. Intelligent ingestion: drop in Word, text, PowerPoint, PDF, transcripts, or Excel/CSV — AI organises the mess into candidate anecdotes (you confirm the column mapping for spreadsheets) and proposes significations; everything passes through your validation queue.

New in v1.3, three things. **The Studio (admin panel):** every probing question, scale label, and respondent-facing line of text is editable in one place, with a guardrail — once stories exist, the app asks whether your edit is a wording fix (applies in place, logged) or a meaning change (creates a new version so old answers stay tied to the words people actually saw). **Paper packs:** one click downloads a print-ready A4 set — story card, large-format signifier sheets for sticky-dot exercises, and a facilitator sheet — so you can run analogue capture in a workshop, then transcribe responses through a rapid batch-entry mode. **Landscape-first patterns:** the 3D fitness landscape is now the primary discovery view with the hero space on screen, always paired with a precise 2D contour twin, while every supporting chart (demographics, filters, distributions) follows a strict simple-and-elegant visual grammar — one hue, direct labels, no chart junk.

Everything runs locally; the only network traffic is your Tailscale mesh, optional browser voice dictation, and your explicit Claude API calls during import.

---

## 1. Scope

**IN (v1.3):**
1. **The Studio (Framework Designer, elevated)** — one admin panel to create and change everything respondents see:
   - Prompting question + optional alternative prompt; every triad corner, dyad pole, stones axis and chip label; every signifier question; MCQ options; welcome, anonymity, and thank-you text; time promise.
   - Live phone-frame preview updating as you type; "respondent minutes" estimate; warning past ~6 signifier screens.
   - **Edit semantics (the guardrail):** while a framework has zero stories, edit freely. Once stories exist, every save prompts one choice:
     - *Wording fix* — typo or clarity, same meaning. Applies in place; appended to the framework's edit log (old text, new text, timestamp).
     - *Meaning change* — creates framework version n+1. Existing anecdotes stay bound to the version whose wording they answered; new capture links point at the new version; the dashboard shows a version chip on any view mixing versions, and landscape/pattern views default to one version at a time.
2. Capture — three digital entry modes sharing one wizard (admin · remote QR link over Tailscale/LAN · kiosk), per §5a, plus:
   - **Paper pack download:** per framework version, a print-optimised pack (opens as a print-ready page; use the browser's Print → Save as PDF): (a) A4 story card — prompt, ruled writing space, respondent-group tick boxes, the anonymity line, optional QR to the digital link; (b) one A4 landscape-orientation sheet per signifier — the widget rendered large with its labels, for sticky-dot or pen marking; (c) facilitator sheet — running instructions, materials list, and a reconciliation grid (sheets handed out / returned / entered).
   - **Paper batch entry:** a rapid transcription mode in admin capture — type or paste the story, click placements on each widget, Enter advances; each record stamped input_method=paper. Built for entering 30 workshop responses in one sitting.
3. Ingestion — as v1.2: `.docx`, `.txt`, `.md`, `.pdf`, `.pptx`, `.xlsx` (multi-sheet), `.csv`, `.vtt`/`.srt` through the two-stage AI pipeline (Stage A Organise with human-confirmed column mapping + exact row reconciliation for tables; Stage B Propose), all into the validation queue.
4. Validation queue — as v1.2.
5. **Patterns, landscape-first** — the Patterns tab opens on the **Landscape** by default:
   - **Primary (hero):** the Narrative Landscape — rotatable 3D density terrain per triad, peaks labelled directly with story counts, click/lasso a region → the stories beneath it, side-by-side split by any filter. Every landscape has a one-tap **2D contour twin** (same KDE, top-down contour with dots) for precise reading; exports default to the contour.
   - **Supporting (quiet):** demographics and MCQ breakdowns as sorted horizontal bars; dyads as strip + histogram; stones as 2D scatter; filter rail. All at reduced visual weight per the §5b grammar — the landscape is the only bold thing on screen.
   - **3D Explorer** and optional deterministic k-means overlay ("statistical clusters — descriptive only") — as v1.2, one level down in the navigation.
   - Analyst notes panel (closure-constraint caveats, constraint 12).
6. Story browser — full-text search, tag, star, export selected.
7. Exports — dataset CSV; landscape + contour PNG; supporting charts PNG; analyst "Pattern Brief" markdown; respondent-safe "What We Heard" with small-group suppression. Export headlines are findings, not topics (§5b).
8. One-click launch — `Start Narrative Lens.bat`; QR of the active capture link on the admin home screen.

**OUT (explicitly not built now):** unchanged from v1.2 (no audio transcription, no AI interviewer, no AI-generated patterns, no auth/cloud/public internet, no inference stats, no SATS anything, no cross-wave animation), plus: no server-side PDF generation library (paper packs use print-optimised pages + the browser's own Save-as-PDF — zero fragile dependencies on Windows).

---

## 2. Binding constraints (restate these in every session)

1. **AI senses, you decide.** No AI-organised anecdote and no AI-proposed signification ever enters the dataset without explicit human validation, at any confidence level. Applies to both ingestion stages; Stage A output (including column mappings) requires confirmation before Stage B may run.
2. **Confidence < 0.70 is flagged visually** (amber) but routing is identical — everything queues.
3. **Provenance on every record.** source_type · entry_mode (admin | link | kiosk) · input_method (typed | voice | paper | imported) · source_file · source_locator · signified_by · validated_at · framework version. Displayed and exportable.
4. **Local-first.** SQLite + local files. Permitted network: Tailscale/LAN capture serving, browser speech when chosen, `api.anthropic.com` only on an explicit Analyse click. Fully functional offline for capture (typed/paper), validation, all patterns, exports, and paper-pack printing.
5. **Additive-only migrations.**
6. **Everything mock-testable.** One `ai_client.py`, mocks for both stages, `NL_MOCK_AI=1` runs everything with zero network, strict-JSON with one repair-retry then graceful plain-English failure.
7. **Non-technical operator.** Zero terminal after install; plain-English errors with suggested actions; no config editing.
8. **Original names and materials only.** The app is "Narrative Lens"; "SenseMaker" (a registered trademark of Cognitive Edge / The Cynefin Company) appears nowhere in UI, code, or docs; method pattern replicated, no proprietary material copied.
9. **Respondent anonymity is engineered, not promised.** No IP, fingerprint, user agent, name, or email anywhere in the schema; hour-rounded timestamps; the on-screen anonymity statement must be literally true of the code — and is printed verbatim on the paper story card.
10. **The respondent experience bar.** ≤4 minutes typical, 375px-clean, tap targets ≥44px, visible progress, honest time promise, reflection on by default, voice always paired with typing.
11. **Patterns are computed, never composed.** All aggregation, KDE, landscapes, contours, and clustering are local, deterministic statistical code. AI never generates, smooths, interpolates, labels, or narrates any pattern.
12. **Tables are gated; triads are respected.** Tabular ingestion requires a human-confirmed column mapping and displayed exact row reconciliation. Closure-constraint caveats documented in the analyst notes; pattern reading is exploratory/abductive, never causal.
13. **The visual grammar.** (a) The landscape is the ONE bold element; everything else is quiet — hero space to the landscape, supporting charts at reduced visual weight, filters in a slim rail. (b) Decorative 3D is banned everywhere; the landscape is the sole exception because its z-axis encodes data (density), and it must always offer its 2D contour twin, which is the default for print/export. (c) Per chart: ≤4 colors — one data hue, one accent, gray for context; sequential colorblind-safe scale for the terrain; never red/green as primary encoding; must survive grayscale. (d) Categorical comparisons are horizontal bars sorted by value; bar axes start at zero; direct labels beat legends; no decorative gridlines or icons. (e) WCAG AA contrast, ≥12px chart text, keyboard-reachable interactions. (f) Export and brief headlines state findings ("Ops stories cluster on time-pressure"), never topics ("Triad 2 results"). (g) Wording edits to live frameworks follow the wording-fix vs meaning-change guardrail — no silent in-place semantic changes, ever.

---

## 3. Data model (SQLite, via SQLAlchemy + Alembic)

```
frameworks      id · name · version · definition_json · edit_log_json
                · parent_framework_id (nullable — links version n+1 to n)
                · created_at · is_active
                (definition_json as v1.2: prompt_text, prompt_text_alt, triads[],
                 dyads[], stones, mcqs[], capture_settings;
                 edit_log_json: [{field_path, old_text, new_text, edited_at,
                                  kind: wording_fix}] — meaning changes create a
                 new row, not a log entry)

capture_links   id · framework_id · token · label · is_active · created_at
                · revoked_at (nullable)

anecdotes       id · framework_id (binds the story to the exact version answered)
                · text · title_auto · source_type · entry_mode (admin|link|kiosk)
                · capture_link_id (nullable)
                · input_method (typed | voice | paper | imported)
                · source_file · source_locator · import_job_id (nullable)
                · respondent_group · created_at_hour
                · status (pending_validation | validated | rejected)
                (deliberately absent: ip, user_agent, email, name — constraint 9)

significations  id · anecdote_id · signifier_id · signifier_type · value_json
                · ai_confidence (nullable) · signified_by · validated_at (nullable)
                (triad barycentric sums to 1.0; dyad 0–1; stones [{label,x,y}];
                 mcq {selected[]})

import_jobs     id · filename · file_type · file_hash
                · stage (uploaded | organised | mapping_confirmed | proposed |
                         done | failed)
                · normalised_json · column_mapping_json · segments_found
                · error_message · created_at

tags            id · anecdote_id · tag_text
```

Migration 001 creates all six tables (frameworks now includes edit_log_json and parent_framework_id; anecdotes includes the four-value input_method). No further schema in v1.

---

## 4. API contract (FastAPI, all JSON)

Admin endpoints (localhost only):

| Endpoint | Method | Purpose | Notes |
|---|---|---|---|
| `/api/frameworks` · `/api/frameworks/{id}` | GET/POST/PUT | list/create/fetch; PUT on a framework **with anecdotes** requires `edit_kind: wording_fix | meaning_change` — wording_fix patches definition_json and appends to edit_log_json; meaning_change creates version n+1 with parent_framework_id set and returns the new id; PUT without edit_kind on a live framework → 409 with a plain-English explanation | 200ms |
| `/api/frameworks/{id}/paper-pack` | GET | print-optimised HTML page (story card + per-signifier A4 sheets + facilitator sheet, print CSS with page breaks) | 200ms |
| `/api/capture-links` · `…/{id}/revoke` | GET/POST | as v1.2 (+QR PNG) | 200ms |
| `/api/capture` | POST | admin + paper batch entry (accepts input_method typed | paper) | 200ms |
| `/api/import` → `/organise` → `/mapping` → `/propose` → job status | as v1.2 | Stage machine with the 409 stage gate | AI endpoints async, exempt from 200ms |
| `/api/queue` · `/api/queue/{anecdote_id}` | GET/PUT | as v1.2 | 200ms |
| `/api/patterns/{framework_id}` | GET | 2D aggregates + filters; refuses silently mixing framework versions — a version parameter or an explicit `mixed=true` with the version chip data returned | 200ms |
| `/api/landscape/{framework_id}/{triad_id}` | GET | KDE grid (64×64) + peak coordinates + counts + per-cell anecdote ids; serves both the 3D surface and its 2D contour twin from the same response | 200ms ≤5,000 anecdotes; scipy gaussian_kde, Scott bandwidth, deterministic |
| `/api/explorer/{framework_id}` · `/api/clusters/{framework_id}` | GET | as v1.2 (deterministic, fixed seed) | 200ms |
| `/api/export/csv` `/brief` `/heard` | GET | as v1.2; brief/heard headlines generated from computed figures using finding-style templates (constraint 13f) — template text, not AI | 200ms |

Public capture endpoints: unchanged from v1.2 (token-gated, rate-limited, identifier-free; framework fetch always returns the exact version the link points at).

Error shape everywhere: `{"error": {"code": "...", "message": "plain-English sentence", "action": "what to do"}}`.

### 4a. AI call specs — unchanged from v1.2 (Stage A Organise per file class with deterministic post-confirmation table extraction; Stage B Propose chunked ≤20 anecdotes; `claude-sonnet-4-6`, temperature 0, strict JSON, mocks for both stages).

---

## 5. Frontend (React + Vite)

Admin app — four nav tabs:
1. **Studio** — the admin panel of §1.1: full editing surface for every question, label, and respondent-facing string; live phone-frame preview; minutes estimate; the wording-fix / meaning-change dialog on any save to a live framework; version history sidebar (versions with story counts, edit log per version); Paper pack button per version.
2. **Capture & Links** — admin capture · **paper batch entry mode** (story field + widgets + Enter-to-advance, running count of entries this sitting) · link manager with QR poster · kiosk launcher.
3. **Import & Validate** — as v1.2 (staged pipeline, Mapping screen with reconciliation line, validation queue).
4. **Patterns** — **opens on Landscape.** Layout per constraint 13a: landscape hero (~40% and the visual anchor), filter rail slim (~10%), supporting charts in a quiet lower band; sub-navigation: Landscape (default) · Supporting charts · 3D Explorer · Story browser. Landscape view: triad picker, rotatable terrain with directly-labelled peaks, contour-twin toggle, filter split, region→stories drawer, camera reset, PNG snapshot (defaults to contour). Version chip whenever data spans framework versions.

### 5a. Capture wizard — unchanged from v1.1/v1.2.

### 5b. Design system (binding on all UI, enforced as constraint 13)

- **Token plan (Phase 2 deliverable, in `frontend/src/tokens.css`):** 4–6 named colors — one ink, one paper/background, one data hue, one accent (used only for the highlight/selected state), gray for context; terrain uses a named colorblind-safe sequential scale (e.g., viridis/cividis family), never red→green. Two typefaces by role: a readable UI/body face and a tabular-numerals face for data labels; no decorative display font.
- **The signature element is the landscape.** Everything else passes the "quiet test": if a supporting chart draws the eye before the landscape does, reduce it (opacity ~65% for secondary data, ~45% labels).
- **Supporting-chart grammar:** horizontal bars sorted by value for every categorical/demographic view; histograms for distributions; direct labels on data, no legends where a label will do; no gridline decoration; bar axes start at zero; ≤4 colors per chart; survives grayscale.
- **Dashboard hierarchy:** 10-second test — a first-time viewer states what the view shows and where stories cluster within 10 seconds; zero clicks to a meaningful default (latest framework version, all data, landscape of triad 1).
- **Accessibility floor:** WCAG AA contrast, ≥12px chart text (16px for labels users must read), visible keyboard focus, reduced-motion respected, alt text on exported images stating chart type and the key finding.
- **Print grammar (paper pack):** pure black-on-white, widgets at maximum size on the page, ≥14pt labels, page-break-per-sheet, no color dependence (a photocopier is the test).

---

## 6. Phased build plan (each phase = one Claude Code session, each ends with its gate)

**Phase 1 — Skeleton + data layer.** As v1.2, with the §3 schema including edit_log_json, parent_framework_id, and the four-value input_method.
Tests: CRUD, migration up/down, schema-absence (constraint 9). Gate: pytest green · ruff 0. Commit: `phase-1: skeleton, schema, launcher`.

**Phase 2 — Studio + widgets + tokens + paper pack.** Studio editing surface with live preview; `tokens.css` per §5b; shared widget components; framework JSON validation; **edit-semantics flow** (free edit at zero stories; wording-fix vs meaning-change dialog once stories exist; version history sidebar); **paper-pack print page** with print CSS.
Tests: barycentric golden maths; edit-semantics state machine (PUT without edit_kind on live framework → 409; wording_fix logs and patches; meaning_change spawns version with parent link and leaves old anecdotes bound); paper-pack page contains every signifier of the version with its exact labels and the verbatim anonymity line; print CSS produces one sheet per page (assert page-break rules present). Gate: pytest + ruff + eslint 0. Commit: `phase-2: studio, tokens, widgets, paper pack`.

**Phase 3 — Capture wizard (local) + paper batch entry.** Wizard per §5a; paper batch entry mode with Enter-to-advance; provenance stamping incl. input_method=paper.
Tests: wizard round-trip; draft survives reload; batch entry writes paper provenance and loops correctly; p95 < 200ms on submit. Gate: full regression. Commit: `phase-3: capture wizard + paper entry`.

**Phase 4 — Remote links, kiosk, voice.** As v1.2 Phase 4 (identifier-absence test, token lifecycle, 375px snapshot, voice fallback).
Gate: full regression. Commit: `phase-4: remote capture + kiosk + voice`.

**Phase 5 — Ingestion + Stage A (mock-first).** As v1.2 Phase 5 (all parsers, stage machine, Mapping screen, deterministic extraction, reconciliation arithmetic, stage-gate 409 test).
Gate: full suite green with `NL_MOCK_AI=1`. Commit: `phase-5: multi-format ingestion + organise stage`.

**Phase 6 — Stage B + validation queue (mock-first).** As v1.2 Phase 6 (no-bypass test).
Gate: full suite, `NL_MOCK_AI=1`. Commit: `phase-6: proposals + validation queue`.

**Phase 7 — Live AI + supporting charts + exports.** Real Claude for both stages; **supporting charts built to §5b grammar** (sorted horizontal bars, direct labels, quiet weight); filters; version-chip behaviour; CSV + Pattern Brief with finding-style headlines.
Tests: repair path; offline degradation; version mixing requires explicit flag; 2D aggregation vs golden `patterns_20_anecdotes.json` (byte-identical thereafter); a chart-grammar test asserting categorical endpoints return value-sorted data. Gate: full suite + golden, ruff + eslint 0. Commit: `phase-7: live AI + supporting charts`.

**Phase 8 — Landscape suite (primary view).** KDE endpoint serving surface + contour twin; landscape as the Patterns default with the §5b hero layout; directly-labelled peaks; region→stories drill; filter split; 3D Explorer; k-means overlay; analyst notes; snapshot (contour default).
Tests: KDE determinism; landscape peaks on golden set stable ±0.02; region query exact; contour twin derives from the identical grid as the surface (single-source test); default route lands on Landscape; cluster determinism; interactive at 1,000 points. Gate: full regression incl. both goldens. Commit: `phase-8: landscape-first patterns`.

**Phase 9 — Closing the loop + operator hardening + critique pass.** "What We Heard" with <5 suppression; plain-English error pass; empty states; README-for-Eric (incl. "printing a paper pack" and "reading a landscape" one-pagers); **critique pass per the design skill: remove one element per view, verify the landscape is the single boldest thing, grayscale screenshot check.**
Gate: full regression; manual smoke incl. one phone over Tailscale, one xlsx through the pipeline, and one paper pack printed to PDF. Commit: `phase-9: v1.3`.

**Regression list (green in every phase from introduction onward):** all prior suites · schema/identifier-absence · edit-semantics state machine · stage-gate + no-bypass · barycentric maths · `patterns_20_anecdotes.json` byte-identical · landscape peaks ±0.02 · surface/contour single-source.

---

## 7. Acceptance criteria (definition of done, all checkable)

1. `Start Narrative Lens.bat` opens the app ≤15s, no terminal, QR on home.
2. In the Studio, every prompting question, corner/pole/axis/chip label, MCQ option, and respondent-facing string is editable with live preview; with zero stories, edits apply freely.
3. On a framework with stories, saving an edit forces the wording-fix / meaning-change choice; wording fixes appear in the edit log; a meaning change creates version n+1, old stories stay bound to the old wording, and mixed-version views show the version chip.
4. The paper pack prints from the browser as: one A4 story card (with the verbatim anonymity line and optional QR), one A4 sheet per signifier with exact labels at photocopier-safe black-on-white, and one facilitator sheet with the reconciliation grid — one sheet per page.
5. Paper batch entry lets a tester enter 5 fixture responses in under 4 minutes, each stamped input_method=paper.
6. A phone on Tailscale completes the wizard in <4 minutes at 375px; voice fallback works; reflection shows the respondent's dot; drafts survive reload; revoked links close.
7. All-format fixtures (docx, txt, pdf, pptx, xlsx 2-sheet, csv, vtt) pass Stage A with `NL_MOCK_AI=1`; the xlsx mapping screen's reconciliation matches the fixture; `/propose` is impossible before confirmation (409 by test); no anecdote reaches Patterns unvalidated (no-bypass test).
8. No record anywhere contains IP, user agent, name, or email; every CSV record carries full provenance including input_method and framework version.
9. **Patterns opens on the Landscape by default** with the hero layout; the golden triad renders as rotatable terrain with directly-labelled peaks; clicking the main peak lists exactly its stories; the contour twin derives from the identical grid; exports default to contour; peaks stable ±0.02.
10. Supporting charts obey the grammar: categorical views are horizontal bars sorted by value with direct labels, zero-based axes, ≤4 colors, and remain readable in a grayscale screenshot.
11. 3D Explorer plots any three dimensions; cluster overlay is deterministic and always labelled "descriptive only".
12. Fully offline: capture (typed/paper), validation, landscape, contour, supporting charts, paper-pack printing, and all exports work; Analyse buttons and voice fail plain-English with working fallbacks.
13. "What We Heard" suppresses slices <5; brief headlines are findings, not topics.
14. `pytest -q` green incl. both goldens · ruff 0 · eslint 0 · p95 < 200ms on non-AI endpoints (landscape at 5,000 anecdotes).
15. "SenseMaker", "Cynefin", "Cognitive Edge" appear nowhere except one README attribution line.

---

## 8. Verbatim prompts (copy-paste into Claude Code)

### Kickoff prompt (Phase 1 — start here)

```
You are building "Narrative Lens", a local-first narrative sense-making web app, from the PRD in PRD_Narrative-Lens_v1.3_20260814.md in this directory. Read that file completely before writing any code.

First actions, in order:
1. Create CLAUDE.md containing, verbatim, the thirteen binding constraints from PRD §2, plus: "The operator is non-technical. Every session: read CLAUDE.md and PROGRESS.md first, work in small verified steps, run the full test suite before claiming anything is done, and update PROGRESS.md and LATEST.md before ending."
2. Create PROGRESS.md (phase checklist from PRD §6) and LATEST.md (current state, next step).
3. Build Phase 1 exactly as specified in PRD §6: FastAPI + SQLAlchemy + SQLite + Alembic migration 001 (six-table schema in PRD §3, including edit_log_json, parent_framework_id, and the four-value input_method), pytest harness including the schema-absence test for respondent identifiers, ruff config, a /api/health endpoint, and "Start Narrative Lens.bat" that launches the server and opens the browser.
4. Gate: pytest -q fully green, ruff check . zero warnings. Show me the gate output.
5. Commit as "phase-1: skeleton, schema, launcher" and update PROGRESS.md and LATEST.md.

Do not build ahead of Phase 1. Do not add features not in the PRD. If the PRD is ambiguous, choose the simpler option and record the choice in PROGRESS.md under "Decisions".
```

### Resume prompt (any later session)

```
Continue building Narrative Lens. You have no memory of prior sessions; the files are the memory.

1. Read CLAUDE.md, PRD_Narrative-Lens_v1.3_20260814.md, PROGRESS.md, and LATEST.md.
2. Run the full test suite (pytest -q, and if the frontend exists, eslint) to verify the base is clean BEFORE changing anything. If anything is red, fix that first and tell me — do not start new work on a red base.
3. Build the next unchecked phase from PROGRESS.md, exactly per PRD §6, including its tests and gate.
4. Run the full regression list from PRD §6 (all prior suites, schema/identifier-absence, edit-semantics, stage-gate, no-bypass, barycentric maths, and both golden baselines where they exist).
5. Show me the gate output, commit with the phase's commit message, update PROGRESS.md and LATEST.md.

Never regenerate files wholesale to fix a small issue; make targeted edits. Never mark a phase complete without showing green gate output.
```

### Bug-fix prompt

```
There is a bug in Narrative Lens. Symptom: <<describe what you saw, in plain words>>.

1. Read CLAUDE.md and LATEST.md.
2. Reproduce the bug first — write a failing test that captures it. Show me the failing test output.
3. Fix it with the smallest change that makes that test pass.
4. Run the FULL regression: entire pytest suite, schema/identifier-absence, edit-semantics, stage-gate, no-bypass, both golden baselines, ruff, eslint. Show output.
5. Commit as "fix: <one line>" and log the bug + fix in PROGRESS.md under "Fixed".

Do not refactor unrelated code while fixing. If the fix requires a schema change, it must be a new additive Alembic migration, never an edit to an existing one.
```

---

## 9. Assumptions made (flagged, not asked)

1–7. Unchanged from v1.2 (Windows target; Tailscale present; one-time Python/Node install; browser voice acceptable with notice; single operator; imports pre-sanitised through your confidentiality gate; reflection shows one signifier).
8. **Landscape maths pinned** (Scott-bandwidth gaussian KDE, 64×64 grid, k-means seed 42) for determinism; revisit in v2 with real data.
9. **Deck ingestion is text-only** (slide text + notes); embedded images/charts ignored in v1.
10. **Per-sheet mapping handles mixed-role workbooks**; "ignore" sheets skipped whole.
11. **Paper packs use browser print, not a PDF library** — avoids fragile Windows dependencies (e.g., GTK for weasyprint) and gives you print preview for free. If pixel-perfect PDFs ever matter, that is a v2 decision.
12. **Wording-fix trust:** the app cannot verify that a "wording fix" truly preserves meaning — that judgement is yours; the edit log exists so it stays auditable.

## 10. Future upgrades — document, do not build

Unchanged from v1.2 (local Whisper; public-internet capture; non-leading AI follow-up probes; labelled AI theming; cross-wave landscape animation; signify-others mode; pulse waves; OCR; closure-aware statistics; commercial packaging behind the employment gate), plus: server-side pixel-perfect PDF packs · scanned-paper-response OCR entry (photograph the sticky-dot sheet, AI proposes the placements into the validation queue — a natural marriage of the paper pack and Stage B).

---

## 11. Changelog v1.2 → v1.3

Rationale: make the admin panel an explicit, guarded editing surface; support analogue elicitation end-to-end; establish the fitness landscape as the primary discovery view with a binding simple-and-elegant grammar for everything else.

1. §1 — Design tab elevated to **the Studio**: every question, label, and respondent-facing string editable with live preview, version history, and the **wording-fix vs meaning-change guardrail** (in-place logged edit vs new version with old data bound to old wording). New **paper pack** download (story card + per-signifier A4 sheets + facilitator sheet with reconciliation grid, browser-print based) and **paper batch entry** mode. Patterns restructured landscape-first with the **2D contour twin** and quiet supporting charts.
2. §2 — Constraint 3 gains input_method=paper and framework version. Constraint 9 extends the anonymity statement to the printed story card. New constraint 13: the visual grammar (landscape as sole bold element; decorative-3D ban with the data-bearing landscape as the only exception, contour twin mandatory and default for export; color/label/axis/accessibility rules; finding-style headlines; edit guardrail).
3. §3 — frameworks gains edit_log_json and parent_framework_id; anecdotes input_method becomes typed | voice | paper | imported.
4. §4 — Framework PUT now enforces edit_kind semantics (409 without it on live frameworks); new `/paper-pack` print endpoint; `/api/capture` accepts paper; patterns endpoints refuse silent version mixing; landscape endpoint serves surface + contour from one grid; brief headlines from finding-style templates (template text, not AI).
5. §5 — Tab 1 renamed Studio with the full editing surface and version sidebar; paper batch entry in Tab 2; Patterns opens on Landscape with the hero layout. New §5b binding design system (tokens, quiet test, supporting-chart grammar, 10-second test, accessibility floor, print grammar).
6. §6 — Phase 2 expands (Studio, tokens.css, edit-semantics, paper pack) and Phase 3 adds paper batch entry; Phase 7 builds supporting charts to grammar with a sort-order test; Phase 8 makes Landscape the default with the single-source surface/contour test; Phase 9 adds the critique pass and grayscale check. Regression list gains edit-semantics and surface/contour single-source.
7. §7 — Criteria grown 16 → 15 consolidated items covering Studio editing, the guardrail, paper pack printing, batch entry speed, landscape-default hero layout, contour twin, and supporting-chart grammar/grayscale.
8. §8 — Prompts reference v1.3 and thirteen constraints.
9. §9, §10 — New assumptions 11–12 (browser-print choice; wording-fix trust); Future gains pixel-perfect PDFs and scanned-paper OCR entry.

Unchanged from v1.2: the capture wizard and respondent experience, engineered anonymity, the two-stage ingestion pipeline and its gates, validation-queue doctrine, deterministic pattern mathematics, mock-first testing, additive migrations, and the trademark rule.
