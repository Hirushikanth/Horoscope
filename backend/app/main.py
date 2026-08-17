"""
main.py — FastAPI application factory.

``create_app()`` is the single entry point for both the ASGI server
(``uvicorn app.main:app``) and the test suite. No module-level global
state is created during import; the ephemeris loads lazily on first use.
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.config import Settings, get_settings
from app.exceptions import register_exception_handlers
from app.logging import RequestIDMiddleware, setup_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure the FastAPI application."""
    cfg = settings or get_settings()
    setup_logging(cfg.log_level)

    app = FastAPI(
        title=cfg.app_name,
        description=(
            "Precision Vedic astrology API — NASA JPL DE440 ephemeris via Skyfield, "
            "Thirukanitham (Drik Ganita) tradition, Lahiri ayanamsa, "
            "IEEE 754 float64 precision."
        ),
        version=cfg.version,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    register_exception_handlers(app)
    app.include_router(api_router, prefix=cfg.api_prefix)

    return app


def run() -> None:
    """Entry point for ``jyotisha-api`` console script (development use)."""
    cfg = get_settings()
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=not cfg.is_production,
    )


app = create_app()
