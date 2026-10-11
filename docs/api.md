# AI-Powered Personal Health Copilot - REST API Specification

## 1. Base URL & Common Conventions
All endpoints are versioned under `/api/v1`.
All dates follow ISO 8601 strings (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`).
Internal identifiers are RFC 4122 UUID v4 strings.

---

## 2. Endpoints Summary

### Authentication & Patient Profile
- `POST /api/v1/auth/demo-login` - Instant session activation for synthetic demo user
- `GET /api/v1/patient/me` - Fetch authenticated patient demographic profile
- `PATCH /api/v1/patient/me` - Update patient preferences (e.g. language)

### Documents
- `POST /api/v1/documents` - Multipart upload for PDF/JPG/PNG reports
- `GET /api/v1/documents` - List patient documents with pagination & filter by status/type
- `GET /api/v1/documents/{document_id}` - Retrieve document metadata & private signed access URL
- `DELETE /api/v1/documents/{document_id}` - Delete document and cascade unconfirmed extractions
- `POST /api/v1/documents/{document_id}/process` - Trigger asynchronous/immediate OCR & extraction
- `GET /api/v1/documents/{document_id}/status` - Polling endpoint for processing status

### Extraction & Human Review
- `GET /api/v1/documents/{document_id}/extraction` - Fetch candidate OCR & structured extraction
- `PATCH /api/v1/documents/{document_id}/extraction` - User correction of candidate fields
- `POST /api/v1/documents/{document_id}/confirm` - Promote reviewed candidate items into confirmed health records

### AI Health Summaries & Translation
- `POST /api/v1/documents/{document_id}/summary` - Generate or refresh plain-language grounded summary
- `GET /api/v1/documents/{document_id}/summary` - Retrieve summary in requested language (`en` or `ta`)
- `POST /api/v1/documents/{document_id}/summary/translate` - Request Sarvam-powered Tamil translation

### Longitudinal Health Records & Timeline
- `GET /api/v1/health-records` - Query FHIR R4 normalized records
- `GET /api/v1/observations` - Query lab values and trends (filter by `test_name`, date range)
- `GET /api/v1/medications` - Query medication history (distinguishing `active` vs `prescribed`)
- `PATCH /api/v1/medications/{medication_id}` - Toggle medication active status (prescribed vs confirmed taking)
- `GET /api/v1/timeline` - Chronological unified medical timeline with source provenance

### ABDM / ABHA Readiness
- `GET /api/v1/abha/status` - Current linkage status, active provider (`mock`), and provider mode
- `POST /api/v1/abha/link` - Initiate linking with fictional identifier (`MOCK-ABHA-XXXX`)
- `POST /api/v1/abha/verify` - Complete mock OTP verification
- `POST /api/v1/abha/revoke` - Disconnect mock ABHA link

---

## 3. Representative Schemas

### Document Upload Response
```json
{
  "id": "30000000-0000-0000-0000-000000000001",
  "patient_id": "00000000-0000-0000-0000-000000000001",
  "original_filename": "lipid_glucose_panel_2026.pdf",
  "mime_type": "application/pdf",
  "file_size_bytes": 245890,
  "document_type": "lab_report",
  "processing_status": "processing",
  "created_at": "2026-09-15T09:30:00Z"
}
```

### Extraction Candidate Schema
```json
{
  "document_id": "30000000-0000-0000-0000-000000000001",
  "document_type": "lab_report",
  "document_date": "2026-09-15",
  "healthcare_provider": "Metro Diagnostics & Labs, Chennai",
  "validation_status": "needs_review",
  "observations": [
    {
      "test_name": "Fasting Blood Glucose",
      "value_numeric": 138,
      "unit": "mg/dL",
      "reference_low": 70,
      "reference_high": 99,
      "source_abnormal_flag": "H",
      "confidence": "high",
      "validation_status": "needs_review",
      "source_text": "Fasting Blood Glucose : 138 mg/dL (Ref: 70 - 99 mg/dL) [H]"
    }
  ],
  "medications": []
}
```

### Bilingual Grounded Summary Response
```json
{
  "document_id": "30000000-0000-0000-0000-000000000001",
  "language": "en",
  "overview": "Laboratory report from Metro Diagnostics dated 15 Sep 2026 detailing Fasting Glucose and Lipid Panel.",
  "key_findings": [
    "Fasting Blood Glucose is recorded at 138 mg/dL (Reference: 70 - 99 mg/dL).",
    "HbA1c is recorded at 7.4% (Reference: 4.0 - 5.6%)."
  ],
  "abnormal_explanations": [
    {
      "test_name": "Fasting Blood Glucose",
      "value": "138 mg/dL",
      "reference": "70 - 99 mg/dL",
      "status": "Above Reference Range",
      "plain_explanation": "Blood sugar after overnight fasting. Elevated levels indicate that insulin handling may need review with your clinician."
    }
  ],
  "questions_for_doctor": [
    "Should my diabetes medication be adjusted based on the current HbA1c of 7.4%?"
  ],
  "limitations": "Based strictly on printed laboratory values. Clinical diagnosis requires doctor examination.",
  "safety_disclaimer": "INFORMATIONAL ASSISTANCE ONLY: This tool is not a doctor or diagnostic system."
}
```
