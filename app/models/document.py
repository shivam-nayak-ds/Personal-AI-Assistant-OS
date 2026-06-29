from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class DocumentStatus(str, enum.Enum):
    """Document status enumeration"""
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"
    ARCHIVED = "archived"


class Document(Base):
    """Document model for RAG and knowledge management"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String)
    file_size = Column(Integer)
    file_type = Column(String)  # pdf, docx, txt, etc.
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    content = Column(Text)
    embedding_model = Column(String, default="text-embedding-3-small")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")