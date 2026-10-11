-- AI-Powered Personal Health Copilot
-- Synthetic Demonstration Dataset (Fully De-identified / Fictional)
-- WARNING: All patient names, clinic names, and IDs in this file are completely synthetic.

-- 1. Synthetic Patient
INSERT INTO patients (id, user_id, full_name, date_of_birth, gender, blood_group, contact_phone, email, emergency_contact, preferred_language)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'Ananya Sharma',
    '1988-06-14',
    'female',
    'B+',
    '+91-98765-43210',
    'ananya.sharma@example.internal',
    '+91-98765-12345 (Spouse)',
    'en'
) ON CONFLICT (id) DO NOTHING;

-- 2. Organizations & Practitioners
INSERT INTO organizations (id, name, organization_type, external_identifier)
VALUES
    ('10000000-0000-0000-0000-000000000001', 'Metro Diagnostics & Labs, Chennai', 'laboratory', 'LAB-CH-042'),
    ('10000000-0000-0000-0000-000000000002', 'Cauvery Multi-Specialty Clinic', 'clinic', 'CLINIC-CAU-108')
ON CONFLICT (id) DO NOTHING;

INSERT INTO practitioners (id, name, practitioner_type, external_identifier)
VALUES
    ('20000000-0000-0000-0000-000000000001', 'Dr. R. Sundaram, MD (Gen Med)', 'Physician', 'MCI-TN-45892'),
    ('20000000-0000-0000-0000-000000000002', 'Dr. Meera Krishnan, MD (Pathology)', 'Pathologist', 'MCI-TN-31204')
ON CONFLICT (id) DO NOTHING;

-- 3. Synthetic Documents
INSERT INTO documents (id, patient_id, storage_path, original_filename, mime_type, file_size_bytes, document_type, document_date, processing_status)
VALUES
    (
        '30000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000001',
        'patient_001/docs/lipid_glucose_panel_2026.pdf',
        'lipid_glucose_panel_2026.pdf',
        'application/pdf',
        245890,
        'lab_report',
        '2026-09-15',
        'completed'
    ),
    (
        '30000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000001',
        'patient_001/docs/doctor_prescription_sep2026.jpg',
        'doctor_prescription_sep2026.jpg',
        'image/jpeg',
        524100,
        'prescription',
        '2026-09-18',
        'completed'
    ),
    (
        '30000000-0000-0000-0000-000000000003',
        '00000000-0000-0000-0000-000000000001',
        'patient_001/docs/cbc_baseline_2026.pdf',
        'cbc_baseline_2026.pdf',
        'application/pdf',
        198400,
        'lab_report',
        '2026-03-10',
        'completed'
    )
ON CONFLICT (id) DO NOTHING;

-- 4. Health Records (FHIR R4 Normalized)
INSERT INTO health_records (id, patient_id, document_id, resource_type, resource_version, normalized_resource, review_status, recorded_at)
VALUES
    (
        '40000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000001',
        'DiagnosticReport',
        '4.0.1',
        '{"resourceType": "DiagnosticReport", "status": "final", "code": {"coding": [{"system": "http://loinc.org", "code": "24331-1", "display": "Lipid & Fasting Glucose Panel"}]}, "issued": "2026-09-15T09:30:00Z"}'::jsonb,
        'confirmed',
        '2026-09-15T09:30:00Z'
    ),
    (
        '40000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000002',
        'MedicationRequest',
        '4.0.1',
        '{"resourceType": "MedicationRequest", "status": "active", "intent": "order", "authoredOn": "2026-09-18"}'::jsonb,
        'confirmed',
        '2026-09-18T11:00:00Z'
    )
ON CONFLICT (id) DO NOTHING;

