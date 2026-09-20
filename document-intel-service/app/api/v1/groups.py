from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import DocumentGroup, Document
from app.schemas.document import DocumentGroupCreate, DocumentGroupResponse, DocumentResponse
from app.services.security import get_current_user

router = APIRouter()


@router.post("", response_model=DocumentGroupResponse, status_code=status.HTTP_201_CREATED)
def create_document_group(
    group_in: DocumentGroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    group = DocumentGroup(
        user_id=current_user.id,
        name=group_in.name
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.get("/{group_id}")
def get_document_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(DocumentGroup).filter(
        DocumentGroup.id == group_id,
        DocumentGroup.user_id == current_user.id
    ).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document group not found."
        )

    documents = db.query(Document).filter(Document.group_id == group_id).all()
    
    return {
        "id": group.id,
        "name": group.name,
        "created_at": group.created_at,
        "documents": [DocumentResponse.model_validate(doc) for doc in documents]
    }
