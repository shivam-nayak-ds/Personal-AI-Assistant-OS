from sqlalchemy import Column, String, Integer, DateTime, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships — all models have back_populates="user" on their side
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", foreign_keys="[Review.user_id]", cascade="all, delete-orphan")
    # Notification (in user_profile.py) has no back_populates — use backref
    notifications = relationship("Notification", backref="user_obj", cascade="all, delete-orphan")