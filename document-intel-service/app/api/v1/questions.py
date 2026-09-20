from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.question import Question
from app.schemas.question import QuestionResponse
from app.services.security import get_current_user

router = APIRouter()


@router.get("", response_model=List[QuestionResponse])
def get_questions(
    document_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Question).join(Document, Question.document_id == Document.id).filter(Document.user_id == current_user.id)
    if document_id:
        query = query.filter(Question.document_id == document_id)
    return query.all()


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).join(Document, Question.document_id == Document.id).filter(
        Question.id == question_id,
        Document.user_id == current_user.id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )
    return question
