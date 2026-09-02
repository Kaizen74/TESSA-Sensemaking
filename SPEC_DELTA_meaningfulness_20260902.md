# Spec Delta: Meaningfulness | Status: DRAFT | Targets: PRD v1.3 §1, §2, §3, §4, §5, §6

This is a **delta**, not a replacement. `PRD_Narrative-Lens_v1.3_20260814.md` remains the specification of record for everything it already covers. This file adds to it. Where the two disagree, this delta wins for the six items named in §1 and the PRD wins everywhere else.

---

## 0. What you're getting (plain language)

Six changes that make the app's central claim — that meaning comes from the person who lived the experience — true in what you see, not just in what the database stores. The landscape will stop mixing stories people signified themselves with stories you signified on their behalf. Respondents will name their own stories. The Studio will critique your question design before you publish it, and the dashboard will warn you when respondents didn't understand a question rather than letting confusion look like consensus. A room will be able to interpret its own pattern together, with what they conclude stored as their words. And stories told in Malay, Tamil or Mandarin will stay in the language they were told in, translated only when you read them, never when the app calculates.

---

## 1. Scope

**IN:**

| # | Item | Phase |
|---|---|---|
| 1 | Landscape and patterns split by `signified_by`; self-signified is the default view | A |
| 2 | Respondent-chosen story title, replacing the machine-derived one when given | A |
| 3 | Framework design linter in the Studio (AI-calling, design-time only) | C |
| 4 | Data-quality signals: centre-parking and skip-rate detection | B |
| 5 | Collective sense-making mode — a room interprets its own pattern, stored as an artefact | D |
| 6 | Original-language preservation with read-time translation only | E, F |

**OUT (explicitly not built now):**
- Any change to the two-stage ingestion pipeline, the stage gate, or the validation queue's routing
- Any change to KDE parameters, grid size, bandwidth method, or the surface/contour single-source rule
- AI theming, clustering, or narration of story text (constraint 11 — permanently out)
- Automatic translation of stories at capture or at Stage B (constraint 14 below)
- Turning collective interpretations into significations, or letting them alter a landscape (constraint 15 below)
- Multi-user auth, cloud deployment, public-internet capture — unchanged from PRD §1 OUT
- Any retro-fitting of existing data: no fielded data exists yet, so no backfill is required or permitted

---

## 2. Binding constraints restated

Reproduced verbatim from `CLAUDE.md` / PRD §2. All thirteen remain in force. Constraints 8 and 12 are not directly implicated by this delta but are not suspended.

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
13. **The visual grammar.** (a) The landscape is the ONE bold element; everything else is quiet. (b) Decorative 3D is banned; the landscape is the sole exception because its z-axis encodes data, and it must always offer its 2D contour twin, which is the default for print/export. (c) Per chart: ≤4 colors — one data hue, one accent, gray for context; sequential colorblind-safe scale for the terrain; never red/green as primary encoding; must survive grayscale. (d) Categorical comparisons are horizontal bars sorted by value; bar axes start at zero; direct labels beat legends; no decorative gridlines or icons. (e) WCAG AA contrast, ≥12px chart text, keyboard-reachable interactions. (f) Export and brief headlines state findings, never topics. (g) Wording edits to live frameworks follow the wording-fix vs meaning-change guardrail — no silent in-place semantic changes, ever.

**Three new constraints, added by this delta. Append these to `CLAUDE.md` in Phase A.**

14. **Self-signification is visible, not merely recorded.** Every view that aggregates significations must state whose interpretation it is showing. The default for every pattern, landscape, contour and export is `signified_by = participant` only. Expert-validated points (`ai_validated`) are shown only when explicitly selected, and any view containing them carries a visible label saying so. A view may never silently mix the two.
15. **The original language is the record.** Significations attach only to the text as told. Translation is read-time, display-only, always labelled as a translation, never stored as the story, never sent to Stage B, and never used to compute anything. A translated text is never signified by anyone.
16. **Collective interpretation is an artefact, not data.** What a room concludes about a pattern is stored as an interpretation note bound to a framework, a filter state and a timestamp, in the room's own words. It never becomes a signification, never enters the KDE, and never changes a landscape. It is reported alongside the pattern, never merged into it.

