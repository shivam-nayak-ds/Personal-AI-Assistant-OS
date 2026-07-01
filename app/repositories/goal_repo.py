"""
Goal Repository for Hermes AI OS

Handles all Goal-related database queries.
Inherits base CRUD from BaseRepository.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.repositories.base_repo import BaseRepository
from app.models.goal import Goal, GoalStatus
from app.core.logger import get_logger

logger = get_logger(__name__)


class GoalRepository(BaseRepository[Goal]):
    """
    Goal-specific DB operations.

    Inherited from BaseRepository:
        create(), get_by_id(), get_all(), update(), delete(), count(), exists()

    Goal-specific:
        get_by_user(), get_active(), count_active(), mark_completed(), mark_abandoned()
    """

    def __init__(self, db: Session):
        super().__init__(Goal, db)

    # ─────────────────────────────────────────
    # USER-SCOPED QUERIES
    # ─────────────────────────────────────────

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Goal]:
        """Get all goals for a specific user"""
        return self.db.query(Goal).filter(
            Goal.user_id == user_id
        ).offset(skip).limit(limit).all()

    def get_active(self, user_id: int) -> List[Goal]:
        """Get all active goals for a user"""
        return self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == GoalStatus.ACTIVE
        ).all()

    def count_by_user(self, user_id: int) -> int:
        """Count total goals for a user"""
        return self.db.query(Goal).filter(
            Goal.user_id == user_id
        ).count()

    def count_active(self, user_id: int) -> int:
        """Count active goals for a user (for limit checking)"""
        return self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == GoalStatus.ACTIVE
        ).count()

    def count_completed(self, user_id: int) -> int:
        """Count completed goals for stats"""
        return self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == GoalStatus.COMPLETED
        ).count()

    # ─────────────────────────────────────────
    # STATUS UPDATES
    # ─────────────────────────────────────────

    def mark_completed(self, goal_id: int) -> Optional[Goal]:
        """Mark a goal as completed"""
        goal = self.get_by_id(goal_id)
        if not goal:
            return None
        goal.status = GoalStatus.COMPLETED
        goal.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(goal)
        logger.info(f"✅ Goal {goal_id} marked completed")
        return goal

    def mark_abandoned(self, goal_id: int) -> Optional[Goal]:
        """Mark a goal as abandoned"""
        goal = self.get_by_id(goal_id)
        if not goal:
            return None
        goal.status = GoalStatus.ABANDONED
        goal.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(goal)
        logger.info(f"🚫 Goal {goal_id} marked abandoned")
        return goal

    def get_by_status(self, user_id: int, status: GoalStatus) -> List[Goal]:
        """Get goals filtered by status"""
        return self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == status
        ).all()

    def get_overdue(self, user_id: int) -> List[Goal]:
        """Get goals past their target date that are still active"""
        return self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == GoalStatus.ACTIVE,
            Goal.target_date < datetime.utcnow()
        ).all()
