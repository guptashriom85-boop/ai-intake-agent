# AI Intake Agent

**Clinic + Legal Intake Automation MVP** — capture a request, triage urgency, persist the case, request appointments, and hand off high-risk cases to a human professional.

> Safety: this is an intake/routing product, not a medical diagnostic system or legal advice service. Do not use it as a substitute for emergency services or qualified professionals.

## What is included

- Clinic and legal modes
- Deterministic critical/high/routine triage
- Automatic human-handoff flag for urgent cases
- SQLite persistence (PostgreSQL-ready via `DATABASE_URL`)
- Appointment request workflow
- JWT-protected admin endpoints
- Admin statistics + case lists
- Optional OpenAI enrichment (kept optional so the core app works without an API key)
- Browser UI
- Dockerfile
- GitHub Actions CI
- Swagger/OpenAPI at `/docs`

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

Default admin credentials come from `.env` (`ADMIN_EMAIL` / `ADMIN_PASSWORD`). **Change them before deployment.**

## Optional AI mode

Install the SDK and set your key:

```bash
pip install "openai>=1.99,<2"
```

Then set `OPENAI_API_KEY` and `OPENAI_MODEL`. If unavailable or if the call fails, the system safely falls back to deterministic intake messaging.

## API

- `POST /api/intake` — create and triage an intake
- `POST /api/appointments` — request an appointment
- `POST /api/intake/{id}/handoff` — force human escalation (admin)
- `GET /api/admin/intakes` — list intakes (admin)
- `GET /api/admin/appointments` — list appointment requests (admin)
- `GET /api/admin/stats` — dashboard stats (admin)
- `POST /auth/login` — obtain JWT
- `GET /health` — health check
- `GET /docs` — interactive Swagger UI

## Docker

```bash
docker build -t ai-intake-agent .
docker run -p 8000:8000 --env-file .env ai-intake-agent
```

## Production checklist

Before handling real patient/client information: use PostgreSQL, HTTPS, a proper identity provider, encrypted secret storage, rate limiting, audit logs, consent/privacy controls, region-specific emergency escalation, backups, monitoring, and a real case-management dashboard. Review applicable healthcare/legal privacy and professional regulations for your deployment region.
