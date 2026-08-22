import uuid
from app.llm import IntakeLLM
from app.models import Domain, IntakeResult
from app.safety import decide


FIELD_MAP = {
    Domain.clinic: ["name", "age", "main concern", "onset/duration", "severity", "medications/allergies", "preferred appointment time"],
    Domain.legal: ["name", "location/jurisdiction", "legal issue", "key dates/deadlines", "documents available", "desired outcome"],
}


def detect_fields(domain: Domain, text: str) -> dict[str, str | None]:
    lower = text.lower()
    fields = {key: None for key in FIELD_MAP[domain]}
    if domain == Domain.clinic:
        if "name" in lower: fields["name"] = "provided"
        if any(token in lower for token in ["year old", "years old", "age"]): fields["age"] = "provided"
        if any(token in lower for token in ["pain", "fever", "cough", "rash", "headache", "symptom"]): fields["main concern"] = "provided"
        if any(token in lower for token in ["today", "yesterday", "days", "weeks", "months"]): fields["onset/duration"] = "provided"
        if any(token in lower for token in ["mild", "moderate", "severe", "10/10", "8/10", "9/10"]): fields["severity"] = "provided"
        if any(token in lower for token in ["medicine", "medication", "allergy", "allergic"]): fields["medications/allergies"] = "provided"
    else:
        if "name" in lower: fields["name"] = "provided"
        if any(token in lower for token in ["india", "delhi", "noida", "up", "uttar pradesh", "jurisdiction"]): fields["location/jurisdiction"] = "provided"
        if any(token in lower for token in ["contract", "tenant", "landlord", "employment", "divorce", "property", "notice", "claim"]): fields["legal issue"] = "provided"
        if any(token in lower for token in ["today", "tomorrow", "deadline", "hearing", "date", "last week"]): fields["key dates/deadlines"] = "provided"
        if any(token in lower for token in ["document", "agreement", "notice", "pdf", "file"]): fields["documents available"] = "provided"
        if any(token in lower for token in ["want", "seeking", "goal", "outcome"]): fields["desired outcome"] = "provided"
    return fields


def handle_intake(domain: Domain, message: str, session_id: str | None = None) -> IntakeResult:
    decision = decide(domain, message)
    fields = detect_fields(domain, message)
    missing = [key for key, value in fields.items() if value is None]
    llm = IntakeLLM()
    generated = llm.generate(domain=domain, message=message, risk_level=decision.risk_level, fields=fields, missing=missing)

    if decision.escalation_required:
        if domain == Domain.clinic:
            reply = "This may need urgent medical attention. Please contact your local emergency service or seek urgent in-person care now. Do not rely on this intake assistant for diagnosis or treatment."
            disclaimer = "Emergency triage only; not medical advice."
        else:
            reply = "This may be time-sensitive or safety-critical. Please contact a qualified local lawyer or the appropriate emergency authority promptly. This assistant cannot provide legal advice."
            disclaimer = "Urgent routing only; not legal advice."
    else:
        reply = generated["reply"]
        disclaimer = "This assistant only collects intake information and is not a substitute for professional advice."

    return IntakeResult(
        session_id=session_id or str(uuid.uuid4()),
        domain=domain,
        reply=reply,
        summary=generated["summary"],
        risk_level=decision.risk_level,
        escalation_required=decision.escalation_required,
        collected_fields=generated["collected_fields"],
        missing_fields=generated["missing_fields"],
        next_questions=generated["next_questions"],
        disclaimer=disclaimer,
        ai_used=llm.client is not None,
    )
