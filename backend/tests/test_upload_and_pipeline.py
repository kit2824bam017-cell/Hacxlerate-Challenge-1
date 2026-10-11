import pytest
import sys
import os
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_document_upload_and_auto_ocr():
    # Simulate a PDF upload
    pdf_content = b"%PDF-1.4 sample lab report content for lipid panel"
    files = {
        "file": ("new_lipid_panel.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    
    upload_resp = client.post("/api/v1/documents", files=files)
    assert upload_resp.status_code == 200
    doc = upload_resp.json()
    assert doc["original_filename"] == "new_lipid_panel.pdf"
    assert doc["processing_status"] in ("awaiting_review", "completed")
    doc_id = doc["id"]
    
    # Check status endpoint
    status_resp = client.get(f"/api/v1/documents/{doc_id}/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["processing_status"] in ("awaiting_review", "completed")
    
    # Check extraction record was generated
    ext_resp = client.get(f"/api/v1/documents/{doc_id}/extraction")
    assert ext_resp.status_code == 200
    ext = ext_resp.json()
    candidate_obs = ext["structured_candidate_data"]["observations"]
    assert len(candidate_obs) > 0
    assert any("Glucose" in o["test_name"] for o in candidate_obs)
    
    # Check auto-generated summary
    sum_resp = client.get(f"/api/v1/documents/{doc_id}/summary?lang=en")
    assert sum_resp.status_code == 200
    summary = sum_resp.json()
    assert len(summary["key_findings"]) > 0
    assert len(summary["abnormal_explanations"]) > 0

    # User review & confirm extraction
    confirm_resp = client.post(
        f"/api/v1/documents/{doc_id}/confirm",
        json={"confirm_all": True, "active_medications": []}
    )
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "confirmed"
    
    # Verify doc is completed
    doc_after = client.get(f"/api/v1/documents/{doc_id}").json()
    assert doc_after["processing_status"] == "completed"
