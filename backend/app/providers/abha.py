from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from app.core.config import settings

class BaseABHAProvider(ABC):
    @abstractmethod
    async def initiate_link(self, patient_id: UUID, abha_identifier: str) -> Dict[str, Any]:
        """Initiate ABHA linking request"""
        pass

    @abstractmethod
    async def verify_otp(self, patient_id: UUID, transaction_id: str, otp: str) -> Dict[str, Any]:
        """Verify linking with OTP"""
        pass

    @abstractmethod
    async def get_status(self, patient_id: UUID) -> Dict[str, Any]:
        """Query current connection status"""
        pass

    @abstractmethod
    async def revoke_link(self, patient_id: UUID) -> Dict[str, Any]:
        """Revoke linked account"""
        pass

class MockABHAProvider(BaseABHAProvider):
    """
    Transparent Mock ABHA Provider for development & testing.
    Uses explicitly fictional identifiers like 'MOCK-ABHA-0001'.
    """
    async def initiate_link(self, patient_id: UUID, abha_identifier: str) -> Dict[str, Any]:
        clean_id = abha_identifier.strip().upper()
        if not clean_id.startswith("MOCK-ABHA-"):
            clean_id = f"MOCK-ABHA-{clean_id}"
            
        txn_id = f"txn_mock_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "status": "otp_sent",
            "transaction_id": txn_id,
            "abha_identifier": clean_id,
            "message": "Simulated OTP (use 123456) dispatched to linked mobile number.",
            "is_mock": True
        }

    async def verify_otp(self, patient_id: UUID, transaction_id: str, otp: str) -> Dict[str, Any]:
        if otp != "123456":
            return {
                "success": False,
                "message": "Invalid simulated OTP. For mock demonstration, enter '123456'."
            }
        
        return {
            "success": True,
            "message": "Successfully linked mock ABHA account.",
            "verified_at": datetime.now().isoformat(),
            "is_mock": True
        }

    async def get_status(self, patient_id: UUID) -> Dict[str, Any]:
        from app.repositories.store import store
        link = store.abha_links.get(patient_id)
        if not link or link.get("status") != "linked":
            return {
                "patient_id": patient_id,
                "provider_mode": "mock",
                "environment": "sandbox",
                "is_linked": False,
                "external_reference": None,
                "verification_method": None,
                "verified_at": None,
                "simulated_disclaimer": "NOTICE: This connection is a simulated mock integration for the Altrix challenge prototype."
            }
        return {
            "patient_id": patient_id,
            "provider_mode": "mock",
            "environment": link.get("environment", "sandbox"),
            "is_linked": True,
            "external_reference": link.get("external_reference"),
            "verification_method": link.get("verification_method", "simulated_otp"),
            "verified_at": link.get("verified_at"),
            "simulated_disclaimer": "NOTICE: This connection is a simulated mock integration for the Altrix challenge prototype."
        }

    async def revoke_link(self, patient_id: UUID) -> Dict[str, Any]:
        from app.repositories.store import store
        if patient_id in store.abha_links:
            store.abha_links[patient_id]["status"] = "revoked"
        return {
            "success": True,
            "message": "Mock ABHA linkage disconnected successfully."
        }

class LiveABDMProvider(BaseABHAProvider):
    """
    Genuine ABDM Gateway Provider.
    Activated when ABHA_PROVIDER='abdm' and ABDM sandbox credentials are supplied.
    """
    def __init__(self, client_id: str, client_secret: str, environment: str = "sandbox"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://dev.abdm.gov.in/gateway/v0.5"

    async def initiate_link(self, patient_id: UUID, abha_identifier: str) -> Dict[str, Any]:
        if not self.client_id or not self.client_secret:
            raise ValueError("ABDM credentials missing. Set ABDM_CLIENT_ID and ABDM_CLIENT_SECRET.")
        raise NotImplementedError("Live ABDM Gateway communication requires official NHA sandbox onboarding.")

    async def verify_otp(self, patient_id: UUID, transaction_id: str, otp: str) -> Dict[str, Any]:
        raise NotImplementedError("Live ABDM Gateway communication requires official NHA sandbox onboarding.")

    async def get_status(self, patient_id: UUID) -> Dict[str, Any]:
        raise NotImplementedError("Live ABDM Gateway communication requires official NHA sandbox onboarding.")

    async def revoke_link(self, patient_id: UUID) -> Dict[str, Any]:
        raise NotImplementedError("Live ABDM Gateway communication requires official NHA sandbox onboarding.")

def get_abha_provider() -> BaseABHAProvider:
    if settings.ABHA_PROVIDER == "abdm" and settings.ABDM_CLIENT_ID:
        return LiveABDMProvider(settings.ABDM_CLIENT_ID, settings.ABDM_CLIENT_SECRET, settings.ABDM_ENVIRONMENT)
    return MockABHAProvider()
