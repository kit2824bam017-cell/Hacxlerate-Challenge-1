from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class PatientBase(BaseModel):
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    preferred_language: str = "en"

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    preferred_language: Optional[str] = None

class PatientResponse(PatientBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
