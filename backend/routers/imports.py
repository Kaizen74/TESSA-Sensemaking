"""Ingestion endpoints (PRD §4) — the staged import machine.

``/api/import`` → ``/organise`` → ``/mapping`` → ``/propose``, each step refusing
to run out of turn (:mod:`backend.stage_machine`). The gate between ``/mapping``
and ``/propose`` is the one constraint 1 is about: Stage B cannot run on a file
whose Stage A output a person has not confirmed, and asking for it returns 409
rather than quietly doing the confirmation first.

The division of labour is the point of this module:

* **Upload parses.** Reading the file is deterministic and offline, so it
  happens as the file arrives. The AI is never shown the file — only the text
  the parser found, with its locators.
* **Organise proposes.** Stage A writes its proposal onto the job and stops.
  Nothing enters the dataset (constraint 1).
* **Mapping confirms.** The operator's confirmation is checked against the file,
  the rows are then read deterministically, and the reconciliation is computed
  and returned for display (constraint 12).
* **Propose marks up.** Stage B suggests where each story sits, and the stories
  are written as anecdotes that are ``pending_validation`` — in the queue, not
  in the data. The last stage, ``done``, is reached only by a person working
  through that queue (:mod:`backend.routers.queue`).
"""

from __future__ import annotations

import datetime as dt
import hashlib
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import errors, stage_machine
from backend.ai_client import AiError
from backend.dataset import STATUS_PENDING
from backend.db import get_session
from backend.extraction import (
    ConfirmedExtraction,
    ExtractionError,
    Reconciliation,
    SheetMapping,
    confirm,
)
from backend.framework_schema import FrameworkDefinition
from backend.models import Anecdote, Framework, ImportJob, Signification, hour_rounded_now
from backend.organise import (
    NarrativeSegment,
    OrganiseError,
    OrganiseResult,
    SheetProposal,
    organise,
)
from backend.parsers import FILE_CLASSES, NormalisedDocument, ParseError, classify, parse
from backend.propose import (
    SIGNIFIED_BY_AI,
    SOURCE_TYPE_IMPORT,
    ProposeError,
    propose,
)
from backend.routers.queue import QueueCounts
from backend.routers.queue import counts as queue_counts

router = APIRouter(prefix="/api/import", tags=["import"])

#: How many rows of each sheet the Mapping screen shows so the operator can see
#: what they are mapping. The screen is for choosing a column, not for reading
#: the data — that is what the validation queue is for.
PREVIEW_ROWS = 5


class SheetView(BaseModel):
    """One sheet as the Mapping screen needs it."""

    model_config = ConfigDict(extra="forbid")

    name: str
    headers: list[str]
    row_count: int
    sample_rows: list[list[str]]


class ConfirmationView(BaseModel):
    """What confirmation produced, without repeating every candidate's text."""

    model_config = ConfigDict(extra="forbid")

    reconciliation: Reconciliation
    candidate_count: int
    sheets: list[SheetMapping] = []
    accepted: list[int] = []


class ImportJobSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    filename: str
    file_type: str
    file_class: str
    stage: str
    #: The stage in words, so no screen has to translate a stage name.
    stage_label: str
    segments_found: int | None
    error_message: str | None
    created_at: dt.datetime


class ImportJobDetail(ImportJobSummary):
    block_count: int
    sheets: list[SheetView] = []
    organisation: OrganiseResult | None = None
    confirmation: ConfirmationView | None = None
    #: How this file's stories are getting on in the validation queue. Zeroes
    #: until Stage B has run, and the only figures the Import screen quotes.
    queue: QueueCounts | None = None


class ProposeRequest(BaseModel):
    """Which question set the file's stories are being marked up against.

    The operator states it: a file of stories carries no idea of which triads it
    should be read through, and guessing would bind stories to wording their
    tellers never saw.
    """

    model_config = ConfigDict(extra="forbid")

    framework_id: int


class MappingConfirmation(BaseModel):
    """The operator's confirmation of Stage A (constraint 1).

    Prose files send ``accepted`` — which of the proposed passages really are
    whole stories. Tables send ``sheets`` — the confirmed column mapping. The
    shapes are separate because the two decisions are separate, and sending
    neither is refused rather than treated as "accept everything".
    """

    model_config = ConfigDict(extra="forbid")

    accepted: list[int] | None = None
    sheets: list[SheetMapping] | None = None


def _summary(job: ImportJob) -> ImportJobSummary:
    return ImportJobSummary(
        id=job.id,
        filename=job.filename,
        file_type=job.file_type,
        file_class=FILE_CLASSES[job.file_type],
        stage=job.stage,
        stage_label=stage_machine.STAGE_LABELS[job.stage],
        segments_found=job.segments_found,
        error_message=job.error_message,
        created_at=job.created_at,
    )


