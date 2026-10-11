import pytest
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "sarvam_provider_mode" in data

def test_demo_auth_and_patient():
    response = client.post("/api/v1/auth/demo-login")
    assert response.status_code == 200
    auth_data = response.json()
    assert "access_token" in auth_data
    assert auth_data["patient_id"] == settings.DEMO_PATIENT_ID

    patient_resp = client.get("/api/v1/patient/me")
    assert patient_resp.status_code == 200
    patient = patient_resp.json()
    assert patient["full_name"] == "Ananya Sharma"
    assert patient["gender"] == "female"

def test_documents_listing():
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 3
    doc_types = {d["document_type"] for d in docs}
    assert "lab_report" in doc_types
    assert "prescription" in doc_types

def test_extraction_and_summary_retrieval():
    doc_id = "30000000-0000-0000-0000-000000000001"
    
    # 1. Candidate extraction
    ext_resp = client.get(f"/api/v1/documents/{doc_id}/extraction")
    assert ext_resp.status_code == 200
    ext = ext_resp.json()
    assert ext["review_status"] in ("approved", "pending")
    candidate_obs = ext["structured_candidate_data"]["observations"]
    assert len(candidate_obs) >= 5
    
    # 2. English summary
    sum_resp = client.get(f"/api/v1/documents/{doc_id}/summary?lang=en")
    assert sum_resp.status_code == 200
    summary = sum_resp.json()
    assert summary["language"] == "en"
    assert len(summary["key_findings"]) > 0
    assert "Fasting Blood Glucose" in summary["key_findings"][0]
    assert len(summary["abnormal_explanations"]) > 0

    # 3. Tamil summary
    sum_ta_resp = client.get(f"/api/v1/documents/{doc_id}/summary?lang=ta")
    assert sum_ta_resp.status_code == 200
    sum_ta = sum_ta_resp.json()
    assert sum_ta["language"] == "ta"
    assert "138 mg/dL" in str(sum_ta["key_findings"])  # numerical precision preserved
    assert "Fasting Blood Glucose" in str(sum_ta["abnormal_explanations"])  # entity preserved

def test_observations_and_trends():
    obs_resp = client.get("/api/v1/observations")
    assert obs_resp.status_code == 200
    obs_list = obs_resp.json()
    assert len(obs_list) >= 8

    trends_resp = client.get("/api/v1/observations/trends")
    assert trends_resp.status_code == 200
    trends = trends_resp.json()
    trend_names = {t["test_name"] for t in trends}
    assert "Fasting Blood Glucose" in trend_names
    assert "HbA1c" in trend_names

def test_medications_and_status_toggle():
    meds_resp = client.get("/api/v1/medications")
    assert meds_resp.status_code == 200
    meds = meds_resp.json()
    assert len(meds) >= 3
    
    target_med = meds[0]
    med_id = target_med["id"]
    new_status = "active" if target_med["medication_status"] != "active" else "prescribed"
    
    patch_resp = client.patch(f"/api/v1/medications/{med_id}", json={"medication_status": new_status})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["medication_status"] == new_status

def test_timeline_aggregation():
    resp = client.get("/api/v1/timeline")
    assert resp.status_code == 200
    timeline = resp.json()
    assert timeline["total_count"] > 0
    event_types = {e["event_type"] for e in timeline["events"]}
    assert "document_upload" in event_types
    assert "lab_observation" in event_types
    assert "prescription" in event_types

def test_mock_abha_link_and_verify():
    status_resp = client.get("/api/v1/abha/status")
    assert status_resp.status_code == 200
    
    link_resp = client.post("/api/v1/abha/link", json={"abha_identifier": "MOCK-ABHA-9999"})
    assert link_resp.status_code == 200
    link_data = link_resp.json()
    assert link_data["status"] == "otp_sent"
    
    verify_resp = client.post("/api/v1/abha/verify", json={"transaction_id": link_data["transaction_id"], "otp": "123456"})
    assert verify_resp.status_code == 200
    assert verify_resp.json()["success"] is True
