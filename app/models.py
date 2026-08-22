from enum import Enum
from pydantic import BaseModel, Field


class Domain(str, Enum):
    clinic = "clinic"
    legal = "legal"


class IntakeRequest(BaseModel):
    domain: Domain = Domain.clinic
    message: str = Field(min_length=1, max_length=6000)
    session_id: str | None = None


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    emergency = "emergency"


class IntakeResult(BaseModel):
    session_id: str
    domain: Domain
    reply: str
    summary: str
    risk_level: RiskLevel
    escalation_required: bool
    collected_fields: dict[str, str | None]
    missing_fields: list[str]
    next_questions: list[str]
    disclaimer: str
    ai_used: bool
