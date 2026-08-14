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

echo "1/3 Lint (ruff)..."
$PYTHON -m ruff check .

echo "2/3 Automated tests (pytest)..."
$PYTHON -m pytest -q

echo "3/3 Smoke test (server starts and answers)..."
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

echo
echo "ALL CHECKS PASSED"
