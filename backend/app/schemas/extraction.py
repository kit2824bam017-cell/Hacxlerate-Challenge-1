from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import date, datetime
from uuid import UUID

class ExtractedObservationItem(BaseModel):
    id: Optional[str] = None
    test_name: str
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    unit: Optional[str] = None
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    source_abnormal_flag: Optional[str] = None  # 'H', 'L', 'CRITICAL', 'NORMAL', None
    confidence: str = "high"  # 'high', 'needs_review', 'unreadable_or_missing'
    validation_status: str = "needs_review"  # 'needs_review', 'verified', 'flagged'
    source_text: Optional[str] = None

class ExtractedMedicationItem(BaseModel):
    id: Optional[str] = None
    medication_name: str
    generic_name: Optional[str] = None
    strength: Optional[str] = None
    dose_instructions: Optional[str] = None
    route: Optional[str] = "oral"
    frequency: Optional[str] = None
    duration: Optional[str] = None
    prescription_date: Optional[date] = None
    confidence: str = "high"  # 'high', 'needs_review', 'unreadable_or_missing'
    validation_status: str = "needs_review"
    source_text: Optional[str] = None

class ExtractedDischargeItem(BaseModel):
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None
    diagnoses: List[str] = Field(default_factory=list)
    procedures: List[str] = Field(default_factory=list)
    follow_up_recommendations: Optional[str] = None
    warning_signs: List[str] = Field(default_factory=list)

class CandidateExtractionData(BaseModel):
    document_type: str = "lab_report"  # 'lab_report', 'prescription', 'discharge_summary'
    document_date: Optional[date] = None
    healthcare_provider: Optional[str] = None
    practitioner_name: Optional[str] = None
    observations: List[ExtractedObservationItem] = Field(default_factory=list)
    medications: List[ExtractedMedicationItem] = Field(default_factory=list)
    discharge_summary: Optional[ExtractedDischargeItem] = None
    unreadable_segments: List[str] = Field(default_factory=list)

class ExtractionResultResponse(BaseModel):
    id: UUID
    document_id: UUID
    raw_ocr_text: Optional[str] = None
    structured_candidate_data: CandidateExtractionData
    extraction_provider: str = "sarvam"
    provider_model: Optional[str] = None
    validation_status: str = "needs_review"
    review_status: str = "pending"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExtractionUpdateRequest(BaseModel):
    structured_candidate_data: CandidateExtractionData
    review_status: Optional[str] = "in_review"

class ExtractionConfirmRequest(BaseModel):
    confirm_all: bool = True
    active_medications: List[str] = Field(default_factory=list, description="List of medication names that user currently takes")
