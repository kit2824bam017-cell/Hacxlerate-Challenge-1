from fastapi import APIRouter, Query
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.repositories.store import store
from app.schemas.timeline import TimelineEvent, TimelineResponse
from app.core.config import settings

router = APIRouter(prefix="/timeline", tags=["Health Timeline"])

@router.get("", response_model=TimelineResponse)
async def get_chronological_timeline(category: Optional[str] = Query(None)):
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    events: List[TimelineEvent] = []
    
    # 1. Documents
    for d in store.documents.values():
        if d["patient_id"] == patient_id:
            events.append(TimelineEvent(
                id=f"doc_{d['id']}",
                event_type="document_upload",
                title=f"Uploaded {d['document_type'].replace('_', ' ').title()}",
                description=f"File: {d['original_filename']} ({d['processing_status']})",
                event_date=d["created_at"],
                category="Diagnostic",
                source_document_id=d["id"],
                badge_color="teal",
                metadata={"filename": d["original_filename"], "status": d["processing_status"]}
            ))
            
    # 2. Lab Observations (Grouped by document/date)
    for o in store.observations.values():
        if o["patient_id"] == patient_id:
            flag_str = f" [{o['source_abnormal_flag']}]" if o.get("source_abnormal_flag") else ""
            events.append(TimelineEvent(
                id=f"obs_{o['id']}",
                event_type="lab_observation",
                title=f"Laboratory Test: {o['display_name']}",
                description=f"Result: {o['value_numeric']} {o.get('unit', '')}{flag_str}",
                event_date=o["effective_at"] or o["created_at"],
                category="Diagnostic",
                source_document_id=o.get("document_id"),
                badge_color="red" if o.get("source_abnormal_flag") in ("H", "L", "CRITICAL") else "green",
                metadata={"test_name": o["display_name"], "value": o["value_numeric"]}
            ))
            
    # 3. Medications Prescribed
    for m in store.medications.values():
        if m["patient_id"] == patient_id:
            events.append(TimelineEvent(
                id=f"med_{m['id']}",
                event_type="prescription",
                title=f"Prescription: {m['medication_name']} ({m.get('strength', '')})",
                description=f"Directions: {m.get('dose_instructions', '')} | Status: {m['medication_status'].upper()}",
                event_date=m["created_at"],
                category="Medication",
                source_document_id=m.get("document_id"),
                badge_color="blue",
                metadata={"drug": m["medication_name"], "status": m["medication_status"]}
            ))
            
    # 4. ABHA Integration Events
    link = store.abha_links.get(patient_id)
    if link and link.get("status") == "linked":
        events.append(TimelineEvent(
            id=f"abha_{link['id']}",
            event_type="abha_link",
            title=f"ABHA Digital Account Linked ({link['external_reference']})",
            description="Verified via simulated OTP. Ready for ABDM health exchange.",
            event_date=link["verified_at"] or link["created_at"],
            category="Integration",
            badge_color="purple",
            metadata={"reference": link["external_reference"]}
        ))
        
    # Filter by category if requested
    if category:
        events = [e for e in events if e.category.lower() == category.lower()]
        
    # Sort newest first
    events.sort(key=lambda x: x.event_date, reverse=True)
    
    return TimelineResponse(
        patient_id=patient_id,
        events=events,
        total_count=len(events)
    )
