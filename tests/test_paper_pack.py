"""The printable paper pack (PRD §6 Phase 2 tests, §5b print grammar).

Two assertions the PRD names explicitly:

* the page contains every signifier of the version with its exact labels, and
  the verbatim anonymity line;
* the print CSS produces one sheet per page (the page-break rules are present).
"""

from __future__ import annotations

import re

from fastapi.testclient import TestClient

from backend.framework_schema import CANONICAL_ANONYMITY_TEXT

TRIAD = {"id": "pressure", "title": "What drove this?", "corners": ["Speed", "Care", "Cost"]}
DYAD = {"id": "clarity", "title": "How clear was it?", "left": "Murky", "right": "Crystal clear"}
STONES = {
    "id": "forces",
    "title": "Place the forces at work",
    "x_axis": {"low": "Rare", "high": "Constant"},
    "y_axis": {"low": "Minor", "high": "Major"},
    "chips": ["Time", "Kit", "People"],
}
MCQ = {"id": "team", "title": "Which team were you with?", "options": ["Ramp", "Cabin", "Cargo"]}

FULL_DEFINITION = {
    "prompt_text": "Tell us about a moment at work that stuck with you.",
    "prompt_text_alt": "Or a time something went unexpectedly well.",
    "triads": [TRIAD],
    "dyads": [DYAD],
    "stones": STONES,
    "mcqs": [MCQ],
    "capture_settings": {"respondent_groups": ["Ramp", "Cabin"]},
}


