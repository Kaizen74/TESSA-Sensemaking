"""Validation of ``definition_json`` and the anonymity statement it carries."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.framework_schema import (
    CANONICAL_ANONYMITY_TEXT,
    SIGNIFIER_SCREEN_WARNING_THRESHOLD,
    FrameworkDefinition,
    default_definition,
    validate_definition,
)
from backend.models import Base

MINIMAL_TRIAD = {
    "id": "pressure",
    "title": "What drove this?",
    "corners": ["Speed", "Care", "Cost"],
}
MINIMAL_DYAD = {"id": "clarity", "title": "How clear?", "left": "Murky", "right": "Clear"}
MINIMAL_MCQ = {"id": "team", "title": "Which team?", "options": ["Ramp", "Cabin"]}
MINIMAL_STONES = {
    "id": "forces",
    "title": "Place the forces",
    "x_axis": {"low": "Rare", "high": "Constant"},
    "y_axis": {"low": "Minor", "high": "Major"},
    "chips": ["Time", "Kit", "People"],
}


class TestDefaults:
    def test_a_new_framework_is_valid_with_no_signifiers(self) -> None:
        """The operator starts from something valid and fills it in."""
        definition = default_definition()
        assert definition.signifier_count == 0
        assert definition.prompt_text

    def test_anonymity_text_defaults_to_the_canonical_statement(self) -> None:
        assert default_definition().capture_settings.anonymity_text == CANONICAL_ANONYMITY_TEXT

    def test_reflection_and_voice_default_on(self) -> None:
        """Constraint 10: reflection on by default; voice paired with typing."""
        settings = default_definition().capture_settings
        assert settings.reflection_enabled is True
        assert settings.voice_enabled is True


class TestAnonymityStatementIsTrueOfTheCode:
    """Constraint 9: the statement must be literally true of the schema.

    Each clause of :data:`CANONICAL_ANONYMITY_TEXT` is checked against the live
    database metadata, so the sentence cannot quietly become a lie.
    """

    def _all_columns(self) -> set[str]:
        return {
            column.name.lower()
            for table in Base.metadata.tables.values()
            for column in table.columns
        }

    def test_claim_no_name_is_true(self) -> None:
        assert "your name" in CANONICAL_ANONYMITY_TEXT
        respondent_columns = {
            column.name.lower()
            for table_name in ("anecdotes", "significations", "tags", "capture_links")
            for column in Base.metadata.tables[table_name].columns
        }
        assert "name" not in respondent_columns

    def test_claim_no_email_is_true(self) -> None:
        assert "your email" in CANONICAL_ANONYMITY_TEXT
        assert not any("email" in column for column in self._all_columns())

    def test_claim_no_device_is_true(self) -> None:
        assert "your device" in CANONICAL_ANONYMITY_TEXT
        for banned in ("device_id", "user_agent", "fingerprint"):
            assert banned not in self._all_columns()

    def test_claim_no_network_address_is_true(self) -> None:
        assert "network address" in CANONICAL_ANONYMITY_TEXT
        for banned in ("ip", "ip_address", "remote_addr"):
            assert banned not in self._all_columns()

    def test_claim_time_is_rounded_to_the_hour_is_true(self) -> None:
        assert "rounded to the hour" in CANONICAL_ANONYMITY_TEXT
        anecdote_columns = {c.name for c in Base.metadata.tables["anecdotes"].columns}
        assert "created_at_hour" in anecdote_columns
        assert "created_at" not in anecdote_columns

    def test_claim_about_what_is_saved_is_true(self) -> None:
        """Story, placements, and chosen group — and that is the whole list."""
        assert "your story, your placements, and the group you pick" in CANONICAL_ANONYMITY_TEXT
        anecdote_columns = {c.name for c in Base.metadata.tables["anecdotes"].columns}
        assert "text" in anecdote_columns
        assert "respondent_group" in anecdote_columns


class TestTriadValidation:
    def test_valid_triad_accepted(self) -> None:
        definition = validate_definition({"triads": [MINIMAL_TRIAD]})
        assert definition.triads[0].corners == ["Speed", "Care", "Cost"]

    def test_triad_needs_exactly_three_corners(self) -> None:
        with pytest.raises(ValidationError):
            validate_definition({"triads": [{**MINIMAL_TRIAD, "corners": ["A", "B"]}]})

    def test_triad_corners_must_differ(self) -> None:
        with pytest.raises(ValidationError, match="must be different"):
            validate_definition({"triads": [{**MINIMAL_TRIAD, "corners": ["A", "B", "a"]}]})

    def test_empty_corner_label_rejected(self) -> None:
        with pytest.raises(ValidationError):
            validate_definition({"triads": [{**MINIMAL_TRIAD, "corners": ["A", "B", ""]}]})


class TestDyadValidation:
    def test_valid_dyad_accepted(self) -> None:
        definition = validate_definition({"dyads": [MINIMAL_DYAD]})
        assert definition.dyads[0].left == "Murky"

    def test_poles_must_differ(self) -> None:
        with pytest.raises(ValidationError, match="must be different"):
            validate_definition({"dyads": [{**MINIMAL_DYAD, "left": "Same", "right": "same"}]})


class TestStonesValidation:
    def test_valid_stones_accepted(self) -> None:
        definition = validate_definition({"stones": MINIMAL_STONES})
        assert definition.stones is not None
        assert definition.stones.chips == ["Time", "Kit", "People"]

    def test_axis_ends_must_differ(self) -> None:
        broken = {**MINIMAL_STONES, "x_axis": {"low": "Same", "high": "Same"}}
        with pytest.raises(ValidationError, match="two different end labels"):
            validate_definition({"stones": broken})

    def test_chips_must_be_distinct(self) -> None:
        broken = {**MINIMAL_STONES, "chips": ["Time", "time"]}
        with pytest.raises(ValidationError, match="own label"):
            validate_definition({"stones": broken})

    def test_stones_needs_at_least_one_chip(self) -> None:
        with pytest.raises(ValidationError):
            validate_definition({"stones": {**MINIMAL_STONES, "chips": []}})


class TestMcqValidation:
    def test_valid_mcq_accepted(self) -> None:
        definition = validate_definition({"mcqs": [MINIMAL_MCQ]})
        assert definition.mcqs[0].multi is False

    def test_mcq_needs_at_least_two_options(self) -> None:
        with pytest.raises(ValidationError):
            validate_definition({"mcqs": [{**MINIMAL_MCQ, "options": ["Only one"]}]})

    def test_options_must_be_distinct(self) -> None:
        with pytest.raises(ValidationError, match="own label"):
            validate_definition({"mcqs": [{**MINIMAL_MCQ, "options": ["Ramp", "ramp"]}]})


class TestIdRules:
    def test_signifier_ids_must_be_unique_across_kinds(self) -> None:
        """Significations key on the id alone, so one namespace covers all kinds."""
        with pytest.raises(ValidationError, match="used twice"):
            validate_definition(
                {
                    "triads": [{**MINIMAL_TRIAD, "id": "shared"}],
                    "dyads": [{**MINIMAL_DYAD, "id": "shared"}],
                }
            )

    def test_ids_reject_awkward_characters(self) -> None:
        with pytest.raises(ValidationError):
            validate_definition({"triads": [{**MINIMAL_TRIAD, "id": "Has Spaces"}]})

    def test_unknown_key_is_rejected(self) -> None:
        """A typo in the Studio should fail loudly, not vanish silently."""
        with pytest.raises(ValidationError):
            validate_definition({"prompt_txt": "typo"})


class TestScreenCountAndEstimate:
    def _full_definition(self) -> FrameworkDefinition:
        return validate_definition(
            {
                "triads": [MINIMAL_TRIAD],
                "dyads": [MINIMAL_DYAD],
                "stones": MINIMAL_STONES,
                "mcqs": [MINIMAL_MCQ],
            }
        )

    def test_signifier_count_covers_every_kind(self) -> None:
        assert self._full_definition().signifier_count == 4

    def test_signifiers_in_order_returns_each_with_its_kind(self) -> None:
        ordered = self._full_definition().signifiers_in_order()
        assert [kind for kind, _ in ordered] == ["triad", "dyad", "stones", "mcq"]

    def test_estimate_grows_with_more_signifiers(self) -> None:
        lean = validate_definition({"triads": [MINIMAL_TRIAD]})
        assert self._full_definition().estimated_seconds() > lean.estimated_seconds()

    def test_a_lean_framework_fits_the_four_minute_bar(self) -> None:
        """Constraint 10: ≤4 minutes typical."""
        lean = validate_definition({"triads": [MINIMAL_TRIAD], "dyads": [MINIMAL_DYAD]})
        assert lean.estimated_minutes() <= 4.0

    def test_warning_triggers_past_six_signifier_screens(self) -> None:
        """PRD §1.1: warn past roughly six signifier screens."""
        many = validate_definition(
            {
                "triads": [{**MINIMAL_TRIAD, "id": f"t{i}"} for i in range(4)],
                "dyads": [{**MINIMAL_DYAD, "id": f"d{i}"} for i in range(3)],
            }
        )
        assert many.signifier_count > SIGNIFIER_SCREEN_WARNING_THRESHOLD
        assert many.exceeds_screen_warning is True

    def test_no_warning_at_the_threshold(self) -> None:
        at_limit = validate_definition(
            {"triads": [{**MINIMAL_TRIAD, "id": f"t{i}"} for i in range(6)]}
        )
        assert at_limit.signifier_count == SIGNIFIER_SCREEN_WARNING_THRESHOLD
        assert at_limit.exceeds_screen_warning is False
