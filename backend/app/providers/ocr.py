from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

class BaseOCRProvider(ABC):
    @abstractmethod
    async def extract_text_and_data(self, file_bytes: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """Extract raw text and candidate structured fields from file"""
        pass

class SarvamOCRProvider(BaseOCRProvider):
    """
    Adapter for Sarvam AI Document Intelligence API.
    Used when SARVAM_API_KEY is provided and SARVAM_PROVIDER_MODE == 'live'.
    """
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    async def extract_text_and_data(self, file_bytes: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY is not configured for live provider mode.")
        
        headers = {"api-subscription-key": self.api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"file": (filename, file_bytes, mime_type)}
            # Call Sarvam Document Intelligence endpoint
            response = await client.post(
                f"{self.base_url}/document-intelligence/v1/extract",
                headers=headers,
                files=files
            )
            response.raise_for_status()
            return response.json()

class MockOCRProvider(BaseOCRProvider):
    """
    High-fidelity deterministic Mock OCR Provider.
    Extracts realistic medical fields from sample files for testing and offline execution.
    """
    async def extract_text_and_data(self, file_bytes: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        fname_lower = filename.lower()
        
        # 1. Laboratory Report Mock
        if "lipid" in fname_lower or "glucose" in fname_lower or "lab" in fname_lower or "cbc" in fname_lower:
            raw_text = (
                f"APOLLO DIAGNOSTICS & RESEARCH CENTRE\n"
                f"File: {filename}\n"
                f"Patient Name: Ananya Sharma   Age/Gender: 38/F\n"
                f"Fasting Blood Glucose: 142 mg/dL (Reference: 70 - 99 mg/dL) [HIGH]\n"
                f"HbA1c (Glycated Hb): 7.6 % (Reference: 4.0 - 5.6 %) [HIGH]\n"
                f"Total Cholesterol: 232 mg/dL (Reference: 125 - 200 mg/dL) [HIGH]\n"
                f"HDL Cholesterol: 48 mg/dL (Reference: 40 - 60 mg/dL) [NORMAL]\n"
                f"Serum Triglycerides: 195 mg/dL (Reference: 50 - 150 mg/dL) [HIGH]\n"
                f"Specimen: Fluoride Plasma & Whole Blood EDTA\n"
                f"Doctor: Dr. Meera Krishnan, MD (Pathology)"
            )
            return {
                "raw_ocr_text": raw_text,
                "provider": "mock_sarvam_intelligence",
                "structured_candidate_data": {
                    "document_type": "lab_report",
                    "document_date": "2026-10-05",
                    "healthcare_provider": "Apollo Diagnostics & Research Centre",
                    "practitioner_name": "Dr. Meera Krishnan, MD",
                    "observations": [
                        {
                            "id": "obs-new-1",
                            "test_name": "Fasting Blood Glucose",
                            "value_numeric": 142.0,
                            "unit": "mg/dL",
                            "reference_low": 70.0,
                            "reference_high": 99.0,
                            "source_abnormal_flag": "H",
                            "confidence": "high",
                            "validation_status": "needs_review",
                            "source_text": "Fasting Blood Glucose: 142 mg/dL (Reference: 70 - 99 mg/dL) [HIGH]"
                        },
                        {
                            "id": "obs-new-2",
                            "test_name": "HbA1c",
                            "value_numeric": 7.6,
                            "unit": "%",
                            "reference_low": 4.0,
                            "reference_high": 5.6,
                            "source_abnormal_flag": "H",
                            "confidence": "high",
                            "validation_status": "needs_review",
                            "source_text": "HbA1c (Glycated Hb): 7.6 % (Reference: 4.0 - 5.6 %) [HIGH]"
                        },
                        {
                            "id": "obs-new-3",
                            "test_name": "Total Cholesterol",
                            "value_numeric": 232.0,
                            "unit": "mg/dL",
                            "reference_low": 125.0,
                            "reference_high": 200.0,
                            "source_abnormal_flag": "H",
                            "confidence": "high",
                            "validation_status": "needs_review",
                            "source_text": "Total Cholesterol: 232 mg/dL (Reference: 125 - 200 mg/dL) [HIGH]"
                        },
                        {
                            "id": "obs-new-4",
                            "test_name": "HDL Cholesterol",
                            "value_numeric": 48.0,
                            "unit": "mg/dL",
                            "reference_low": 40.0,
                            "reference_high": 60.0,
                            "source_abnormal_flag": "NORMAL",
                            "confidence": "high",
                            "validation_status": "needs_review",
                            "source_text": "HDL Cholesterol: 48 mg/dL (Reference: 40 - 60 mg/dL) [NORMAL]"
                        },
                        {
                            "id": "obs-new-5",
                            "test_name": "Serum Triglycerides",
                            "value_numeric": 195.0,
                            "unit": "mg/dL",
                            "reference_low": 50.0,
                            "reference_high": 150.0,
                            "source_abnormal_flag": "H",
                            "confidence": "high",
                            "validation_status": "needs_review",
                            "source_text": "Serum Triglycerides: 195 mg/dL (Reference: 50 - 150 mg/dL) [HIGH]"
                        }
                    ],
                    "medications": [],
                    "unreadable_segments": []
                }
            }
        
        # 2. Prescription Mock
        elif "presc" in fname_lower or "rx" in fname_lower:
            raw_text = (
                f"DR. R. SUNDARAM, MD (GENERAL MEDICINE)\n"
                f"Reg No: MCI-TN-45892 | Cauvery Multi-Specialty Clinic\n"
                f"Date: 06-Oct-2026\n"
                f"Rx:\n"
                f"1. Tab. Glycomet 500 SR (Metformin 500mg) - 1 tab OD after dinner x 90 days\n"
                f"2. Tab. Telma 40 (Telmisartan 40mg) - 1 tab OD in morning x 90 days\n"
                f"3. Tab. Atorva 10 (Atorvastatin 10mg) - 1 tab at bedtime x 90 days\n"
                f"[Special Note]: Routine fasting sugar and lipid review in 3 months.\n"
                f"[Unclear scribbled text at bottom]: Advised morning brisk walk 30 mins."
            )
            return {
                "raw_ocr_text": raw_text,
                "provider": "mock_sarvam_intelligence",
                "structured_candidate_data": {
                    "document_type": "prescription",
                    "document_date": "2026-10-06",
                    "healthcare_provider": "Cauvery Multi-Specialty Clinic",
                    "practitioner_name": "Dr. R. Sundaram, MD",
                    "observations": [],
                    "medications": [
                        {
                            "id": "med-new-1",
                            "medication_name": "Glycomet 500 SR",
                            "generic_name": "Metformin Hydrochloride",
                            "strength": "500 mg",
                            "dose_instructions": "1 tablet after dinner",
                            "route": "oral",
                            "frequency": "Once daily",
                            "duration": "90 days",
                            "prescription_date": "2026-10-06",
                            "confidence": "high",
                            "validation_status": "needs_review",
                            "source_text": "Tab. Glycomet 500 SR - 1 tab OD after dinner x 90 days"
                        },
                        {
                            "id": "med-new-2",
                            "medication_name": "Telma 40",
                            "generic_name": "Telmisartan",
                            "strength": "40 mg",
                            "dose_instructions": "1 tablet in the morning after breakfast",
                            "route": "oral",
                            "frequency": "Once daily",
                            "duration": "90 days",
                            "prescription_date": "2026-10-06",
                            "confidence": "high",
                            "validation_status": "needs_review",
                            "source_text": "Tab. Telma 40 - 1 tab OD in morning x 90 days"
                        },
                        {
                            "id": "med-new-3",
                            "medication_name": "Atorva 10",
                            "generic_name": "Atorvastatin",
                            "strength": "10 mg",
                            "dose_instructions": "1 tablet at bedtime",
                            "route": "oral",
                            "frequency": "Once daily at night",
                            "duration": "90 days",
                            "prescription_date": "2026-10-06",
                            "confidence": "high",
                            "validation_status": "needs_review",
                            "source_text": "Tab. Atorva 10 - 1 tab at bedtime x 90 days"
                        }
                    ],
                    "unreadable_segments": ["Scribbled handwriting in lifestyle advice note marked as needs review"]
                }
            }
        
        # 3. Generic Medical Document Mock
        else:
            raw_text = (
                f"MEDICAL HEALTH REPORT - {filename}\n"
                f"Date: 2026-10-10\n"
                f"Summary Consultation Note:\n"
                f"Blood Pressure: 128/82 mmHg [NORMAL]\n"
                f"Pulse: 74 bpm [NORMAL]\n"
                f"Hemoglobin: 13.2 g/dL (Reference: 12.0 - 15.5 g/dL) [NORMAL]\n"
                f"Impression: Stable vitals on current pharmacotherapy."
            )
            return {
                "raw_ocr_text": raw_text,
                "provider": "mock_sarvam_intelligence",
                "structured_candidate_data": {
                    "document_type": "lab_report",
                    "document_date": "2026-10-10",
                    "healthcare_provider": "City Health Consultation Centre",
                    "practitioner_name": "Dr. R. Sundaram",
                    "observations": [
                        {
                            "id": "obs-gen-1",
                            "test_name": "Hemoglobin",
                            "value_numeric": 13.2,
                            "unit": "g/dL",
                            "reference_low": 12.0,
                            "reference_high": 15.5,
                            "source_abnormal_flag": "NORMAL",
                            "confidence": "high",
                            "validation_status": "needs_review",
                            "source_text": "Hemoglobin: 13.2 g/dL (Reference: 12.0 - 15.5 g/dL)"
                        }
                    ],
                    "medications": [],
                    "unreadable_segments": []
                }
            }

def get_ocr_provider() -> BaseOCRProvider:
    if settings.SARVAM_PROVIDER_MODE == "live" and settings.SARVAM_API_KEY:
        return SarvamOCRProvider(settings.SARVAM_API_KEY, settings.SARVAM_BASE_URL)
    return MockOCRProvider()