def _create_full(client: TestClient) -> dict:
    response = client.post(
        "/api/frameworks",
        json={"name": "Ground handling pilot", "definition": FULL_DEFINITION},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _pack_html(client: TestClient, framework_id: int) -> str:
    response = client.get(f"/api/frameworks/{framework_id}/paper-pack")
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("text/html")
    return response.text


class TestEverySignifierAppears:
    """PRD §6: the page contains every signifier of the version, exact labels."""

    def test_every_signifier_title_appears(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])

        for title in (
            TRIAD["title"],
            DYAD["title"],
            STONES["title"],
            MCQ["title"],
        ):
            assert title in html, f"signifier '{title}' missing from the pack"

    def test_every_triad_corner_label_appears(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        for corner in TRIAD["corners"]:
            assert corner in html, f"triad corner '{corner}' missing"

    def test_both_dyad_poles_appear(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        assert DYAD["left"] in html
        assert DYAD["right"] in html

    def test_every_stones_axis_end_and_chip_appears(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        for label in (
            STONES["x_axis"]["low"],
            STONES["x_axis"]["high"],
            STONES["y_axis"]["low"],
            STONES["y_axis"]["high"],
            *STONES["chips"],
        ):
            assert label in html, f"stones label '{label}' missing"

    def test_every_mcq_option_appears(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        for option in MCQ["options"]:
            assert option in html, f"MCQ option '{option}' missing"

    def test_the_prompt_and_its_alternative_appear(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        assert FULL_DEFINITION["prompt_text"] in html
        assert FULL_DEFINITION["prompt_text_alt"] in html

    def test_respondent_group_tick_boxes_appear(self, client: TestClient) -> None:
        """PRD §1.2a: the story card carries respondent-group tick boxes."""
        html = _pack_html(client, _create_full(client)["id"])
        assert "Which group are you in?" in html
        for group in FULL_DEFINITION["capture_settings"]["respondent_groups"]:
            assert group in html

    def test_one_signifier_sheet_per_signifier(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        sheets = re.findall(r'data-sheet="signifier"', html)
        assert len(sheets) == 4, "expected one sheet each for triad, dyad, stones and MCQ"

    def test_labels_reflect_an_edit(self, client: TestClient) -> None:
        """The pack renders the version's current wording, not a cached copy."""
        created = _create_full(client)
        edited = {**FULL_DEFINITION, "triads": [{**TRIAD, "corners": ["Speed", "Care", "Budget"]}]}
        client.put(f"/api/frameworks/{created['id']}", json={"definition": edited})

        html = _pack_html(client, created["id"])
        assert "Budget" in html
        assert "Cost" not in html


class TestAnonymityLineIsVerbatim:
    """Constraint 9: the anonymity statement is printed verbatim on the card."""

    def test_the_full_statement_appears_word_for_word(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        assert CANONICAL_ANONYMITY_TEXT in html

    def test_it_sits_on_the_story_card(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        card = html.split('data-sheet="story-card"')[1].split("</section>")[0]
        assert CANONICAL_ANONYMITY_TEXT in card

    def test_an_edited_statement_is_printed_as_edited(self, client: TestClient) -> None:
        """Whatever this version says is what the card prints — no substitution."""
        custom = "This is anonymous. Nothing about you is stored."
        created = client.post(
            "/api/frameworks",
            json={
                "name": "Custom wording",
                "definition": {
                    **FULL_DEFINITION,
                    "capture_settings": {"anonymity_text": custom},
                },
            },
        ).json()

        html = _pack_html(client, created["id"])
        assert custom in html
        assert CANONICAL_ANONYMITY_TEXT not in html


class TestPrintCssOneSheetPerPage:
    """PRD §6: assert the page-break rules are present."""

    def test_page_break_rule_is_present(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        assert "page-break-after: always" in html
        assert "break-after: page" in html

    def test_sheets_are_kept_off_page_boundaries(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        assert "page-break-inside: avoid" in html
        assert "break-inside: avoid" in html

    def test_page_size_is_a4(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        assert "@page" in html
        assert "A4" in html

    def test_sheet_count_matches_story_card_plus_signifiers_plus_facilitator(
        self, client: TestClient
    ) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        total = len(re.findall(r'class="sheet[ "]', html))
        assert total == 1 + 4 + 1

    def test_the_on_screen_intro_does_not_print(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        printed = html.split("@media print")[1]
        assert ".pack-intro { display: none; }" in printed


class TestPhotocopierSafe:
    """PRD §5b print grammar: black on white, no colour dependence."""

    def test_no_colour_is_used(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        colours = set(re.findall(r"#[0-9a-fA-F]{3,6}", html))
        assert colours <= {"#000", "#fff"}, f"non-monochrome colours in the pack: {colours}"

    def test_labels_are_at_least_fourteen_point(self, client: TestClient) -> None:
        """§5b: ≥14pt labels on the printed sheets."""
        html = _pack_html(client, _create_full(client)["id"])
        label_rule = re.search(r"\.sheet-label \{[^}]*font-size:\s*(\d+)pt", html)
        assert label_rule is not None
        assert int(label_rule.group(1)) >= 14

    def test_pack_is_self_contained(self, client: TestClient) -> None:
        """Constraint 4: printing must work with no network at all."""
        html = _pack_html(client, _create_full(client)["id"])
        assert "<style>" in html
        for remote in ("http://", "https://", "<script", "@import"):
            assert remote not in html, f"paper pack reaches outside itself via {remote!r}"


class TestFacilitatorSheet:
    """PRD §1.2c: instructions, materials, and a reconciliation grid."""

    def test_facilitator_sheet_exists(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        assert 'data-sheet="facilitator"' in html

    def test_reconciliation_grid_has_its_three_counts(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        facilitator = html.split('data-sheet="facilitator"')[1]
        for heading in ("Handed out", "Returned", "Entered"):
            assert heading in facilitator

    def test_it_lists_every_sheet_in_the_pack(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        facilitator = html.split('data-sheet="facilitator"')[1]
        for title in (TRIAD["title"], DYAD["title"], STONES["title"], MCQ["title"]):
            assert title in facilitator

    def test_it_tells_the_facilitator_not_to_collect_names(self, client: TestClient) -> None:
        html = _pack_html(client, _create_full(client)["id"])
        facilitator = html.split('data-sheet="facilitator"')[1]
        assert "No names." in facilitator


class TestEdgeCases:
    def test_a_framework_with_no_signifiers_still_prints(self, client: TestClient) -> None:
        """An empty framework gives a story card and a facilitator sheet."""
        created = client.post("/api/frameworks", json={"name": "Just a prompt"}).json()

        html = _pack_html(client, created["id"])

        assert 'data-sheet="story-card"' in html
        assert 'data-sheet="facilitator"' in html
        assert 'data-sheet="signifier"' not in html

    def test_labels_are_html_escaped(self, client: TestClient) -> None:
        """A label with angle brackets must not break the page."""
        created = client.post(
            "/api/frameworks",
            json={
                "name": "Escaping",
                "definition": {
                    "dyads": [
                        {
                            "id": "risky",
                            "title": "Tag <script>alert(1)</script> test",
                            "left": "A & B",
                            "right": "C > D",
                        }
                    ]
                },
            },
        ).json()

        html = _pack_html(client, created["id"])

        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html
        assert "A &amp; B" in html

    def test_missing_framework_explains_itself(self, client: TestClient) -> None:
        response = client.get("/api/frameworks/4242/paper-pack")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "framework_not_found"

    def test_each_version_prints_its_own_wording(self, client: TestClient, session) -> None:  # noqa: ANN001
        """A meaning change must not retro-print onto the old version's pack."""
        from backend.models import Anecdote

        created = _create_full(client)
        session.add(
            Anecdote(
                framework_id=created["id"],
                text="A story.",
                source_type="capture",
                entry_mode="admin",
                input_method="typed",
            )
        )
        session.commit()

        child = client.put(
            f"/api/frameworks/{created['id']}",
            json={
                "definition": {**FULL_DEFINITION, "prompt_text": "A different question entirely."},
                "edit_kind": "meaning_change",
            },
        ).json()

        assert FULL_DEFINITION["prompt_text"] in _pack_html(client, created["id"])
        assert "A different question entirely." in _pack_html(client, child["id"])


# --------------------------------------------------------------------------
# Corner labels have to fit on the sheet
# --------------------------------------------------------------------------
#
# They did not. Anchored outward, a corner label grew into an 80px margin and
# SVG clipped the remainder without a word: "Doing it by the book" arrived on
# the printed sheet as "Doing it b". A facilitator then handed that to a room,
# and nobody in it could know what the third corner had been called.
#
# The widget on screen had the same defect and the same cause. Both now anchor
# inward and wrap into the half of the base they start from.


class TestCornerLabelsFitTheSheet:
    LONG = ["Speed", "Doing it by the book", "Looking after each other"]

    def _triad_svg(self, client: TestClient, corners: list[str]) -> str:
        definition = {
            "prompt_text": "Tell us about a moment at work that stuck with you.",
            "triads": [{"id": "t1", "title": "What drove this?", "corners": corners}],
            "dyads": [],
            "mcqs": [],
            "capture_settings": {},
        }
        created = client.post(
            "/api/frameworks", json={"name": "Labels", "definition": definition}
        )
        assert created.status_code == 201, created.text
        return _pack_html(client, created.json()["id"])

    def test_a_long_corner_name_survives_onto_the_sheet(self, client: TestClient) -> None:
        """Every word of every corner has to reach the paper."""
        html = self._triad_svg(client, self.LONG)

        for corner in self.LONG:
            for word in corner.split():
                assert word in html, f"{word!r} of {corner!r} never reached the sheet"

    def test_the_labels_are_anchored_inward(self, client: TestClient) -> None:
        """The fix itself, so a later edit cannot quietly undo it.

        Anchoring the left corner "end" is what put the label in the margin.
        """
        html = self._triad_svg(client, self.LONG)
        triad = html[html.index("Triangle with corners") :][:1400]

        assert 'text-anchor="start"' in triad
        assert 'text-anchor="end"' in triad
        assert 'text-anchor="middle"' in triad

    def test_a_long_name_is_wrapped_rather_than_cut(self, client: TestClient) -> None:
        """Wrapped means more <text> lines than there are corners."""
        from backend.paper_pack import wrap_label

        wrapped = wrap_label("Getting it done before the shift ends", 260.0)

        assert len(wrapped) > 1
        assert " ".join(wrapped) == "Getting it done before the shift ends"

    def test_a_single_long_word_keeps_its_own_line(self) -> None:
        """Better slightly over the line than broken into nonsense."""
        from backend.paper_pack import wrap_label

        assert wrap_label("Interdepartmental", 40.0) == ["Interdepartmental"]

    def test_a_short_name_is_left_alone(self) -> None:
        from backend.paper_pack import wrap_label

        assert wrap_label("Speed", 260.0) == ["Speed"]

    def test_an_empty_corner_does_not_crash_the_sheet(self) -> None:
        from backend.paper_pack import wrap_label

        assert wrap_label("", 260.0) == [""]
        assert wrap_label(None, 260.0) == [""]
