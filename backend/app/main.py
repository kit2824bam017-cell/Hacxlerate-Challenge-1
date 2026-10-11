from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api.v1.auth import router as auth_router
from app.api.v1.patient import router as patient_router
from app.api.v1.documents import router as documents_router
from app.api.v1.extraction import router as extraction_router
from app.api.v1.summaries import router as summaries_router
from app.api.v1.records import router as records_router
from app.api.v1.timeline import router as timeline_router
from app.api.v1.abha import router as abha_router

app = FastAPI(
    title="AI-Powered Personal Health Copilot API",
    description=(
        "Enterprise-grade backend API for Altrix Labs Innovation Challenge. "
        "Provides medical document intelligence, Sarvam-powered Indian language OCR & translation, "
        "evidence-grounded health summaries, longitudinal health history, and ABDM/ABHA sandbox readiness."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local Vite dev server and preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(patient_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(extraction_router, prefix="/api/v1")
app.include_router(summaries_router, prefix="/api/v1")
app.include_router(records_router, prefix="/api/v1")
app.include_router(timeline_router, prefix="/api/v1")
app.include_router(abha_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "AI-Powered Personal Health Copilot",
        "version": "1.0.0",
        "sarvam_provider_mode": settings.SARVAM_PROVIDER_MODE,
        "abha_provider": settings.ABHA_PROVIDER
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
