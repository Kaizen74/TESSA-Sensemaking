"""One run through the whole app, in the order an operator would use it.

Every other test file is about one part. This one is about the joins: it writes
a question set in the Studio, collects stories every way the app collects them,
imports a file through both AI stages, works the queue, reads the patterns, and
takes the exports — then checks that the figures those last steps produce agree
with the stories the first steps put in.

The failures this is here to catch are the ones no unit test sees: a stage that
works alone but disagrees with the next one, a filter that means one thing to
the charts and another to the CSV, a story that is counted twice because two
paths both claim it. Contract drift, in other words, which is the thing a
phased build is most likely to grow.

Runs entirely on mocks with no network (constraint 6).
"""

from __future__ import annotations

import csv
import io

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import Anecdote
from tests import ingest_fixtures as fx
from tests.patterns_fixtures import GOLDEN_DEFINITION

MAPPING_KEYS = ("sheet", "role", "story_column", "respondent_group_column", "title_column")


def test_the_whole_app_agrees_with_itself(client: TestClient, session: Session) -> None:
    # ---------------------------------------------------------------- Studio
    framework = client.post(
        "/api/frameworks", json={"name": "Hangar", "definition": GOLDEN_DEFINITION}
    ).json()
    fid = framework["id"]
    assert framework["version"] == 1

    def capture(text: str, group: str, **extra) -> dict:
        body = {
            "framework_id": fid,
            "text": text,
            "respondent_group": group,
            "significations": [
                {"signifier_id": "t1", "value": {"Speed": 0.6, "Care": 0.3, "Cost": 0.1}},
                {"signifier_id": "d1", "value": {"value": 0.7}},
                {"signifier_id": "m1", "value": {"selected": ["Well"]}},
            ],
            **extra,
        }
        response = client.post("/api/capture", json=body)
        assert response.status_code == 201, response.text
        return response.json()

    # ------------------------------------------------- capture, three ways
    capture("Typed at the operator's own desk.", "Ops")
    capture("Read off a returned paper sheet.", "Deck", input_method="paper")
    capture("Entered at the workshop kiosk.", "Support", entry_mode="kiosk")

    link = client.post("/api/capture-links", json={"framework_id": fid, "label": "Hangar wall"})
    assert link.status_code == 201, link.text
    token = link.json()["token"]
    remote = client.post(
        f"/api/public/capture/{token}",
        json={
            "text": "Scanned the poster on the way out and typed this in.",
            "respondent_group": "Ops",
            "significations": [
                {"signifier_id": "t1", "value": {"Speed": 0.2, "Care": 0.7, "Cost": 0.1}},
                {"signifier_id": "d1", "value": {"value": 0.3}},
            ],
        },
    )
    assert remote.status_code == 201, remote.text
    assert remote.json()["entry_mode"] == "link"

    # Four stories collected, all of them data because no AI touched any.
    assert client.get(f"/api/patterns/{fid}").json()["total"] == 4

    # ---------------------------------------------------- import, both stages
    uploaded = client.post(
        "/api/import", files={"file": ("workshop.xlsx", fx.xlsx_bytes())}
    ).json()
    job_id = uploaded["id"]

    # The stage gate holds before anything else happens.
    assert client.post(f"/api/import/{job_id}/mapping", json={"sheets": []}).status_code == 409
    assert (
        client.post(f"/api/import/{job_id}/propose", json={"framework_id": fid}).status_code
        == 409
    )

    organised = client.post(f"/api/import/{job_id}/organise").json()
    confirmed = client.post(
        f"/api/import/{job_id}/mapping",
        json={
            "sheets": [
                {key: sheet[key] for key in MAPPING_KEYS}
                for sheet in organised["organisation"]["sheets"]
            ]
        },
    ).json()
    tally = confirmed["confirmation"]["reconciliation"]
    assert tally["balanced"] is True
    assert sum(line["count"] for line in tally["lines"]) == tally["total"] == 6
    assert confirmed["confirmation"]["candidate_count"] == 3

    marked = client.post(
        f"/api/import/{job_id}/propose", json={"framework_id": fid}
    ).json()
    assert marked["stage"] == "proposed"

    # Constraint 1: still four. Three stories are waiting, none of them counted.
    assert client.get(f"/api/patterns/{fid}").json()["total"] == 4
    assert client.get("/api/queue").json()["counts"]["pending"] == 3

    # ------------------------------------------------------------- the queue
    items = client.get("/api/queue").json()["items"]
    client.put(f"/api/queue/{items[0]['anecdote_id']}", json={"action": "accept"})

    # Move one marker and leave another exactly as proposed — the case the
    # per-placement provenance exists for, and the one a real operator produces.
    proposed = {p["signifier_id"]: p["value"] for p in items[1]["significations"]}
    corrected = client.put(
        f"/api/queue/{items[1]['anecdote_id']}",
        json={
            "action": "correct",
            "significations": [
                {"signifier_id": "t1", "value": {"Speed": 0.1, "Care": 0.1, "Cost": 0.8}},
                {"signifier_id": "d1", "value": proposed["d1"]},
            ],
        },
    ).json()
    stamped = {p["signifier_id"]: p["signified_by"] for p in corrected["significations"]}
    assert stamped == {"t1": "analyst", "d1": "ai"}

    client.put(f"/api/queue/{items[2]['anecdote_id']}", json={"action": "reject"})

    finished = client.get(f"/api/import/{job_id}").json()
    assert finished["stage"] == "done"
    assert finished["queue"] == {"pending": 0, "validated": 2, "rejected": 1}

    # ------------------------------------------------------------- patterns
    patterns = client.get(f"/api/patterns/{fid}").json()
    # Four captured plus two validated from the file. The rejected one never.
    assert patterns["total"] == 6
    assert session.query(Anecdote).count() == 7

    # Every categorical view is sorted by value, still (§5b).
    for chart in patterns["mcqs"] + patterns["demographics"]:
        counts = [bar["count"] for bar in chart["bars"]]
        assert counts == sorted(counts, reverse=True), chart["id"]

    # ------------------------------------------------------------ landscape
    land = client.get(f"/api/landscape/{fid}/t1").json()
    panel = land["panels"][0]
    assert land["total"] == patterns["total"]
    assert panel["count"] == patterns["triads"][0]["answered"]
    # One grid, two readings (constraint 13b).
    if panel["has_surface"]:
        highest = max(max(row) for row in panel["density"])
        assert abs(panel["max_density"] - highest) < 1e-6
    # Every story sits in exactly one cell, so a region drill is exact.
    celled = [i for cell in panel["cells"] for i in cell["anecdote_ids"]]
    assert sorted(celled) == sorted(point["anecdote_id"] for point in panel["points"])

    # ------------------------------------------------------------- explorer
    explorer = client.get(f"/api/explorer/{fid}").json()
    assert explorer["total"] == patterns["total"]
    clusters = client.get(f"/api/clusters/{fid}", params={"k": 2}).json()
    assert clusters["caveat"] == "statistical clusters — descriptive only"

    # -------------------------------------------------------------- exports
    export = client.get("/api/export/csv", params={"framework_id": fid})
    rows = list(csv.DictReader(io.StringIO(export.text)))
    assert len(rows) == patterns["total"]
    assert {row["status"] for row in rows} == {"validated"}

    # Provenance survived every route into the app (constraint 3).
    by_mode = {row["entry_mode"] for row in rows}
    by_method = {row["input_method"] for row in rows}
    assert by_mode == {"admin", "kiosk", "link"}
    assert by_method == {"typed", "paper", "imported"}
    assert any(row["signified_by"] == "ai|analyst" for row in rows), "the corrected story"
    assert any(row["source_file"] == "workshop.xlsx" for row in rows)

    # Constraint 9 held all the way to the file.
    assert all(row["created_at_hour"].endswith(":00:00") for row in rows)
    header = export.text.splitlines()[0].lower()
    for banned in ("user_agent", "email", "ip_", "fingerprint"):
        assert banned not in header

    brief = client.get("/api/export/brief", params={"framework_id": fid}).text
    assert f"{patterns['total']} stories" in brief
    assert "not evidence of what caused what" in brief

    # --------------------------------------------------- filters agree, too
    ops_patterns = client.get(f"/api/patterns/{fid}", params={"respondent_group": "Ops"}).json()
    ops_land = client.get(f"/api/landscape/{fid}/t1", params={"respondent_group": "Ops"}).json()
    ops_csv = list(
        csv.DictReader(
            io.StringIO(
                client.get(
                    "/api/export/csv",
                    params={"framework_id": fid, "respondent_group": "Ops"},
                ).text
            )
        )
    )
    assert ops_patterns["total"] == ops_land["total"] == len(ops_csv)
    assert {row["respondent_group"] for row in ops_csv} == {"Ops"}

    # --------------------------------------------------------- the browser
    # The last view, and the one that has to agree with all of them: the same
    # stories the charts counted, readable one at a time.
    browsed = client.get(f"/api/stories/{fid}").json()
    assert browsed["total"] == patterns["total"]
    assert {story["anecdote_id"] for story in browsed["stories"]} == {
        int(row["anecdote_id"]) for row in rows
    }

    ops_browsed = client.get(f"/api/stories/{fid}", params={"respondent_group": "Ops"}).json()
    assert ops_browsed["matched"] == ops_patterns["total"]

    # Search, star, tag, and take a chosen one out — the whole of §1.6.
    hunted = client.get(f"/api/stories/{fid}", params={"q": "workshop"}).json()
    picked = browsed["stories"][0]
    marked = client.put(
        f"/api/stories/{picked['anecdote_id']}/marks",
        json={"starred": True, "tags": ["worth a second look"]},
    ).json()
    assert marked["starred"] is True
    assert marked["tags"] == ["worth a second look"]
    assert hunted["matched"] <= browsed["total"]

    starred = client.get(f"/api/stories/{fid}", params={"starred": True}).json()
    assert starred["matched"] == 1
    assert starred["stories"][0]["anecdote_id"] == picked["anecdote_id"]

    selected = client.get(
        "/api/export/csv",
        params={"framework_id": fid, "ids": str(picked["anecdote_id"])},
    ).text
    chosen_rows = list(csv.DictReader(io.StringIO(selected)))
    assert len(chosen_rows) == 1
    assert int(chosen_rows[0]["anecdote_id"]) == picked["anecdote_id"]
    # Same columns as the whole export: one code path, one provenance promise.
    assert selected.splitlines()[0] == export.text.splitlines()[0]

    # --------------------------------------------- and the respondents' copy
    heard = client.get("/api/export/heard", params={"framework_id": fid}).text
    assert heard.startswith("# What we heard")
    for row in rows:
        assert row["text"] not in heard, "a story reached the respondents' copy"
    for leak in ("input_method", "entry_mode", "workshop.xlsx", "signified_by"):
        assert leak not in heard, leak


