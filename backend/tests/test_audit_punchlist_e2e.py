import pytest
import io
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_audit_punchlist_end_to_end_validation():
    """
    End-to-End Audit Validation Test:
    1. Upload previously unseen medical report (arbitrary filename & content).
    2. Inspect extracted values, reference intervals, flags, and source lines.
    3. Human-in-the-loop: modify/correct an extracted value.
    4. Verify grounded summaries generated in English and Tamil.
    5. Confirm extraction into patient health records.
    6. Verify timeline event and longitudinal trend update.
    7. Verify standards-compliant FHIR R4 Bundle export.
    """
    # Step 1: Upload unseen medical document
    unseen_content = (
        "NATIONAL HEALTHCARE DIAGNOSTICS & RESEARCH\n"
        "Patient: Ananya Sharma (Age: 38)\n"
        "Report ID: NHDR-2026-8812\n"
        "Date: 11-Oct-2026\n"
        "Doctor: Dr. A. K. Sengupta, MD\n"
        "Fasting Blood Glucose: 144 mg/dL (Reference: 70 - 99 mg/dL) [HIGH]\n"
        "HbA1c: 7.7 % (Reference: 4.0 - 5.6 %) [HIGH]\n"
        "Total Cholesterol: 236 mg/dL (Reference: 125 - 200 mg/dL) [HIGH]\n"
        "Serum Creatinine: 1.1 mg/dL (Reference: 0.6 - 1.2 mg/dL) [NORMAL]\n"
        "Advised endocrinology follow-up and glycemic optimization."
    ).encode("utf-8")

    files = {
        "file": ("unseen_clinical_report_2026.pdf", io.BytesIO(unseen_content), "application/pdf")
    }

    upload_resp = client.post("/api/v1/documents", files=files)
    assert upload_resp.status_code == 200
    doc = upload_resp.json()
    doc_id = doc["id"]
    assert doc["original_filename"] == "unseen_clinical_report_2026.pdf"
    assert doc["processing_status"] in ("awaiting_review", "completed")

    # Step 2: Inspect candidate extraction
    ext_resp = client.get(f"/api/v1/documents/{doc_id}/extraction")
    assert ext_resp.status_code == 200
    ext = ext_resp.json()
    cand = ext["structured_candidate_data"]
    assert cand["document_type"] == "lab_report"
    assert len(cand["observations"]) >= 4

    glucose_obs = next(o for o in cand["observations"] if "Glucose" in o["test_name"])
    assert glucose_obs["value_numeric"] == 144.0
    assert glucose_obs["unit"] == "mg/dL"
    assert glucose_obs["source_abnormal_flag"] == "H"
    assert "144 mg/dL" in glucose_obs["source_text"]

    hba1c_obs = next(o for o in cand["observations"] if "HbA1c" in o["test_name"])
    assert hba1c_obs["value_numeric"] == 7.7
    assert hba1c_obs["unit"] == "%"

    # Step 3: Human-in-the-loop edit (correcting an extracted value)
    cand["observations"][0]["value_numeric"] = 145.0
    cand["observations"][0]["validation_status"] = "verified"
    update_resp = client.put(f"/api/v1/documents/{doc_id}/extraction", json={"structured_candidate_data": cand})
    assert update_resp.status_code == 200
    updated_cand = update_resp.json()["structured_candidate_data"]
    assert updated_cand["observations"][0]["value_numeric"] == 145.0

    # Step 4: Verify English and Tamil evidence-grounded summaries
    sum_en = client.get(f"/api/v1/documents/{doc_id}/summary?lang=en").json()
    assert len(sum_en["key_findings"]) >= 3
    assert len(sum_en["abnormal_explanations"]) >= 3
    assert "INFORMATIONAL ASSISTANCE ONLY" in sum_en["safety_disclaimer"]
    assert "not a doctor" in sum_en["safety_disclaimer"].lower()

    sum_ta = client.get(f"/api/v1/documents/{doc_id}/summary?lang=ta").json()
    assert sum_ta["language"] == "ta"
    assert len(sum_ta["key_findings"]) >= 3
    assert any("144" in kf or "145" in kf or "7.7" in kf for kf in sum_ta["key_findings"])

    # Step 5: Confirm extraction into longitudinal record
    confirm_resp = client.post(
        f"/api/v1/documents/{doc_id}/confirm",
        json={"confirm_all": True, "active_medications": []}
    )
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "confirmed"

    # Step 6: Verify Timeline & Trends
    timeline_resp = client.get("/api/v1/timeline")
    assert timeline_resp.status_code == 200
    events = timeline_resp.json()["events"]
    assert any(str(doc_id) in str(e.get("source_document_id")) for e in events)

    trends_resp = client.get("/api/v1/observations/trends")
    assert trends_resp.status_code == 200
    trends = trends_resp.json()
    glucose_trend = next(t for t in trends if "Glucose" in t["test_name"])
    assert len(glucose_trend["history"]) >= 2  # Has multiple historical points now

    # Step 7: Verify FHIR R4 Bundle Export
    fhir_resp = client.get("/api/v1/fhir/bundle")
    assert fhir_resp.status_code == 200
    fhir_bundle = fhir_resp.json()
    assert fhir_bundle["resourceType"] == "Bundle"
    assert fhir_bundle["type"] == "collection"
    assert fhir_bundle["total"] >= 10
