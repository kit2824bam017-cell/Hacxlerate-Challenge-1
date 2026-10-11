import pytest
import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.providers.translation import validate_translation_preservation, get_translation_provider
from app.providers.ocr import MockOCRProvider
from app.services.summary_service import _get_plain_explanation

def test_ocr_field_extraction_accuracy():
    """Verify that Mock OCR accurately identifies key lab parameters and units without loss."""
    provider = MockOCRProvider()
    res = asyncio.run(provider.extract_text_and_data(b"sample bytes", "lipid_panel.pdf", "application/pdf"))
    candidate = res["structured_candidate_data"]
    
    assert candidate["document_type"] == "lab_report"
    observations = candidate["observations"]
    test_names = [o["test_name"] for o in observations]
    
    assert "Fasting Blood Glucose" in test_names
    assert "HbA1c" in test_names
    assert "Total Cholesterol" in test_names
    
    glucose_obs = next(o for o in observations if o["test_name"] == "Fasting Blood Glucose")
    assert glucose_obs["value_numeric"] == 142.0
    assert glucose_obs["unit"] == "mg/dL"
    assert glucose_obs["reference_low"] == 70.0
    assert glucose_obs["reference_high"] == 99.0
    assert glucose_obs["source_abnormal_flag"] == "H"

def test_prescription_extraction_fidelity():
    """Verify prescription field segmentation (brand, strength, frequency, duration)."""
    provider = MockOCRProvider()
    res = asyncio.run(provider.extract_text_and_data(b"sample rx", "doctor_rx.jpg", "image/jpeg"))
    candidate = res["structured_candidate_data"]
    
    assert candidate["document_type"] == "prescription"
    meds = candidate["medications"]
    assert len(meds) >= 3
    
    glycomet = next(m for m in meds if "Glycomet" in m["medication_name"])
    assert glycomet["strength"] == "500 mg"
    assert "dinner" in glycomet["dose_instructions"]
    assert glycomet["frequency"] == "Once daily"
    assert glycomet["duration"] == "90 days"

def test_summary_grounding_safety():
    """Verify that plain explanations remain conservative and non-diagnostic."""
    glucose_exp = _get_plain_explanation("Fasting Blood Glucose", "high", "138 mg/dL")
    assert "insulin handling" in glucose_exp
    assert "doctor" in glucose_exp or "clinician" in glucose_exp
    # Must not diagnose diabetes definitively in isolation
    assert "You have diabetes" not in glucose_exp

def test_tamil_translation_numerical_preservation():
    """Verify that translation preserves numbers, units, and critical medical entities."""
    sample_en = "Fasting Blood Glucose is recorded at 138 mg/dL (Reference: 70 - 99 mg/dL)."
    provider = get_translation_provider()
    sample_ta = asyncio.run(provider.translate_text(sample_en, "en", "ta"))
    
    # Must preserve 138, 70, 99
    is_safe = validate_translation_preservation(sample_en, sample_ta)
    assert is_safe is True
    assert "138" in sample_ta
    assert "70" in sample_ta
    assert "99" in sample_ta
    assert "mg/dL" in sample_ta