def test_a_meaning_change_keeps_the_two_versions_apart_everywhere(
    client: TestClient,
) -> None:
    """The guardrail, followed all the way to the landscape and the exports."""
    framework = client.post(
        "/api/frameworks", json={"name": "Hangar", "definition": GOLDEN_DEFINITION}
    ).json()
    fid = framework["id"]

    for index in range(4):
        client.post(
            "/api/capture",
            json={
                "framework_id": fid,
                "text": f"Story {index} against the first wording.",
                "significations": [
                    {
                        "signifier_id": "t1",
                        "value": {"Speed": 0.5 + index / 20, "Care": 0.3, "Cost": 0.2 - index / 20},
                    }
                ],
            },
        )

    # A meaning change: version 2, and the old stories stay on version 1.
    changed = dict(GOLDEN_DEFINITION)
    changed["triads"] = [
        {"id": "t1", "title": "What really drove it?", "corners": ["Speed", "Care", "Cost"]},
        GOLDEN_DEFINITION["triads"][1],
    ]
    second = client.put(
        f"/api/frameworks/{fid}", json={"definition": changed, "edit_kind": "meaning_change"}
    ).json()
    client.post(
        "/api/capture",
        json={
            "framework_id": second["id"],
            "text": "The only story told against the new wording.",
            "significations": [
                {"signifier_id": "t1", "value": {"Speed": 0.1, "Care": 0.1, "Cost": 0.8}}
            ],
        },
    )

    # Apart by default, in every view.
    assert client.get(f"/api/patterns/{second['id']}").json()["total"] == 1
    assert client.get(f"/api/landscape/{second['id']}/t1").json()["total"] == 1
    assert client.get(f"/api/explorer/{second['id']}").json()["total"] == 1
    alone = list(
        csv.DictReader(
            io.StringIO(
                client.get("/api/export/csv", params={"framework_id": second["id"]}).text
            )
        )
    )
    assert len(alone) == 1

    # Together only when asked — and then everything says so.
    mixed_patterns = client.get(
        f"/api/patterns/{second['id']}", params={"mixed": True}
    ).json()
    mixed_land = client.get(
        f"/api/landscape/{second['id']}/t1", params={"mixed": True}
    ).json()
    mixed_csv = list(
        csv.DictReader(
            io.StringIO(
                client.get(
                    "/api/export/csv",
                    params={"framework_id": second["id"], "mixed": True},
                ).text
            )
        )
    )
    mixed_brief = client.get(
        "/api/export/brief", params={"framework_id": second["id"], "mixed": True}
    ).text

    assert mixed_patterns["total"] == mixed_land["total"] == len(mixed_csv) == 5
    assert [entry["version"] for entry in mixed_patterns["versions"]] == [1, 2]
    assert [entry["version"] for entry in mixed_land["versions"]] == [1, 2]
    assert {row["framework_version"] for row in mixed_csv} == {"1", "2"}
    assert "mixes framework versions" in mixed_brief

    # And the landscape draws the version the operator is standing in.
    assert mixed_land["available_triads"][0]["title"] == "What really drove it?"


