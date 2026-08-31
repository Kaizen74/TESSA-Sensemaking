"""Public capture endpoints (PRD §4).

"Token-gated, rate-limited, identifier-free; framework fetch always returns the
exact version the link points at."

These are the only endpoints a device that is not the operator's laptop ever
touches, so they are where constraint 9 has to hold hardest. Three rules govern
this module:

1. **Nothing about the requester is read.** No header, no client address, no
   user agent is inspected, logged, or stored — not even transiently. The
   request object is deliberately never accepted as a parameter here, so there
   is no way to reach for one by accident, and a test asserts that.
2. **The token decides everything.** The framework version, the entry mode, and
   the link id all come from the token, never from the body. A respondent's
   browser cannot point its story at a different question set or claim to be a
   different entry mode.
3. **A closed link is closed.** PRD §7.6 requires revoked links to close, so a
   revoked or unknown token is refused before anything else happens.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import errors
from backend.capture_schema import PublicCaptureSubmission
from backend.db import get_session
from backend.framework_schema import FrameworkDefinition
from backend.models import CaptureLink, Framework
from backend.rate_limit import fetch_limiter, submit_limiter
from backend.routers.capture import CaptureResult, store_capture

router = APIRouter(prefix="/api/public", tags=["public-capture"])

#: Entry mode every story through a capture link carries (PRD §3).
ENTRY_MODE_LINK = "link"


class PublicFrameworkOut(BaseModel):
    """What a respondent's browser is told: the questions, and nothing else.

    No framework id, no link id, no counts, no operator-facing metadata — the
    wizard needs the wording and the shape, so that is all it gets.
    """

    definition: FrameworkDefinition
    framework_version: int


def _link_or_refuse(session: Session, token: str) -> CaptureLink:
    """Resolve a token to an open link, or refuse in plain English.

    An unknown token and a revoked token give the same shape of answer, so the
    page a respondent sees is helpful without turning the endpoint into an
    oracle for guessing valid tokens.
    """
    link = session.scalars(select(CaptureLink).where(CaptureLink.token == token)).first()

    if link is None:
        raise errors.not_found(
            "capture_link_not_found",
            "This link is not one we recognise.",
            "Check with whoever gave you the link or the QR code — they may have "
            "a newer one.",
        )

    if not link.is_active:
        raise errors.not_found(
            "capture_link_closed",
            "This link has been closed, so it is no longer collecting stories.",
            "If you still have something to share, ask whoever gave you the link "
            "for the current one.",
        )

    return link


def _framework_or_refuse(session: Session, link: CaptureLink) -> Framework:
    framework = session.get(Framework, link.framework_id)
    if framework is None:
        raise errors.not_found(
            "framework_not_found",
            "The questions this link points at are no longer available.",
            "Ask whoever gave you the link for a current one.",
        )
    return framework


def _rate_limit(limiter, token: str) -> None:  # noqa: ANN001
    """Refuse politely when a single link is being hammered.

    Keyed by token, never by requester — see ``backend/rate_limit.py`` for why
    that is the only option open to us.
    """
    if not limiter.check(token):
        raise errors.AppError(
            429,
            "too_many_requests",
            "This link is busy right now, so your story was not sent.",
            "Wait a minute and press send again — what you wrote is still here.",
        )


@router.get("/capture/{token}", response_model=PublicFrameworkOut)
def get_public_framework(
    token: str,
    session: Annotated[Session, Depends(get_session)],
) -> PublicFrameworkOut:
    """The exact framework version this link points at (PRD §4).

    Always the version the link was created against, never "the latest" — that
    is what keeps a story bound to the wording its teller actually saw, even
    after the Studio has moved on.
    """
    _rate_limit(fetch_limiter, token)
    link = _link_or_refuse(session, token)
    framework = _framework_or_refuse(session, link)

    return PublicFrameworkOut(
        definition=FrameworkDefinition.model_validate(framework.definition_json),
        framework_version=framework.version,
    )


@router.post("/capture/{token}", response_model=CaptureResult, status_code=201)
def create_public_capture(
    token: str,
    body: PublicCaptureSubmission,
    session: Annotated[Session, Depends(get_session)],
) -> CaptureResult:
    """Store a story that arrived through a capture link.

    ``entry_mode`` is fixed to ``link`` and the framework comes from the token,
    so neither can be chosen by the caller.
    """
    _rate_limit(submit_limiter, token)
    link = _link_or_refuse(session, token)
    framework = _framework_or_refuse(session, link)

    return store_capture(
        session,
        framework,
        body,
        entry_mode=ENTRY_MODE_LINK,
        capture_link_id=link.id,
    )