-- 5. Observations (Lab Values with Ranges and Abnormal Flags)
INSERT INTO observations (id, patient_id, document_id, health_record_id, code, display_name, value_numeric, unit, reference_low, reference_high, source_abnormal_flag, effective_at, validation_status)
VALUES
    -- Sep 2026 Panel
    ('50000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', '1558-6', 'Fasting Blood Glucose', 138, 'mg/dL', 70, 99, 'H', '2026-09-15T08:00:00Z', 'validated'),
    ('50000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', '4548-4', 'HbA1c', 7.4, '%', 4.0, 5.6, 'H', '2026-09-15T08:00:00Z', 'validated'),
    ('50000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', '2093-3', 'Total Cholesterol', 228, 'mg/dL', 125, 200, 'H', '2026-09-15T08:00:00Z', 'validated'),
    ('50000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', '2085-9', 'HDL Cholesterol', 46, 'mg/dL', 40, 60, 'NORMAL', '2026-09-15T08:00:00Z', 'validated'),
    ('50000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', '13457-7', 'LDL Cholesterol', 142, 'mg/dL', 0, 100, 'H', '2026-09-15T08:00:00Z', 'validated'),
    -- Baseline Mar 2026 Panel for Trend Comparison
    ('50000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000001', '1558-6', 'Fasting Blood Glucose', 114, 'mg/dL', 70, 99, 'H', '2026-03-10T08:00:00Z', 'validated'),
    ('50000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000001', '4548-4', 'HbA1c', 6.6, '%', 4.0, 5.6, 'H', '2026-03-10T08:00:00Z', 'validated'),
    ('50000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000001', '2093-3', 'Total Cholesterol', 210, 'mg/dL', 125, 200, 'H', '2026-03-10T08:00:00Z', 'validated')
ON CONFLICT (id) DO NOTHING;

-- 6. Medications (Prescribed vs Confirmed Active Intake)
INSERT INTO medications (id, patient_id, document_id, medication_name, generic_name, strength, dose_instructions, route, frequency, duration, prescription_date, medication_status, review_status)
VALUES
    (
        '60000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000002',
        'Glycomet 500 SR',
        'Metformin Hydrochloride',
        '500 mg',
        '1 tablet with dinner',
        'oral',
        'Once daily',
        '90 days',
        '2026-09-18',
        'active',
        'confirmed'
    ),
    (
        '60000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000002',
        'Telma 40',
        'Telmisartan',
        '40 mg',
        '1 tablet in the morning after breakfast',
        'oral',
        'Once daily',
        '90 days',
        '2026-09-18',
        'active',
        'confirmed'
    ),
    (
        '60000000-0000-0000-0000-000000000003',
        '00000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000002',
        'Atorva 10',
        'Atorvastatin Calcium',
        '10 mg',
        '1 tablet at bedtime',
        'oral',
        'Once daily at night',
        '90 days',
        '2026-09-18',
        'prescribed',
        'confirmed'
    )
ON CONFLICT (id) DO NOTHING;

-- 7. Encounters
INSERT INTO encounters (id, patient_id, document_id, organization_id, practitioner_id, encounter_type, start_at, end_at, summary)
VALUES
    (
        '70000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000002',
        '10000000-0000-0000-0000-000000000002',
        '20000000-0000-0000-0000-000000000001',
        'outpatient',
        '2026-09-18T10:30:00Z',
        '2026-09-18T11:00:00Z',
        'Routine follow-up for blood glucose and blood pressure review. Advised lifestyle modifications and updated pharmacotherapy.'
    )
ON CONFLICT (id) DO NOTHING;

