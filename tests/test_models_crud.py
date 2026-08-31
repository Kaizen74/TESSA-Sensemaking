"""CRUD across the six tables of PRD §3, plus the vocabularies they enforce."""

from __future__ import annotations

import datetime as dt

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.models import (
    INPUT_METHODS,
    Anecdote,
    CaptureLink,
    Framework,
    ImportJob,
    Signification,
    Tag,
)


def _framework(session, **overrides) -> Framework:  # noqa: ANN001
    defaults = {
        "name": "Ground handling pilot",
        "version": 1,
        "definition_json": {"prompt_text": "Tell us about a recent shift."},
        "edit_log_json": [],
    }
    framework = Framework(**{**defaults, **overrides})
    session.add(framework)
    session.flush()
    return framework


def _anecdote(session, framework: Framework, **overrides) -> Anecdote:  # noqa: ANN001
    defaults = {
        "framework_id": framework.id,
        "text": "The inbound was early and nobody had the paperwork.",
        "source_type": "capture",
        "entry_mode": "admin",
        "input_method": "typed",
    }
    anecdote = Anecdote(**{**defaults, **overrides})
    session.add(anecdote)
    session.flush()
    return anecdote


class TestFramework:
    def test_create_and_read(self, session) -> None:  # noqa: ANN001
        framework = _framework(session)
        session.commit()

        loaded = session.get(Framework, framework.id)
        assert loaded is not None
        assert loaded.name == "Ground handling pilot"
        assert loaded.version == 1
        assert loaded.is_active is True
        assert loaded.parent_framework_id is None
        assert loaded.edit_log_json == []
        assert isinstance(loaded.created_at, dt.datetime)

    def test_edit_log_json_records_a_wording_fix(self, session) -> None:  # noqa: ANN001
        """A wording fix appends to the log in place (PRD §3)."""
        framework = _framework(session)
        framework.edit_log_json = [
            {
                "field_path": "triads.0.corners.1",
                "old_text": "Time presure",
                "new_text": "Time pressure",
                "edited_at": "2026-08-14T10:00:00",
                "kind": "wording_fix",
            }
        ]
        session.commit()

        loaded = session.get(Framework, framework.id)
        assert len(loaded.edit_log_json) == 1
        assert loaded.edit_log_json[0]["kind"] == "wording_fix"
        assert loaded.edit_log_json[0]["old_text"] == "Time presure"

    def test_parent_framework_id_links_version_n_plus_1_to_n(self, session) -> None:  # noqa: ANN001
        """A meaning change creates a new row pointing back at its parent."""
        v1 = _framework(session, version=1)
        v2 = _framework(session, version=2, parent_framework_id=v1.id)
        session.commit()

        assert v2.parent_framework_id == v1.id
        chain = session.scalars(
            select(Framework).where(Framework.parent_framework_id == v1.id)
        ).all()
        assert [f.id for f in chain] == [v2.id]

    def test_update_and_delete(self, session) -> None:  # noqa: ANN001
        framework = _framework(session)
        session.commit()

        framework.is_active = False
        session.commit()
        assert session.get(Framework, framework.id).is_active is False

        session.delete(framework)
        session.commit()
        assert session.get(Framework, framework.id) is None


class TestCaptureLink:
    def test_create_and_revoke(self, session) -> None:  # noqa: ANN001
        framework = _framework(session)
        link = CaptureLink(framework_id=framework.id, token="tok-abc123", label="Shift A")
        session.add(link)
        session.commit()

        assert link.is_active is True
        assert link.revoked_at is None

        link.is_active = False
        link.revoked_at = dt.datetime(2026, 8, 14, 12, 0, 0)
        session.commit()

        loaded = session.get(CaptureLink, link.id)
        assert loaded.is_active is False
        assert loaded.revoked_at == dt.datetime(2026, 8, 14, 12, 0, 0)

    def test_token_is_unique(self, session) -> None:  # noqa: ANN001
        framework = _framework(session)
        session.add(CaptureLink(framework_id=framework.id, token="duplicate"))
        session.commit()

        session.add(CaptureLink(framework_id=framework.id, token="duplicate"))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