---

## 3. Data model changes

All additive. Four new migrations, applied in phase order. Each `downgrade()` removes only what its own migration added.

**Migration 002 — `respondent_title` (Phase A)**
```
anecdotes.respondent_title   TEXT NULL
```
Display rule: `respondent_title` when present, else `title_auto`. Never overwrite `title_auto`; both are retained and both are exported.

**Migration 003 — language fields (Phase E)**
```
anecdotes.language_code      TEXT NULL     -- BCP-47, e.g. "en", "ms", "ta", "zh-Hans"
anecdotes.language_source    TEXT NULL     -- "respondent_selected" | "admin_entered" | "unknown"
```
No column stores a translation. Translations are computed at read time and never persisted in Phase E; see Phase F for the cache decision.

**Migration 004 — translation cache (Phase F)**
```
translations   id · anecdote_id (FK) · target_language_code · translated_text
               · translated_at · model_used
               UNIQUE (anecdote_id, target_language_code)
```
This is a display cache only. Deleting every row must leave the app fully correct, only slower. A test must assert that no aggregation, KDE, export-of-record, or Stage B input reads this table.

**Migration 005 — collective interpretations (Phase D)**
```
interpretations   id · framework_id (FK) · signifier_id · filter_state_json
                  · view_kind (landscape | contour | supporting)
                  · session_label · interpretation_text · recorded_at
                  · participant_count (integer, nullable)
```
No foreign key to `anecdotes` and no `signification` linkage — by design, per constraint 16.

---

## 4. API contract

Error shape unchanged: `{"error": {"code": "...", "message": "plain-English sentence", "action": "what to do"}}`.

| Endpoint | Method | Change | Notes |
|---|---|---|---|
| `/api/patterns/{framework_id}` | GET | Accepts `signified_by` filter. Absent → defaults to `participant`. Accepts `participant`, `ai_validated`, `all`. Response gains `signified_by_applied` and `counts_by_signified_by` so the UI can label honestly | 200ms |
| `/api/landscape/{framework_id}/{triad_id}` | GET | Same filter, same default, same two response fields | 200ms |
| `/api/explorer/{framework_id}` · `/api/clusters/{framework_id}` | GET | Same filter, same default | 200ms |
| `/api/capture` · `/api/s/{token}/submit` | POST | Accept optional `respondent_title` (≤120 chars) and optional `language_code` | 200ms |
| `/api/frameworks/{id}/lint` | POST | **AI-calling.** Returns design critique of the framework's current definition_json | async; exempt from 200ms; must not block |
| `/api/stories/{anecdote_id}/translation` | GET | **AI-calling.** `?target=en`. Returns translated display text plus `is_translation: true` and the original | async; exempt from 200ms |
| `/api/quality/{framework_id}` | GET | Centre-parking and skip-rate signals per signifier | 200ms; pure local computation, no AI |
| `/api/interpretations` | GET/POST | List / record a collective interpretation | 200ms |
| `/api/export/csv` `/brief` `/heard` | GET | Gain `signified_by` filter with the same default; CSV gains `respondent_title`, `language_code`; brief gains an interpretations section when any exist for the framework | 200ms |

### 4a. New AI calls — both through `ai_client.request_json`, both mocked

**Design linter** (`/api/frameworks/{id}/lint`). Input: the framework's `definition_json`. The system prompt asks Claude to critique the *design*, never to produce or judge data. Checks returned as a list of findings, each with `severity` (info | warning), `location` (field path), `finding`, and `suggestion`:
- Does any triad have a corner a respondent would read as the "right" answer, making the other two decoys?
- Are the three corners mutually exhaustive enough that a real story can be placed, and tensioned enough that placement requires a trade-off?
- Does any dyad pole carry evaluative loading (one end obviously good)?
- Does the prompting question embed a hypothesis, or lead toward a desired kind of story?
- Are any labels longer than roughly six words, or above a plain-reading level appropriate to a frontline workforce?

