# AI-Powered Personal Health Copilot - System Architecture

## 1. Overview
The **AI-Powered Personal Health Copilot** is an enterprise-grade, privacy-first healthcare informatics solution designed for the Altrix Labs Innovation Challenge. The system transforms unstructured, fragmented Indian medical documents (prescriptions, laboratory reports, discharge summaries) into organized, FHIR-compatible digital health records with evidence-grounded bilingual summaries (English and Tamil) and ABDM/ABHA integration readiness.

---

## 2. System Architecture Diagram

```mermaid
flowchart TD
    subgraph Frontend["React 19 + TypeScript + Vite + Tailwind (shadcn-admin)"]
        UI_Upload[Document Upload Drag & Drop]
        UI_Review[Candidate Extraction Review Screen]
        UI_Summary[Bilingual Grounded Summary Viewer]
        UI_Timeline[Chronological Health Timeline & Trends]
        UI_Medications[Medication History (Prescribed vs Active)]
        UI_ABHA[ABHA Linkage & Sandbox Status]
        UI_I18N[Tamil / English Localization]
    end

    subgraph BackendGateway["FastAPI Gateway (/api/v1)"]
        AuthMiddleware[Bearer Auth / Synthetic Session Guard]
        AuditInterceptor[Privacy-Preserving Audit Logger]
        RateLimiter[Request & File Size Validator]
    end

    subgraph CoreServices["Backend Domain Services"]
        DocService[Document Processing Coordinator]
        OCRService[OCR & Document Intelligence Engine]
        ExtractionService[Schema Extraction & Normalizer]
        ValidationService[Confidence & Range Validator]
        SummaryEngine[Evidence-Grounded AI Summary Engine]
        TranslationService[Indian Language Translation Engine]
        ABHAService[ABDM / ABHA Provider Abstraction]
        FHIRMapper[FHIR R4 Mapping & Provenance Layer]
    end

    subgraph Providers["Replaceable Provider Adapters"]
        SarvamVision[Sarvam AI Document Intelligence Adapter]
        SarvamMayura[Sarvam Mayura Translation Adapter]
        MockOCR[High-Fidelity Synthetic OCR / Extraction Mock]
        MockABHA[MockABHAProvider (Visibly Simulated)]
        LiveABDM[ABDM Sandbox Provider (Config-Toggled)]
    end

    subgraph Persistence["Storage & Database (Supabase PostgreSQL)"]
        EncryptedStorage[(Private Document Storage Bucket)]
        DB_Patients[(patients)]
        DB_Documents[(documents)]
        DB_Extractions[(extraction_results)]
        DB_FHIR[(health_records - FHIR R4)]
        DB_Observations[(observations)]
        DB_Medications[(medications)]
        DB_ABHA[(abha_links)]
        DB_Audit[(audit_logs)]
    end

    %% Data Flow Connections
    UI_Upload -->|Authenticated Multipart Upload| BackendGateway
    BackendGateway --> DocService
    DocService --> EncryptedStorage
    DocService --> OCRService
    OCRService --> Providers
    Providers --> ExtractionService
    ExtractionService --> ValidationService
    ValidationService --> DB_Extractions
    DB_Extractions --> UI_Review

    UI_Review -->|User Confirms & Corrects Fields| DocService
    DocService --> FHIRMapper
    FHIRMapper --> DB_FHIR
    FHIRMapper --> DB_Observations
    FHIRMapper --> DB_Medications
    DocService --> SummaryEngine
    SummaryEngine --> TranslationService
    SummaryEngine --> UI_Summary

    UI_Timeline --> DB_Observations
    UI_Medications --> DB_Medications
    UI_ABHA --> ABHAService
    ABHAService --> MockABHA
```

---

## 3. Key Design Principles & Data Privacy

1. **Informational Health Assistant Boundary**: The copilot is strictly an educational and organizational tool. It does not issue clinical diagnoses, prescribe drug modifications, or replace licensed medical practitioners.
2. **Provenance & Evidence Grounding**: Every test value, reference interval, and medication instruction is linked to its source document and candidate extraction record. The AI summarizer is constrained to explicit facts printed in the document.
3. **No Phantom Facts / Zero Confabulation**: If an OCR segment or doctor's handwriting is illegible or ambiguous, it is tagged as `unreadable_or_missing` or `needs_review`. The system never invents missing dosages.
4. **Data Privacy & Server-Side Privilege Isolation**:
   - Original medical files are stored in private storage accessible only via authenticated signed URLs.
   - External provider credentials (`SARVAM_API_KEY`, Supabase service role keys) remain strictly on the backend.
   - Row Level Security (RLS) guarantees complete patient tenant isolation.
5. **Standards Compliance**: FHIR R4 resource representations (`Observation`, `DiagnosticReport`, `MedicationRequest`, `Encounter`) with internal UUIDs as primary keys, ready for official ABDM sandbox integration.
