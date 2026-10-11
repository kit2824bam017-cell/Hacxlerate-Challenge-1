from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class TimelineEvent(BaseModel):
    id: str
    event_type: str  # 'document_upload', 'lab_observation', 'prescription', 'encounter', 'abha_link'
    title: str
    description: str
    event_date: datetime
    category: str  # 'Diagnostic', 'Medication', 'Consultation', 'Integration'
    source_document_id: Optional[UUID] = None
    badge_color: Optional[str] = "teal"
    metadata: Dict[str, Any] = {}

class TimelineResponse(BaseModel):
    patient_id: UUID
    events: List[TimelineEvent]
    total_count: int
