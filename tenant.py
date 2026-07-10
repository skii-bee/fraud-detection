"""
app.models.tenant
~~~~~~~~~~~~~~~~~

Pydantic schemas for tenant identity and API-key metadata.

Each API key maps to exactly one tenant.  Tenant isolation is enforced
at the database layer (one SQLite file per tenant).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Tenant(BaseModel):
    """Represents a tenant in the system."""

    tenant_id: str = Field(..., description="Unique tenant identifier.")
    name: str = Field(default="", description="Human-readable tenant name.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class ApiKeyInfo(BaseModel):
    """Resolved API key → tenant mapping returned by the auth layer."""

    key_prefix: str = Field(
        ..., description="First 8 chars of the key (for logging, never the full key)."
    )
    tenant_id: str
    description: str = ""