Findings are advisory. **The linter can never block publishing and never edits the framework** — it reports, you decide. Mock fixture: `tests/fixtures/mock_lint_response.json`. Model, temperature, parse and repair identical to existing stages.

**Read-time translation** (`/api/stories/{id}/translation`). Input: the original story text and a target language. Returns translated text only. The response must carry `is_translation: true` and the original text alongside, so the UI cannot display a translation unlabelled. Mock fixture: `tests/fixtures/mock_translation_response.json`.

Both endpoints fail gracefully per constraint 6: plain-English message, the underlying view still works, no partial state written.

---

## 5. Frontend changes

**Untouched:** the capture wizard's screen sequence and timing, all signifier widgets, the import pipeline UI, the validation queue, the paper pack, the QR/link manager, kiosk mode, `tokens.css`.

**Patterns tab (Phase A).** A signifier-provenance control in the filter rail, defaulting to "Told and interpreted by the storyteller". When anything other than the default is selected, a persistent label appears above the landscape naming what is being shown. Follow the `web-design-dataviz` skill: this label is context-weight, not a bold alert, and the control is a segmented three-option control, not a dropdown, because the choice is epistemic and should be visible without a click.

**Capture wizard, story screen (Phase A).** One optional single-line field beneath the story box: "If you gave this story a name, what would it be?" — placeholder empty, skippable, no validation beyond length. It must not add a screen and must not push the story box above the fold at 375px. Appears identically in admin capture, remote link, kiosk, and paper batch entry, and is added to the printed story card in the paper pack.

**Studio (Phase C).** A "Check this design" button beside the publish control. Findings render in a quiet panel grouped by severity, each naming the field it refers to and offering the suggestion as text you can copy — never as a one-click apply. The panel states plainly that these are suggestions about question design, not about data.

**Patterns tab, quality panel (Phase B).** A collapsed-by-default panel below the supporting charts: per signifier, the proportion of placements within a small radius of the triad centroid, and the proportion of respondents who skipped it. Presented as counts and proportions with a plain-English reading note ("high centre-clustering often means the question didn't fit the stories"). Per constraint 13a this panel is quiet and never competes with the landscape; per constraint 11 it reports computed proportions and offers no interpretation of what the pattern means.

**Session mode (Phase D).** A projector-friendly view reachable from the Patterns tab: the landscape at full screen with controls hidden, plus a side panel where you type what the room concludes. Recording an interpretation captures the current filter state and signifier automatically. Existing interpretations appear as a list beneath the landscape in normal mode, in the room's words, timestamped and labelled with the filter they were made under.

**Story display (Phase E/F).** Every story shown anywhere displays its language when known. Where a translation is available, a toggle shows it with a persistent "translated — the original is above" label. The original is always the primary text; the translation is always secondary weight.

---

## 6. Phased build plan

Every phase: one session, ends with `./run_checks.sh` fully green, plus the phase's own tests, plus the full regression list. Every phase updates `PROGRESS.md` and `LATEST.md` before ending. The `resilient-build` skill governs the session loop throughout; `web-design-dataviz` governs Phases A, B, D and F wherever UI is touched.

### CRITICAL — golden baseline handling (read before Phase A)

Phase A changes the **default** filter on patterns and landscape endpoints. The existing golden tests (`patterns_20_anecdotes.json`, landscape peaks ±0.02) call these endpoints without a `signified_by` parameter and would therefore silently start measuring a different population. **Do not regenerate the goldens.** Instead:

