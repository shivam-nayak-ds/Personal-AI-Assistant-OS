# task.py — Re-exports TaskResponse from goal.py (defined there alongside GoalWithTasks)
# This avoids duplication while keeping imports clean in router files

from app.schemas.goal import (
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskWithDetails,
    TaskPriority,
)

__all__ = [
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskWithDetails",
    "TaskPriority",
]
