"""
app.models.transaction
~~~~~~~~~~~~~~~~~~~~~~

Pydantic schemas for transaction data flowing through the RustGuard API.

* **TransactionCreate** — inbound payload (POST body).
* **TransactionResponse** — outbound representation (includes scoring).
* **ScoringResult** — structured output from the scoring engine.
* **BatchScoreRequest / BatchScoreResponse** — batch endpoint models.
* **FeedbackRequest** — analyst feedback payload.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class TransactionType(str, Enum):
    """Allowed transaction types in a microfinance context."""
    DISBURSEMENT = "disbursement"
    REPAYMENT = "repayment"
    TRANSFER = "transfer"
    MOBILE_MONEY = "mobile_money"


class Channel(str, Enum):
    """Transaction origination channel."""
    BRANCH = "branch"
    MOBILE_APP = "mobile_app"
    USSD = "ussd"
    AGENT = "agent"


class AlertTier(str, Enum):
    """Risk tiers derived from fraud_score thresholds."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NORMAL = "NORMAL"


class RecommendedAction(str, Enum):
    """Actions the scoring engine can recommend."""
    BLOCK = "BLOCK"
    REVIEW = "REVIEW"
    ALLOW = "ALLOW"


# ---------------------------------------------------------------------------
# Inbound schemas
# ---------------------------------------------------------------------------
class TransactionCreate(BaseModel):
    """Schema for creating / scoring a single transaction."""

    transaction_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique ID; auto-generated UUID if omitted.",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Transaction timestamp (UTC).",
    )
    amount: float = Field(..., gt=0, description="Transaction amount (must be > 0).")
    currency: str = Field(default="ZAR", max_length=3, description="ISO 4217 currency code.")
    transaction_type: TransactionType
    borrower_id: str = Field(..., min_length=1, description="Unique borrower identifier.")
    borrower_phone: str | None = Field(default=None, description="Borrower phone number.")
    national_id_hash: str | None = Field(default=None, description="SHA-256 hash of national ID.")
    channel: Channel | None = Field(default=None, description="Origination channel.")
    agent_id: str | None = Field(default=None, description="ID of the agent processing the txn.")
    merchant_category: str | None = Field(default=None, description="Merchant category code.")
    description: str | None = Field(default=None, description="Free-text description.")
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    registered_location: str | None = Field(default=None, description="Borrower's registered location.")
    loan_id: str | None = Field(default=None, description="Associated loan identifier.")
    loan_amount: float | None = Field(default=None, gt=0, description="Total loan amount.")
    is_fraud: bool | None = Field(default=None, description="Ground-truth label (analyst-provided).")

    @field_validator("currency")
    @classmethod
    def _uppercase_currency(cls, v: str) -> str:
        return v.upper()


class FeedbackRequest(BaseModel):
    """Analyst feedback on a scored transaction."""
    is_fraud: bool
    notes: str | None = None


# ---------------------------------------------------------------------------
# Scoring result
# ---------------------------------------------------------------------------
class ScoringResult(BaseModel):
    """Output from the scoring engine for a single transaction."""

    fraud_score: float = Field(..., ge=0.0, le=1.0, description="Probability of fraud (0-1).")
    alert_tier: AlertTier = AlertTier.NORMAL
    is_flagged: bool = False
    detectors: dict[str, Any] = Field(default_factory=dict, description="Per-detector sub-scores.")
    risk_factors: list[str] = Field(default_factory=list, description="Human-readable risk reasons.")
    recommended_action: RecommendedAction = RecommendedAction.ALLOW


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class TransactionResponse(BaseModel):
    """Full transaction record returned by the API (data + scoring)."""

    transaction_id: str
    tenant_id: str
    timestamp: datetime
    amount: float
    currency: str
    transaction_type: TransactionType
    borrower_id: str
    borrower_phone: str | None = None
    national_id_hash: str | None = None
    channel: Channel | None = None
    agent_id: str | None = None
    merchant_category: str | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    registered_location: str | None = None
    loan_id: str | None = None
    loan_amount: float | None = None
    is_fraud: bool | None = None

    # Scoring fields
    fraud_score: float | None = None
    alert_tier: AlertTier | None = None
    is_flagged: bool | None = None
    risk_factors: list[str] = Field(default_factory=list)
    recommended_action: RecommendedAction | None = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Batch schemas
# ---------------------------------------------------------------------------
class BatchScoreRequest(BaseModel):
    """Batch of transactions to score (max 1 000)."""
    transactions: list[TransactionCreate] = Field(
        ..., min_length=1, max_length=1000,
    )


class BatchScoreResponse(BaseModel):
    """Response for a batch scoring request."""
    processed: int
    results: list[TransactionResponse]


# ---------------------------------------------------------------------------
# Paginated listing
# ---------------------------------------------------------------------------
class PaginatedTransactions(BaseModel):
    """Paginated response wrapper."""
    total: int
    page: int
    page_size: int
    items: list[TransactionResponse]
