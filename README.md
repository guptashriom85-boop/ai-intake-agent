# AI Intake Agent

A voice-first virtual intake assistant for clinic and legal workflows. It captures a user's request, detects urgency, creates a structured handoff summary, stores cases in the backend, and helps request appointments.

> Safety: this is an intake and routing product, not a medical diagnostic system or legal advice service. Do not use it as a substitute for emergency services or qualified professionals.

## Live Demo

The repository includes a static portfolio demo in `index.html`. It works without a backend and is ready for GitHub Pages.

Expected Pages URL after enabling Pages:

```text
https://guptashriom85-boop.github.io/ai-intake-agent/
```

## Highlights

- Real-time virtual assistant chat UI
- Browser microphone input with Web Speech API support
- Optional spoken assistant replies with browser speech synthesis
- Clinic and legal modes
- Deterministic critical, high, and routine triage
- Automatic human-handoff flag for urgent cases
- SQLite persistence, PostgreSQL-ready through `DATABASE_URL`
- Appointment request workflow
- JWT-protected admin dashboard
- Optional OpenAI enrichment
- Dockerfile and GitHub Actions CI
- Swagger/OpenAPI docs at `/docs`

## Run the Full Backend App

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Admin dashboard:

```text
http://127.0.0.1:8000/admin
```

Default admin credentials come from `.env`:

```text
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me
```

Change them before deployment.

## Optional AI Mode

The core product works without an API key. To enable AI-enriched assistant responses, install the OpenAI SDK and set your key:

```bash
pip install "openai>=1.99,<2"
```

Then set:

```text
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5-mini
```

If the AI call fails or no key is configured, the app safely falls back to deterministic intake messaging.

## API Endpoints

- `POST /api/intake` - create and triage an intake
- `POST /api/appointments` - request an appointment
- `POST /api/intake/{id}/handoff` - force human escalation, admin only
- `GET /api/admin/intakes` - list intakes, admin only
- `GET /api/admin/appointments` - list appointment requests, admin only
- `GET /api/admin/stats` - dashboard stats, admin only
- `POST /auth/login` - obtain JWT
- `GET /health` - health check
- `GET /docs` - interactive Swagger UI

## Docker

```bash
docker build -t ai-intake-agent .
docker run -p 8000:8000 --env-file .env ai-intake-agent
```

## GitHub Pages Setup

1. Open repository **Settings**.
2. Go to **Pages**.
3. Select source **Deploy from a branch**.
4. Select branch `main` and folder `/root`.
5. Save.

The static demo will publish from `index.html`.

## Production Checklist

Before handling real patient or client information, add PostgreSQL, HTTPS, a proper identity provider, encrypted secret storage, rate limiting, audit logs, consent and privacy controls, region-specific emergency escalation, backups, monitoring, and a real case-management dashboard. Review applicable healthcare, legal, privacy, and professional regulations for your deployment region.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT authentication
- HTML, CSS, JavaScript
- Browser Web Speech API
- Docker
- GitHub Actions
