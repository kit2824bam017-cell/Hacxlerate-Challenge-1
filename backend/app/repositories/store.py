import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from uuid import UUID

from app.schemas.patient import PatientResponse, PatientUpdate
from app.schemas.document import DocumentResponse
from app.schemas.extraction import (
    ExtractionResultResponse, CandidateExtractionData,
    ExtractedObservationItem, ExtractedMedicationItem, ExtractedDischargeItem
)
from app.schemas.summary import DocumentSummaryResponse, AbnormalExplanationItem
from app.schemas.observation import ObservationResponse, TrendPoint, TestTrendResponse
from app.schemas.medication import MedicationResponse
from app.schemas.timeline import TimelineEvent, TimelineResponse
from app.schemas.abha import ABHAStatusResponse

class MemoryDataStore:
    """
    High-fidelity in-memory persistence and synthetic repository.
    Guarantees reliable, instant execution and testing for local development
    and Altrix challenge demonstration, perfectly mirroring the Supabase PostgreSQL schema.
    """
    def __init__(self):
        self.patients: Dict[UUID, Dict[str, Any]] = {}
        self.documents: Dict[UUID, Dict[str, Any]] = {}
        self.document_files: Dict[UUID, bytes] = {}
        self.extractions: Dict[UUID, Dict[str, Any]] = {}
        self.observations: Dict[UUID, Dict[str, Any]] = {}
        self.medications: Dict[UUID, Dict[str, Any]] = {}
        self.encounters: Dict[UUID, Dict[str, Any]] = {}
        self.summaries: Dict[str, Dict[str, Any]] = {}  # key: f"{doc_id}_{lang}"
        self.abha_links: Dict[UUID, Dict[str, Any]] = {}
        self.audit_logs: List[Dict[str, Any]] = []
        
        self._seed_synthetic_data()

    def _seed_synthetic_data(self):
        # 1. Synthetic Patient (Ananya Sharma)
        patient_id = UUID("00000000-0000-0000-0000-000000000001")
        user_id = UUID("00000000-0000-0000-0000-000000000001")
        self.patients[patient_id] = {
            "id": patient_id,
            "user_id": user_id,
            "full_name": "Ananya Sharma",
            "date_of_birth": date(1988, 6, 14),
            "gender": "female",
            "blood_group": "B+",
            "contact_phone": "+91-98765-43210",
            "email": "ananya.sharma@example.internal",
            "emergency_contact": "+91-98765-12345 (Spouse)",
            "preferred_language": "en",
            "created_at": datetime(2026, 1, 15, 10, 0, 0),
            "updated_at": datetime(2026, 9, 20, 10, 0, 0)
        }

        # 2. Synthetic Documents
        doc1_id = UUID("30000000-0000-0000-0000-000000000001")
        self.documents[doc1_id] = {
            "id": doc1_id,
            "patient_id": patient_id,
            "storage_path": "patient_001/docs/lipid_glucose_panel_2026.pdf",
            "original_filename": "lipid_glucose_panel_2026.pdf",
            "mime_type": "application/pdf",
            "file_size_bytes": 245890,
            "document_type": "lab_report",
            "document_date": date(2026, 9, 15),
            "processing_status": "completed",
            "error_message": None,
            "created_at": datetime(2026, 9, 15, 9, 30, 0),
            "updated_at": datetime(2026, 9, 15, 9, 35, 0)
        }
        self.document_files[doc1_id] = b"%PDF-1.4 [Synthetic Lipid & Fasting Blood Sugar Report Content]"

        doc2_id = UUID("30000000-0000-0000-0000-000000000002")
        self.documents[doc2_id] = {
            "id": doc2_id,
            "patient_id": patient_id,
            "storage_path": "patient_001/docs/doctor_prescription_sep2026.jpg",
            "original_filename": "doctor_prescription_sep2026.jpg",
            "mime_type": "image/jpeg",
            "file_size_bytes": 524100,
            "document_type": "prescription",
            "document_date": date(2026, 9, 18),
            "processing_status": "completed",
            "error_message": None,
            "created_at": datetime(2026, 9, 18, 11, 0, 0),
            "updated_at": datetime(2026, 9, 18, 11, 5, 0)
        }
        self.document_files[doc2_id] = b"[Synthetic Doctor Prescription Image Content]"

        doc3_id = UUID("30000000-0000-0000-0000-000000000003")
        self.documents[doc3_id] = {
            "id": doc3_id,
            "patient_id": patient_id,
            "storage_path": "patient_001/docs/cbc_baseline_2026.pdf",
            "original_filename": "cbc_baseline_2026.pdf",
            "mime_type": "application/pdf",
            "file_size_bytes": 198400,
            "document_type": "lab_report",
            "document_date": date(2026, 3, 10),
            "processing_status": "completed",
            "error_message": None,
            "created_at": datetime(2026, 3, 10, 8, 30, 0),
            "updated_at": datetime(2026, 3, 10, 8, 35, 0)
        }
        self.document_files[doc3_id] = b"%PDF-1.4 [Synthetic Baseline Lab Report Content]"

        # 3. Extraction Result for Doc 1
        ext1_id = UUID("40000000-0000-0000-0000-000000000001")
        self.extractions[doc1_id] = {
            "id": ext1_id,
            "document_id": doc1_id,
            "raw_ocr_text": "METRO DIAGNOSTICS & LABS, CHENNAI\nDate: 15-Sep-2026\nPatient: Ananya Sharma (F/38)\nFasting Blood Glucose: 138 mg/dL (70-99) [H]\nHbA1c (Glycated Hemoglobin): 7.4 % (4.0-5.6) [H]\nTotal Cholesterol: 228 mg/dL (125-200) [H]\nHDL Cholesterol: 46 mg/dL (40-60) [NORMAL]\nLDL Cholesterol: 142 mg/dL (<100) [H]",
            "structured_candidate_data": {
                "document_type": "lab_report",
                "document_date": "2026-09-15",
                "healthcare_provider": "Metro Diagnostics & Labs, Chennai",
                "practitioner_name": "Dr. Meera Krishnan, MD",
                "observations": [
                    {
                        "id": "obs-1",
                        "test_name": "Fasting Blood Glucose",
                        "value_numeric": 138,
                        "unit": "mg/dL",
                        "reference_low": 70,
                        "reference_high": 99,
                        "source_abnormal_flag": "H",
                        "confidence": "high",
                        "validation_status": "verified",
                        "source_text": "Fasting Blood Glucose: 138 mg/dL (70-99) [H]"
                    },
                    {
                        "id": "obs-2",
                        "test_name": "HbA1c",
                        "value_numeric": 7.4,
                        "unit": "%",
                        "reference_low": 4.0,
                        "reference_high": 5.6,
                        "source_abnormal_flag": "H",
                        "confidence": "high",
                        "validation_status": "verified",
                        "source_text": "HbA1c (Glycated Hemoglobin): 7.4 % (4.0-5.6) [H]"
                    },
                    {
                        "id": "obs-3",
                        "test_name": "Total Cholesterol",
                        "value_numeric": 228,
                        "unit": "mg/dL",
                        "reference_low": 125,
                        "reference_high": 200,
                        "source_abnormal_flag": "H",
                        "confidence": "high",
                        "validation_status": "verified",
                        "source_text": "Total Cholesterol: 228 mg/dL (125-200) [H]"
                    },
                    {
                        "id": "obs-4",
                        "test_name": "HDL Cholesterol",
                        "value_numeric": 46,
                        "unit": "mg/dL",
                        "reference_low": 40,
                        "reference_high": 60,
                        "source_abnormal_flag": "NORMAL",
                        "confidence": "high",
                        "validation_status": "verified",
                        "source_text": "HDL Cholesterol: 46 mg/dL (40-60) [NORMAL]"
                    },
                    {
                        "id": "obs-5",
                        "test_name": "LDL Cholesterol",
                        "value_numeric": 142,
                        "unit": "mg/dL",
                        "reference_low": 0,
                        "reference_high": 100,
                        "source_abnormal_flag": "H",
                        "confidence": "high",
                        "validation_status": "verified",
                        "source_text": "LDL Cholesterol: 142 mg/dL (<100) [H]"
                    }
                ],
                "medications": [],
                "unreadable_segments": []
            },
            "extraction_provider": "sarvam",
            "provider_model": "sarvam-doc-intelligence-v1",
            "validation_status": "high_confidence",
            "review_status": "approved",
            "created_at": datetime(2026, 9, 15, 9, 32, 0),
            "updated_at": datetime(2026, 9, 15, 9, 35, 0)
        }

        # 4. Confirmed Observations (Sep 2026 & Mar 2026)
        obs_seed = [
            # Sep 2026
            (UUID("50000000-0000-0000-0000-000000000001"), doc1_id, "1558-6", "Fasting Blood Glucose", 138, "mg/dL", 70, 99, "H", datetime(2026, 9, 15, 8, 0, 0)),
            (UUID("50000000-0000-0000-0000-000000000002"), doc1_id, "4548-4", "HbA1c", 7.4, "%", 4.0, 5.6, "H", datetime(2026, 9, 15, 8, 0, 0)),
            (UUID("50000000-0000-0000-0000-000000000003"), doc1_id, "2093-3", "Total Cholesterol", 228, "mg/dL", 125, 200, "H", datetime(2026, 9, 15, 8, 0, 0)),
            (UUID("50000000-0000-0000-0000-000000000004"), doc1_id, "2085-9", "HDL Cholesterol", 46, "mg/dL", 40, 60, "NORMAL", datetime(2026, 9, 15, 8, 0, 0)),
            (UUID("50000000-0000-0000-0000-000000000005"), doc1_id, "13457-7", "LDL Cholesterol", 142, "mg/dL", 0, 100, "H", datetime(2026, 9, 15, 8, 0, 0)),
            # Mar 2026 Baseline
            (UUID("50000000-0000-0000-0000-000000000006"), doc3_id, "1558-6", "Fasting Blood Glucose", 114, "mg/dL", 70, 99, "H", datetime(2026, 3, 10, 8, 0, 0)),
            (UUID("50000000-0000-0000-0000-000000000007"), doc3_id, "4548-4", "HbA1c", 6.6, "%", 4.0, 5.6, "H", datetime(2026, 3, 10, 8, 0, 0)),
            (UUID("50000000-0000-0000-0000-000000000008"), doc3_id, "2093-3", "Total Cholesterol", 210, "mg/dL", 125, 200, "H", datetime(2026, 3, 10, 8, 0, 0)),
        ]
        for oid, did, code, name, val, unit, rlow, rhigh, flag, eff in obs_seed:
            self.observations[oid] = {
                "id": oid,
                "patient_id": patient_id,
                "document_id": did,
                "health_record_id": None,
                "code": code,
                "display_name": name,
                "value_numeric": val,
                "value_text": str(val),
                "unit": unit,
                "reference_low": rlow,
                "reference_high": rhigh,
                "source_abnormal_flag": flag,
                "effective_at": eff,
                "validation_status": "validated",
                "created_at": eff
            }

        # 5. Confirmed Medications
        med_seed = [
            (UUID("60000000-0000-0000-0000-000000000001"), doc2_id, "Glycomet 500 SR", "Metformin Hydrochloride", "500 mg", "1 tab with dinner", "oral", "Once daily", "90 days", date(2026, 9, 18), "active"),
            (UUID("60000000-0000-0000-0000-000000000002"), doc2_id, "Telma 40", "Telmisartan", "40 mg", "1 tab in morning after food", "oral", "Once daily", "90 days", date(2026, 9, 18), "active"),
            (UUID("60000000-0000-0000-0000-000000000003"), doc2_id, "Atorva 10", "Atorvastatin Calcium", "10 mg", "1 tab at bedtime", "oral", "Once daily at night", "90 days", date(2026, 9, 18), "prescribed"),
        ]
        for mid, did, mname, gname, strn, dose, rt, freq, dur, pdate, mstatus in med_seed:
            self.medications[mid] = {
                "id": mid,
                "patient_id": patient_id,
                "document_id": did,
                "medication_name": mname,
                "generic_name": gname,
                "strength": strn,
                "dose_instructions": dose,
                "route": rt,
                "frequency": freq,
                "duration": dur,
                "prescription_date": pdate,
                "medication_status": mstatus,
                "review_status": "confirmed",
                "created_at": datetime(2026, 9, 18, 11, 0, 0)
            }

        # 6. Summaries (English & Tamil) for Doc 1
        sum1_en_id = UUID("80000000-0000-0000-0000-000000000001")
        self.summaries[f"{doc1_id}_en"] = {
            "id": sum1_en_id,
            "document_id": doc1_id,
            "language": "en",
            "overview": "This laboratory report from Metro Diagnostics dated 15 Sep 2026 details your Fasting Blood Glucose, HbA1c, and Lipid Panel measurements.",
            "key_findings": [
                "Fasting Blood Glucose is recorded at 138 mg/dL (Reference: 70 - 99 mg/dL).",
                "HbA1c is recorded at 7.4% (Reference: 4.0 - 5.6%).",
                "Total Cholesterol is 228 mg/dL and LDL is 142 mg/dL, both elevated above standard laboratory cutoffs.",
                "HDL Cholesterol is 46 mg/dL, within the desirable range."
            ],
            "abnormal_explanations": [
                {
                    "test_name": "Fasting Blood Glucose",
                    "value": "138 mg/dL",
                    "reference": "70 - 99 mg/dL",
                    "status": "Above Reference Range",
                    "plain_explanation": "Blood sugar after overnight fasting. Elevated levels indicate that insulin handling may need review with your clinician."
                },
                {
                    "test_name": "HbA1c",
                    "value": "7.4%",
                    "reference": "4.0 - 5.6%",
                    "status": "Above Reference Range",
                    "plain_explanation": "Reflects average blood sugar control over the past 2 to 3 months."
                },
                {
                    "test_name": "LDL Cholesterol",
                    "value": "142 mg/dL",
                    "reference": "< 100 mg/dL",
                    "status": "Above Reference Range",
                    "plain_explanation": "Often referred to as low-density lipoprotein; elevated levels are considered in cardiovascular risk assessments."
                }
            ],
            "questions_for_doctor": [
                "Should my diabetes medication be adjusted based on the current HbA1c of 7.4%?",
                "Do I need dietary changes or medication for elevated LDL cholesterol (142 mg/dL)?",
                "When should I repeat these blood tests?"
            ],
            "limitations": "This summary is based solely on the values printed in the provided laboratory report. Clinical diagnosis requires comprehensive medical evaluation.",
            "safety_disclaimer": "INFORMATIONAL ASSISTANCE ONLY: This tool is not a doctor, diagnostic system, or emergency service. Never alter prescription medications without consulting your healthcare provider.",
            "created_at": datetime(2026, 9, 15, 9, 35, 0)
        }

        sum1_ta_id = UUID("80000000-0000-0000-0000-000000000002")
        self.summaries[f"{doc1_id}_ta"] = {
            "id": sum1_ta_id,
            "document_id": doc1_id,
            "language": "ta",
            "overview": "இது 15 செப்டம்பர் 2026 அன்று மெட்ரோ டயக்னாஸ்டிக்ஸ் ஆய்வகத்தால் வழங்கப்பட்ட உண்ணாநிலை இரத்த சர்க்கரை, HbA1c மற்றும் கொழுப்பு அளவுகளின் பரிசோதனை அறிக்கை.",
            "key_findings": [
                "உண்ணாநிலை இரத்த சர்க்கரை அளவு 138 mg/dL ஆக பதிவாகியுள்ளது (இயல்பு வரம்பு: 70 - 99 mg/dL).",
                "HbA1c அளவு 7.4% ஆக உள்ளது (இயல்பு வரம்பு: 4.0 - 5.6%).",
                "மொத்த கொலஸ்ட்ரால் 228 mg/dL மற்றும் LDL கொலஸ்ட்ரால் 142 mg/dL ஆக இயல்பு வரம்பை விட அதிகமாக உள்ளன.",
                "HDL கொலஸ்ட்ரால் 46 mg/dL ஆக சாதாரண வரம்பில் உள்ளது."
            ],
            "abnormal_explanations": [
                {
                    "test_name": "Fasting Blood Glucose",
                    "value": "138 mg/dL",
                    "reference": "70 - 99 mg/dL",
                    "status": "இயல்பு வரம்பை விட அதிகம்",
                    "plain_explanation": "இரவு உணவுக்குப் பிறகு காலையில் எடுக்கப்படும் இரத்த சர்க்கரை அளவு. இது அதிகரித்திருப்பது மருத்துவ ஆலோசனையை பரிந்துரைக்கிறது."
                },
                {
                    "test_name": "HbA1c",
                    "value": "7.4%",
                    "reference": "4.0 - 5.6%",
                    "status": "இயல்பு வரம்பை விட அதிகம்",
                    "plain_explanation": "கடந்த 2 முதல் 3 மாதங்களின் சராசரி இரத்த சர்க்கரை அளவைக் குறிக்கிறது."
                },
                {
                    "test_name": "LDL Cholesterol",
                    "value": "142 mg/dL",
                    "reference": "< 100 mg/dL",
                    "status": "இயல்பு வரம்பை விட அதிகம்",
                    "plain_explanation": "இரத்தக் குழாய்களில் படியக்கூடிய கெட்ட கொழுப்பு வகையாகும்."
                }
            ],
            "questions_for_doctor": [
                "எனது தற்போதைய HbA1c 7.4% அடிப்படையில் சர்க்கரை நோய் மருந்துகளை மாற்ற வேண்டுமா?",
                "அதிகரித்துள்ள LDL கொலஸ்ட்ராலுக்கு (142 mg/dL) உணவு முறை மாற்றம் அல்லது புதிய மருந்து தேவையா?",
                "அடுத்த பரிசோதனையை எப்போது மேற்கொள்ள வேண்டும்?"
            ],
            "limitations": "இந்த விளக்கம் வழங்கப்பட்ட ஆய்வக அறிக்கையில் உள்ள தகவல்களை மட்டுமே அடிப்படையாகக் கொண்டது.",
            "safety_disclaimer": "தகவல் உதவி மட்டுமே: இந்த செயலி மருத்துவரோ அல்லது அவசர சிகிச்சை முறையோ அல்ல. உங்கள் மருத்துவரை கலந்தாலோசிக்காமல் மருந்துகளில் எந்த மாற்றமும் செய்யாதீர்கள்.",
            "created_at": datetime(2026, 9, 15, 9, 36, 0)
        }

        # 7. Mock ABHA Link
        self.abha_links[patient_id] = {
            "id": UUID("90000000-0000-0000-0000-000000000001"),
            "patient_id": patient_id,
            "provider": "mock",
            "environment": "sandbox",
            "external_reference": "MOCK-ABHA-0001",
            "status": "linked",
            "verification_method": "simulated_otp",
            "verified_at": datetime(2026, 9, 20, 10, 0, 0),
            "created_at": datetime(2026, 9, 20, 10, 0, 0),
            "updated_at": datetime(2026, 9, 20, 10, 0, 0)
        }

store = MemoryDataStore()
