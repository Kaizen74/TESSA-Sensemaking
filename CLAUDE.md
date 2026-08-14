# Narrative Lens — binding project instructions

The project is **Narrative Lens**, a local-first narrative sense-making web app.
The specification of record is `PRD_Narrative-Lens_v1.3_20260814.md` in this
directory. Read it before writing code.

The operator is non-technical. Every session: read CLAUDE.md and PROGRESS.md first, work in small verified steps, run the full test suite before claiming anything is done, and update PROGRESS.md and LATEST.md before ending.

---

## Binding constraints (restate these in every session)

Reproduced verbatim from PRD §2.

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

## Session protocol

- **Never build ahead of the current phase.** The phase list is PRD §6, tracked
  in `PROGRESS.md`. Do not add features that are not in the PRD.
- **Ambiguity rule.** If the PRD is ambiguous, choose the simpler option and
  record the choice in `PROGRESS.md` under "Decisions".
- **The gate is the definition of done.** `./run_checks.sh` must be fully green
  — `ruff check .` with zero warnings and `pytest -q` with zero failures —
  before any phase is marked complete. Never mark a phase complete without
  showing green gate output.
- **Never regenerate files wholesale** to fix a small issue; make targeted edits.
- **Schema changes are new additive Alembic migrations**, never edits to an
  existing migration (constraint 5). After `alembic revision --autogenerate`,
  run `ruff format` on the new revision file — raw autogenerate output exceeds
  the line limit and would fail the gate.
- **Regression list** (green in every phase from introduction onward): all prior
  suites · schema/identifier-absence · edit-semantics state machine · stage-gate
  + no-bypass · barycentric maths · `patterns_20_anecdotes.json` byte-identical ·
  landscape peaks ±0.02 · surface/contour single-source.

## Project skills

`.claude/skills/` carries three skills that govern this build:

- **resilient-build** — session loop, checkpoint discipline, testing protocol,
  anti-drift and anti-hallucination rules. Applies to every coding session.
- **web-design-dataviz** — design and visualisation standards. Applies from
  Phase 2 onward (tokens, widgets) and is the "design skill" referenced by the
  Phase 9 critique pass.
- **graphify** — knowledge-graph tooling for codebase questions.

---

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
