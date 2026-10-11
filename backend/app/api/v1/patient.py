from fastapi import APIRouter, HTTPException
from uuid import UUID
from datetime import datetime
from app.repositories.store import store
from app.schemas.patient import PatientResponse, PatientUpdate
from app.core.config import settings

router = APIRouter(prefix="/patient", tags=["Patient Profile"])

@router.get("/me", response_model=PatientResponse)
async def get_patient_profile():
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    patient = store.patients.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
    return patient

@router.patch("/me", response_model=PatientResponse)
async def update_patient_profile(update_data: PatientUpdate):
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    patient = store.patients.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        if v is not None:
            patient[k] = v
    patient["updated_at"] = datetime.now()
    return patient
