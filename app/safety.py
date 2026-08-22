import re
from dataclasses import dataclass
from app.models import Domain, RiskLevel


@dataclass
class SafetyDecision:
    risk_level: RiskLevel
    escalation_required: bool
    reason: str


CLINIC_EMERGENCY = [
    r"chest pain",
    r"can't breathe|cannot breathe|difficulty breathing|shortness of breath",
    r"severe bleeding|bleeding heavily",
    r"unconscious|passed out",
    r"stroke|face drooping|slurred speech",
    r"suicid|kill myself|self harm|overdose",
]

LEGAL_HIGH_RISK = [
    r"arrested|police custody|detained",
    r"domestic violence|abuse|threatened",
    r"court(?: hearing)?\s+(?:is\s+)?(?:today|tomorrow)|hearing\s+(?:is\s+)?(?:today|tomorrow)",
    r"eviction today|lockout",
    r"imminent deadline|deadline today",
]


def decide(domain: Domain, text: str) -> SafetyDecision:
    value = text.lower()
    patterns = CLINIC_EMERGENCY if domain == Domain.clinic else LEGAL_HIGH_RISK
    if any(re.search(pattern, value) for pattern in patterns):
        return SafetyDecision(
            risk_level=RiskLevel.emergency if domain == Domain.clinic else RiskLevel.high,
            escalation_required=True,
            reason="Potentially urgent situation detected.",
        )

    if domain == Domain.clinic and re.search(r"pain|fever|vomit|rash|cough|dizzy|medicine", value):
        return SafetyDecision(RiskLevel.medium, False, "Clinical symptom content detected.")
    if domain == Domain.legal and re.search(r"contract|notice|agreement|landlord|employment|divorce|claim", value):
        return SafetyDecision(RiskLevel.medium, False, "Legal matter detected.")

    return SafetyDecision(RiskLevel.low, False, "No urgent risk pattern detected.")
