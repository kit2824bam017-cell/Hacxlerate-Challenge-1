from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class MedicationResponse(BaseModel):
    id: UUID
    patient_id: UUID
    document_id: Optional[UUID] = None
    medication_name: str
    generic_name: Optional[str] = None
    strength: Optional[str] = None
    dose_instructions: Optional[str] = None
    route: Optional[str] = "oral"
    frequency: Optional[str] = None
    duration: Optional[str] = None
    prescription_date: Optional[date] = None
    medication_status: str = "prescribed"  # 'prescribed', 'active', 'discontinued', 'completed'
    review_status: str = "confirmed"
    created_at: datetime

    class Config:
        from_attributes = True

class MedicationStatusUpdate(BaseModel):
    medication_status: str  # 'active', 'prescribed', 'discontinued'
