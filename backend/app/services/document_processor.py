import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional
from uuid import UUID
from fastapi import UploadFile, HTTPException

from app.repositories.store import store
from app.providers.ocr import get_ocr_provider
from app.services.summary_service import generate_evidence_grounded_summary

ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "jpeg",
    "image/jpg": "jpg",
    "image/png": "png"
}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

class DocumentProcessorService:
    @staticmethod
    async def upload_document(file: UploadFile, patient_id: UUID) -> Dict[str, Any]:
        # 1. MIME Validation
        content_type = file.content_type or ""
        if content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{content_type}'. Allowed types: PDF, JPG, JPEG, PNG."
            )
        
        file_bytes = await file.read()
        file_size = len(file_bytes)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Uploaded file exceeds the maximum 15MB limit.")

        doc_id = uuid.uuid4()
        storage_path = f"patient_{patient_id}/docs/{doc_id}_{file.filename}"
        
        # Initial document metadata
        doc_record = {
            "id": doc_id,
            "patient_id": patient_id,
            "storage_path": storage_path,
            "original_filename": file.filename or "uploaded_document",
            "mime_type": content_type,
            "file_size_bytes": file_size,
            "document_type": "other",
            "document_date": date.today(),
            "processing_status": "queued",
            "error_message": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        store.documents[doc_id] = doc_record
        store.document_files[doc_id] = file_bytes
        
        # Trigger immediate processing for prototype
        await DocumentProcessorService.process_document(doc_id)
        
        return store.documents[doc_id]

    @staticmethod
    async def process_document(document_id: UUID) -> Dict[str, Any]:
        doc = store.documents.get(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        doc["processing_status"] = "processing"
        doc["updated_at"] = datetime.now()
        
        file_bytes = store.document_files.get(document_id, b"")
        filename = doc["original_filename"]
        mime_type = doc["mime_type"]
        
        try:
            ocr_provider = get_ocr_provider()
            extraction_output = await ocr_provider.extract_text_and_data(file_bytes, filename, mime_type)
            
            candidate_data = extraction_output.get("structured_candidate_data", {})
            raw_ocr = extraction_output.get("raw_ocr_text", "")
            doc_type = candidate_data.get("document_type", "lab_report")
            
            # Update document type
            doc["document_type"] = doc_type
            if candidate_data.get("document_date"):
                try:
                    doc["document_date"] = date.fromisoformat(str(candidate_data["document_date"]))
                except Exception:
                    pass
            
            # Save candidate extraction result
            ext_id = uuid.uuid4()
            store.extractions[document_id] = {
                "id": ext_id,
                "document_id": document_id,
                "raw_ocr_text": raw_ocr,
                "structured_candidate_data": candidate_data,
                "extraction_provider": extraction_output.get("provider", "sarvam"),
                "provider_model": "sarvam-doc-intelligence-v1",
                "validation_status": "needs_review",
                "review_status": "pending",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Mark document as awaiting user review
            doc["processing_status"] = "awaiting_review"
            doc["updated_at"] = datetime.now()
            store.documents[document_id] = doc
            
            # Pre-generate plain-language evidence-grounded summary
            await generate_evidence_grounded_summary(document_id, candidate_data)
            
            return store.extractions[document_id]

        except Exception as e:
            doc["processing_status"] = "failed"
            doc["error_message"] = str(e)
            doc["updated_at"] = datetime.now()
            store.documents[document_id] = doc
            raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

    @staticmethod
    async def confirm_extraction(document_id: UUID, confirm_all: bool, active_meds: list) -> Dict[str, Any]:
        doc = store.documents.get(document_id)
        ext = store.extractions.get(document_id)
        if not doc or not ext:
            raise HTTPException(status_code=404, detail="Document or extraction record not found.")

        candidate = ext["structured_candidate_data"]
        patient_id = doc["patient_id"]
        
        # 1. Promote Candidate Observations into Confirmed Observations
        observations = candidate.get("observations", [])
        for obs in observations:
            obs_id = uuid.uuid4()
            store.observations[obs_id] = {
                "id": obs_id,
                "patient_id": patient_id,
                "document_id": document_id,
                "health_record_id": None,
                "code": None,
                "display_name": obs.get("test_name", "Unknown Test"),
                "value_numeric": obs.get("value_numeric"),
                "value_text": str(obs.get("value_numeric") or ""),
                "unit": obs.get("unit"),
                "reference_low": obs.get("reference_low"),
                "reference_high": obs.get("reference_high"),
                "source_abnormal_flag": obs.get("source_abnormal_flag"),
                "effective_at": datetime.now(),
                "validation_status": "validated",
                "created_at": datetime.now()
            }
            
        # 2. Promote Candidate Medications into Confirmed Medications
        medications = candidate.get("medications", [])
        for med in medications:
            med_id = uuid.uuid4()
            mname = med.get("medication_name", "Unknown Drug")
            is_active = mname in active_meds or any(mname.lower() in str(x).lower() for x in active_meds)
            
            store.medications[med_id] = {
                "id": med_id,
                "patient_id": patient_id,
                "document_id": document_id,
                "medication_name": mname,
                "generic_name": med.get("generic_name"),
                "strength": med.get("strength"),
                "dose_instructions": med.get("dose_instructions"),
                "route": med.get("route", "oral"),
                "frequency": med.get("frequency"),
                "duration": med.get("duration"),
                "prescription_date": date.today(),
                "medication_status": "active" if is_active else "prescribed",
                "review_status": "confirmed",
                "created_at": datetime.now()
            }
            
        ext["review_status"] = "approved"
        ext["validation_status"] = "high_confidence"
        doc["processing_status"] = "completed"
        doc["updated_at"] = datetime.now()
        store.extractions[document_id] = ext
        store.documents[document_id] = doc
        
        return {
            "status": "confirmed",
            "message": "Extracted records successfully verified and integrated into health profile."
        }
