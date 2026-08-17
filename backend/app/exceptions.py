"""
exceptions.py — domain exception hierarchy and HTTP error mapping.

Every domain failure raises a typed ``JyotishaError`` subclass carrying a
stable machine-readable ``code`` and an HTTP status. The global exception
handlers registered in ``app.main`` translate these into consistent
``{"detail": {"code": ..., "message": ..., "context": ...}}`` payloads.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class JyotishaError(Exception):
    """Base class for all domain errors."""

    status_code: int = 500
    code: str = "jyotisha_error"

    def __init__(
        self, message: str | None = None, *, context: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message or self.code)
        self.message = message or self.code
        self.context = context


class InvalidBirthDataError(JyotishaError):
    """Birth input (date, time, timezone, coordinates) is malformed."""

    status_code = 400
    code = "invalid_birth_data"


class DateOutOfRangeError(JyotishaError):
    """Date falls outside the DE440 ephemeris coverage window."""

    status_code = 422
    code = "date_out_of_range"


class EphemerisUnavailableError(JyotishaError):
    """JPL DE440 ephemeris file is missing and cannot be loaded."""

    status_code = 503
    code = "ephemeris_unavailable"


class ConfigurationError(JyotishaError):
    """Application configuration is invalid."""

    status_code = 500
    code = "configuration_error"


class UnsupportedFeatureError(JyotishaError):
    """Requested option is reserved but not yet implemented."""

    status_code = 501
    code = "unsupported_feature"


def _error_payload(exc: JyotishaError) -> dict[str, Any]:
    payload: dict[str, Any] = {"code": exc.code, "message": exc.message}
    if exc.context:
        payload["context"] = exc.context
    return payload


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global handlers translating failures into consistent JSON responses.

    Every failure — Pydantic validation errors included — is returned as
    ``{"detail": {"code": ..., "message": ..., "context": ...}}`` so API
    consumers can switch on ``detail.code`` without inspecting HTTP
    status or exception internals.
    """

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        fields = [
            {
                "loc": [str(part) for part in error["loc"]],
                "type": error["type"],
                "message": error["msg"],
            }
            for error in exc.errors()
        ]
        logger.warning("validation error on %s %s: %s", request.method, request.url.path, fields)
        return JSONResponse(
            status_code=422,
            content={
                "detail": {
                    "code": "validation_error",
                    "message": "Request failed validation.",
                    "context": {"fields": fields},
                }
            },
        )

    @app.exception_handler(JyotishaError)
    async def handle_jyotisha_error(request: Request, exc: JyotishaError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("domain error: %s — %s", exc.code, exc.message, exc_info=False)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": _error_payload(exc)},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "detail": {
                    "code": "internal_error",
                    "message": "An internal error occurred.",
                }
            },
        )
