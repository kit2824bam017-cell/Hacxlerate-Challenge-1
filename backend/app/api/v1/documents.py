from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Response, Header
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.repositories.store import store
from app.schemas.document import DocumentResponse, DocumentStatusResponse
from app.services.document_processor import DocumentProcessorService
from app.core.config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("", response_model=DocumentResponse)
async def upload_medical_document(
    file: UploadFile = File(...),
    x_patient_id: Optional[str] = Header(None, alias="X-Patient-Id")
):
    pid_str = x_patient_id if x_patient_id else settings.DEMO_PATIENT_ID
    try:
        patient_id = UUID(pid_str)
    except Exception:
        patient_id = UUID(settings.DEMO_PATIENT_ID)
    doc = await DocumentProcessorService.upload_document(file, patient_id)
    return doc

@router.get("", response_model=List[DocumentResponse])
async def list_medical_documents(
    doc_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    x_patient_id: Optional[str] = Header(None, alias="X-Patient-Id")
):
    pid_str = x_patient_id if x_patient_id else settings.DEMO_PATIENT_ID
    try:
        patient_id = UUID(pid_str)
    except Exception:
        patient_id = UUID(settings.DEMO_PATIENT_ID)
    docs = [d for d in store.documents.values() if d["patient_id"] == patient_id]
    if doc_type:
        docs = [d for d in docs if d.get("document_type") == doc_type]
    if status:
        docs = [d for d in docs if d.get("processing_status") == status]
    # Sort newest first
    docs.sort(key=lambda x: x["created_at"], reverse=True)
    return docs

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_details(document_id: UUID):
    doc = store.documents.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc

@router.get("/{document_id}/file")
async def download_or_preview_document(document_id: UUID):
    doc = store.documents.get(document_id)
    file_bytes = store.document_files.get(document_id)
    if not doc or file_bytes is None:
        raise HTTPException(status_code=404, detail="Document file not found.")
    
    return Response(
        content=file_bytes,
        media_type=doc["mime_type"],
        headers={"Content-Disposition": f'inline; filename="{doc["original_filename"]}"'}
    )

@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(document_id: UUID):
    doc = store.documents.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {
        "id": doc["id"],
        "processing_status": doc["processing_status"],
        "error_message": doc.get("error_message"),
        "updated_at": doc["updated_at"]
    }

@router.post("/{document_id}/process")
async def trigger_document_process(document_id: UUID):
    ext = await DocumentProcessorService.process_document(document_id)
    return {"status": "processing_completed", "extraction_id": str(ext["id"])}

@router.delete("/{document_id}")
async def delete_document(document_id: UUID):
    if document_id not in store.documents:
        raise HTTPException(status_code=404, detail="Document not found.")
    del store.documents[document_id]
    if document_id in store.document_files:
        del store.document_files[document_id]
    if document_id in store.extractions:
        del store.extractions[document_id]
    return {"status": "deleted", "id": str(document_id)}
