from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class AbnormalExplanationItem(BaseModel):
    test_name: str
    value: str
    reference: str
    status: str  # e.g., 'Above Reference Range', 'Below Reference Range'
    plain_explanation: str

class DocumentSummaryResponse(BaseModel):
    id: UUID
    document_id: UUID
    language: str = "en"
    overview: str
    key_findings: List[str] = Field(default_factory=list)
    abnormal_explanations: List[AbnormalExplanationItem] = Field(default_factory=list)
    questions_for_doctor: List[str] = Field(default_factory=list)
    limitations: Optional[str] = None
    safety_disclaimer: str
    created_at: datetime

    class Config:
        from_attributes = True

class TranslationRequest(BaseModel):
    target_language: str = "ta"  # 'ta' for Tamil
