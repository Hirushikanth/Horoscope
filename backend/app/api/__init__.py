"""
api — HTTP layer for the Jyotisha API.

Thin translation layer: request validation (Pydantic schemas), service
invocation, and response serialization. No computation lives here.
"""

from app.api.router import router

__all__ = ["router"]
