"""The error shape from PRD §4.

``{"error": {"code": ..., "message": plain-English sentence, "action": what to do}}``

Constraint 7: the operator is non-technical. A message says what happened in
ordinary words; the action says what to do about it. Neither mentions Python,
HTTP, SQL, or a stack trace.

Phase 9 runs the full plain-English error pass across the app; this module is
the shape those messages will land in.
"""

from __future__ import annotations

from fastapi import HTTPException


class AppError(HTTPException):
    """An error the operator is meant to read and act on."""

    def __init__(self, status_code: int, code: str, message: str, action: str) -> None:
        super().__init__(
            status_code=status_code,
            detail={"error": {"code": code, "message": message, "action": action}},
        )


def not_found(code: str, message: str, action: str) -> AppError:
    return AppError(404, code, message, action)


def bad_request(code: str, message: str, action: str) -> AppError:
    return AppError(400, code, message, action)


def conflict(code: str, message: str, action: str) -> AppError:
    return AppError(409, code, message, action)


def upstream(code: str, message: str, action: str) -> AppError:
    """Something outside the app misbehaved — currently only the AI service."""
    return AppError(502, code, message, action)
