from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class Memory(Base):
    """Memory model for episodic and semantic memory"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    memory_type = Column(String, default="episodic")  # episodic, semantic, procedural
    importance = Column(Integer, default=5)  # 1-10 scale
    tags = Column(String)  # Comma-separated tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memories")