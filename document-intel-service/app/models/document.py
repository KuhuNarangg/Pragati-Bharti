from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base


class DocumentType(str, enum.Enum):
    QUESTION_PAPER = "question_paper"
    ANSWER_KEY = "answer_key"
    UNKNOWN = "unknown"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentGroup(Base):
    __tablename__ = "document_groups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="document_groups")
    documents = relationship("Document", back_populates="group")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(Integer, ForeignKey("document_groups.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    doc_type = Column(String, default=DocumentType.UNKNOWN.value, nullable=False)
    status = Column(String, default=DocumentStatus.PENDING.value, nullable=False)
    page_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="documents")
    group = relationship("DocumentGroup", back_populates="documents")
    questions = relationship("Question", back_populates="document", cascade="all, delete-orphan")
