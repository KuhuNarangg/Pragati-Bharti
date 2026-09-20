from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.question import Question, ExtractionStatus
from app.models.answer import Answer, AnswerStatus
from app.models.review_flag import ReviewFlag
from app.services.security import get_current_user

router = APIRouter()


@router.get("")
def get_review_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all questions requiring review (low confidence, partial extraction, unmatched answer, or review flags)."""
    
    # 1. Fetch review flags for user's documents
    flags = db.query(ReviewFlag).join(Question, ReviewFlag.question_id == Question.id).join(Document, Question.document_id == Document.id).filter(
        Document.user_id == current_user.id,
        ReviewFlag.resolved == False
    ).all()

    flagged_question_ids = {f.question_id: f.reason for f in flags}

    # 2. Fetch questions with low confidence or non-success extraction status
    review_questions = db.query(Question).join(Document, Question.document_id == Document.id).filter(
        Document.user_id == current_user.id,
        or_(
            Question.id.in_(list(flagged_question_ids.keys()) if flagged_question_ids else [-1]),
            Question.confidence < 0.85,
            Question.extraction_status != ExtractionStatus.SUCCESS.value
        )
    ).all()

    items = []
    for q in review_questions:
        # Check associated answer status
        ans = db.query(Answer).filter(Answer.question_id == q.id).first()
        ans_status = ans.status if ans else "unmatched"

        reasons = []
        if q.id in flagged_question_ids:
            reasons.append(flagged_question_ids[q.id])
        if q.confidence < 0.85:
            reasons.append(f"Low extraction confidence score: {q.confidence}")
        if q.extraction_status != ExtractionStatus.SUCCESS.value:
            reasons.append(f"Extraction status marked as {q.extraction_status}")
        if ans_status == "unmatched":
            reasons.append("No confident answer key match found")

        items.append({
            "question_id": q.id,
            "document_id": q.document_id,
            "question_number": q.question_number,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "confidence": q.confidence,
            "extraction_status": q.extraction_status,
            "source_pages": q.source_pages,
            "answer_status": ans_status,
            "reasons": list(set(reasons))
        })

    return {
        "total_review_items": len(items),
        "items": items
    }