class TestAnecdote:
    def test_create_with_provenance(self, session) -> None:  # noqa: ANN001
        """Constraint 3: provenance on every record."""
        framework = _framework(session)
        anecdote = _anecdote(
            session,
            framework,
            source_type="import",
            entry_mode="link",
            input_method="imported",
            source_file="workshop.xlsx",
            source_locator="Sheet1!A14",
            respondent_group="Ramp",
        )
        session.commit()

        loaded = session.get(Anecdote, anecdote.id)
        assert loaded.framework_id == framework.id
        assert loaded.source_file == "workshop.xlsx"
        assert loaded.source_locator == "Sheet1!A14"
        assert loaded.respondent_group == "Ramp"
        assert loaded.status == "pending_validation"

    @pytest.mark.parametrize("input_method", INPUT_METHODS)
    def test_all_four_input_methods_are_accepted(self, session, input_method) -> None:  # noqa: ANN001
        """PRD §3: input_method is typed | voice | paper | imported."""
        framework = _framework(session)
        _anecdote(session, framework, input_method=input_method)
        session.commit()

        stored = session.scalars(select(Anecdote.input_method)).all()
        assert stored == [input_method]

    def test_input_method_rejects_anything_else(self, session) -> None:  # noqa: ANN001
        framework = _framework(session)
        # The helper flushes, so the CHECK fires inside the raises block.
        with pytest.raises(IntegrityError):
            _anecdote(session, framework, input_method="telepathy")
        session.rollback()

    @pytest.mark.parametrize("entry_mode", ["admin", "link", "kiosk"])
    def test_entry_modes_accepted(self, session, entry_mode) -> None:  # noqa: ANN001
        framework = _framework(session)
        _anecdote(session, framework, entry_mode=entry_mode)
        session.commit()
        assert session.scalars(select(Anecdote.entry_mode)).all() == [entry_mode]

    def test_entry_mode_rejects_anything_else(self, session) -> None:  # noqa: ANN001
        framework = _framework(session)
        with pytest.raises(IntegrityError):
            _anecdote(session, framework, entry_mode="carrier_pigeon")
        session.rollback()

    @pytest.mark.parametrize("status", ["pending_validation", "validated", "rejected"])
    def test_statuses_accepted(self, session, status) -> None:  # noqa: ANN001
        framework = _framework(session)
        _anecdote(session, framework, status=status)
        session.commit()
        assert session.scalars(select(Anecdote.status)).all() == [status]

    def test_status_rejects_anything_else(self, session) -> None:  # noqa: ANN001
        framework = _framework(session)
        with pytest.raises(IntegrityError):
            _anecdote(session, framework, status="maybe")
        session.rollback()

    def test_binds_to_the_exact_framework_version_answered(self, session) -> None:  # noqa: ANN001
        """An old story stays on v1 when v2 appears (PRD §3)."""
        v1 = _framework(session, version=1)
        old_story = _anecdote(session, v1)
        session.commit()

        v2 = _framework(session, version=2, parent_framework_id=v1.id)
        new_story = _anecdote(session, v2)
        session.commit()

        assert session.get(Anecdote, old_story.id).framework_id == v1.id
        assert session.get(Anecdote, new_story.id).framework_id == v2.id

    def test_framework_id_must_reference_a_real_framework(self, session) -> None:  # noqa: ANN001
        session.add(
            Anecdote(
                framework_id=9999,
                text="Orphan.",
                source_type="capture",
                entry_mode="admin",
                input_method="typed",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


class TestSignification:
    def test_triad_value_round_trips(self, session) -> None:  # noqa: ANN001
        framework = _framework(session)
        anecdote = _anecdote(session, framework)
        signification = Signification(
            anecdote_id=anecdote.id,
            signifier_id="triad-1",
            signifier_type="triad",
            value_json={"a": 0.5, "b": 0.3, "c": 0.2},
            signified_by="respondent",
        )
        session.add(signification)
        session.commit()

        loaded = session.get(Signification, signification.id)
        assert loaded.value_json == {"a": 0.5, "b": 0.3, "c": 0.2}
        assert sum(loaded.value_json.values()) == pytest.approx(1.0)
        assert loaded.ai_confidence is None
        assert loaded.validated_at is None

    def test_ai_proposal_carries_confidence_and_awaits_validation(self, session) -> None:  # noqa: ANN001
        """Constraints 1 and 2: AI proposals queue like everything else."""
        framework = _framework(session)
        anecdote = _anecdote(session, framework, input_method="imported")
        signification = Signification(
            anecdote_id=anecdote.id,
            signifier_id="dyad-1",
            signifier_type="dyad",
            value_json={"value": 0.62},
            ai_confidence=0.55,
            signified_by="ai",
        )
        session.add(signification)
        session.commit()

        loaded = session.get(Signification, signification.id)
        assert loaded.ai_confidence == pytest.approx(0.55)
        assert loaded.validated_at is None, "an AI proposal must not arrive pre-validated"

    @pytest.mark.parametrize("signifier_type", ["triad", "dyad", "stones", "mcq"])
    def test_signifier_types_accepted(self, session, signifier_type) -> None:  # noqa: ANN001
        framework = _framework(session)
        anecdote = _anecdote(session, framework)
        session.add(
            Signification(
                anecdote_id=anecdote.id,
                signifier_id=f"{signifier_type}-1",
                signifier_type=signifier_type,
                value_json={},
                signified_by="respondent",
            )
        )
        session.commit()
        assert session.scalars(select(Signification.signifier_type)).all() == [signifier_type]

    def test_signifier_type_rejects_anything_else(self, session) -> None:  # noqa: ANN001
        framework = _framework(session)
        anecdote = _anecdote(session, framework)
        session.add(
            Signification(
                anecdote_id=anecdote.id,
                signifier_id="x",
                signifier_type="hexagon",
                value_json={},
                signified_by="respondent",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


class TestImportJob:
    def test_stage_machine_values_round_trip(self, session) -> None:  # noqa: ANN001
        job = ImportJob(
            filename="workshop.xlsx",
            file_type="xlsx",
            file_hash="a" * 64,
            segments_found=27,
        )
        session.add(job)
        session.commit()

        assert job.stage == "uploaded"
        assert job.normalised_json is None
        assert job.column_mapping_json is None

        job.stage = "mapping_confirmed"
        job.column_mapping_json = {"Sheet1": {"story": "B", "group": "C"}}
        session.commit()

        loaded = session.get(ImportJob, job.id)
        assert loaded.stage == "mapping_confirmed"
        assert loaded.column_mapping_json == {"Sheet1": {"story": "B", "group": "C"}}

    def test_stage_rejects_anything_else(self, session) -> None:  # noqa: ANN001
        session.add(
            ImportJob(filename="x.csv", file_type="csv", file_hash="b" * 64, stage="halfway")
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


class TestTag:
    def test_create_and_delete(self, session) -> None:  # noqa: ANN001
        framework = _framework(session)
        anecdote = _anecdote(session, framework)
        tag = Tag(anecdote_id=anecdote.id, tag_text="handover")
        session.add(tag)
        session.commit()

        assert session.scalars(select(Tag.tag_text)).all() == ["handover"]

        session.delete(tag)
        session.commit()
        assert session.scalars(select(Tag)).all() == []
