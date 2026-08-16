#!/usr/bin/env bash
# run_checks.sh — the Phase gate in one command.
#
# Runs everything: the linter, the whole test suite, and a live smoke test that
# actually starts the server and calls it. Green here is the only thing that
# licenses marking a phase complete.
#
# Usage:  ./run_checks.sh
# Success looks like: "ALL CHECKS PASSED" and an exit code of 0.

set -euo pipefail

cd "$(dirname "$0")"

# Constraint 6: the gate runs with zero network. Nothing here may reach
# api.anthropic.com — the AI stages run against their mocks.
export NL_MOCK_AI=1

PYTHON="${PYTHON:-python3}"
SMOKE_PORT="${NL_SMOKE_PORT:-8757}"
TMPDIR_SMOKE="$(mktemp -d)"
SERVER_PID=""

cleanup() {
    if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    rm -rf "$TMPDIR_SMOKE"
}
trap cleanup EXIT

echo "1/5 Lint, backend (ruff)..."
$PYTHON -m ruff check .

echo "2/5 Lint, frontend (eslint)..."
if [[ -d frontend/node_modules ]]; then
    (cd frontend && npx eslint .)
else
    echo "  skipped — run 'npm install' in frontend/ first"
fi

echo "3/5 Automated tests (pytest)..."
$PYTHON -m pytest -q

echo "4/5 Frontend build..."
if [[ -d frontend/node_modules ]]; then
    (cd frontend && npm run build --silent >/dev/null)
    echo "  frontend built"
else
    echo "  skipped — run 'npm install' in frontend/ first"
fi

echo "5/5 Smoke test (server starts and answers)..."
# A throwaway database, so the smoke test never touches the operator's data.
export NL_DATABASE_URL="sqlite:///${TMPDIR_SMOKE}/smoke.db"
$PYTHON -m alembic upgrade head >/dev/null
$PYTHON -m uvicorn backend.main:app \
    --host 127.0.0.1 --port "$SMOKE_PORT" --log-level warning &
SERVER_PID=$!

health_url="http://127.0.0.1:${SMOKE_PORT}/api/health"
for _ in $(seq 1 40); do
    if curl -sf "$health_url" >/dev/null 2>&1; then
        break
    fi
    sleep 0.25
done

body="$(curl -sf "$health_url")" || {
    echo "  FAIL: the server did not answer on ${health_url}"
    exit 1
}

case "$body" in
    *'"status":"ok"'*) echo "  /api/health -> $body" ;;
    *)
        echo "  FAIL: unexpected health response: $body"
        exit 1
        ;;
esac

# One real end-to-end path: create a framework, then print its paper pack.
# This is what catches a frontend/backend contract drift that unit tests miss.
base="http://127.0.0.1:${SMOKE_PORT}/api/frameworks"
created="$(curl -sf -X POST "$base" \
    -H 'Content-Type: application/json' \
    -d '{"name":"Smoke test","definition":{"triads":[{"id":"t1","title":"What drove this?","corners":["Speed","Care","Cost"]}]}}')" || {
    echo "  FAIL: could not create a framework"
    exit 1
}

framework_id="$(printf '%s' "$created" | $PYTHON -c 'import json,sys; print(json.load(sys.stdin)["id"])')"
echo "  created framework $framework_id"

pack="$(curl -sf "${base}/${framework_id}/paper-pack")" || {
    echo "  FAIL: paper pack did not render"
    exit 1
}

case "$pack" in
    *"page-break-after: always"*) echo "  paper pack renders with page breaks" ;;
    *)
        echo "  FAIL: paper pack is missing its print rules"
        exit 1
        ;;
esac

# One real file all the way through the import machine, over HTTP. This is the
# path acceptance criterion 7 names, and it is where a contract drift between
# the Mapping screen and the server would show up.
imports="http://127.0.0.1:${SMOKE_PORT}/api/import"
cat > "${TMPDIR_SMOKE}/smoke.csv" <<'CSV'
Team,Story
Ops,"We were three hours from the deadline when the parts finally arrived."
Deck,"The checklist assumed you had both hands free, which on a wet deck you never do."
Support,""
CSV

