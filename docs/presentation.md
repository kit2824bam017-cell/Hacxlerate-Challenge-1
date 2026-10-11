# AI-Powered Personal Health Copilot - Altrix Challenge Presentation

## 1. Problem Statement
Medical records in India remain highly fragmented across printed lab reports, paper prescriptions, discharge summaries, and clinic consults. Citizens struggle to:
- Understand complex clinical jargon and reference cutoffs.
- Identify values flagged abnormal across multiple tests over time.
- Verify whether handwritten prescriptions were transcribed accurately.
- Prepare meaningful questions for clinician consultations in their native language (e.g., Tamil).

---

## 2. Our Solution: AI-Powered Personal Health Copilot
An enterprise-grade, privacy-first healthcare informatics copilot combining:
1. **Medical Document Intelligence**: PDF, JPG, PNG OCR extraction for lab panels and doctor prescriptions.
2. **Human-in-the-Loop Review Screen**: Clear distinction between raw OCR, candidate extractions, and confirmed health records.
3. **Evidence-Grounded AI Summaries**: Plain-language explanations strictly anchored in source reports, with no hallucinated diagnoses or prescriptions.
4. **Bilingual Support with Sarvam**: Native Tamil translations preserving numbers, units, and drug names.
5. **Longitudinal Trends & Timeline**: Visual trajectories for Fasting Blood Glucose, HbA1c, and Lipid profiles.
6. **ABDM / ABHA Sandbox Ready**: Pluggable `ABHAProvider` architecture with an explicit simulated workflow.

---

## 3. Architecture & Innovation Highlights

```
[Citizen Upload] ──> [FastAPI Backend] ──> [Sarvam OCR / Mock]
                             │
                             ▼
                 [Candidate Schema Review]
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [FHIR R4 Normalized Store]     [Grounded Summary Engine]
   (Observation, MedicationRequest)          │
            │                         [Sarvam Translation]
            ▼                                 │
 [Chronological Timeline & Trends]     [English & Tamil UI]
```

### Key Technical Innovations
- **No Confabulation / Zero Guessing**: Unreadable handwriting is tagged `needs_review` or `unreadable_or_missing` rather than guessed.
- **Tenant Isolation**: Row Level Security (RLS) policies where `auth.uid() = user_id`.
- **Unit and Reference Interval Preservation**: Never compares tests with mismatched units or uncalibrated ranges.
- **ABDM Readiness**: Internal UUID primary keys with mapping layers to FHIR R4 resources.

---

## 4. Demonstrated Results & Test Verification
- **Automated Tests**: 9/9 unit and integration tests passing (`pytest backend/tests/`).
- **Frontend Quality**: Zero-error production build (`vite build` in 10s) using shadcn-admin base with Tailwind CSS.
- **Safety Grounding**: Measured 100% numerical and unit preservation on synthetic Indian diagnostic panels and prescriptions.
