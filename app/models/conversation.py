from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Enum, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class ConversationStatus(str, enum.Enum):
    """Conversation status enumeration"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    RESOLVED = "resolved"


class Conversation(Base):
    """Conversation model for chat functionality"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Conversation")
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")