uploaded="$(curl -sf -X POST "$imports" -F "file=@${TMPDIR_SMOKE}/smoke.csv")" || {
    echo "  FAIL: could not import a CSV"
    exit 1
}
job_id="$(printf '%s' "$uploaded" | $PYTHON -c 'import json,sys; print(json.load(sys.stdin)["id"])')"

# The stage gate: confirming before organising must be refused, not ignored.
gate="$(curl -s -o /dev/null -w '%{http_code}' -X POST "${imports}/${job_id}/mapping" \
    -H 'Content-Type: application/json' -d '{"sheets":[]}')"
if [[ "$gate" != "409" ]]; then
    echo "  FAIL: the stage gate let a mapping through before Organise (got $gate)"
    exit 1
fi
echo "  stage gate refuses a mapping before Organise"

organised="$(curl -sf -X POST "${imports}/${job_id}/organise")" || {
    echo "  FAIL: Stage A did not run"
    exit 1
}
mapping_body="$(printf '%s' "$organised" | $PYTHON -c '
import json, sys

keys = ("sheet", "role", "story_column", "respondent_group_column", "title_column")
sheets = json.load(sys.stdin)["organisation"]["sheets"]
print(json.dumps({"sheets": [{k: s[k] for k in keys} for s in sheets]}))
')"

confirmed="$(curl -sf -X POST "${imports}/${job_id}/mapping" \
    -H 'Content-Type: application/json' -d "$mapping_body")" || {
    echo "  FAIL: the mapping could not be confirmed"
    exit 1
}

printf '%s' "$confirmed" | $PYTHON -c '
import json, sys

job = json.load(sys.stdin)
tally = job["confirmation"]["reconciliation"]
counted = sum(line["count"] for line in tally["lines"])
assert job["stage"] == "mapping_confirmed", job["stage"]
assert tally["balanced"] is True, tally
assert counted == tally["total"] == 3, tally
assert job["confirmation"]["candidate_count"] == 2, job["confirmation"]
print(f"  csv through the machine: {counted} rows, all accounted for")
' || {
    echo "  FAIL: the reconciliation did not add up"
    exit 1
}

# Stage B, and the door it has to wait behind. The whole of constraint 1 in one
# sequence: mark up, find the stories waiting rather than counted, say yes to
# one, and watch that be the only thing that changes.
marked="$(curl -sf -X POST "${imports}/${job_id}/propose" \
    -H 'Content-Type: application/json' -d "{\"framework_id\": ${framework_id}}")" || {
    echo "  FAIL: Stage B did not run"
    exit 1
}
printf '%s' "$marked" | grep -q '"stage":"proposed"' || {
    echo "  FAIL: the file did not reach the proposed stage"
    exit 1
}

queue_url="http://127.0.0.1:${SMOKE_PORT}/api/queue"
waiting="$(curl -sf "$queue_url")" || {
    echo "  FAIL: the validation queue did not answer"
    exit 1
}

story_id="$(printf '%s' "$waiting" | $PYTHON -c '
import json, sys

view = json.load(sys.stdin)
assert view["counts"]["validated"] == 0, view["counts"]
assert view["counts"]["pending"] == 2, view["counts"]
for item in view["items"]:
    assert item["status"] == "pending_validation", item["status"]
    assert item["significations"], "Stage B proposed nothing"
    for placement in item["significations"]:
        assert placement["signified_by"] == "ai", placement
        assert placement["validated_at"] is None, placement
print(view["items"][0]["anecdote_id"])
')" || {
    echo "  FAIL: Stage B put something into the data without asking"
    exit 1
}
echo "  stage B queued 2 stories, none of them data yet"

curl -sf -X PUT "${queue_url}/${story_id}" \
    -H 'Content-Type: application/json' -d '{"action":"accept"}' >/dev/null || {
    echo "  FAIL: the story could not be accepted"
    exit 1
}

curl -sf "$queue_url" | $PYTHON -c '
import json, sys

counts = json.load(sys.stdin)["counts"]
assert counts == {"pending": 1, "validated": 1, "rejected": 0}, counts
print("  saying yes to one story validated exactly that one")
' || {
    echo "  FAIL: the queue decision did not land as expected"
    exit 1
}

echo
echo "ALL CHECKS PASSED"