def test_an_empty_app_answers_every_endpoint_without_falling_over(
    client: TestClient,
) -> None:
    """Day one: a question set, no stories, and nothing that throws."""
    framework = client.post(
        "/api/frameworks", json={"name": "Hangar", "definition": GOLDEN_DEFINITION}
    ).json()
    fid = framework["id"]

    patterns = client.get(f"/api/patterns/{fid}")
    land = client.get(f"/api/landscape/{fid}/t1")
    explorer = client.get(f"/api/explorer/{fid}")
    clusters = client.get(f"/api/clusters/{fid}")
    queue = client.get("/api/queue")
    imports = client.get("/api/import")
    csv_export = client.get("/api/export/csv", params={"framework_id": fid})
    brief = client.get("/api/export/brief", params={"framework_id": fid})
    heard = client.get("/api/export/heard", params={"framework_id": fid})
    browsed = client.get(f"/api/stories/{fid}")
    pack = client.get(f"/api/frameworks/{fid}/paper-pack")

    assert [
        response.status_code
        for response in (
            patterns,
            land,
            explorer,
            clusters,
            queue,
            imports,
            csv_export,
            brief,
            heard,
            browsed,
            pack,
        )
    ] == [200] * 11

    assert patterns.json()["total"] == 0
    assert land.json()["panels"][0]["has_surface"] is False
    assert clusters.json()["computed"] is False
    assert clusters.json()["caveat"]
    assert brief.text.splitlines()[0] == "# No stories match these filters yet"
    assert "Fewer than 5 stories have been shared" in heard.text
    assert browsed.json()["total"] == 0
    assert browsed.json()["stories"] == []
    assert csv_export.text.strip().count("\n") == 0, "header only"
