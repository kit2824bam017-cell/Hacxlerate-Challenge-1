-- AI-Powered Personal Health Copilot
-- Migration: 20261011_initial_schema.sql
-- Complete Supabase PostgreSQL schema with RLS and FHIR-compatible design

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Patients Table
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    gender TEXT CHECK (gender IN ('male', 'female', 'other', 'unknown')),
    blood_group TEXT,
    contact_phone TEXT,
    email TEXT,
    emergency_contact TEXT,
    preferred_language TEXT DEFAULT 'en',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Medical Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    file_size_bytes BIGINT,
    document_type TEXT CHECK (document_type IN ('prescription', 'lab_report', 'discharge_summary', 'radiology_report', 'other')),
    document_date DATE,
    processing_status TEXT NOT NULL DEFAULT 'uploaded' CHECK (processing_status IN ('uploaded', 'queued', 'processing', 'awaiting_review', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. Extraction Results Table (Provenance & Candidate Pipeline)
CREATE TABLE IF NOT EXISTS extraction_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    raw_ocr_text TEXT,
    structured_candidate_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    extraction_provider TEXT NOT NULL DEFAULT 'sarvam',
    provider_model TEXT,
    validation_status TEXT NOT NULL DEFAULT 'needs_review' CHECK (validation_status IN ('high_confidence', 'needs_review', 'unreadable_or_missing')),
    review_status TEXT NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending', 'in_review', 'approved', 'rejected')),
    processing_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Health Records Table (FHIR R4 Normalized Store)
CREATE TABLE IF NOT EXISTS health_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    resource_type TEXT NOT NULL CHECK (resource_type IN ('Observation', 'DiagnosticReport', 'MedicationRequest', 'Condition', 'Encounter', 'DocumentReference')),
    resource_version TEXT NOT NULL DEFAULT '4.0.1',
    normalized_resource JSONB NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'confirmed' CHECK (review_status IN ('candidate', 'reviewed', 'confirmed')),
    recorded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5. Observations Table (Laboratory & Clinical Values)
CREATE TABLE IF NOT EXISTS observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    health_record_id UUID REFERENCES health_records(id) ON DELETE CASCADE,
    code TEXT,
    display_name TEXT NOT NULL,
    value_numeric NUMERIC,
    value_text TEXT,
    unit TEXT,
    reference_low NUMERIC,
    reference_high NUMERIC,
    source_abnormal_flag TEXT CHECK (source_abnormal_flag IN ('H', 'L', 'CRITICAL', 'NORMAL', NULL)),
    effective_at TIMESTAMPTZ,
    validation_status TEXT NOT NULL DEFAULT 'validated',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6. Medications Table (Prescription & Longitudinal Intake)
CREATE TABLE IF NOT EXISTS medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    medication_name TEXT NOT NULL,
    generic_name TEXT,
    strength TEXT,
    dose_instructions TEXT,
    route TEXT,
    frequency TEXT,
    duration TEXT,
    prescription_date DATE,
    medication_status TEXT NOT NULL DEFAULT 'prescribed' CHECK (medication_status IN ('prescribed', 'active', 'discontinued', 'completed')),
    review_status TEXT NOT NULL DEFAULT 'confirmed' CHECK (review_status IN ('candidate', 'reviewed', 'confirmed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 7. Organizations & Practitioners
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    organization_type TEXT,
    external_identifier TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS practitioners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    practitioner_type TEXT,
    external_identifier TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 8. Encounters Table
CREATE TABLE IF NOT EXISTS encounters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    practitioner_id UUID REFERENCES practitioners(id) ON DELETE SET NULL,
    encounter_type TEXT CHECK (encounter_type IN ('outpatient', 'inpatient', 'emergency', 'teleconsult')),
    start_at TIMESTAMPTZ,
    end_at TIMESTAMPTZ,
    summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 9. ABHA Links Table (Simulated Mock & Sandbox Integration Ready)
CREATE TABLE IF NOT EXISTS abha_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    provider TEXT NOT NULL DEFAULT 'mock',
    environment TEXT NOT NULL DEFAULT 'sandbox',
    external_reference TEXT NOT NULL, -- e.g. MOCK-ABHA-0001
    status TEXT NOT NULL DEFAULT 'linked' CHECK (status IN ('linked', 'unlinked', 'revoked')),
    verification_method TEXT DEFAULT 'simulated_otp',
    verified_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 10. Consent Records Table
CREATE TABLE IF NOT EXISTS consent_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    purpose TEXT NOT NULL,
    data_scope JSONB NOT NULL DEFAULT '[]'::jsonb,
    consent_status TEXT NOT NULL DEFAULT 'granted' CHECK (consent_status IN ('granted', 'revoked', 'expired')),
    granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    external_reference TEXT
);

-- 11. Audit Logs Table (Privacy-Preserving Audit Trail)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID NOT NULL,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id UUID,
    outcome TEXT NOT NULL CHECK (outcome IN ('success', 'failure')),
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 12. Document Summaries Table (Bilingual and Grounded)
CREATE TABLE IF NOT EXISTS document_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    language TEXT NOT NULL DEFAULT 'en',
    overview TEXT NOT NULL,
    key_findings JSONB NOT NULL DEFAULT '[]'::jsonb,
    abnormal_explanations JSONB NOT NULL DEFAULT '[]'::jsonb,
    questions_for_doctor JSONB NOT NULL DEFAULT '[]'::jsonb,
    limitations TEXT,
    safety_disclaimer TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_doc_lang UNIQUE (document_id, language)
);

-- Indexes for Fast Querying and Timeline Construction
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_patient_id ON documents(patient_id);
CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_observations_patient_id ON observations(patient_id);
CREATE INDEX IF NOT EXISTS idx_observations_effective_at ON observations(effective_at);
CREATE INDEX IF NOT EXISTS idx_observations_display_name ON observations(display_name);
CREATE INDEX IF NOT EXISTS idx_medications_patient_id ON medications(patient_id);
CREATE INDEX IF NOT EXISTS idx_medications_medication_status ON medications(medication_status);
CREATE INDEX IF NOT EXISTS idx_encounters_patient_id ON encounters(patient_id);
CREATE INDEX IF NOT EXISTS idx_health_records_patient_id ON health_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_patient_id ON audit_logs(patient_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Enable Row Level Security (RLS)
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE extraction_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE medications ENABLE ROW LEVEL SECURITY;
ALTER TABLE encounters ENABLE ROW LEVEL SECURITY;
ALTER TABLE abha_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE consent_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_summaries ENABLE ROW LEVEL SECURITY;

-- Standard RLS Policies: Authenticated users access only records matching auth.uid()
CREATE POLICY "Users can access their own patient profile" ON patients
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access their own documents" ON documents
    FOR ALL USING (patient_id IN (SELECT id FROM patients WHERE user_id = auth.uid()));

CREATE POLICY "Users can access their own extraction results" ON extraction_results
    FOR ALL USING (document_id IN (SELECT d.id FROM documents d JOIN patients p ON d.patient_id = p.id WHERE p.user_id = auth.uid()));

CREATE POLICY "Users can access their own health records" ON health_records
    FOR ALL USING (patient_id IN (SELECT id FROM patients WHERE user_id = auth.uid()));

CREATE POLICY "Users can access their own observations" ON observations
    FOR ALL USING (patient_id IN (SELECT id FROM patients WHERE user_id = auth.uid()));

CREATE POLICY "Users can access their own medications" ON medications
    FOR ALL USING (patient_id IN (SELECT id FROM patients WHERE user_id = auth.uid()));

CREATE POLICY "Users can access their own encounters" ON encounters
    FOR ALL USING (patient_id IN (SELECT id FROM patients WHERE user_id = auth.uid()));

CREATE POLICY "Users can access their own abha links" ON abha_links
    FOR ALL USING (patient_id IN (SELECT id FROM patients WHERE user_id = auth.uid()));

CREATE POLICY "Users can access their own consent records" ON consent_records
    FOR ALL USING (patient_id IN (SELECT id FROM patients WHERE user_id = auth.uid()));

CREATE POLICY "Users can access their own audit logs" ON audit_logs
    FOR ALL USING (actor_id = auth.uid() OR patient_id IN (SELECT id FROM patients WHERE user_id = auth.uid()));

CREATE POLICY "Users can access their own summaries" ON document_summaries
    FOR ALL USING (document_id IN (SELECT d.id FROM documents d JOIN patients p ON d.patient_id = p.id WHERE p.user_id = auth.uid()));
