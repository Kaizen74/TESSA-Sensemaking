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

echo
echo "ALL CHECKS PASSED"
