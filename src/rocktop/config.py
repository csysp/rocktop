"""Unified configuration for Rocktop.

Uses Pydantic BaseSettings to load from environment, with sane defaults.
Enforces shared invariants at construction time.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, BaseSettings, Field, ValidationError, model_validator

from .invariants import AUDIO_FLOAT_DTYPE, SAMPLE_RATE_HZ, enforce_dtype, enforce_sample_rate


class Paths(BaseModel):
    root: Path = Path(".")
    data_dir: Path = Path("data")
    raw_dir: Path = Path("data/raw")
    processed_dir: Path = Path("data/processed")
    cache_dir: Path = Path("cache")
    f0_cache_dir: Path = Path("cache/f0")
    units_cache_dir: Path = Path("cache/units")


class Settings(BaseSettings):
    # Audio invariants
    sample_rate_hz: int = Field(default=SAMPLE_RATE_HZ)
    audio_float_dtype: str = Field(default=AUDIO_FLOAT_DTYPE)

    # Paths
    paths: Paths = Field(default_factory=Paths)

    # Optional service endpoints
    mlflow_tracking_uri: Optional[str] = None
    object_store_endpoint: Optional[str] = None

    # Model Context Protocol server settings (if used)
    mcp_key_required: bool = True

    model_config = {
        "env_prefix": "ROCKTOP_",
        "env_nested_delimiter": "__",
        "extra": "ignore",
    }

    @model_validator(mode="after")
    def _enforce_invariants(self) -> "Settings":
        enforce_sample_rate(self.sample_rate_hz)
        enforce_dtype(self.audio_float_dtype)
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and cache settings to ensure consistency across the process."""
    try:
        return Settings()
    except ValidationError as exc:
        # Re-raise with a shorter message for CLI/server contexts
        raise SystemExit(f"Invalid configuration: {exc}")


def reset_settings_cache() -> None:
    """Clear the cached Settings to allow environment-driven reloads (tests)."""
    try:
        get_settings.cache_clear()  # type: ignore[attr-defined]
    except Exception:
        # Fallback: no-op if cache_clear is unavailable
        pass
