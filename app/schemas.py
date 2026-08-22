from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class IntakeCreate(BaseModel):
    mode: str = Field(pattern="^(clinic|legal)$")
    name: str = Field(min_length=2, max_length=120)
    contact: str = Field(min_length=3, max_length=160)
    message: str = Field(min_length=3, max_length=5000)

class IntakeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; mode: str; name: str; contact: str; message: str; summary: str
    risk: str; urgency: str; category: str; status: str; handoff_requested: int; created_at: datetime

class AppointmentCreate(BaseModel):
    intake_id: int | None = None
    mode: str = Field(pattern="^(clinic|legal)$")
    name: str = Field(min_length=2, max_length=120)
    contact: str = Field(min_length=3, max_length=160)
    preferred_slot: str = Field(min_length=2, max_length=120)
    notes: str = Field(default="", max_length=2000)

class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; intake_id: int | None; mode: str; name: str; contact: str
    preferred_slot: str; notes: str; status: str; created_at: datetime

class LoginRequest(BaseModel):
    email: str
    password: str
