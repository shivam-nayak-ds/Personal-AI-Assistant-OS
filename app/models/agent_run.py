from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class AgentStatus(str, enum.Enum):
    """Agent status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, enum.Enum):
    """Agent type enumeration"""
    PLANNER = "planner"
    RESEARCHER = "researcher"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    REVIEW = "review"
    ORCHESTRATOR = "orchestrator"


class AgentRun(Base):
    """Agent run model for tracking agent executions"""
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_type = Column(Enum(AgentType), default=AgentType.ORCHESTRATOR)
    status = Column(Enum(AgentStatus), default=AgentStatus.PENDING)
    input_data = Column(Text)
    output_data = Column(Text)
    error_message = Column(Text)
    execution_time = Column(Integer)  # in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="agent_runs")