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

# The read side: patterns counted from validated stories only, and the two
# exports that have to agree with what is on screen.
patterns="$(curl -sf "http://127.0.0.1:${SMOKE_PORT}/api/patterns/${framework_id}")" || {
    echo "  FAIL: the patterns endpoint did not answer"
    exit 1
}

printf '%s' "$patterns" | $PYTHON -c '
import json, sys

view = json.load(sys.stdin)
assert view["total"] == 1, view["total"]          # only the accepted story
assert view["mixed"] is False, view
# Constraint 14: asked nothing, the endpoint answers with the storytellers own
# readings, and says so. This story was marked up by Stage B and confirmed by a
# person, so the default view holds none of its placements.
assert view["signified_by_applied"] == "participant", view["signified_by_applied"]
held = view["counts_by_signified_by"]
assert held["participant"] == 0, held
assert held["ai_validated"] > 0, held
for chart in view["mcqs"] + view["demographics"]:
    counts = [bar["count"] for bar in chart["bars"]]
    assert counts == sorted(counts, reverse=True), chart["id"]
print("  patterns count only validated stories, bars sorted by value")
print("  patterns default to the storytellers own readings, and name the view")
' || {
    echo "  FAIL: the patterns endpoint broke its own grammar"
    exit 1
}

csv_out="$(curl -sf "http://127.0.0.1:${SMOKE_PORT}/api/export/csv?framework_id=${framework_id}")" || {
    echo "  FAIL: the CSV export did not answer"
    exit 1
}
case "$csv_out" in
    *"input_method"*"source_locator"*) echo "  csv export carries full provenance" ;;
    *)
        echo "  FAIL: the CSV export is missing provenance columns"
        exit 1
        ;;
esac

brief_out="$(curl -sf "http://127.0.0.1:${SMOKE_PORT}/api/export/brief?framework_id=${framework_id}")" || {
    echo "  FAIL: the Pattern Brief did not answer"
    exit 1
}
case "$brief_out" in
    *"not evidence of what caused what"*) echo "  pattern brief renders with its caveats" ;;
    *)
        echo "  FAIL: the Pattern Brief is missing its caveats"
        exit 1
        ;;
esac

# "What We Heard": the export that goes back to the room. One validated story is
# under the floor of five, so it must show nothing at all.
heard_out="$(curl -sf "http://127.0.0.1:${SMOKE_PORT}/api/export/heard?framework_id=${framework_id}")" || {
    echo "  FAIL: the What We Heard export did not answer"
    exit 1
}
case "$heard_out" in
    *"Fewer than 5 stories have been shared"*)
        echo "  what we heard suppresses a set under the floor of five" ;;
    *)
        echo "  FAIL: What We Heard showed figures for fewer than five stories"
        exit 1
        ;;
esac
case "$heard_out" in
    *"parts finally arrived"*|*"wet deck"*)
        echo "  FAIL: What We Heard leaked a story into the respondents' copy"
        exit 1
        ;;
esac

# The story browser (PRD §1.6): the stories themselves, searched, marked, and
# exported as a selection through the same CSV path as everything else.
browse="http://127.0.0.1:${SMOKE_PORT}/api/stories/${framework_id}"
story_id="$(curl -sf "$browse" | $PYTHON -c '
import json, sys

page = json.load(sys.stdin)
assert page["total"] == 1, page["total"]          # only the accepted story
assert page["matched"] == 1, page["matched"]
print(page["stories"][0]["anecdote_id"])
')" || {
    echo "  FAIL: the story browser did not list the validated story"
    exit 1
}

curl -sf -X PUT "http://127.0.0.1:${SMOKE_PORT}/api/stories/${story_id}/marks" \
    -H 'Content-Type: application/json' \
    -d '{"starred": true, "tags": ["handover"]}' >/dev/null || {
    echo "  FAIL: a story could not be starred"
    exit 1
}

curl -sf "${browse}?starred=true&q=deadline" | $PYTHON -c '
import json, sys

