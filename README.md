# AI Clinic / Legal Intake Agent

An AI-powered intake and routing service for clinics and legal practices.

It turns an unstructured user message into:

- urgency / risk level
- escalation decision
- concise summary
- structured intake fields
- missing information
- next questions
- a safe user-facing response

The project is designed as a portfolio-quality reference implementation, not as a production medical or legal decision system.

## Architecture

```text
Browser / CRM / WhatsApp / Website
              |
              v
        FastAPI /api/intake
              |
       +------+------+
       |             |
       v             v
  Safety rules    Intake field detection
       |             |
       +------+------+
              v
        OpenAI Responses API
          (optional)
              |
              v
     Structured IntakeResult
```

## Features

### Clinic mode
Collects common intake details such as symptoms, duration, severity, medications/allergies and appointment preference.

### Legal mode
Collects legal issue, jurisdiction, deadlines, documents and desired outcome.

### Safety layer
Urgent patterns are detected before normal intake. Clinic emergencies are routed toward urgent in-person/emergency care; legal high-risk situations are routed toward qualified local legal or emergency support.

### No API key required for demo
Without `OPENAI_API_KEY`, the project uses a deterministic fallback so the repository still works locally and in tests.

## Run locally

```bash
git clone https://github.com/guptashriom85-boop/ai-intake-agent.git
cd ai-intake-agent
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env  # macOS/Linux
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` for the demo UI.

API docs: `http://127.0.0.1:8000/docs`

## Add AI

Put your API key in `.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.6
```

The app will automatically switch from the local fallback to the OpenAI Responses API.

## Example request

```bash
curl -X POST http://127.0.0.1:8000/api/intake \
  -H "Content-Type: application/json" \
  -d '{"domain":"clinic","message":"I have fever for two days and need an appointment tomorrow."}'
```

## Example response shape

```json
{
  "session_id": "...",
  "domain": "clinic",
  "reply": "...",
  "summary": "...",
  "risk_level": "medium",
  "escalation_required": false,
  "collected_fields": {},
  "missing_fields": [],
  "next_questions": [],
  "disclaimer": "...",
  "ai_used": true
}
```

## Tests

```bash
pytest -q
```

## Docker

```bash
docker build -t ai-intake-agent .
docker run --rm -p 8000:8000 --env-file .env ai-intake-agent
```

## Production hardening roadmap

1. Add authentication and tenant-level API keys.
2. Replace in-memory processing with Postgres + encrypted secrets.
3. Add consent capture and audit logging.
4. Add human handoff integrations (email, CRM, Slack, WhatsApp, scheduling).
5. Add stricter jurisdiction-specific legal rules and clinician-approved triage rules.
6. Add rate limiting, PII redaction, retention policies and observability.
7. Add signed webhooks and idempotency keys.

## Safety / compliance note

This repository is an intake and routing demo. It must not be used as an autonomous medical diagnosis system or as a substitute for legal counsel. Before production use, the deployment should undergo professional review, privacy/security review, and jurisdiction-specific compliance review.

## License

MIT