def _stored_document(job: ImportJob) -> NormalisedDocument:
    """The parsed file as it was stored at upload."""
    payload = (job.normalised_json or {}).get("document")
    if payload is None:  # pragma: no cover - written on every upload
        raise errors.conflict(
            "job_incomplete",
            f"Narrative Lens has no readable copy of '{job.filename}'.",
            "Import the file again.",
        )
    return NormalisedDocument.model_validate(payload)


def _stored_organisation(job: ImportJob) -> OrganiseResult | None:
    payload = (job.normalised_json or {}).get("stage_a")
    return None if payload is None else OrganiseResult.model_validate(payload)


def _stored_confirmation(job: ImportJob) -> ConfirmedExtraction | None:
    payload = job.column_mapping_json
    return None if payload is None else ConfirmedExtraction.model_validate(payload)


def _detail(session: Session, job: ImportJob) -> ImportJobDetail:
    document = _stored_document(job)
    confirmation = _stored_confirmation(job)
    return ImportJobDetail(
        **_summary(job).model_dump(),
        block_count=len(document.blocks),
        sheets=[
            SheetView(
                name=sheet.name,
                headers=sheet.headers,
                row_count=len(sheet.rows),
                sample_rows=sheet.rows[:PREVIEW_ROWS],
            )
            for sheet in document.sheets
        ],
        organisation=_stored_organisation(job),
        confirmation=None
        if confirmation is None
        else ConfirmationView(
            reconciliation=confirmation.reconciliation,
            candidate_count=len(confirmation.candidates),
            sheets=confirmation.sheets,
            accepted=confirmation.accepted,
        ),
        queue=queue_counts(session, job.id),
    )


def _load(session: Session, job_id: int) -> ImportJob:
    job = session.get(ImportJob, job_id)
    if job is None:
        raise errors.not_found(
            "import_not_found",
            f"There is no imported file numbered {job_id}.",
            "Go back to the list of imports and pick one from there.",
        )
    return job


@router.get("", response_model=list[ImportJobSummary])
def list_imports(session: Annotated[Session, Depends(get_session)]) -> list[ImportJobSummary]:
    """Every file imported so far, newest first."""
    jobs = session.scalars(select(ImportJob).order_by(ImportJob.id.desc())).all()
    return [_summary(job) for job in jobs]


@router.get("/{job_id}", response_model=ImportJobDetail)
def get_import(
    job_id: int, session: Annotated[Session, Depends(get_session)]
) -> ImportJobDetail:
    """One file: where it has got to, and whatever it is waiting on."""
    return _detail(session, _load(session, job_id))


@router.post("", response_model=ImportJobDetail, status_code=201)
async def create_import(
    session: Annotated[Session, Depends(get_session)],
    file: Annotated[UploadFile, File()],
) -> ImportJobDetail:
    """Take a file, read it, and park it at ``uploaded``.

    Parsing here rather than at Organise means an unreadable file is refused
    while the operator is still looking at the file picker, and means the
    original never has to be kept: what is stored is the text, not the document.
    """
    filename = (file.filename or "").strip()
    if not filename:
        raise errors.bad_request(
            "no_file",
            "No file arrived with that upload.",
            "Choose a file and try again.",
        )

    data = await file.read()
    try:
        file_type, _ = classify(filename)
        document = parse(filename, data)
    except ParseError as exc:
        raise errors.bad_request(exc.code, exc.message, exc.action) from exc

    job = ImportJob(
        filename=filename,
        file_type=file_type,
        file_hash=hashlib.sha256(data).hexdigest(),
        stage=stage_machine.STAGE_UPLOADED,
        normalised_json={"document": document.model_dump()},
        column_mapping_json=None,
        segments_found=None,
        error_message=None,
    )
    session.add(job)
    session.commit()
    return _detail(session, job)


@router.post("/{job_id}/organise", response_model=ImportJobDetail)
def organise_import(
    job_id: int, session: Annotated[Session, Depends(get_session)]
) -> ImportJobDetail:
    """Stage A. Proposes how the file breaks into stories, and stops there."""
    job = _load(session, job_id)
    stage_machine.require_stage(job, stage_machine.STAGE_UPLOADED)
    document = _stored_document(job)

    try:
        result = organise(document)
    except AiError as exc:
        stage_machine.record_error(job, exc.message)
        session.commit()
        raise errors.upstream(exc.code, exc.message, exc.action) from exc
    except OrganiseError as exc:
        stage_machine.record_error(job, exc.message)
        session.commit()
        raise errors.upstream(exc.code, exc.message, exc.action) from exc

    job.normalised_json = {
        "document": document.model_dump(),
        "stage_a": result.model_dump(),
    }
    job.segments_found = result.segments_found
    job.error_message = None
    stage_machine.advance(job, stage_machine.STAGE_ORGANISED)
    session.commit()
    return _detail(session, job)


