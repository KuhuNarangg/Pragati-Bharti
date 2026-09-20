from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    UNKNOWN = "unknown"


class ExtractionStatus(str, enum.Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    REVIEW_NEEDED = "review_needed"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(String, nullable=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, default=QuestionType.UNKNOWN.value, nullable=False)
    options = Column(JSON, nullable=True)  # Store list of options as JSON
    source_pages = Column(JSON, nullable=True)  # Store list of page numbers [1, 2]
    confidence = Column(Float, default=1.0, nullable=False)
    extraction_status = Column(String, default=ExtractionStatus.SUCCESS.value, nullable=False)
    image_refs = Column(JSON, nullable=True)  # Store image/table refs
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    review_flags = relationship("ReviewFlag", back_populates="question", cascade="all, delete-orphan")
