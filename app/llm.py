import json
from typing import Any
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from app.config import get_settings
from app.models import Domain, RiskLevel
from app.prompts import system_prompt


class IntakeLLM:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.client = OpenAI(api_key=settings.openai_api_key) if (settings.openai_api_key and OpenAI) else None

    def generate(self, *, domain: Domain, message: str, risk_level: RiskLevel, fields: dict[str, str | None], missing: list[str]) -> dict[str, Any]:
        if not self.client:
            return self._fallback(domain, message, risk_level, fields, missing)

        schema = {
            "type": "object",
            "properties": {
                "reply": {"type": "string"},
                "summary": {"type": "string"},
                "collected_fields": {"type": "object", "additionalProperties": {"type": ["string", "null"]}},
                "missing_fields": {"type": "array", "items": {"type": "string"}},
                "next_questions": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["reply", "summary", "collected_fields", "missing_fields", "next_questions"],
            "additionalProperties": False,
        }
        prompt = f"""
Current domain: {domain.value}
Detected risk: {risk_level.value}
Known fields: {json.dumps(fields)}
Likely missing fields: {json.dumps(missing)}
User message: {message}

Return a compact intake response. If risk is emergency/high, prioritize escalation over routine questions.
""".strip()
        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt(domain),
            input=prompt,
            text={"format": {"type": "json_schema", "name": "intake_result", "schema": schema, "strict": True}},
        )
        return json.loads(response.output_text)

    @staticmethod
    def _fallback(domain: Domain, message: str, risk_level: RiskLevel, fields: dict[str, str | None], missing: list[str]) -> dict[str, Any]:
        if domain == Domain.clinic:
            reply = "Thanks. I can collect your information for the clinic. Please share your main concern, when it started, how severe it is, and your preferred appointment time."
            summary = f"Patient reported: {message[:400]}"
        else:
            reply = "Thanks. I can collect the details for a legal professional. Please share your location/jurisdiction, key dates or deadlines, and the outcome you want."
            summary = f"Prospective client reported: {message[:400]}"
        return {"reply": reply, "summary": summary, "collected_fields": fields, "missing_fields": missing, "next_questions": missing[:3]}
