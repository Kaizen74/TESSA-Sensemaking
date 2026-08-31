# Judgment Protocols — Anti-Drift & Anti-Hallucination

These rules encode the discipline that separates frontier-quality coding sessions from chaotic ones. Follow them literally; they are mandatory, not advisory. They matter MOST for long sessions and smaller models — exactly where drift and hallucination creep in.

## Anti-hallucination

1. **Never code against imagined interfaces.** Before using any library function, verify it: check the installed version (`pip show X` / `package.json`), and read the actual signature (its docs, source, or a quick REPL check). Plausible-but-nonexistent methods are the #1 hallucination failure
2. **Read before you edit.** Open the actual file and find the actual line before changing it. Never patch from memory of what the code "probably" says — memory of code is reconstruction, not recall
3. **Claims about the codebase cite file:line.** "The scoring logic is in engine.py line 40–75" — if the model can't point to it, it doesn't get asserted
4. **Error messages are read, not pattern-matched.** Quote the actual error line, locate the actual failing line, THEN diagnose. Forbidden: "this is usually caused by X" fixes applied without confirming X is present
5. **Uncertainty is stated, then resolved by checking** — not papered over with confident prose. "I'm not sure this API accepts batch requests — checking its docs now" is frontier behavior; guessing is not
6. **No invented data.** Placeholder/sample data is always labeled as such in code comments and in the GUIDE; never present fabricated output as real results

## Anti-drift

7. **Scope lock.** Build what was asked, exactly. Adjacent "improvements" (refactors, upgrades, restyling, extra features) are proposed in one line and done only if the owner says yes. Unrequested changes are how working code breaks mysteriously
8. **Re-anchor every 5 increments or 30 minutes:** re-read PROJECT_STATE.md's "What this project is" and the current session goal. If current work doesn't serve the session goal, stop and say so
9. **Settled decisions stay settled.** Check DECISIONS.md before proposing a change of library, structure, or approach; reversals require new information, stated explicitly, and a new log entry
10. **One increment in flight at a time.** Never start increment 3 while increment 2 has failing checks. Parallel half-done work is the interruption-vulnerability this skill exists to eliminate
11. **Consistency beats novelty.** New code follows the patterns already in the codebase (naming, structure, error handling) even when the model prefers another style. A codebase with three styles is drift made visible
12. **The diff review.** Before every commit, review the actual diff (`git diff --staged`) and confirm every changed line relates to the increment. Unexplained changes are removed, not committed

## Escalation honesty

13. **Three failed attempts on the same bug → stop and report:** what was tried, what the model now believes the cause is, and 2–3 options (including "revert to the last working commit"). Endless silent retry loops burn the owner's budget and trust
14. **Budget awareness:** if a requested feature will foreseeably take many sessions, say so before starting, and structure increments so value ships early ("scoring works end-to-end in session 2; polish comes later")
15. **Never claim done what isn't verified.** "Done" means: checks green, committed, state file updated, guide updated. Anything less is reported as its actual state
