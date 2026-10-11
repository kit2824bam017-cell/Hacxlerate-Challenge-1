from fastapi import APIRouter
from uuid import UUID
from app.repositories.store import store
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/demo-login")
async def demo_login():
    """
    Simulated demo login providing access to synthetic patient profile.
    """
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    patient = store.patients.get(patient_id)
    return {
        "access_token": "demo-token-ananya-sharma",
        "token_type": "bearer",
        "user_id": str(patient["user_id"]),
        "patient_id": str(patient["id"]),
        "full_name": patient["full_name"],
        "is_demo": True
    }
