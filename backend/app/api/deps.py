"""
deps.py — dependency injection: services and caches.

Provides the singleton service instances used by the API routes. All
computation services (jathakam, panchangam, matching, stars) share one
bounded TTL cache for deterministic results on hot endpoints,
configured from application settings.
"""

from __future__ import annotations

from app.config import get_settings
from app.core.cache import TTLCache
from app.services.jathakam_service import JathakamService
from app.services.matching_service import MatchingService
from app.services.panchangam_service import PanchangamService
from app.services.stars_service import StarsService

_cache: TTLCache | None = None
_jathakam_service: JathakamService | None = None
_panchangam_service: PanchangamService | None = None
_matching_service: MatchingService | None = None
_stars_service: StarsService | None = None


def _ensure_cache() -> TTLCache:
    """Create (once) the process-wide TTL cache shared by the services."""
    global _cache
    if _cache is None:
        cfg = get_settings()
        _cache = TTLCache(
            ttl_seconds=cfg.cache_ttl_seconds,
            max_entries=cfg.cache_max_entries,
        )
    return _cache


def get_jathakam_service() -> JathakamService:
    """Return the process-wide ``JathakamService`` singleton (with cache)."""
    global _jathakam_service
    if _jathakam_service is None:
        _jathakam_service = JathakamService(settings=get_settings(), cache=_ensure_cache())
    return _jathakam_service


def get_panchangam_service() -> PanchangamService:
    """Return the process-wide ``PanchangamService`` singleton (with cache)."""
    global _panchangam_service
    if _panchangam_service is None:
        _panchangam_service = PanchangamService(settings=get_settings(), cache=_ensure_cache())
    return _panchangam_service


def get_matching_service() -> MatchingService:
    """Return the process-wide ``MatchingService`` singleton (with cache)."""
    global _matching_service
    if _matching_service is None:
        _matching_service = MatchingService(settings=get_settings(), cache=_ensure_cache())
    return _matching_service


def get_stars_service() -> StarsService:
    """Return the process-wide ``StarsService`` singleton (with cache)."""
    global _stars_service
    if _stars_service is None:
        _stars_service = StarsService(settings=get_settings(), cache=_ensure_cache())
    return _stars_service
