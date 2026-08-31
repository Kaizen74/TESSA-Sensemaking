# State File Templates

Four files live in the repo root. The model creates them on first session and maintains them every session. They are the project's memory — chat history is NOT.

## PROJECT_STATE.md (the resume file — most important)

```markdown
# Project State
*Last updated: [date time] — update after EVERY increment*

## What this project is
[2-3 plain-language sentences: what the app does and for whom]

## Current status
[One sentence: e.g., "Scoring engine works; building the results screen."]

## This session
- [x] Increment 1 — [done]
- [ ] Increment 2 — IN PROGRESS: [exactly what's half-done, which file]
- [ ] Increment 3 — [next]

## Done (all sessions)
- [date] [what works now, plain language]

## Not started yet
- [remaining backlog items]

## How to resume (write this as if for a stranger)
1. The next task is: [specific]
2. The relevant files are: [paths]
3. Watch out for: [any trap, half-finished edit, or failing check]
4. Run `./run_checks.sh` first — all should pass except [known exceptions, if any]

## Known issues
- [anything broken, deferred, or fragile — never leave this section silently empty if issues exist]
```

## DECISIONS.md (why things are the way they are)

```markdown
# Decisions Log
| Date | Decision | Why | Alternative rejected |
|---|---|---|---|
| [date] | Used SQLite for storage | Free, no server needed, fits single-user app | Cloud database (overkill, monthly cost) |
```
One line per decision. This prevents future sessions from re-litigating or silently reversing settled choices — a major drift source.

## GUIDE.md (the owner's manual — plain language only)

```markdown
# [App name] — Owner's Guide
*Updated: [date]*

## What this app does
[Plain language, no jargon]

## How to start it (click by click)
1. Open Terminal (or: double-click [file])
2. Type exactly: `[command]` and press Enter
3. You'll know it worked when: [what appears]
4. Open your browser to: [address]

## How to use it
[Numbered steps per feature, written for someone seeing it fresh]

## What changed recently
- [date]: [change in plain language]

## If something goes wrong
- [Symptom] → [exact steps to fix or recover]
- To stop the app: [exact steps]

## Glossary
[Every technical term that unavoidably appears, defined in one line]
```

## API_CONTRACT.md (only for projects with a backend + frontend)

```markdown
# API Contract
*Any change here requires updating BOTH backend and frontend in the SAME session — never leave them misaligned at a checkpoint.*

## Endpoints
### GET /api/scores
Returns: `[{"ticker": "TSM", "score": 87, "verdict": "High Conviction"}]`
Used by: results screen (frontend/src/Results.jsx)

[one block per endpoint: method, path, request shape, response shape, which frontend components consume it]
```

Rule: the contract file is edited FIRST when an interface changes, then backend, then frontend, then tests — all within one increment.
