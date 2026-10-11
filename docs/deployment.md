# AI-Powered Personal Health Copilot - Deployment & Operations Guide

## 1. Overview
The **AI-Powered Personal Health Copilot** is designed for modern cloud containerized or serverless hosting:
- **Frontend**: Vite SPA hosted on Vercel, Netlify, or AWS S3 + CloudFront.
- **Backend**: FastAPI ASGI service hosted on Render, Railway, AWS ECS/Fargate, or Google Cloud Run.
- **Database & Storage**: Managed PostgreSQL and Private Object Storage on Supabase.
- **AI & Indian Language Engines**: Sarvam AI Document Intelligence & Mayura Translation API.

---

## 2. Local Installation & Development Execution

### Prerequisites
- Python 3.10+ (tested on Python 3.11.9)
- Node.js 18+ (tested on Node.js v24.11.1, npm 11.6.2)
- Git

### Backend Setup
```bash
# 1. Initialize Python virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Copy environment configuration
cp .env.example .env

# 5. Run test suite
pytest backend/tests/ -v

# 6. Launch FastAPI server
uvicorn app.main:app --app-dir backend --reload --port 8000
```
- Interactive Swagger documentation: `http://localhost:8000/docs`
- ReDoc specification: `http://localhost:8000/redoc`

### Frontend Setup
```bash
# 1. Navigate to frontend folder
cd frontend

# 2. Install Node dependencies
npm install --legacy-peer-deps

# 3. Start development server
npm run dev -- --host 127.0.0.1 --port 5173
```
- Application Portal: `http://localhost:5173/`

---

## 3. Production Deployment Guide

### 3.1 Supabase Database & Private Storage
1. Create a project at [supabase.com](https://supabase.com).
2. Open the **SQL Editor** in the Supabase Dashboard.
3. Run the schema migration script:
   [supabase/migrations/20261011_initial_schema.sql](file:///c:/Users/abila/OneDrive/Desktop/ABDM/supabase/migrations/20261011_initial_schema.sql)
4. (Optional) Run the synthetic demonstration seed:
   [supabase/seed.sql](file:///c:/Users/abila/OneDrive/Desktop/ABDM/supabase/seed.sql)
5. Create a **Private Storage Bucket** named `medical-documents-private`:
   - Disable public access.
   - Attach RLS storage policy so only authenticated users with matching `patient_id` can read objects.

### 3.2 FastAPI Backend (Render / Cloud Run)
1. Set the build and start commands:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000`
2. Configure Environment Variables in the hosting dashboard:
   - `ENVIRONMENT=production`
   - `CORS_ORIGINS=https://your-frontend-domain.com`
   - `SUPABASE_URL=https://your-project.supabase.co`
   - `SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key`
   - `SARVAM_PROVIDER_MODE=live` (when Sarvam key is provisioned)
   - `SARVAM_API_KEY=your-sarvam-api-key`
   - `ABHA_PROVIDER=mock`

### 3.3 Frontend (Vercel / Netlify)
1. Connect the GitHub repository.
2. Root directory: `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Set environment variable:
   - `VITE_API_URL=https://your-backend-api-domain.com`

---

## 4. Troubleshooting & FAQ

### Issue: Port 8000 already in use
**Symptom**: `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`  
**Solution**:
```powershell
Get-NetTCPConnection -LocalPort 8000 | Stop-Process -Id {$_.OwningProcess} -Force
```

### Issue: Sarvam API Key missing in production
**Symptom**: System fails to process live OCR requests.  
**Solution**: The backend automatically falls back to `MockOCRProvider` when `SARVAM_PROVIDER_MODE=mock`. If live extraction is desired, verify `SARVAM_API_KEY` in `.env` and set `SARVAM_PROVIDER_MODE=live`.

### Issue: ABHA linking in mock mode
**Behavior**: Mock mode accepts fictional identifiers (`MOCK-ABHA-XXXX`) and verifies with OTP `123456`. It prominently displays a simulated indicator so evaluators can test the flow without government credentials.
