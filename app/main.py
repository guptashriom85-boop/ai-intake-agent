from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from .auth import create_token, require_admin
from .config import settings
from .db import SessionLocal, init_db
from .models import Intake, Appointment
from .schemas import IntakeCreate, IntakeOut, AppointmentCreate, AppointmentOut, LoginRequest
from .agent import assess, maybe_ai_response

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(); yield

app = FastAPI(title=settings.app_name, version="2.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request): return templates.TemplateResponse("index.html", {"request": request})
@app.get("/health")
def health(): return {"status":"ok","version":"2.0.0"}

@app.post("/auth/login")
def login(data: LoginRequest):
    if data.email != settings.admin_email or data.password != settings.admin_password: raise HTTPException(401, "Invalid credentials")
    return {"access_token":create_token(data.email),"token_type":"bearer"}

@app.post("/api/intake", response_model=IntakeOut)
def create_intake(data: IntakeCreate):
    evaluation=assess(data.mode,data.message); ai=maybe_ai_response(data.mode,data.message)
    with SessionLocal() as db:
        row=Intake(**data.model_dump(),summary=evaluation.summary,risk=evaluation.risk,urgency=evaluation.urgency,category=evaluation.category,status="escalate" if evaluation.risk=="critical" else "new",handoff_requested=1 if evaluation.risk in {"critical","high"} else 0)
        db.add(row); db.commit(); db.refresh(row)
        row.summary=(ai or evaluation.response)+" | Intake: "+evaluation.summary; db.commit(); db.refresh(row); return row

@app.post("/api/appointments", response_model=AppointmentOut)
def request_appointment(data: AppointmentCreate):
    with SessionLocal() as db:
        row=Appointment(**data.model_dump()); db.add(row); db.commit(); db.refresh(row); return row

@app.post("/api/intake/{intake_id}/handoff", response_model=IntakeOut)
def handoff(intake_id:int, _:None=Depends(require_admin)):
    with SessionLocal() as db:
        row=db.get(Intake,intake_id)
        if not row: raise HTTPException(404,"Intake not found")
        row.handoff_requested=1; row.status="escalate"; db.commit(); db.refresh(row); return row

@app.get("/api/admin/intakes", response_model=list[IntakeOut])
def admin_intakes(_:None=Depends(require_admin)):
    with SessionLocal() as db: return db.scalars(select(Intake).order_by(Intake.created_at.desc())).all()

@app.get("/api/admin/appointments", response_model=list[AppointmentOut])
def admin_appointments(_:None=Depends(require_admin)):
    with SessionLocal() as db: return db.scalars(select(Appointment).order_by(Appointment.created_at.desc())).all()

@app.get("/api/admin/stats")
def admin_stats(_:None=Depends(require_admin)):
    with SessionLocal() as db:
        return {"intakes":db.scalar(select(func.count(Intake.id))) or 0,"urgent_intakes":db.scalar(select(func.count(Intake.id)).where(Intake.risk.in_(["high","critical"]))) or 0,"handoffs":db.scalar(select(func.count(Intake.id)).where(Intake.handoff_requested==1)) or 0,"appointments":db.scalar(select(func.count(Appointment.id))) or 0}
