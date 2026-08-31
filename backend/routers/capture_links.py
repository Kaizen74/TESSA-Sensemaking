"""Capture link management (PRD §4, §5.2).

A capture link is a token-bearing URL the operator hands out — as a QR poster on
a wall, or a link over Tailscale. It points at one exact framework version, so
stories collected through it stay bound to the wording people actually saw even
after the Studio moves on.

Revoking a link closes it for good. PRD §7.6 requires that revoked links close,
and the public router refuses a revoked token rather than quietly accepting one
more story.
"""

from __future__ import annotations

import datetime as dt
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend import errors, settings
from backend.db import get_session
from backend.models import Anecdote, CaptureLink, Framework, utcnow
from backend.qr import qr_png_bytes
from backend.rate_limit import fetch_limiter, submit_limiter

router = APIRouter(prefix="/api/capture-links", tags=["capture-links"])

#: Token length in bytes before URL-safe encoding. 24 bytes is 192 bits of
#: entropy — unguessable, and still short enough to fit a printed URL.
TOKEN_BYTES = 24


def new_token() -> str:
    """A fresh, unguessable capture token.

    ``secrets`` rather than ``random``: this token is the only thing standing
    between an open LAN and the capture form.
    """
    return secrets.token_urlsafe(TOKEN_BYTES)


def capture_url(token: str, base_url: str | None = None) -> str:
    """The address a respondent's phone opens.

    Defaults to the LAN address the operator's machine answers on, so a QR
    scanned across the room reaches the same server (constraint 4: Tailscale/LAN
    serving is the permitted network).
    """
    base = (base_url or settings.public_base_url()).rstrip("/")
    return f"{base}/c/{token}"


class CaptureLinkCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    framework_id: int
    label: Annotated[str, Field(max_length=200)] | None = None


class CaptureLinkOut(BaseModel):
    id: int
    framework_id: int
    framework_name: str
    framework_version: int
    token: str
    label: str | None
    is_active: bool
    created_at: dt.datetime
    revoked_at: dt.datetime | None
    #: The full address the QR encodes, ready to print or copy.
    url: str
    #: How many stories have come in through this link.
    story_count: int


def _to_out(session: Session, link: CaptureLink) -> CaptureLinkOut:
    framework = session.get(Framework, link.framework_id)
    count = (
        session.scalar(
            select(func.count())
            .select_from(Anecdote)
            .where(Anecdote.capture_link_id == link.id)
        )
        or 0
    )
    return CaptureLinkOut(
        id=link.id,
        framework_id=link.framework_id,
        framework_name=framework.name if framework else "",
        framework_version=framework.version if framework else 0,
        token=link.token,
        label=link.label,
        is_active=link.is_active,
        created_at=link.created_at,
        revoked_at=link.revoked_at,
        url=capture_url(link.token),
        story_count=count,
    )


def _get_or_404(session: Session, link_id: int) -> CaptureLink:
    link = session.get(CaptureLink, link_id)
    if link is None:
        raise errors.not_found(
            "capture_link_not_found",
            f"There is no capture link numbered {link_id}.",
            "Go back to Capture & Links and pick a link from the list.",
        )
    return link


@router.get("", response_model=list[CaptureLinkOut])
def list_capture_links(
    session: Annotated[Session, Depends(get_session)],
) -> list[CaptureLinkOut]:
    """Every link, newest first — open ones and closed ones alike.

    Closed links stay listed on purpose: the stories they collected are still in
    the dataset, and hiding the link would hide where they came from.
    """
    links = session.scalars(
        select(CaptureLink).order_by(CaptureLink.created_at.desc(), CaptureLink.id.desc())
    ).all()
    return [_to_out(session, link) for link in links]


@router.post("", response_model=CaptureLinkOut, status_code=201)
def create_capture_link(
    body: CaptureLinkCreate,
    session: Annotated[Session, Depends(get_session)],
) -> CaptureLinkOut:
    """Open a new capture link against one exact framework version."""
    framework = session.get(Framework, body.framework_id)
    if framework is None:
        raise errors.not_found(
            "framework_not_found",
            f"There is no question set numbered {body.framework_id}.",
            "Pick a question set from the list and try again.",
        )

    link = CaptureLink(
        framework_id=framework.id,
        token=new_token(),
        label=body.label,
        is_active=True,
    )
    session.add(link)
    session.commit()
    return _to_out(session, link)


@router.post("/{link_id}/revoke", response_model=CaptureLinkOut)
def revoke_capture_link(
    link_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> CaptureLinkOut:
    """Close a link for good.

    Revoking is deliberately one-way. A link that could be reopened would mean a
    QR poster taken down from a wall might start working again without anyone
    intending it. Open a new link instead.
    """
    link = _get_or_404(session, link_id)

    if not link.is_active:
        raise errors.conflict(
            "capture_link_already_closed",
            "That link is already closed.",
            "Open a new link if you need to collect more stories.",
        )

    link.is_active = False
    link.revoked_at = utcnow()
    session.commit()

    # Nothing further will be accepted on this token, so its counters are dead
    # weight. Dropping them also keeps the in-memory tables from growing.
    submit_limiter.reset(link.token)
    fetch_limiter.reset(link.token)

    return _to_out(session, link)


@router.get("/{link_id}/qr.png")
def capture_link_qr(
    link_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    """The link's QR code as a PNG, generated locally (constraint 4)."""
    link = _get_or_404(session, link_id)
    png = qr_png_bytes(capture_url(link.token))
    return Response(
        content=png,
        media_type="image/png",
        headers={"Cache-Control": "no-store"},
    )
