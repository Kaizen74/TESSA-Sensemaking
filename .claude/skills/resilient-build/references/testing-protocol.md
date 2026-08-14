# Testing Protocol

## The check script (create in session 1, grow it forever)

Every project gets `run_checks.sh` in the repo root — one command that runs EVERYTHING: automated tests, a syntax/build check, and smoke tests. The owner can run it too ("type `./run_checks.sh` and press Enter — you want to see all green PASS lines").

```bash
#!/bin/bash
# run_checks.sh — run everything; exit non-zero on any failure
set -e
echo "1/3 Build/syntax check..."
[build or compile command]
echo "2/3 Automated tests..."
[test runner command]
echo "3/3 Smoke tests..."
[script that starts the app, hits key endpoints/screens, checks responses]
echo "ALL CHECKS PASSED ✅"
```

## Rules

1. **Test with the feature, not after the project.** Every increment that adds behavior adds at least one test for that behavior in the same increment. A feature without a test doesn't exist — it merely hasn't broken yet
2. **Full suite after every change.** Never run only the new test; regression is precisely the failure of OLD tests after NEW changes. All green or the increment is not done
3. **Mock external dependencies** (market-data APIs, LLM calls, email) so checks run free, fast, and offline. Keep one clearly-marked optional "live test" for real integrations, run only when the user asks — never in the default suite (it costs money and flakes)
4. **A failing test is information, never an obstacle.** Forbidden moves: deleting a failing test, skipping it, loosening its assertion to force green, or hard-coding the expected output. If a test SHOULD change because requirements changed, say so in plain language and log it in DECISIONS.md
5. **Fix verification standard:** a bug fix must include a test that fails before the fix and passes after — otherwise the "fix" is a guess
6. **Frontend-backend alignment check:** for projects with both, the smoke test must exercise at least one real end-to-end path (frontend call → backend → response rendered). Contract drift is caught here, not in production. Any API change follows the contract-first order: API_CONTRACT.md → backend → frontend → tests, one increment, one commit
7. **Report test results in owner language:** "12 of 12 checks passing — including the 3 new ones for the alert feature; nothing previously working has broken." Never bury a red test in a wall of output

## When checks fail at session start

Previous interruption may have left the base broken. Protocol: fix to green BEFORE any new work, even if the user asked for a new feature first — explain in one line why ("yesterday's cutoff left one check failing; fixing that first so we're building on solid ground — 10 minutes").