-- 8. Document Summaries (English and Tamil)
INSERT INTO document_summaries (id, document_id, language, overview, key_findings, abnormal_explanations, questions_for_doctor, limitations, safety_disclaimer)
VALUES
    (
        '80000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000001',
        'en',
        'This laboratory report from Metro Diagnostics dated 15 Sep 2026 details your Fasting Blood Glucose, HbA1c, and Lipid Panel measurements.',
        '["Fasting Blood Glucose is recorded at 138 mg/dL (Reference: 70 - 99 mg/dL).", "HbA1c is recorded at 7.4% (Reference: 4.0 - 5.6%).", "Total Cholesterol is 228 mg/dL and LDL is 142 mg/dL, both elevated above standard laboratory cutoffs.", "HDL Cholesterol is 46 mg/dL, within the desirable range."]'::jsonb,
        '[{"test_name": "Fasting Blood Glucose", "value": "138 mg/dL", "reference": "70 - 99 mg/dL", "status": "Above Reference Range", "plain_explanation": "Blood sugar after overnight fasting. Elevated levels indicate that insulin handling may need review with your clinician."}, {"test_name": "HbA1c", "value": "7.4%", "reference": "4.0 - 5.6%", "status": "Above Reference Range", "plain_explanation": "Reflects average blood sugar control over the past 2 to 3 months."}, {"test_name": "LDL Cholesterol", "value": "142 mg/dL", "reference": "< 100 mg/dL", "status": "Above Reference Range", "plain_explanation": "Often referred to as low-density lipoprotein; elevated levels are considered in cardiovascular risk assessments."}]'::jsonb,
        '["Should my diabetes medication be adjusted based on the current HbA1c of 7.4%?", "Do I need dietary changes or medication for elevated LDL cholesterol (142 mg/dL)?", "When should I repeat these blood tests?"]'::jsonb,
        'This summary is based solely on the values printed in the provided laboratory report. Clinical diagnosis requires comprehensive medical evaluation.',
        'INFORMATIONAL ASSISTANCE ONLY: This tool is not a doctor, diagnostic system, or emergency service. Never alter prescription medications without consulting your healthcare provider.'
    ),
    (
        '80000000-0000-0000-0000-000000000002',
        '30000000-0000-0000-0000-000000000001',
        'ta',
        'இது 15 செப்டம்பர் 2026 அன்று மெட்ரோ டயக்னாஸ்டிக்ஸ் ஆய்வகத்தால் வழங்கப்பட்ட உண்ணாநிலை இரத்த சர்க்கரை, HbA1c மற்றும் கொழுப்பு அளவுகளின் பரிசோதனை அறிக்கை.',
        '["உண்ணாநிலை இரத்த சர்க்கரை அளவு 138 mg/dL ஆக பதிவாகியுள்ளது (இயல்பு வரம்பு: 70 - 99 mg/dL).", "HbA1c அளவு 7.4% ஆக உள்ளது (இயல்பு வரம்பு: 4.0 - 5.6%).", "மொத்த கொலஸ்ட்ரால் 228 mg/dL மற்றும் LDL கொலஸ்ட்ரால் 142 mg/dL ஆக இயல்பு வரம்பை விட அதிகமாக உள்ளன.", "HDL கொலஸ்ட்ரால் 46 mg/dL ஆக சாதாரண வரம்பில் உள்ளது."]'::jsonb,
        '[{"test_name": "Fasting Blood Glucose", "value": "138 mg/dL", "reference": "70 - 99 mg/dL", "status": "இயல்பு வரம்பை விட அதிகம்", "plain_explanation": "இரவு உணவுக்குப் பிறகு காலையில் எடுக்கப்படும் இரத்த சர்க்கரை அளவு. இது அதிகரித்திருப்பது மருத்துவ ஆலோசனையை பரிந்துரைக்கிறது."}, {"test_name": "HbA1c", "value": "7.4%", "reference": "4.0 - 5.6%", "status": "இயல்பு வரம்பை விட அதிகம்", "plain_explanation": "கடந்த 2 முதல் 3 மாதங்களின் சராசரி இரத்த சர்க்கரை அளவைக் குறிக்கிறது."}, {"test_name": "LDL Cholesterol", "value": "142 mg/dL", "reference": "< 100 mg/dL", "status": "இயல்பு வரம்பை விட அதிகம்", "plain_explanation": "இரத்தக் குழாய்களில் படியக்கூடிய கெட்ட கொழுப்பு வகையாகும்."}]'::jsonb,
        '["எனது தற்போதைய HbA1c 7.4% அடிப்படையில் சர்க்கரை நோய் மருந்துகளை மாற்ற வேண்டுமா?", "அதிகரித்துள்ள LDL கொலஸ்ட்ராலுக்கு (142 mg/dL) உணவு முறை மாற்றம் அல்லது புதிய மருந்து தேவையா?", "அடுத்த பரிசோதனையை எப்போது மேற்கொள்ள வேண்டும்?"]'::jsonb,
        'இந்த விளக்கம் வழங்கப்பட்ட ஆய்வக அறிக்கையில் உள்ள தகவல்களை மட்டுமே அடிப்படையாகக் கொண்டது.',
        'தகவல் உதவி மட்டுமே: இந்த செயலி மருத்துவரோ அல்லது அவசர சிகிச்சை முறையோ அல்ல. உங்கள் மருத்துவரை கலந்தாலோசிக்காமல் மருந்துகளில் எந்த மாற்றமும் செய்யாதீர்கள்.'
    )
ON CONFLICT (document_id, language) DO NOTHING;

-- 9. Mock ABHA Link
INSERT INTO abha_links (id, patient_id, provider, environment, external_reference, status, verification_method, verified_at)
VALUES (
    '90000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'mock',
    'sandbox',
    'MOCK-ABHA-0001',
    'linked',
    'simulated_otp',
    '2026-09-20T10:00:00Z'
) ON CONFLICT (id) DO NOTHING;
