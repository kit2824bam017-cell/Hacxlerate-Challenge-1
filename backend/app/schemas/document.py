from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class DocumentBase(BaseModel):
    document_type: Optional[str] = "other"  # 'prescription', 'lab_report', 'discharge_summary', 'other'
    document_date: Optional[date] = None

class DocumentResponse(DocumentBase):
    id: UUID
    patient_id: UUID
    storage_path: str
    original_filename: str
    mime_type: str
    file_size_bytes: Optional[int] = None
    processing_status: str  # 'uploaded', 'queued', 'processing', 'awaiting_review', 'completed', 'failed'
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentStatusResponse(BaseModel):
    id: UUID
    processing_status: str
    error_message: Optional[str] = None
    updated_at: datetime
