# AI-Powered Personal Health Copilot - Repeatable Demonstration Script

## 1. Overview & Setup
This script guides evaluators through a complete, end-to-end repeatable demonstration of the **AI-Powered Personal Health Copilot** created for the Altrix Labs Innovation Challenge.

- **Frontend URL**: `http://localhost:5173/`
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`
- **Test Credentials**: Automatic instant session for synthetic demo patient **Ananya Sharma** (38/F, B+ Positive).

---

## 2. Step-by-Step Demonstration Walkthrough

### Step 1: Portal Overview & Baseline Health State
1. Open `http://localhost:5173/` in your browser.
2. Observe the patient header:
   - Patient Profile: **Ananya Sharma** (38/F)
   - Blood Group: **B+**
   - Active ABHA Status: Connected (`MOCK-ABHA-0001`)
   - Informational Safety Banner emphasizing non-diagnostic healthcare assistance.
3. Review the KPI Cards:
   - Total Documents (3 seeded baseline documents)
   - Extractions verified (0 pending reviews)
   - Active Medications (2 active drugs: Metformin, Telmisartan)
   - ABHA Connection (Simulated sandbox linked)
4. Inspect the **Reported Laboratory Highlights** card showing Fasting Blood Glucose (138 mg/dL [H]), HbA1c (7.4% [H]), and Total Cholesterol (228 mg/dL [H]) compared against printed lab reference intervals.

---

### Step 2: Medical Document Upload & Real-Time OCR Intelligence
1. Click the **Documents** tab (or the top **Upload Document** button).
2. Inspect the drag-and-drop upload zone supporting PDF, JPG, JPEG, and PNG (up to 15MB).
3. Upload a sample medical document (e.g., `new_lipid_panel.pdf` or any sample PDF/image).
4. Notice the real-time processing indicator:
   - File is securely validated by MIME type and size.
   - Dispatched to the OCR pipeline (`SarvamOCRProvider` / high-fidelity mock adapter).
   - Document status immediately updates to **Awaiting Review** with an amber alert badge.

---

### Step 3: Human-in-the-Loop Extraction Verification & Correction
1. Click the **Review Extractions** tab.
2. Observe the candidate verification workspace:
   - Document picker lets you toggle between uploaded files.
   - Click **Inspect Raw OCR** to inspect the source text provenance extracted from the document.
   - Review candidate laboratory biomarkers (Test Name, Numeric Value, Unit, Reference Interval Low/High, Abnormal Flag).
   - Edit any field (e.g. adjust Fasting Blood Glucose to `140 mg/dL` or update unit).
   - Under **Extracted Prescriptions**, review drug brand name, salt, strength, frequency, and duration.
   - Toggle the **Currently Taking** button to distinguish between prescribed drugs and confirmed active intake.
3. Click **Confirm & Save Records**.
4. The system validates the schemas, updates status to **Completed**, and promotes approved candidate records into the longitudinal health timeline.

---

### Step 4: Evidence-Grounded Plain-Language AI Health Summary
1. Click the **AI Summary** tab.
2. Select the reviewed document.
3. Inspect the English summary:
   - **Document Overview**: Clear context on reporting laboratory and test panel.
   - **Important Findings**: Plain-language breakdown of key readings strictly grounded in source text.
   - **Values Outside Reference Range**: Contextual educational explanations of elevated Glucose and HbA1c based on laboratory cutoffs (strictly non-alarmist, non-diagnostic).
   - **Questions for Your Doctor**: Neutral questions to help the patient prepare for clinical consultation.
   - **Healthcare Safety & Scope**: Explicit statement that the assistant does not diagnose or prescribe.
4. **Bilingual Tamil Switch**: Click the **தமிழ் (Tamil)** button in the header.
   - Observe the Tamil translation powered by the Sarvam translation adapter.
   - Verify that all numerical values (`138 mg/dL`, `7.4%`, `228 mg/dL`) and medical entities (`Fasting Blood Glucose`, `HbA1c`, `LDL Cholesterol`) are preserved without corruption.

---

### Step 5: Longitudinal Trend Analysis & Chronological Timeline
1. Click the **Timeline & Trends** tab.
2. In the **Longitudinal Biomarker Analysis** chart:
   - Select **Fasting Blood Glucose**: Observe historical trajectory comparing Mar 2026 baseline (114 mg/dL) against Sep 2026 follow-up (138 mg/dL).
   - Select **HbA1c**: Observe change from 6.6% to 7.4%.
   - Select **Total Cholesterol**: Observe trajectory from 210 mg/dL to 228 mg/dL.
   - Hover over chart data points to see tooltips displaying exact dates, units, and laboratory reference ranges.
3. Scroll to the **Chronological Health Timeline**:
   - Filter events by **Diagnostic**, **Medication**, or **Integration**.
   - See dated entries linking directly to source documents.

---

### Step 6: Medication Regimen & Active Intake Control
1. Click the **Medications** tab.
2. Review the table of prescriptions:
   - **Glycomet 500 SR** (Metformin 500 mg) — Active
   - **Telma 40** (Telmisartan 40 mg) — Active
   - **Atorva 10** (Atorvastatin 10 mg) — Prescribed / Historical
3. Filter by **Active** vs **Historical**.
4. Click **Confirm Active** on Atorva 10 to simulate the patient confirming they are actively taking this medication; observe instant persistence and counter updates.

---

### Step 7: ABDM / ABHA Sandbox Verification Workflow
1. Click the **ABHA Sandbox** tab.
2. Observe current simulated connection (`MOCK-ABHA-0001`).
3. Click **Disconnect Link** to simulate unlinking.
4. Re-link the mock account:
   - Enter mock identifier: `MOCK-ABHA-0002`
   - Click **Link Mock ABHA**
   - In the simulated OTP dialog, enter `123456`
   - Click **Confirm & Link**
5. Observe the verified timestamp, environment status (`sandbox`), and ABDM Gateway Roadmap detailing Milestones M1, M2, and M3.
