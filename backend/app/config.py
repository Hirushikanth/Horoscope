"""
config.py — application settings.

Loaded once via ``get_settings()`` (memoised). All values overridable
through environment variables with the ``JYOTISHA_`` prefix or a local
``.env`` file.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Runtime configuration for the Jyotisha API."""

    model_config = SettingsConfigDict(
        env_prefix="JYOTISHA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ═══════════════════════════════════════════════════════════════════════ #
    # Application
    # ═══════════════════════════════════════════════════════════════════════ #
    app_name: str = "Jyotisha API"
    version: str = "2.0.0"
    environment: Literal["development", "production"] = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v2"

    # ═══════════════════════════════════════════════════════════════════════ #
    # CORS
    # ═══════════════════════════════════════════════════════════════════════ #
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # ═══════════════════════════════════════════════════════════════════════ #
    # Ephemeris (NASA JPL DE440)
    # ═══════════════════════════════════════════════════════════════════════ #
    data_dir: Path = _BACKEND_ROOT / "data"
    ephemeris_filename: str = "de440.bsp"
    auto_download_ephemeris: bool = False

    # ═══════════════════════════════════════════════════════════════════════ #
    # Computation defaults
    # ═══════════════════════════════════════════════════════════════════════ #
    node_convention: Literal["mean", "true"] = "mean"
    cache_ttl_seconds: int = 300
    cache_max_entries: int = 1024

    # ═══════════════════════════════════════════════════════════════════════ #
    # Derived
    # ═══════════════════════════════════════════════════════════════════════ #
    @property
    def ephemeris_path(self) -> Path:
        """Absolute path to the JPL DE440 ephemeris file."""
        return self.data_dir / self.ephemeris_filename

    @property
    def is_production(self) -> bool:
        """True when running in a production environment."""
        return self.environment == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the memoised application settings singleton."""
    return Settings()