1. Update the existing golden tests to pass `signified_by=all` explicitly. Their expected values must remain **byte-identical**. If any value changes, something else broke — stop and investigate rather than regenerate.
2. Add a **new** golden, `patterns_20_anecdotes_participant.json`, capturing the new default view, generated once via `tests/regenerate_golden.py` and thereafter byte-identical.
3. `tests/regenerate_golden.py` must not be run for the pre-existing baselines in any phase of this delta.

A phase that regenerates an existing golden has failed its gate regardless of what the test output says.

---

**Phase A — Provenance made visible + respondent title.** (Items 1, 2)
Migration 002. Add `signified_by` to `FILTERABLE` in `backend/patterns.py` and apply the default to patterns, landscape, explorer, clusters and all three exports. Add `respondent_title` through capture, submit, story browser, drill drawer, paper story card and CSV. Add constraints 14–16 to `CLAUDE.md`.
Tests: `test_signification_provenance.py` — default view excludes every `ai_validated` point; `all` returns both; `counts_by_signified_by` matches a hand-computed fixture; no export path bypasses the default. `test_respondent_title.py` — title round-trips from all four capture paths, display falls back to `title_auto`, `title_auto` is never overwritten, 120-char limit enforced, paper card renders the field. Golden handling per the block above.
Gate: `./run_checks.sh` green · both goldens · full regression. Commit: `delta-A: signification provenance visible + respondent title`.

**Phase B — Data-quality signals.** (Item 4)
No schema change; skips are derivable from absent signification rows. Add `backend/quality.py` and `/api/quality/{framework_id}`; add the quiet panel.
Tests: `test_quality_signals.py` — centre-parking proportion correct on a fixture where placements are deliberately clustered at the centroid; skip rate correct where a signifier has no rows for some anecdotes; the endpoint is pure-local and makes no AI call under `NL_MOCK_AI=0` with no key present; panel respects the visual grammar (quiet weight assertion in the frontend test).
Gate: full regression. Commit: `delta-B: data-quality signals`.

**Phase C — Framework design linter.** (Item 3)
Extend `ai_client.py` with the lint call and its mock fixture. Add `/api/frameworks/{id}/lint` and the Studio panel.
Tests: `test_design_linter.py` — mock returns findings and they render; the endpoint never writes to `frameworks`; publishing succeeds with findings outstanding (linter cannot block); malformed JSON triggers one repair then a plain-English failure that leaves the Studio usable; `NL_MOCK_AI=1` covers the whole path with zero network. Add an assertion that the lint prompt receives only `definition_json` and never any anecdote text.
Gate: full regression. Commit: `delta-C: framework design linter`.

**Phase D — Collective sense-making mode.** (Item 5)
Migration 005. `/api/interpretations` GET/POST; projector view; interpretation list; brief export section.
Tests: `test_interpretations.py` — recording captures signifier and filter state; an interpretation never appears in any signification query; landscape output is byte-identical before and after recording one (this is the constraint-16 guard); the brief includes interpretations verbatim and attributes them to the room, not the analyst; projector view hides controls and is keyboard-escapable.
Gate: full regression including the byte-identical landscape assertion. Commit: `delta-D: collective sense-making mode`.

**Phase E — Language of record.** (Item 6, part 1)
Migration 003. Language selection on the capture welcome screen (a short list configured per framework in the Studio, defaulting to English only so nothing changes for existing frameworks); language displayed wherever a story is shown; language added to CSV and to `FILTERABLE`.
Tests: `test_language_capture.py` — language round-trips from all capture paths; absent language renders as unknown rather than assuming English; Stage B receives original text only; a story's `language_code` never affects any computation; filter works.
Gate: full regression. Commit: `delta-E: original language of record`.

