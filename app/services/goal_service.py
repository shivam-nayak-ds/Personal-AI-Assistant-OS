"""
Goal Service for Hermes AI OS

Business logic for goal management:
- Create goals with AI task breakdown
- Complete/abandon goals
- Goal statistics
- Validation rules
"""

from typing import Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.goal_repo import GoalRepository
from app.repositories.task_repo import TaskRepository
from app.models.goal import Goal, GoalStatus
from app.schemas.goal import GoalCreate, GoalUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)

# Business Rules
MAX_ACTIVE_GOALS = 10


class GoalService:
    """
    Goal business logic layer.

    Usage in router:
        service = GoalService(db)
        goal = service.create_goal(user_id=1, data=goal_data)
    """

    def __init__(self, db: Session):
        self.db = db
        self.goal_repo = GoalRepository(db)
        self.task_repo = TaskRepository(db)

    # ─────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────

    def create_goal(self, user_id: int, data: GoalCreate) -> Goal:
        """
        Create a new goal with validation.

        Rules:
        - Max 10 active goals per user
        - Deadline must be in the future
        """
        # Rule 1: Max active goals check
        active_count = self.goal_repo.count_active(user_id)
        if active_count >= MAX_ACTIVE_GOALS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {MAX_ACTIVE_GOALS} active goals allowed. Complete or abandon existing goals first."
            )

        # Rule 2: Deadline must be future
        if data.target_date and data.target_date < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target date must be in the future."
            )

        # Create goal
        goal = self.goal_repo.create({
            "user_id": user_id,
            "title": data.title,
            "description": data.description,
            "status": data.status or GoalStatus.ACTIVE,
            "priority": data.priority or "medium",
            "target_date": data.target_date,
        })

        logger.info(f"🎯 Goal created: '{data.title}' for user {user_id}")
        return goal

    # ─────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────

    def get_goal(self, goal_id: int, user_id: int) -> Goal:
        """Get a goal — verify ownership"""
        goal = self.goal_repo.get_by_id(goal_id)

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        if goal.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your goal!"
            )
        return goal

    def get_user_goals(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Goal]:
        """Get all goals for a user"""
        return self.goal_repo.get_by_user(user_id, skip=skip, limit=limit)

    # ─────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────

    def update_goal(self, goal_id: int, user_id: int, data: GoalUpdate) -> Goal:
        """Update goal — verify ownership first"""
        goal = self.get_goal(goal_id, user_id)  # Ownership check inside

        updated = self.goal_repo.update(goal_id, data.model_dump(exclude_none=True))
        logger.info(f"✏️ Goal {goal_id} updated by user {user_id}")
        return updated

    # ─────────────────────────────────────────
    # COMPLETE / ABANDON
    # ─────────────────────────────────────────

    def complete_goal(self, goal_id: int, user_id: int) -> Goal:
        """
        Mark goal as completed.

        Rule: All tasks must be completed first!
        """
        goal = self.get_goal(goal_id, user_id)

        if goal.status == GoalStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Goal is already completed!"
            )

        # Check pending tasks
        pending = self.task_repo.count_pending_for_goal(goal_id)
        if pending > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Complete all tasks first! {pending} tasks still pending."
            )

        completed = self.goal_repo.mark_completed(goal_id)
        logger.info(f"🏆 Goal {goal_id} completed by user {user_id}")
        return completed

    def abandon_goal(self, goal_id: int, user_id: int) -> Goal:
        """Mark goal as abandoned"""
        self.get_goal(goal_id, user_id)  # Ownership check
        abandoned = self.goal_repo.mark_abandoned(goal_id)
        logger.info(f"🚫 Goal {goal_id} abandoned by user {user_id}")
        return abandoned

    # ─────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────

    def delete_goal(self, goal_id: int, user_id: int) -> bool:
        """Delete goal — verify ownership"""
        self.get_goal(goal_id, user_id)  # Ownership check
        result = self.goal_repo.delete(goal_id)
        logger.info(f"🗑️ Goal {goal_id} deleted by user {user_id}")
        return result

    # ─────────────────────────────────────────
    # STATISTICS
    # ─────────────────────────────────────────

    def get_stats(self, user_id: int) -> Dict:
        """Get goal statistics for a user"""
        total = self.goal_repo.count_by_user(user_id)
        completed = self.goal_repo.count_completed(user_id)
        active = self.goal_repo.count_active(user_id)
        overdue = len(self.goal_repo.get_overdue(user_id))

        return {
            "total": total,
            "active": active,
            "completed": completed,
            "overdue": overdue,
            "completion_rate": round((completed / total * 100), 1) if total > 0 else 0
        }
