from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ObservationResponse(BaseModel):
    id: UUID
    patient_id: UUID
    document_id: Optional[UUID] = None
    health_record_id: Optional[UUID] = None
    code: Optional[str] = None
    display_name: str
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    unit: Optional[str] = None
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    source_abnormal_flag: Optional[str] = None
    effective_at: Optional[datetime] = None
    validation_status: str = "validated"
    created_at: datetime

    class Config:
        from_attributes = True

class TrendPoint(BaseModel):
    date: str
    value: float
    unit: str
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    source_document_id: Optional[UUID] = None

class TestTrendResponse(BaseModel):
    test_name: str
    unit: str
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    history: List[TrendPoint]