**Phase F — Read-time translation.** (Item 6, part 2)
Migration 004. Translation endpoint with mock; cache table; UI toggle with the permanent translation label.
Tests: `test_translation_readtime.py` — the translated text is never stored in `anecdotes`; deleting all cache rows leaves every pattern, export and landscape byte-identical (the cache-is-display-only guard); no aggregation or Stage B path reads `translations`; the UI cannot render a translation without its label (assert the label is in the same component and not conditionally hidden); offline failure leaves the original readable.
Gate: full regression including the cache-deletion equivalence test. Commit: `delta-F: read-time translation`.

**Regression list — green in every phase of this delta, in addition to the existing list:**
all prior suites · schema/identifier-absence · edit-semantics state machine · stage-gate + no-bypass · barycentric maths · `patterns_20_anecdotes.json` byte-identical **with `signified_by=all`** · `patterns_20_anecdotes_participant.json` byte-identical (from Phase A) · landscape peaks ±0.02 · surface/contour single-source · default-view-excludes-validated (from Phase A) · landscape-unchanged-by-interpretation (from Phase D) · cache-deletion-equivalence (from Phase F).

---

## 7. Acceptance criteria

1. With a framework containing both participant-signified and validated stories, the Patterns tab on first load shows only participant-signified points, states so on screen, and reports both counts.
2. Selecting "all" or "expert-validated" changes the landscape and displays a persistent label naming what is shown; no view can present a mixed population without that label.
3. All three exports honour the same default; a CSV taken without changing filters contains no `ai_validated` significations.
4. A respondent can name their story in under ten seconds from any capture path, the name appears in the story browser and drill drawer, and stories without one still display correctly.
5. The paper story card includes the story-name line and still prints one sheet per page in black and white.
6. The quality panel reports centre-parking and skip rates that match hand computation on the fixture, sits below the supporting charts, and never competes visually with the landscape.
7. The design linter returns findings for a deliberately badly designed fixture framework (one triad with an obviously correct corner, one evaluative dyad, one leading prompt), cannot edit the framework, cannot block publishing, and never receives story text.
8. A collective interpretation can be recorded from the projector view, appears verbatim in the interpretation list and the Pattern Brief, and leaves the landscape output byte-identical.
9. A story captured in a non-English language stores and displays that language, is signified in its original text only, and its translation — when requested — is labelled as a translation with the original still primary.
10. Deleting every row from `translations` changes nothing except speed; a test proves it.
11. `NL_MOCK_AI=1` exercises the linter and the translation endpoint with zero network; with networking disabled both fail in plain English and leave their views usable.
12. `./run_checks.sh` fully green · `ruff check .` zero warnings · `eslint` zero warnings · p95 < 200ms on all non-AI endpoints including `/api/quality` and `/api/interpretations`.
13. Every golden baseline that existed before this delta is byte-identical to its pre-delta value, verified with `signified_by=all`.

---

## 8. Verbatim prompts

### Kickoff prompt (Phase A — start here)

```
Read CLAUDE.md, PRD_Narrative-Lens_v1.3_20260814.md, PROGRESS.md and LATEST.md first. Then read SPEC_DELTA_meaningfulness_20260902.md in this directory completely. It is a delta on the PRD, not a replacement — the PRD stands for everything the delta does not name.

Before writing any code:
1. Run ./run_checks.sh to confirm the base is green. If anything is red, fix that first and tell me — do not start new work on a red base.
2. Append constraints 14, 15 and 16 from delta §2 verbatim to CLAUDE.md.
3. Add the delta's six phases (A–F) to PROGRESS.md as an unchecked list.

Then build Phase A exactly as specified in delta §6, and nothing beyond it.

CRITICAL: Phase A changes the default filter on the patterns and landscape endpoints. Read the "golden baseline handling" block in delta §6 before touching any test. You must NOT regenerate patterns_20_anecdotes.json or the landscape peak baseline. Update those tests to pass signified_by=all explicitly and prove their values are unchanged. Add a new participant-only golden alongside them. If an existing golden value changes, stop and tell me — that is a bug, not an expected update.

Gate: ./run_checks.sh fully green, plus every test in the delta's regression list. Show me the gate output. Then commit as "delta-A: signification provenance visible + respondent title" and update PROGRESS.md and LATEST.md.

If the delta is ambiguous, choose the simpler option and record the choice in PROGRESS.md under "Decisions".
```

