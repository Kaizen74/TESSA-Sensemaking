---
name: resilient-build
description: Govern Claude Code build sessions for a non-technical owner — persistent project state that survives interruptions and spending-cap cutoffs, checkpoint-and-resume discipline, mandatory regression testing after every change, backend-frontend contract alignment, anti-drift and anti-hallucination protocols, and plain-language documentation of every step. Use this skill for ANY coding session — building apps, scripts, dashboards, agents, or fixing bugs — whenever the user starts, resumes, or continues a software build. Trigger on "build the app", "continue where we left off", "resume the build", "fix this bug", or any Claude Code session in a project directory.
---

# Resilient Build

The owner of this project is non-technical. That changes everything: the project's memory, quality control, and documentation cannot live in the owner's head or in chat history — they must live in FILES in the repository, maintained by the model, current at all times. A session may be cut off at any moment (spending caps, closed laptop); the repository must always be one `git log` away from full recovery.

Read `references/judgment-protocols.md` before writing any code. Templates for all state files: `references/state-templates.md`. Testing rules: `references/testing-protocol.md`.

## The session loop (every session, no exceptions)

### 1. SESSION START — recover state before touching anything

1. Read `PROJECT_STATE.md` in the repo root. If it exists, say in plain language: what was done last time, what was in progress, what's next — then confirm the plan for this session in one short message
2. If it does NOT exist (new project): create it from the template, plus `DECISIONS.md` and `GUIDE.md`, before any code
3. Run `git status` and the check script (`./run_checks.sh` if present). If anything is broken from a previous interruption, fix that FIRST — never build on a broken base
4. Never rely on chat memory of previous sessions; the files are the truth. If chat memory and PROJECT_STATE.md disagree, the file wins

### 2. PLAN — small increments

Break the session goal into increments of ≤30 minutes each, ordered so that the project is in a working, committed state after every one. Write the increment list into PROJECT_STATE.md under "This session" before starting. Rule: if the cap cuts the session at any random moment, at most one increment of work is lost.

### 3. BUILD — one increment at a time

- Read files before editing them; never edit from memory of what a file "probably" contains
- Smallest change that achieves the increment; no refactors, upgrades, or "improvements" that weren't asked for (scope-lock — see judgment protocols)
- New libraries/APIs: verify they exist and check the installed version before using (see anti-hallucination rules)

### 4. TEST — after every increment, before calling it done

Run the full check script (see testing-protocol.md). ALL checks must pass — not just the new one. A fix that breaks something else is not a fix. Never mark an increment complete on the promise that tests "should" pass.

### 5. CHECKPOINT — commit + state update, every increment

1. `git add -A && git commit -m "<plain-language description of what now works>"`
2. Update PROJECT_STATE.md: move the increment to Done, set the next one as In Progress, refresh "How to resume"
3. Log any decision made (library chosen, approach changed, trade-off accepted) in DECISIONS.md with one-line reasoning

This is the resilience mechanism: commit + state update means any interruption, at any moment, loses at most the current half-increment.

### 6. SESSION END (or when the user says "wrap up")

1. Final checkpoint (commit + state update)
2. Update GUIDE.md: what the app now does, how to run it click-by-click, what changed today — written for a non-technical reader
3. Close with the plain-language report card: ✅ what got built · 🧪 test status (X of Y passing) · 📍 exact resume point · ▶ suggested next session goal

If a session is interrupted before this step, the per-increment checkpoints ensure nothing meaningful is lost — the next session's SESSION START recovers automatically.

## Communication rules (owner is non-technical)

- Explain in outcomes, not implementation ("the app now saves your scores between sessions", not "added SQLite persistence layer")
- Any question to the owner must be answerable without reading code: offer options in plain language with a recommendation
- Never ask the owner to run terminal commands without giving the exact command to copy-paste and stating what it will do and what success looks like
- Errors reported honestly: what broke, what it affects, what the fix plan is — no jargon walls, no minimizing
