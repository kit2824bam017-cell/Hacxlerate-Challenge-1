from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ABHALinkRequest(BaseModel):
    abha_identifier: str  # Visibly fictional, e.g. MOCK-ABHA-0001

class ABHAVerifyRequest(BaseModel):
    transaction_id: str
    otp: str = "123456"

class ABHAStatusResponse(BaseModel):
    patient_id: UUID
    provider_mode: str  # 'mock' or 'abdm'
    environment: str    # 'sandbox'
    is_linked: bool
    external_reference: Optional[str] = None
    verification_method: Optional[str] = None
    verified_at: Optional[datetime] = None
    simulated_disclaimer: str = "NOTICE: This connection is explicitly a simulated mock integration for the Altrix challenge prototype."
