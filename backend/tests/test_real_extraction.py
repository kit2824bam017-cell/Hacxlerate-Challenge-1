import pytest
import io
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.services.medical_nlp import parse_medical_document_text, extract_raw_text_from_file

client = TestClient(app)

def test_arbitrary_unseen_lab_report_extraction():
    """
    Verifies that an arbitrary medical report with unseen filename and novel biomarkers
    (e.g., TSH, Serum Creatinine, Platelet Count) is genuinely parsed from content,
    extracting numeric values, units, reference intervals, flags, and source lines.
    """
    raw_report = (
        "SRI RAMACHANDRA MEDICAL CENTRE & LABS\n"
        "Report ID: SRMC-2026-99214\n"
        "Patient: Rajesh Kumar, 45/M\n"
        "Date: 11-Oct-2026\n"
        "Doctor: Dr. K. Venkataraman, MD\n"
        "Serum Creatinine: 1.8 mg/dL (Reference: 0.6 - 1.2 mg/dL) [HIGH]\n"
        "Platelet Count: 1.2 lakhs/cumm (Reference: 1.5 - 4.5 lakhs/cumm) [LOW]\n"
        "Thyroid Stimulating Hormone (TSH): 5.8 uIU/mL (Reference: 0.4 - 4.5 uIU/mL) [HIGH]\n"
        "Advised nephrology consultation and repeat TSH in 6 weeks."
    )
    
    parsed = parse_medical_document_text(raw_report, "unseen_random_doc_9921.txt")
    assert parsed["document_type"] == "lab_report"
    assert parsed["healthcare_provider"] == "SRI RAMACHANDRA MEDICAL CENTRE & LABS"
    assert "Dr. K. Venkataraman" in parsed["practitioner_name"]
    
    obs = parsed["observations"]
    assert len(obs) == 3
    
    # Check Creatinine
    creat = next(o for o in obs if "Creatinine" in o["test_name"])
    assert creat["value_numeric"] == 1.8
    assert creat["unit"] == "mg/dL"
    assert creat["reference_low"] == 0.6
    assert creat["reference_high"] == 1.2
    assert creat["source_abnormal_flag"] == "H"
    
    # Check Platelets
    plat = next(o for o in obs if "Platelet" in o["test_name"])
    assert plat["value_numeric"] == 1.2
    assert plat["source_abnormal_flag"] == "L"
    
    # Check TSH
    tsh = next(o for o in obs if "TSH" in o["test_name"])
    assert tsh["value_numeric"] == 5.8
    assert tsh["source_abnormal_flag"] == "H"

def test_arbitrary_unseen_prescription_extraction():
    """
    Verifies that an arbitrary prescription with unseen filename extracts
    novel medication regimens, dosages, formulations, and flags scribbled notes.
    """
    rx_text = (
        "HEALTHFIRST CLINIC & PHARMACY\n"
        "Date: 11-Oct-2026\n"
        "Doctor: Dr. S. Anitha, MBBS\n"
        "Rx:\n"
        "1. Tab. Januvia 100 mg - 1 tab OD after breakfast x 30 days\n"
        "2. Tab. Pan-D (Pantoprazole + Domperidone) - 1 tab before breakfast x 14 days\n"
        "Unclear scribbled lifestyle note: hydrate well and walk daily"
    )
    
    parsed = parse_medical_document_text(rx_text, "custom_rx_file_001.txt")
    assert parsed["document_type"] == "prescription"
    meds = parsed["medications"]
    assert len(meds) >= 2
    
    januvia = next(m for m in meds if "Januvia" in m["medication_name"])
    assert januvia["strength"] == "100 mg"
    assert januvia["frequency"] == "Once daily"
    
    # Check flagged scribbled segment for human review
    assert len(parsed["unreadable_segments"]) >= 1
