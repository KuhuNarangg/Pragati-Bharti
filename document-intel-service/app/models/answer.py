from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class AnswerStatus(str, enum.Enum):
    MATCHED = "matched"
    UNMATCHED = "unmatched"


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    answer_text = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    match_confidence = Column(Float, nullable=True)
    status = Column(String, default=AnswerStatus.UNMATCHED.value, nullable=False)

    question = relationship("Question", back_populates="answers")
