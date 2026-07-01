from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Enum, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class MessageRole(str, enum.Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base):
    """Message model for conversation history"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(MessageRole), default=MessageRole.USER)
    content = Column(Text, nullable=False)
    metadata_json = Column(String)  # JSON string for additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")