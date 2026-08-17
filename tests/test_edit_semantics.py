"""The wording-fix vs meaning-change state machine (PRD §6, constraint 13g).

This module is on the PRD §6 regression list and must stay green in every later
phase. The state machine it pins down:

    no stories        → any edit applies in place
    stories, no kind  → 409, explained in plain English
    stories, wording  → patch in place, append to the edit log
    stories, meaning  → new version n+1, old stories stay put
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import Anecdote, Framework, Signification

TRIAD = {
    "id": "pressure",
    "title": "What drove this?",
    "corners": ["Speed", "Care", "Cost"],
}
DYAD = {"id": "clarity", "title": "How clear?", "left": "Murky", "right": "Clear"}


def _definition(**overrides) -> dict:
    base = {
        "prompt_text": "Tell us about a moment at work that stuck with you.",
        "triads": [TRIAD],
        "dyads": [DYAD],
    }
    base.update(overrides)
    return base


def _create(client: TestClient, name: str = "Ground handling") -> dict:
    response = client.post("/api/frameworks", json={"name": name, "definition": _definition()})
    assert response.status_code == 201, response.text
    return response.json()


def _add_story(session: Session, framework_id: int, text: str = "A late handover.") -> Anecdote:
    anecdote = Anecdote(
        framework_id=framework_id,
        text=text,
        source_type="capture",
        entry_mode="admin",
        input_method="typed",
    )
    session.add(anecdote)
    session.commit()
    return anecdote


class TestZeroStoriesEditsFreely:
    """PRD §1.1: while a framework has zero stories, edit freely."""

    def test_edit_applies_in_place_without_edit_kind(self, client: TestClient) -> None:
        created = _create(client)
        assert created["is_live"] is False

        changed = _definition(prompt_text="A completely different question.")
        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": changed},
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["id"] == created["id"], "a free edit must not spawn a new version"
        assert body["version"] == 1
        assert body["definition"]["prompt_text"] == "A completely different question."

    def test_free_edit_writes_no_edit_log_entry(self, client: TestClient) -> None:
        """Before stories exist there is nothing to be auditable against."""
        created = _create(client)
        client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(prompt_text="Reworded.")},
        )
        body = client.get(f"/api/frameworks/{created['id']}").json()
        assert body["edit_log"] == []

    def test_structure_may_change_freely_before_stories(self, client: TestClient) -> None:
        created = _create(client)
        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(dyads=[])},
        )
        assert response.status_code == 200
        assert response.json()["definition"]["dyads"] == []


class TestLiveFrameworkRequiresEditKind:
    """PRD §4: PUT without edit_kind on a live framework → 409."""

    def test_put_without_edit_kind_is_refused(self, client: TestClient, session: Session) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(prompt_text="Changed.")},
        )

        assert response.status_code == 409

    def test_the_refusal_is_explained_in_plain_english(
        self, client: TestClient, session: Session
    ) -> None:
        """Constraint 7: the operator must be able to act on the message."""
        created = _create(client)
        _add_story(session, created["id"])

        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(prompt_text="Changed.")},
        )
        error = response.json()["error"]

        assert error["code"] == "edit_kind_required"
        assert "1 story" in error["message"]
        assert "Fix wording" in error["action"]
        assert "Change meaning" in error["action"]
        for jargon in ("409", "HTTP", "None", "null", "Traceback"):
            assert jargon not in error["message"]

    def test_the_refusal_changes_nothing(self, client: TestClient, session: Session) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(prompt_text="Changed.")},
        )

        after = client.get(f"/api/frameworks/{created['id']}").json()
        assert after["definition"]["prompt_text"] == _definition()["prompt_text"]
        assert after["edit_log"] == []

    def test_message_counts_stories_correctly_in_the_plural(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        for index in range(3):
            _add_story(session, created["id"], f"Story {index}.")

        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(prompt_text="Changed.")},
        )
        assert "3 stories" in response.json()["error"]["message"]


class TestWordingFix:
    """A wording fix patches in place and appends to the edit log."""

    def test_patches_in_place_without_creating_a_version(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={
                "definition": _definition(prompt_text="Tell us about a moment that stuck."),
                "edit_kind": "wording_fix",
            },
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["id"] == created["id"]
        assert body["version"] == 1
        assert body["definition"]["prompt_text"] == "Tell us about a moment that stuck."

    def test_logs_old_text_new_text_and_timestamp(
        self, client: TestClient, session: Session
    ) -> None:
        """PRD §3: edit_log_json carries field_path, old_text, new_text, edited_at."""
        created = _create(client)
        _add_story(session, created["id"])

        client.put(
            f"/api/frameworks/{created['id']}",
            json={
                "definition": _definition(prompt_text="Reworded prompt."),
                "edit_kind": "wording_fix",
            },
        )

        log = client.get(f"/api/frameworks/{created['id']}").json()["edit_log"]
        assert len(log) == 1
        entry = log[0]
        assert entry["field_path"] == "prompt_text"
        assert entry["old_text"] == _definition()["prompt_text"]
        assert entry["new_text"] == "Reworded prompt."
        assert entry["kind"] == "wording_fix"
        assert entry["edited_at"]

    def test_logs_a_nested_corner_label_with_its_path(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        retitled = {**TRIAD, "corners": ["Speed", "Care", "Budget"]}
        client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(triads=[retitled]), "edit_kind": "wording_fix"},
        )

        log = client.get(f"/api/frameworks/{created['id']}").json()["edit_log"]
        assert len(log) == 1
        assert log[0]["field_path"] == "triads.0.corners.2"
        assert log[0]["old_text"] == "Cost"
        assert log[0]["new_text"] == "Budget"

    def test_successive_fixes_accumulate_in_the_log(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        for text in ("First rewording.", "Second rewording."):
            client.put(
                f"/api/frameworks/{created['id']}",
                json={"definition": _definition(prompt_text=text), "edit_kind": "wording_fix"},
            )

        log = client.get(f"/api/frameworks/{created['id']}").json()["edit_log"]
        assert [entry["new_text"] for entry in log] == [
            "First rewording.",
            "Second rewording.",
        ]

    def test_stories_stay_attached_to_the_same_row(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        anecdote = _add_story(session, created["id"])

        client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(prompt_text="Reworded."), "edit_kind": "wording_fix"},
        )

        session.expire_all()
        assert session.get(Anecdote, anecdote.id).framework_id == created["id"]

    def test_an_edit_that_changes_nothing_logs_nothing(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(), "edit_kind": "wording_fix"},
        )

        assert response.status_code == 200
        assert response.json()["edit_log"] == []

    def test_structural_change_is_refused_as_a_wording_fix(
        self, client: TestClient, session: Session
    ) -> None:
        """Removing a question would strand answers already given to it."""
        created = _create(client)
        _add_story(session, created["id"])

        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(dyads=[]), "edit_kind": "wording_fix"},
        )

        assert response.status_code == 409
        error = response.json()["error"]
        assert error["code"] == "structural_change_needs_new_version"
        assert "Change meaning" in error["action"]

    def test_adding_an_option_is_refused_as_a_wording_fix(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        four_corners = {**TRIAD, "corners": ["Speed", "Care", "Cost"]}
        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={
                "definition": _definition(
                    triads=[four_corners],
                    mcqs=[{"id": "team", "title": "Team?", "options": ["Ramp", "Cabin"]}],
                ),
                "edit_kind": "wording_fix",
            },
        )

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "structural_change_needs_new_version"


class TestMeaningChange:
    """A meaning change creates version n+1 and leaves old stories bound."""

    def test_creates_a_new_version_with_a_new_id(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={
                "definition": _definition(prompt_text="A genuinely different question."),
                "edit_kind": "meaning_change",
            },
        )

        assert response.status_code == 200, response.text
        child = response.json()
        assert child["id"] != created["id"]
        assert child["version"] == 2

    def test_new_version_points_back_at_its_parent(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        child = client.put(
            f"/api/frameworks/{created['id']}",
            json={
                "definition": _definition(prompt_text="Different."),
                "edit_kind": "meaning_change",
            },
        ).json()

        assert child["parent_framework_id"] == created["id"]

    def test_old_stories_stay_bound_to_the_old_wording(
        self, client: TestClient, session: Session
    ) -> None:
        """The point of the whole guardrail."""
        created = _create(client)
        anecdote = _add_story(session, created["id"])
        original_prompt = _definition()["prompt_text"]

        client.put(
            f"/api/frameworks/{created['id']}",
            json={
                "definition": _definition(prompt_text="Different."),
                "edit_kind": "meaning_change",
            },
        )

        session.expire_all()
        assert session.get(Anecdote, anecdote.id).framework_id == created["id"]

        parent = client.get(f"/api/frameworks/{created['id']}").json()
        assert parent["definition"]["prompt_text"] == original_prompt
        assert parent["anecdote_count"] == 1

    def test_the_new_version_starts_with_no_stories(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        child = client.put(
            f"/api/frameworks/{created['id']}",
            json={
                "definition": _definition(prompt_text="Different."),
                "edit_kind": "meaning_change",
            },
        ).json()

        assert child["anecdote_count"] == 0
        assert child["is_live"] is False

    def test_the_new_version_starts_with_a_fresh_edit_log(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        _add_story(session, created["id"])
        client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(prompt_text="Fix."), "edit_kind": "wording_fix"},
        )

        child = client.put(
            f"/api/frameworks/{created['id']}",
            json={
                "definition": _definition(prompt_text="Different."),
                "edit_kind": "meaning_change",
            },
        ).json()

        assert child["edit_log"] == []
        assert len(client.get(f"/api/frameworks/{created['id']}").json()["edit_log"]) == 1

    def test_structural_change_is_allowed_as_a_meaning_change(
        self, client: TestClient, session: Session
    ) -> None:
        created = _create(client)
        _add_story(session, created["id"])

        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(dyads=[]), "edit_kind": "meaning_change"},
        )

        assert response.status_code == 200
        assert response.json()["definition"]["dyads"] == []

    def test_versions_keep_climbing_across_a_chain(
        self, client: TestClient, session: Session
    ) -> None:
        current = _create(client)
        for step in range(3):
            _add_story(session, current["id"], f"Story for version {step + 1}.")
            current = client.put(
                f"/api/frameworks/{current['id']}",
                json={
                    "definition": _definition(prompt_text=f"Question {step + 2}."),
                    "edit_kind": "meaning_change",
                },
            ).json()

        assert current["version"] == 4

    def test_each_version_keeps_its_own_stories(self, client: TestClient, session: Session) -> None:
        v1 = _create(client)
        _add_story(session, v1["id"], "Story on v1.")

        v2 = client.put(
            f"/api/frameworks/{v1['id']}",
            json={"definition": _definition(prompt_text="Second."), "edit_kind": "meaning_change"},
        ).json()
        _add_story(session, v2["id"], "Story on v2.")
        _add_story(session, v2["id"], "Another on v2.")

        assert client.get(f"/api/frameworks/{v1['id']}").json()["anecdote_count"] == 1
        assert client.get(f"/api/frameworks/{v2['id']}").json()["anecdote_count"] == 2

    def test_a_branch_does_not_reuse_a_version_number(
        self, client: TestClient, session: Session
    ) -> None:
        """Two meaning changes from the same parent get distinct versions."""
        v1 = _create(client)
        _add_story(session, v1["id"])

        first = client.put(
            f"/api/frameworks/{v1['id']}",
            json={
                "definition": _definition(prompt_text="Branch A."),
                "edit_kind": "meaning_change",
            },
        ).json()
        second = client.put(
            f"/api/frameworks/{v1['id']}",
            json={
                "definition": _definition(prompt_text="Branch B."),
                "edit_kind": "meaning_change",
            },
        ).json()

        assert first["version"] != second["version"]
        assert {first["version"], second["version"]} == {2, 3}


class TestEditKindIgnoredWhenNotLive:
    def test_meaning_change_on_an_empty_framework_edits_in_place(self, client: TestClient) -> None:
        """With no stories to protect, there is nothing to fork away from."""
        created = _create(client)

        response = client.put(
            f"/api/frameworks/{created['id']}",
            json={"definition": _definition(prompt_text="Changed."), "edit_kind": "meaning_change"},
        )

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]
        assert response.json()["version"] == 1


class TestLineageBookkeeping:
    def test_a_framework_row_exists_per_version(self, client: TestClient, session: Session) -> None:
        v1 = _create(client)
        _add_story(session, v1["id"])
        client.put(
            f"/api/frameworks/{v1['id']}",
            json={"definition": _definition(prompt_text="Second."), "edit_kind": "meaning_change"},
        )

        rows = session.query(Framework).all()
        assert len(rows) == 2
        assert sorted(row.version for row in rows) == [1, 2]


class TestARenameCarriesTheAnswers:
    """PRD §1.1: a wording fix keeps the stories attached — including their answers.

    Three of the four signifier kinds store an answer *by its label*: a triad is
    ``{corner: weight}``, stones are placements naming their chip, an MCQ is the
    options that were chosen. A wording fix is allowed to rewrite those labels,
    and when it did, every stored answer was left keyed by a word the framework
    no longer contained. The Patterns tab failed outright on a renamed triad
    corner; a renamed option or chip stopped being counted without saying so.

    Found by running the whole app end to end rather than by any unit test —
    each piece was behaving exactly as written.
    """

    FULL = {
        "prompt_text": "Tell us about a moment at work that stuck with you.",
        "triads": [{"id": "t1", "title": "What drove this?", "corners": ["Speed", "Care", "Cost"]}],
        "dyads": [{"id": "d1", "title": "How clear?", "left": "Murky", "right": "Clear"}],
        "stones": {
            "id": "s1",
            "title": "Where did the effort go?",
            "x_axis": {"low": "Routine", "high": "Novel"},
            "y_axis": {"low": "Quiet", "high": "Fraught"},
            "chips": ["Planning", "Doing"],
        },
        "mcqs": [{"id": "m1", "title": "How did it end?", "options": ["Well", "Badly"]}],
    }

    def _with_a_story(self, client: TestClient) -> dict:
        created = client.post("/api/frameworks", json={"name": "Hangar", "definition": self.FULL})
        framework = created.json()
        stored = client.post(
            "/api/capture",
            json={
                "framework_id": framework["id"],
                "text": "The parts arrived three hours before the deadline.",
                "significations": [
                    {"signifier_id": "t1", "value": {"Speed": 0.6, "Care": 0.3, "Cost": 0.1}},
                    {"signifier_id": "d1", "value": {"value": 0.4}},
                    {
                        "signifier_id": "s1",
                        "value": {
                            "placements": [
                                {"label": "Planning", "x": 0.2, "y": 0.8},
                                {"label": "Doing", "x": 0.5, "y": 0.5},
                            ]
                        },
                    },
                    {"signifier_id": "m1", "value": {"selected": ["Well"]}},
                ],
            },
        )
        assert stored.status_code == 201, stored.text
        return framework

    def _renamed(self) -> dict:
        import copy

        changed = copy.deepcopy(self.FULL)
        changed["triads"][0]["corners"][1] = "Carefulness"
        changed["stones"]["chips"][0] = "Planning it"
        changed["mcqs"][0]["options"][0] = "It went well"
        return changed

    def test_patterns_still_answer_after_a_corner_is_renamed(self, client: TestClient) -> None:
        framework = self._with_a_story(client)

        fixed = client.put(
            f"/api/frameworks/{framework['id']}",
            json={"definition": self._renamed(), "edit_kind": "wording_fix"},
        )
        assert fixed.status_code == 200, fixed.text

        view = client.get(f"/api/patterns/{framework['id']}")

        assert view.status_code == 200, view.text
        assert view.json()["total"] == 1

    def test_the_answer_is_counted_under_its_new_words(self, client: TestClient) -> None:
        framework = self._with_a_story(client)
        client.put(
            f"/api/frameworks/{framework['id']}",
            json={"definition": self._renamed(), "edit_kind": "wording_fix"},
        )

        view = client.get(f"/api/patterns/{framework['id']}").json()

        triad = view["triads"][0]
        assert triad["corners"] == ["Speed", "Carefulness", "Cost"]
        assert triad["answered"] == 1
        # The weights are unchanged; it is only the word for the middle corner
        # that moved. 0.6 towards Speed on a unit triangle is x = 0.6·1 + 0.3·0.
        assert triad["points"][0]["x"] == pytest.approx(0.3 + 0.1 / 2)

        chosen = {bar["label"]: bar["count"] for bar in view["mcqs"][0]["bars"]}
        assert chosen == {"It went well": 1, "Badly": 0}

        placed = {point["label"] for point in view["stones"]["points"]}
        assert placed == {"Planning it", "Doing"}

    def test_the_landscape_is_drawn_from_the_renamed_corners(self, client: TestClient) -> None:
        framework = self._with_a_story(client)
        client.put(
            f"/api/frameworks/{framework['id']}",
            json={"definition": self._renamed(), "edit_kind": "wording_fix"},
        )

        land = client.get(f"/api/landscape/{framework['id']}/t1")

        assert land.status_code == 200, land.text
        assert land.json()["panels"][0]["corners"] == ["Speed", "Carefulness", "Cost"]

    def test_an_untouched_answer_is_left_exactly_alone(
        self, client: TestClient, session: Session
    ) -> None:
        """A dyad has no label to rename, and nothing else may drift either."""
        framework = self._with_a_story(client)
        before = {
            row.signifier_id: dict(row.value_json) for row in session.query(Signification).all()
        }

        client.put(
            f"/api/frameworks/{framework['id']}",
            json={"definition": self._renamed(), "edit_kind": "wording_fix"},
        )
        session.expire_all()
        after = {
            row.signifier_id: dict(row.value_json) for row in session.query(Signification).all()
        }

        assert after["d1"] == before["d1"]
        assert after["t1"]["Speed"] == before["t1"]["Speed"]
        assert set(after["t1"]) == {"Speed", "Carefulness", "Cost"}

    def test_the_edit_log_still_records_the_words_that_changed(self, client: TestClient) -> None:
        """The rename is carried, and it is also on the record."""
        framework = self._with_a_story(client)

        fixed = client.put(
            f"/api/frameworks/{framework['id']}",
            json={"definition": self._renamed(), "edit_kind": "wording_fix"},
        ).json()

        changed = {(entry["old_text"], entry["new_text"]) for entry in fixed["edit_log"]}
        assert ("Care", "Carefulness") in changed
        assert ("Well", "It went well") in changed
        assert ("Planning", "Planning it") in changed