### Resume prompt (Phases B–F, any later session)

```
Continue the meaningfulness delta on Narrative Lens. You have no memory of prior sessions; the files are the memory.

1. Read CLAUDE.md, PRD_Narrative-Lens_v1.3_20260814.md, SPEC_DELTA_meaningfulness_20260902.md, PROGRESS.md and LATEST.md.
2. Run ./run_checks.sh to verify the base is clean BEFORE changing anything. If anything is red, fix that first and tell me — do not start new work on a red base.
3. Build the next unchecked delta phase from PROGRESS.md, exactly per delta §6, including its named tests and its gate. Do not build ahead into a later phase.
4. Run the full regression list from delta §6 — this includes the pre-delta baselines, which must stay byte-identical. Never regenerate a golden to make a test pass; a changed golden means a bug.
5. Show me the gate output, commit with the phase's commit message, and update PROGRESS.md and LATEST.md.

Never regenerate files wholesale to fix a small issue; make targeted edits. Schema changes are new additive Alembic migrations, never edits to existing ones, and run ruff format on any autogenerated revision file. Never mark a phase complete without showing green gate output.
```

### Bug-fix prompt

```
There is a bug in Narrative Lens. Symptom: <<describe what you saw, in plain words>>.

1. Read CLAUDE.md, LATEST.md and SPEC_DELTA_meaningfulness_20260902.md.
2. Reproduce the bug first — write a failing test that captures it. Show me the failing test output.
3. Fix it with the smallest change that makes that test pass.
4. Run the FULL regression from delta §6: the whole pytest suite, schema/identifier-absence, edit-semantics, stage-gate, no-bypass, barycentric maths, both patterns goldens, landscape peaks, surface/contour single-source, default-view-excludes-validated, landscape-unchanged-by-interpretation, and cache-deletion-equivalence where they exist. Show output.
5. Commit as "fix: <one line>" and log the bug and fix in PROGRESS.md under "Fixed".

Do not refactor unrelated code while fixing. Do not regenerate any golden baseline. If the fix requires a schema change, it must be a new additive Alembic migration.
```

---

## 9. Assumptions made

1. **No fielded data exists**, so no backfill, no data migration, and no reinterpretation of existing significations is needed. If real data has been collected before Phase A runs, tell the model — the default-view change would alter what you already believe about that dataset.
2. **The linter calls Claude at design time only.** It never sees anecdote text and never touches a signification, so constraint 11 is not implicated. It costs one API call per check.
3. **Translation is on demand, per story, per target language** — not a batch operation over a dataset. This keeps cost proportional and keeps the "display-only" claim easy to test.
4. **Language lists are per framework**, defaulting to English alone, so nothing changes for a framework you don't configure.
5. **Interpretations are free text**, not structured. A room's conclusion resists a schema, and forcing one would be the same error as machine-coding a story.
6. **Phase order is by dependency and value, not urgency.** If frontline multilingual capture becomes the binding need before the linter does, E and F can be moved ahead of C and D without conflict — they share no code. A and B should stay first.
7. **`respondent_title` is treated exactly like story text for anonymity purposes.** A respondent could type a name into it, as they could into the story; the anonymity claim covers what the system collects, not what a person volunteers, and that claim is unchanged.

---

## 10. Future upgrades — document, do not build

Cross-wave landscape comparison and drift animation (the natural successor once two waves exist) · scanned-paper OCR entry feeding Stage B · an empirical linter that learns from your own quality-signal history rather than critiquing from first principles · interpretation-versus-pattern divergence reporting (where a room read the terrain differently from what the maths suggests) · per-language landscape comparison to test whether meaning travels across languages · packaging the linter's rule set as standalone IP.
