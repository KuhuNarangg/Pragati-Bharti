from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


class QuestionResponse(BaseModel):
    id: int
    document_id: int
    question_number: Optional[str] = None
    question_text: str
    question_type: str
    options: Optional[List[Any]] = None
    source_pages: Optional[List[int]] = None
    confidence: float
    extraction_status: str
    image_refs: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnswerResponse(BaseModel):
    id: int
    question_id: int
    answer_text: str
    source: Optional[str] = None
    match_confidence: Optional[float] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class ReviewFlagResponse(BaseModel):
    id: int
    question_id: int
    reason: str
    created_at: datetime
    resolved: bool
    question: Optional[QuestionResponse] = None

    model_config = ConfigDict(from_attributes=True)
