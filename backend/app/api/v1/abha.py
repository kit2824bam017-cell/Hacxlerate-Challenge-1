from fastapi import APIRouter, HTTPException
from uuid import UUID
from datetime import datetime

from app.repositories.store import store
from app.schemas.abha import ABHALinkRequest, ABHAVerifyRequest, ABHAStatusResponse
from app.providers.abha import get_abha_provider
from app.core.config import settings

router = APIRouter(prefix="/abha", tags=["ABDM / ABHA Integration"])

@router.get("/status", response_model=ABHAStatusResponse)
async def get_abha_connection_status():
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    provider = get_abha_provider()
    res = await provider.get_status(patient_id)
    return res

@router.post("/link")
async def initiate_abha_linking(req: ABHALinkRequest):
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    provider = get_abha_provider()
    res = await provider.initiate_link(patient_id, req.abha_identifier)
    return res

@router.post("/verify")
async def verify_abha_linking(req: ABHAVerifyRequest):
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    provider = get_abha_provider()
    res = await provider.verify_otp(patient_id, req.transaction_id, req.otp)
    
    if res.get("success"):
        # Store mock link record
        store.abha_links[patient_id] = {
            "id": UUID("90000000-0000-0000-0000-000000000001"),
            "patient_id": patient_id,
            "provider": "mock",
            "environment": "sandbox",
            "external_reference": "MOCK-ABHA-0001",
            "status": "linked",
            "verification_method": "simulated_otp",
            "verified_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    return res

@router.post("/revoke")
async def revoke_abha_link():
    patient_id = UUID(settings.DEMO_PATIENT_ID)
    provider = get_abha_provider()
    res = await provider.revoke_link(patient_id)
    return res
