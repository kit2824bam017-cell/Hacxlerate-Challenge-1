# AI-Powered Personal Health Copilot - Security, Privacy & Safety Architecture

## 1. Healthcare Safety & Clinical Non-Maleficence Principles

Medical data assistants operate under stringent patient safety standards:
1. **Explicit Informational Scope**:
   - The system prominently presents clear disclaimers that it is an informational aid, not a diagnostic engine or medical practitioner.
   - It never suggests altering prescribed medication dosages.
2. **Conservative & Non-Alarmist Communication**:
   - Out-of-range observations are objectively described relative to the report's printed reference intervals.
   - Abnormal values are never equated to definitive diseases without doctor evaluation.
3. **Data Integrity & Zero Confabulation**:
   - Unreadable handwriting in prescriptions is flagged as `unreadable_or_missing` or `needs_review` rather than guessed.
   - Incomplete reference ranges or mismatched units are flagged rather than silently compared.

---

## 2. Technical Security Guardrails

### 2.1 Storage & Document Isolation
- Uploaded files (PDFs, JPEGs, PNGs) are routed directly to private Supabase storage.
- No public bucket URLs are generated.
- Document viewing uses time-limited signed URLs or backend authenticated streaming.

### 2.2 Privilege Isolation & API Key Secrecy
- Client bundles contain zero third-party AI keys (`SARVAM_API_KEY`) and zero database service-role secrets.
- All external AI processing and database write operations are handled exclusively by the FastAPI backend.

### 2.3 Row Level Security (RLS) & Tenant Isolation
- Every database table incorporates strict PostgreSQL RLS policies where `auth.uid() = user_id`.
- Changing identifiers in client payloads cannot access other patients' medical records.

### 2.4 Protection Against Prompt Injection & Document Exploitation
- Extracted medical text is treated strictly as structured data payloads, never as system instructions or executable prompts.
- All candidate values pass through Pydantic strict schemas before persistence.

### 2.5 Privacy-Preserving Audit Logging
- User interactions, document uploads, reviews, and linking events are logged with actor IDs and outcomes.
- Sensitive diagnostic text and credentials are excluded from audit records.
