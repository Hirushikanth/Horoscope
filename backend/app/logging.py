"""
logging.py — structured logging with per-request correlation IDs.

The ``RequestIDMiddleware`` stamps every request with an ID (honouring an
incoming ``X-Request-ID`` header) exposed through a context variable, and
emits an access log line per request. The ID is echoed on the response.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

logger = logging.getLogger("jyotisha")


class _RequestIDFilter(logging.Filter):
    """Inject the current request ID into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def setup_logging(level: str = "INFO") -> None:
    """Configure root logging with a request-ID-aware formatter."""
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(message)s"
        )
    )
    handler.addFilter(_RequestIDFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assign a correlation ID per request and log an access line.

    The access line carries the method, path, status and wall-clock
    duration so that slow endpoints are greppable by request ID. The ID
    is echoed on the response as ``X-Request-ID``.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        token = request_id_var.set(rid)
        started = time.monotonic()
        try:
            response = await call_next(request)
            duration_ms = (time.monotonic() - started) * 1000.0
            response.headers["X-Request-ID"] = rid
            logger.info(
                "%s %s -> %d (%.1f ms)",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )
            return response
        finally:
            request_id_var.reset(token)
