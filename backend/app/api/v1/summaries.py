from fastapi import APIRouter, HTTPException, Query
from uuid import UUID
from app.repositories.store import store
from app.schemas.summary import DocumentSummaryResponse, TranslationRequest
from app.services.summary_service import generate_evidence_grounded_summary, translate_summary_to_tamil

router = APIRouter(prefix="/documents", tags=["AI Summaries"])

@router.get("/{document_id}/summary", response_model=DocumentSummaryResponse)
async def get_document_summary(document_id: UUID, lang: str = Query("en")):
    key = f"{document_id}_{lang}"
    summary = store.summaries.get(key)
    
    # If Tamil requested but not present, generate from English
    if not summary and lang == "ta":
        en_summary = store.summaries.get(f"{document_id}_en")
        if en_summary:
            summary = await translate_summary_to_tamil(document_id, en_summary)
            
    if not summary:
        # Fallback to English if available
        summary = store.summaries.get(f"{document_id}_en")
        
    if not summary:
        # Attempt generation if extraction exists
        ext = store.extractions.get(document_id)
        if ext:
            summary = await generate_evidence_grounded_summary(document_id, ext["structured_candidate_data"])
            if lang == "ta":
                summary = store.summaries.get(f"{document_id}_ta")
                
    if not summary:
        raise HTTPException(status_code=404, detail="No summary available for this document.")
    return summary

@router.post("/{document_id}/summary", response_model=DocumentSummaryResponse)
async def refresh_document_summary(document_id: UUID):
    ext = store.extractions.get(document_id)
    if not ext:
        raise HTTPException(status_code=404, detail="Extraction record required to generate summary.")
    summary = await generate_evidence_grounded_summary(document_id, ext["structured_candidate_data"])
    return summary

@router.post("/{document_id}/summary/translate", response_model=DocumentSummaryResponse)
async def translate_summary(document_id: UUID, req: TranslationRequest):
    en_summary = store.summaries.get(f"{document_id}_en")
    if not en_summary:
        raise HTTPException(status_code=404, detail="Base English summary not found.")
    ta_summary = await translate_summary_to_tamil(document_id, en_summary)
    return ta_summary
