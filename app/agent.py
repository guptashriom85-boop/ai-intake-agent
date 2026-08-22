from dataclasses import dataclass
from .config import settings

EMERGENCY = {
    "clinic": ["chest pain", "can't breathe", "cannot breathe", "severe bleeding", "unconscious", "stroke", "suicide", "overdose"],
    "legal": ["arrested right now", "police station now", "court today", "court tomorrow", "deported today", "custody hearing today", "immediate deportation"],
}
HIGH = {
    "clinic": ["high fever", "difficulty breathing", "severe pain", "fainted", "blood in stool"],
    "legal": ["deadline", "eviction notice", "termination notice", "summons", "lawsuit", "police notice"],
}

@dataclass
class Assessment:
    summary: str
    risk: str
    urgency: str
    category: str
    response: str

def _hits(text: str, terms: list[str]) -> list[str]:
    t = text.lower()
    return [term for term in terms if term in t]

def assess(mode: str, message: str) -> Assessment:
    msg = " ".join(message.strip().split())
    emergency_hits = _hits(msg, EMERGENCY[mode])
    high_hits = _hits(msg, HIGH[mode])
    risk = "critical" if emergency_hits else ("high" if high_hits else "low")
    urgency = "emergency" if emergency_hits else ("same_day" if high_hits else "routine")
    category = ("urgent " if risk != "low" else "general ") + ("medical" if mode == "clinic" else "legal")
    if mode == "clinic":
        response = ("This system cannot diagnose or treat medical conditions. Emergency symptoms should be handled by local emergency services or an appropriate clinician." if urgency == "emergency" else "Your intake has been captured. A clinician should review the details; this tool does not provide a diagnosis.")
    else:
        response = ("This system does not provide legal representation. An urgent matter should be escalated to a qualified lawyer immediately." if urgency == "emergency" else "Your intake has been captured. A qualified legal professional should review the details before advice is given.")
    return Assessment(msg[:500], risk, urgency, category, response)

def maybe_ai_response(mode: str, message: str) -> str | None:
    if not settings.openai_api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        result = client.responses.create(model=settings.openai_model, input=f"You are an intake assistant for {mode}. Do not diagnose, give legal advice, or pretend to be a professional. Ask only for missing operational intake details. User: {message}")
        return result.output_text.strip() or None
    except Exception:
        return None
