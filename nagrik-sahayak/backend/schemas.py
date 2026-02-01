from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RegisterRequest(BaseModel):
    name: str
    mobile: str
    password: str

class LoginRequest(BaseModel):
    mobile: str
    password: str

class UserResponse(BaseModel):
    id: int
    fullName: str
    phone: str
    language: str
    ai_updates: bool
    created_at: str

class UpdateProfileRequest(BaseModel):
    fullName: str

class UpdatePreferencesRequest(BaseModel):
    language: str
    ai_updates: bool

# --- NEW DASHBOARD & COMPLAINT SCHEMAS ---
# Added to support your dashboard.py logic
class ComplaintOut(BaseModel):
    id: int
    title: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True # Allows Pydantic to read SQLAlchemy models

class DashboardStats(BaseModel):
    total: int
    in_progress: int
    resolved: int
    escalated: int

class DashboardResponse(BaseModel):
    user_name: str
    complaints: List[ComplaintOut]
    stats: DashboardStats

class ComplaintHistoryOut(BaseModel):
    id: int
    title: str
    category: str
    status: str
    reference_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True
