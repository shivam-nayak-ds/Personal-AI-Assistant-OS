"""
Task Repository for Hermes AI OS

Handles all Task-related database queries.
Inherits base CRUD from BaseRepository.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.repositories.base_repo import BaseRepository
from app.models.task import Task
from app.core.logger import get_logger

logger = get_logger(__name__)


class TaskRepository(BaseRepository[Task]):
    """
    Task-specific DB operations.

    Inherited from BaseRepository:
        create(), get_by_id(), get_all(), update(), delete(), count(), exists()

    Task-specific:
        get_by_user(), get_by_goal(), get_pending(), mark_completed()
    """

    def __init__(self, db: Session):
        super().__init__(Task, db)

    # ─────────────────────────────────────────
    # USER-SCOPED QUERIES
    # ─────────────────────────────────────────

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks for a specific user"""
        return self.db.query(Task).filter(
            Task.user_id == user_id
        ).offset(skip).limit(limit).all()

    def get_pending(self, user_id: int) -> List[Task]:
        """Get all incomplete tasks for a user"""
        return self.db.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == False
        ).all()

    def count_pending(self, user_id: int) -> int:
        """Count pending tasks for a user"""
        return self.db.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == False
        ).count()

    # ─────────────────────────────────────────
    # GOAL-SCOPED QUERIES
    # ─────────────────────────────────────────

    def get_by_goal(self, goal_id: int) -> List[Task]:
        """Get all tasks for a specific goal"""
        return self.db.query(Task).filter(
            Task.goal_id == goal_id
        ).all()

    def count_pending_for_goal(self, goal_id: int) -> int:
        """Count incomplete tasks for a goal (used before marking goal complete)"""
        return self.db.query(Task).filter(
            Task.goal_id == goal_id,
            Task.completed == False
        ).count()

    def count_completed_for_goal(self, goal_id: int) -> int:
        """Count completed tasks for a goal"""
        return self.db.query(Task).filter(
            Task.goal_id == goal_id,
            Task.completed == True
        ).count()

    # ─────────────────────────────────────────
    # STATUS UPDATES
    # ─────────────────────────────────────────

    def mark_completed(self, task_id: int) -> Optional[Task]:
        """Mark a task as completed"""
        task = self.get_by_id(task_id)
        if not task:
            return None
        task.completed = True
        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        logger.info(f"✅ Task {task_id} completed")
        return task

    def mark_incomplete(self, task_id: int) -> Optional[Task]:
        """Reopen a completed task"""
        task = self.get_by_id(task_id)
        if not task:
            return None
        task.completed = False
        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_overdue(self, user_id: int) -> List[Task]:
        """Get incomplete tasks past their due date"""
        return self.db.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date < datetime.utcnow()
        ).all()
