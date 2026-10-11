from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from collections import defaultdict

from app.repositories.store import store
from app.schemas.observation import ObservationResponse, TestTrendResponse, TrendPoint
from app.schemas.medication import MedicationResponse, MedicationStatusUpdate
from app.core.config import settings

router = APIRouter(tags=["Health Records"])

@router.get("/observations", response_model=List[ObservationResponse])
async def list_observations(test_name: Optional[str] = Query(None)):
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    obs_list = [o for o in store.observations.values() if o["patient_id"] == patient_id]
    if test_name:
        obs_list = [o for o in obs_list if test_name.lower() in o["display_name"].lower()]
    obs_list.sort(key=lambda x: x["effective_at"] or x["created_at"], reverse=True)
    return obs_list

@router.get("/observations/trends", response_model=List[TestTrendResponse])
async def get_observation_trends():
    """
    Returns comparable longitudinal history for tests having multiple data points.
    Strictly groups identical test names and units to prevent invalid comparisons.
    """
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    obs_list = [o for o in store.observations.values() if o["patient_id"] == patient_id and o.get("value_numeric") is not None]
    
    grouped = defaultdict(list)
    for o in obs_list:
        key = (o["display_name"], o.get("unit") or "")
        grouped[key].append(o)
        
    trends: List[TestTrendResponse] = []
    for (tname, unit), items in grouped.items():
        # Sort chronologically (oldest to newest)
        items.sort(key=lambda x: x["effective_at"] or x["created_at"])
        
        history = [
            TrendPoint(
                date=(item["effective_at"] or item["created_at"]).strftime("%Y-%m-%d"),
                value=float(item["value_numeric"]),
                unit=unit,
                reference_low=item.get("reference_low"),
                reference_high=item.get("reference_high"),
                source_document_id=item.get("document_id")
            )
            for item in items
        ]
        
        latest = items[-1]
        trends.append(TestTrendResponse(
            test_name=tname,
            unit=unit,
            reference_low=latest.get("reference_low"),
            reference_high=latest.get("reference_high"),
            history=history
        ))
        
    return trends

@router.get("/medications", response_model=List[MedicationResponse])
async def list_medications(status: Optional[str] = Query(None)):
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    meds = [m for m in store.medications.values() if m["patient_id"] == patient_id]
    if status:
        meds = [m for m in meds if m.get("medication_status") == status]
    meds.sort(key=lambda x: x["prescription_date"] or x["created_at"].date(), reverse=True)
    return meds

@router.patch("/medications/{medication_id}", response_model=MedicationResponse)
async def update_medication_status(medication_id: UUID, req: MedicationStatusUpdate):
    med = store.medications.get(medication_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medication record not found.")
    med["medication_status"] = req.medication_status
    return med
