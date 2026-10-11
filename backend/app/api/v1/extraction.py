from fastapi import APIRouter, HTTPException
from uuid import UUID
from datetime import datetime
from app.repositories.store import store
from app.schemas.extraction import (
    ExtractionResultResponse, ExtractionUpdateRequest, ExtractionConfirmRequest
)
from app.services.document_processor import DocumentProcessorService

router = APIRouter(prefix="/documents", tags=["Extraction Review"])

@router.get("/{document_id}/extraction", response_model=ExtractionResultResponse)
async def get_candidate_extraction(document_id: UUID):
    ext = store.extractions.get(document_id)
    if not ext:
        raise HTTPException(status_code=404, detail="No extraction found for this document.")
    return ext

@router.patch("/{document_id}/extraction", response_model=ExtractionResultResponse)
@router.put("/{document_id}/extraction", response_model=ExtractionResultResponse)
async def update_candidate_extraction(document_id: UUID, req: ExtractionUpdateRequest):
    ext = store.extractions.get(document_id)
    if not ext:
        raise HTTPException(status_code=404, detail="No extraction found for this document.")
    
    ext["structured_candidate_data"] = req.structured_candidate_data.model_dump()
    if req.review_status:
        ext["review_status"] = req.review_status
    ext["updated_at"] = datetime.now()
    store.extractions[document_id] = ext
    return ext

@router.post("/{document_id}/confirm")
async def confirm_extraction_and_promote(document_id: UUID, req: ExtractionConfirmRequest):
    res = await DocumentProcessorService.confirm_extraction(
        document_id,
        confirm_all=req.confirm_all,
        active_meds=req.active_medications
    )
    return res
