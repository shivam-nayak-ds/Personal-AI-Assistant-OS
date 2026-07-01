"""
Task Service for Hermes AI OS

Business logic for task management:
- Create tasks linked to goals
- Complete tasks + auto-check goal completion
- Task statistics
"""

from typing import Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.task_repo import TaskRepository
from app.repositories.goal_repo import GoalRepository
from app.models.task import Task
from app.schemas.goal import TaskCreate, TaskUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)


class TaskService:
    """
    Task business logic layer.

    Usage in router:
        service = TaskService(db)
        task = service.create_task(user_id=1, data=task_data)
    """

    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.goal_repo = GoalRepository(db)

    # ─────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────

    def create_task(self, user_id: int, data: TaskCreate) -> Task:
        """
        Create a new task.

        Rules:
        - If linked to a goal, verify goal belongs to user
        - Due date must be in future
        """
        # Rule 1: Goal ownership check
        if data.goal_id:
            goal = self.goal_repo.get_by_id(data.goal_id)
            if not goal:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Goal not found"
                )
            if goal.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="That goal doesn't belong to you!"
                )

        task = self.task_repo.create({
            "user_id": user_id,
            "goal_id": data.goal_id,
            "title": data.title,
            "description": data.description,
            "priority": data.priority or "medium",
            "due_date": data.due_date,
            "completed": False,
        })

        logger.info(f"📝 Task created: '{data.title}' for user {user_id}")
        return task

    # ─────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────

    def get_task(self, task_id: int, user_id: int) -> Task:
        """Get task — verify ownership"""
        task = self.task_repo.get_by_id(task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        if task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your task!"
            )
        return task

    def get_user_tasks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Task]:
        """Get all tasks for user"""
        return self.task_repo.get_by_user(user_id, skip=skip, limit=limit)

    def get_goal_tasks(self, goal_id: int, user_id: int) -> List[Task]:
        """Get all tasks for a specific goal"""
        goal = self.goal_repo.get_by_id(goal_id)
        if not goal or goal.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Goal not found or not yours"
            )
        return self.task_repo.get_by_goal(goal_id)

    # ─────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────

    def update_task(self, task_id: int, user_id: int, data: TaskUpdate) -> Task:
        """Update task — verify ownership"""
        self.get_task(task_id, user_id)  # ownership check
        updated = self.task_repo.update(task_id, data.model_dump(exclude_none=True))
        return updated

    # ─────────────────────────────────────────
    # COMPLETE
    # ─────────────────────────────────────────

    def complete_task(self, task_id: int, user_id: int) -> Task:
        """Mark task as completed"""
        task = self.get_task(task_id, user_id)

        if task.completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is already completed!"
            )

        completed = self.task_repo.mark_completed(task_id)
        logger.info(f"✅ Task {task_id} completed by user {user_id}")
        return completed

    def reopen_task(self, task_id: int, user_id: int) -> Task:
        """Reopen a completed task"""
        self.get_task(task_id, user_id)
        return self.task_repo.mark_incomplete(task_id)

    # ─────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Delete task — verify ownership"""
        self.get_task(task_id, user_id)
        result = self.task_repo.delete(task_id)
        logger.info(f"🗑️ Task {task_id} deleted by user {user_id}")
        return result

    # ─────────────────────────────────────────
    # STATISTICS
    # ─────────────────────────────────────────

    def get_stats(self, user_id: int) -> Dict:
        """Get task statistics for a user"""
        all_tasks = self.task_repo.get_by_user(user_id, limit=10000)
        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.completed)
        pending = total - completed
        overdue = len(self.task_repo.get_overdue(user_id))

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": round((completed / total * 100), 1) if total > 0 else 0
        }
