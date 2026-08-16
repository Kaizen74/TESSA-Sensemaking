"""Shared helpers for the Stage B and validation-queue suites.

One framework carrying all four signifier kinds, and one file driven as far as
the stage before the test's own subject. Written once here so a test about the
queue is about the queue, rather than about six lines of setup.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests import ingest_fixtures as fx

MAPPING_KEYS = ("sheet", "role", "story_column", "respondent_group_column", "title_column")

#: Every signifier kind PRD §3 names, so a Stage B proposal has to satisfy all
#: four value shapes rather than only the easy one.
FULL_DEFINITION = {
    "prompt_text": "Tell us about a moment at work that stuck with you.",
    "triads": [
        {"id": "t1", "title": "What drove this?", "corners": ["Speed", "Care", "Cost"]},
        {"id": "t2", "title": "Who decided?", "corners": ["Me", "My team", "Someone else"]},
    ],
    "dyads": [{"id": "d1", "title": "How supported?", "left": "Alone", "right": "Backed"}],
    "stones": {
        "id": "s1",
        "title": "Where did the effort go?",
        "x_axis": {"low": "Routine", "high": "Novel"},
        "y_axis": {"low": "Quiet", "high": "Fraught"},
        "chips": ["Planning", "Doing", "Fixing"],
    },
    "mcqs": [
        {"id": "m1", "title": "How did it end?", "options": ["Well", "Badly", "Unresolved"]}
    ],
    "capture_settings": {"respondent_groups": ["Ops", "Deck", "Support"]},
}


def make_framework(client: TestClient, definition: dict | None = None) -> dict:
    response = client.post(
        "/api/frameworks",
        json={"name": "Hangar", "definition": definition or FULL_DEFINITION},
    )
    assert response.status_code == 201, response.text
    return response.json()


def confirmed_import(
    client: TestClient, filename: str = "workshop.xlsx", data: bytes | None = None
) -> dict:
    """Drive a file as far as ``mapping_confirmed``, accepting Stage A as-is."""
    payload = data if data is not None else fx.ALL_FORMATS[filename]
    uploaded = client.post("/api/import", files={"file": (filename, payload)}).json()
    organised = client.post(f"/api/import/{uploaded['id']}/organise").json()

    if organised["file_class"] == "tabular":
        body = {
            "sheets": [
                {key: sheet[key] for key in MAPPING_KEYS}
                for sheet in organised["organisation"]["sheets"]
            ]
        }
    else:
        body = {"accepted": list(range(len(organised["organisation"]["segments"])))}

    confirmed = client.post(f"/api/import/{uploaded['id']}/mapping", json=body)
    assert confirmed.status_code == 200, confirmed.text
    return confirmed.json()


def proposed_import(client: TestClient, framework_id: int, **kwargs) -> dict:
    """Drive a file all the way to ``proposed`` — stories in the queue."""
    job = confirmed_import(client, **kwargs)
    response = client.post(
        f"/api/import/{job['id']}/propose", json={"framework_id": framework_id}
    )
    assert response.status_code == 200, response.text
    return response.json()