page = json.load(sys.stdin)
assert page["matched"] == 1, page["matched"]
assert page["stories"][0]["starred"] is True, page["stories"][0]
assert page["stories"][0]["tags"] == ["handover"], page["stories"][0]
print("  story browser: searched, starred and tagged")
' || {
    echo "  FAIL: the story browser lost a mark or a search"
    exit 1
}

selected="$(curl -sf "http://127.0.0.1:${SMOKE_PORT}/api/export/csv?framework_id=${framework_id}&ids=${story_id}")" || {
    echo "  FAIL: the selected export did not answer"
    exit 1
}
if [[ "$(printf '%s' "$selected" | grep -c .)" != "2" ]]; then
    echo "  FAIL: a selection of one story did not export one row"
    exit 1
fi
echo "  export selected: one story, with the same provenance header"

# Constraint 7 on the paths nobody wrote a message for: a mistyped address must
# come back as a sentence in the one error shape, never as framework wording.
missing="$(curl -s "http://127.0.0.1:${SMOKE_PORT}/api/no-such-thing")"
printf '%s' "$missing" | $PYTHON -c '
import json, sys

body = json.load(sys.stdin)
assert set(body) == {"error"}, body
error = body["error"]
assert set(error) == {"code", "message", "action"}, error
for word in ("HTTP", "Not Found", "detail", "Internal"):
    assert word not in error["message"], error
assert error["action"], error
print("  a mistyped address answers in plain English, in the one error shape")
' || {
    echo "  FAIL: an unknown address did not answer in the app's own error shape"
    exit 1
}

# The landscape: one grid, two readings, and a peak that knows its stories.
land="http://127.0.0.1:${SMOKE_PORT}/api/landscape/${framework_id}/t1"
curl -sf "$land" | $PYTHON -c '
import json, sys

panel = json.load(sys.stdin)["panels"][0]
assert panel["grid"] == 64, panel["grid"]
if panel["has_surface"]:
    highest = max(max(row) for row in panel["density"])
    assert abs(panel["max_density"] - highest) < 1e-6, "contour and surface disagree"
    assert all(level < highest for level in panel["contour_levels"]), panel["contour_levels"]
seen = [i for cell in panel["cells"] for i in cell["anecdote_ids"]]
assert sorted(seen) == sorted(p["anecdote_id"] for p in panel["points"]), "region drill is lossy"
count = panel["count"]
print("  landscape: 64x64 grid, %d stories, one grid for both readings" % count)
' || {
    echo "  FAIL: the landscape endpoint broke one of its own guarantees"
    exit 1
}

# Constraint 14 over the wire, on the view it matters most for: the terrain
# drawn by default holds nobody elses reading of anybody, and asking for both
# is what puts the expert-validated story on the map.
curl -sf "${land}" | $PYTHON -c '
import json, sys

view = json.load(sys.stdin)
assert view["signified_by_applied"] == "participant", view["signified_by_applied"]
assert view["panels"][0]["count"] == 0, view["panels"][0]["count"]
' || {
    echo "  FAIL: the default landscape drew a placement nobody told it to"
    exit 1
}

curl -sf "${land}?signified_by=all" | $PYTHON -c '
import json, sys

view = json.load(sys.stdin)
assert view["signified_by_applied"] == "all", view["signified_by_applied"]
assert view["panels"][0]["count"] == 1, view["panels"][0]["count"]
print("  landscape: default holds only self-signified marks; \"all\" adds the rest")
' || {
    echo "  FAIL: asking for both did not put the expert-validated story on the map"
    exit 1
}

curl -sf "http://127.0.0.1:${SMOKE_PORT}/api/clusters/${framework_id}?k=2" | $PYTHON -c '
import json, sys

view = json.load(sys.stdin)
assert view["seed"] == 42, view["seed"]
assert view["caveat"] == "statistical clusters — descriptive only", view["caveat"]
print("  clusters carry their seed and their caveat")
' || {
    echo "  FAIL: the cluster endpoint dropped its caveat"
    exit 1
}

echo
echo "ALL CHECKS PASSED"
