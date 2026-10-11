import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    
    # Supabase Settings
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "medical-documents-private"
    
    # Sarvam AI OCR & Indian Language Provider
    SARVAM_PROVIDER_MODE: str = "mock"  # 'mock' or 'live'
    SARVAM_API_KEY: str = ""
    SARVAM_BASE_URL: str = "https://api.sarvam.ai"
    
    # Summary Provider
    SUMMARY_MODEL_PROVIDER: str = "mock"  # 'mock' or 'sarvam' or 'openai'
    SUMMARY_MODEL_API_KEY: str = ""
    
    # ABDM / ABHA Provider
    ABHA_PROVIDER: str = "mock"  # 'mock' or 'abdm'
    ABDM_ENVIRONMENT: str = "sandbox"
    ABDM_CLIENT_ID: str = ""
    ABDM_CLIENT_SECRET: str = ""
    
    # Demo Synthetic Patient Preset
    DEMO_PATIENT_ENABLED: bool = True
    DEMO_PATIENT_ID: str = "00000000-0000-0000-0000-000000000001"
    DEMO_USER_ID: str = "00000000-0000-0000-0000-000000000001"
    
    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