@router.post("/{job_id}/mapping", response_model=ImportJobDetail)
def confirm_mapping(
    job_id: int,
    body: MappingConfirmation,
    session: Annotated[Session, Depends(get_session)],
) -> ImportJobDetail:
    """The human confirmation constraint 1 requires, and the reconciliation.

    This is the only door between Stage A and Stage B. The stage gate above it
    means Stage A must have run; the transition table below it means Stage B
    cannot run until this has.
    """
    job = _load(session, job_id)
    stage_machine.require_stage(job, stage_machine.STAGE_ORGANISED)

    document = _stored_document(job)
    organisation = _stored_organisation(job)
    proposed: list[NarrativeSegment] = [] if organisation is None else organisation.segments

    try:
        confirmed = confirm(
            document,
            proposed_segments=proposed,
            accepted=body.accepted,
            mappings=body.sheets,
        )
    except ExtractionError as exc:
        raise errors.bad_request(exc.code, exc.message, exc.action) from exc

    job.column_mapping_json = confirmed.model_dump()
    job.error_message = None
    stage_machine.advance(job, stage_machine.STAGE_MAPPING_CONFIRMED)
    session.commit()
    return _detail(session, job)


@router.post("/{job_id}/propose", response_model=ImportJobDetail)
def propose_import(
    job_id: int,
    body: ProposeRequest,
    session: Annotated[Session, Depends(get_session)],
) -> ImportJobDetail:
    """Stage B. Marks the file's stories up and puts them in the queue.

    The gate on the first line is acceptance criterion 7: a file whose Stage A
    output has not been confirmed by a person cannot be marked up, and asking
    for it returns 409 rather than confirming on the operator's behalf.

    What is written here is deliberately not data. Every anecdote is
    ``pending_validation``, every signification is ``signified_by="ai"`` with no
    ``validated_at``, and only the queue can change either (constraint 1).
    """
    job = _load(session, job_id)
    stage_machine.require_stage(job, stage_machine.STAGE_MAPPING_CONFIRMED)

    framework = session.get(Framework, body.framework_id)
    if framework is None:
        raise errors.not_found(
            "framework_not_found",
            f"There is no question set numbered {body.framework_id}.",
            "Pick a question set from the list and try again.",
        )

    confirmation = _stored_confirmation(job)
    candidates = [] if confirmation is None else confirmation.candidates
    if not candidates:
        raise errors.bad_request(
            "nothing_to_mark_up",
            f"You kept no stories from '{job.filename}', so there is nothing to "
            "mark up.",
            "Import the file again and keep at least one story, or import a "
            "different file.",
        )

    definition = FrameworkDefinition.model_validate(framework.definition_json)
    try:
        proposals = propose(definition, [candidate.text for candidate in candidates])
    except AiError as exc:
        stage_machine.record_error(job, exc.message)
        session.commit()
        raise errors.upstream(exc.code, exc.message, exc.action) from exc
    except ProposeError as exc:
        stage_machine.record_error(job, exc.message)
        session.commit()
        raise errors.upstream(exc.code, exc.message, exc.action) from exc

    by_index = {proposal.index: proposal for proposal in proposals}
    for index, candidate in enumerate(candidates):
        anecdote = Anecdote(
            # Bound to the exact version being marked up against, so a later
            # meaning change cannot retro-fit new wording onto it.
            framework_id=framework.id,
            text=candidate.text,
            title_auto=candidate.title,
            # Constraint 3: the whole provenance, stamped in one place.
            source_type=SOURCE_TYPE_IMPORT,
            entry_mode="admin",
            capture_link_id=None,
            input_method="imported",
            source_file=job.filename,
            source_locator=candidate.source_locator,
            import_job_id=job.id,
            respondent_group=candidate.respondent_group,
            created_at_hour=hour_rounded_now(),
            # Constraint 1: in the queue, not in the data.
            status=STATUS_PENDING,
        )
        session.add(anecdote)
        session.flush()

        for placement in by_index[index].placements:
            session.add(
                Signification(
                    anecdote_id=anecdote.id,
                    signifier_id=placement.signifier_id,
                    signifier_type=placement.signifier_type,
                    value_json=placement.value,
                    ai_confidence=placement.confidence,
                    signified_by=SIGNIFIED_BY_AI,
                    # Nobody has validated this yet, and saying otherwise would
                    # be the app validating on the operator's behalf.
                    validated_at=None,
                )
            )

    job.error_message = None
    stage_machine.advance(job, stage_machine.STAGE_PROPOSED)
    session.commit()
    return _detail(session, job)


__all__ = [
    "ImportJobDetail",
    "ImportJobSummary",
    "MappingConfirmation",
    "ProposeRequest",
    "SheetProposal",
    "router",
]
