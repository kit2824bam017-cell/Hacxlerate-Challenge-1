# AI-Powered Personal Health Copilot

> **Altrix Labs Innovation Challenge — Prototype Implementation**  
> An enterprise-grade, privacy-first personal health copilot transforming fragmented Indian medical documents (prescriptions, laboratory reports, discharge summaries) into structured, FHIR-compatible digital records, evidence-grounded bilingual summaries (English & Tamil), longitudinal trend visualizations, and simulated ABDM/ABHA integration.

---

## 1. Key Capabilities

- **Medical Document Intelligence & OCR**: Seamless upload of PDF, JPG, and PNG documents with extraction of patient details, laboratory parameters (values, units, reference intervals, abnormal flags), and prescribed medications (brand name, active salt, strength, frequency).
- **Human-in-the-Loop Extraction Review**: Verification interface allowing patients to review candidate extracted data, correct values or dosage instructions, and promote approved records into their confirmed health history.
- **Evidence-Grounded AI Summaries**: Clear, plain-language summaries strictly grounded in source documents, with contextual explanations of abnormal laboratory flags and tailored questions for clinicians.
- **Bilingual Indian Language Localization**: English and Tamil support with translation safety validation to preserve numerical values, units, and drug names.
- **Longitudinal Health Analysis & Trends**: Interactive chronological timeline and Recharts visualizations comparing identical lab parameters across historical tests.
- **ABDM / ABHA Ready Architecture**: Pluggable provider abstraction with an explicitly simulated mock workflow (`MOCK-ABHA-0001`) and a documented roadmap to official sandbox integration.

---

## 2. Technology Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, shadcn-admin UI component library, Lucide Icons, Recharts, TanStack Query.
- **Backend**: Python 3.11, FastAPI, Pydantic v2, Uvicorn, httpx, Pytest.
- **Database & Storage**: Supabase PostgreSQL with Row Level Security (RLS) migrations and synthetic de-identified dataset seed.
- **AI & OCR Providers**: Sarvam AI Document Intelligence & Mayura translation adapters with deterministic offline mock fallback.

---

## 3. Quick Start & Local Execution

### Backend Setup
```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/macOS

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Copy environment configuration
cp .env.example .env

# 4. Run automated test suite
pytest backend/tests/ -v

# 5. Start FastAPI server
uvicorn app.main:app --app-dir backend --reload --port 8000
```
Backend API documentation is available at: `http://localhost:8000/docs`

### Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install --legacy-peer-deps

# 3. Start development server
npm run dev
```
Frontend application is accessible at: `http://localhost:5173`

---

## 4. Documentation Directory

- [Architecture & Data Flow](file:///c:/Users/abila/OneDrive/Desktop/ABDM/docs/architecture.md)
- [Database Schema & RLS Policies](file:///c:/Users/abila/OneDrive/Desktop/ABDM/docs/database-schema.md)
- [REST API Specification](file:///c:/Users/abila/OneDrive/Desktop/ABDM/docs/api.md)
- [ABDM / ABHA Integration Roadmap](file:///c:/Users/abila/OneDrive/Desktop/ABDM/docs/abdm-integration-plan.md)
- [Healthcare Safety & Security](file:///c:/Users/abila/OneDrive/Desktop/ABDM/docs/security.md)
- [AI & OCR Evaluation Methodology](file:///c:/Users/abila/OneDrive/Desktop/ABDM/docs/ai-evaluation.md)
