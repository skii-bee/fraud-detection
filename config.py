"""
app.config
~~~~~~~~~~

Centralised configuration for the RustGuard service.

Loads values from ``config.yaml`` at the project root, with optional
overrides via environment variables prefixed with ``RUSTGUARD_``.
Nested keys use ``__`` as separator
(e.g. ``RUSTGUARD_API__PORT=9000``).

Usage::

    from app.config import settings
    print(settings.app.name)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"


# ---------------------------------------------------------------------------
# Sub-models (plain BaseModel — not settings themselves)
# ---------------------------------------------------------------------------
class AppConfig(BaseModel):
    """Application-level metadata."""
    name: str = "RustGuard"
    version: str = "0.1.0"
    description: str = "B2B SaaS microfinance fraud detection service"
    debug: bool = False


class ApiConfig(BaseModel):
    """HTTP / FastAPI settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    rate_limit_per_minute: int = 120
    max_batch_size: int = 1000


class DbConfig(BaseModel):
    """Database settings — one SQLite file per tenant."""
    data_dir: str = "data"
    echo_sql: bool = False

    @property
    def data_path(self) -> Path:
        """Absolute path to the data directory."""
        return PROJECT_ROOT / self.data_dir


class ApiKeyEntry(BaseModel):
    """A single API key entry."""
    key: str
    tenant_id: str
    description: str = ""


class AuthConfig(BaseModel):
    """Authentication / authorisation."""
    api_keys: list[ApiKeyEntry] = Field(default_factory=list)


class ScoringThresholds(BaseModel):
    """Map raw fraud scores (0-1) to alert tiers."""
    critical: float = 0.85
    high: float = 0.65
    medium: float = 0.40


class ScoringConfig(BaseModel):
    """Scoring engine configuration."""
    thresholds: ScoringThresholds = Field(default_factory=ScoringThresholds)
    default_currency: str = "ZAR"


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


# ---------------------------------------------------------------------------
# Root settings — merges YAML + env vars
# ---------------------------------------------------------------------------
def _load_yaml() -> dict[str, Any]:
    """Read config.yaml if it exists, else return empty dict."""
    if CONFIG_FILE.is_file():
        with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    return {}


class Settings(BaseSettings):
    """
    Root settings object for RustGuard.

    Resolution order (last wins):
        1. Defaults defined here
        2. ``config.yaml``
        3. Environment variables (prefix ``RUSTGUARD_``)
    """

    model_config = SettingsConfigDict(
        env_prefix="RUSTGUARD_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    app: AppConfig = Field(default_factory=AppConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    db: DbConfig = Field(default_factory=DbConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def from_yaml(cls) -> "Settings":
        """Construct settings by layering YAML then env vars."""
        yaml_data = _load_yaml()
        return cls(**yaml_data)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
settings: Settings = Settings.from_yaml()


def configure_logging() -> None:
    """Apply the logging configuration from settings."""
    logging.basicConfig(
        level=getattr(logging, settings.logging.level.upper(), logging.INFO),
        format=settings.logging.format,
    )
