import os
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.document import Document, DocumentStatus, DocumentType
from app.schemas.document import DocumentResponse, DocumentStatusResponse
from app.services.security import get_current_user
from app.services.storage import storage_service
from app.workers.tasks import process_document_task

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form(DocumentType.QUESTION_PAPER.value),
    group_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: PDF, JPG, JPEG, PNG."
        )

    # 2. Read content to check file size
    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )
    
    # Reset file cursor for saving
    await file.seek(0)

    # 3. Create document record in DB
    valid_doc_type = doc_type if doc_type in [e.value for e in DocumentType] else DocumentType.UNKNOWN.value
    doc = Document(
        user_id=current_user.id,
        group_id=group_id,
        filename=file.filename,
        storage_path="",  # Will update after saving
        doc_type=valid_doc_type,
        status=DocumentStatus.PENDING.value,
        page_count=0
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 4. Save file to storage: storage/{user_id}/{document_id}/{filename}
    try:
        saved_path = storage_service.save_document(current_user.id, doc.id, file)
        doc.storage_path = saved_path
        db.commit()
        db.refresh(doc)
    except Exception as e:
        db.delete(doc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save document: {str(e)}"
        )

    # 5. Enqueue background processing task (or process inline if broker unavailable)
    try:
        if settings.ENVIRONMENT == "testing":
            process_document_task(doc.id)
        else:
            process_document_task.delay(doc.id)
    except Exception:
        process_document_task(doc.id)

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "message": "Document uploaded successfully and processing started."
    }


@router.get("", response_model=List[DocumentResponse])
def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Document).filter(Document.user_id == current_user.id).all()


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    return doc


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    
    # Delete from local storage
    if doc.storage_path:
        storage_service.delete_document(doc.storage_path)

    db.delete(doc)
    db.commit()
    return {"message": f"Document {document_id} deleted successfully."}
