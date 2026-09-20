from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.question import Question
from app.models.answer import Answer, AnswerStatus
from app.schemas.question import AnswerResponse
from app.services.security import get_current_user

router = APIRouter()


@router.get("/{question_id}/answer")
def get_question_answer(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check question ownership
    question = db.query(Question).join(Document, Question.document_id == Document.id).filter(
        Question.id == question_id,
        Document.user_id == current_user.id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )

    # Fetch answer record
    ans = db.query(Answer).filter(Answer.question_id == question_id).first()

    if not ans or ans.status != AnswerStatus.MATCHED.value or not ans.match_confidence:
        return {
            "question_id": question_id,
            "status": "unmatched",
            "message": "no confident match found",
            "match_confidence": None,
            "answer_text": None
        }

    return AnswerResponse.model_validate(ans)
