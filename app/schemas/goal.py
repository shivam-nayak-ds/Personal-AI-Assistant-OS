from pydantic import BaseModel, Field, PositiveInt
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GoalStatus(str, Enum):
    """Goal status enumeration"""
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class GoalBase(BaseModel):
    """Base goal schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_date: Optional[datetime] = None


class GoalCreate(GoalBase):
    """Schema for goal creation"""
    status: Optional[GoalStatus] = GoalStatus.ACTIVE
    priority: Optional[str] = Field("medium", min_length=4, max_length=10)


class GoalUpdate(BaseModel):
    """Schema for goal update"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[GoalStatus] = None
    target_date: Optional[datetime] = None
    priority: Optional[str] = Field(None, min_length=4, max_length=10)


class GoalResponse(GoalBase):
    """Schema for goal response"""
    id: int
    user_id: int
    status: GoalStatus
    priority: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GoalWithTasks(GoalResponse):
    """Schema for goal with tasks"""
    tasks: List["TaskResponse"] = []


class TaskPriority(str, Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Schema for task creation"""
    goal_id: Optional[PositiveInt] = None
    user_id: PositiveInt
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM


class TaskUpdate(BaseModel):
    """Schema for task update"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    goal_id: Optional[int] = None
    user_id: PositiveInt
    completed: bool
    priority: Optional[TaskPriority] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskWithDetails(TaskResponse):
    """Schema for task with additional details"""
    goal_title: Optional[str] = None
    goal_status: Optional[str] = None