from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Float, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class ReviewStatus(str, enum.Enum):
    """Review status enumeration"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewType(str, enum.Enum):
    """Review type enumeration"""
    GOAL = "goal"
    TASK = "task"
    MEMORY = "memory"
    DOCUMENT = "document"


class Review(Base):
    """Review model for content moderation and validation"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_type = Column(Enum(ReviewType), default=ReviewType.MEMORY)
    content_id = Column(Integer)
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    comments = Column(Text)
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])