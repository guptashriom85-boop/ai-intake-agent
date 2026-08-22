from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.intake import handle_intake
from app.models import IntakeRequest, IntakeResult

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", description="AI-powered clinic/legal intake and routing agent")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

if settings.allow_cors:
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.post("/api/intake", response_model=IntakeResult)
def intake(request: IntakeRequest) -> IntakeResult:
    return handle_intake(request.domain, request.message, request.session_id)


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse("app/static/index.html")
