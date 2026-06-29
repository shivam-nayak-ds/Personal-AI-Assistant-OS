from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.dependencies import get_db, get_redis, check_rate_limit
from app.core.logger import api_logger
from app.models.goal import Goal
from app.models.task import Task
from app.schemas.goal import (
    GoalCreate, GoalUpdate, GoalResponse, GoalWithTasks
)


router = APIRouter()


@router.post(
    "/goals",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new goal"
)
async def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    redis: redis = Depends(get_redis)
):
    """
    Create a new goal

    - **title**: Goal title (1-200 characters)
    - **description**: Goal description
    - **target_date**: Target date for goal completion
    - **status**: Goal status (active, in_progress, completed, abandoned)
    - **priority**: Priority level (low, medium, high, urgent)
    """
    try:
        # Verify user exists
        from app.models.user import User
        user = db.query(User).filter(User.id == goal_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Create goal
        db_goal = Goal(
            user_id=goal_data.user_id,
            title=goal_data.title,
            description=goal_data.description,
            status=goal_data.status,
            priority=goal_data.priority,
            target_date=goal_data.target_date
        )

        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)

        api_logger.info(f"✅ Goal created: {goal_data.title}")

        # Add to Redis cache
        redis.setex(
            f"goal:{db_goal.id}",
            3600,
            {"title": goal_data.title, "status": goal_data.status}
        )

        return db_goal

    except Exception as e:
        db.rollback()
        api_logger.error(f"❌ Error creating goal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create goal"
        )


@router.get(
    "/goals",
    response_model=List[GoalResponse],
    summary="List all goals"
)
async def list_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List goals with optional filtering"""
    try:
        query = db.query(Goal)

        # Apply filters
        if status:
            query = query.filter(Goal.status == status)

        if user_id:
            query = query.filter(Goal.user_id == user_id)

        # Get results with pagination
        goals = query.offset(skip).limit(limit).all()
        return goals

    except Exception as e:
        api_logger.error(f"❌ Error listing goals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list goals"
        )


@router.get(
    "/goals/{goal_id}",
    response_model=GoalWithTasks,
    summary="Get goal by ID"
)
async def get_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific goal with its tasks"""
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )

        # Get associated tasks
        tasks = db.query(Task).filter(Task.goal_id == goal_id).all()
        goal_dict = goal.__dict__
        goal_dict["tasks"] = [task.__dict__ for task in tasks]

        return goal

    except Exception as e:
        api_logger.error(f"❌ Error getting goal {goal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get goal"
        )


@router.put(
    "/goals/{goal_id}",
    response_model=GoalResponse,
    summary="Update goal"
)
async def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    db: Session = Depends(get_db)
):
    """Update goal information"""
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )

        # Update fields if provided
        if goal_data.title:
            goal.title = goal_data.title
        if goal_data.description is not None:
            goal.description = goal_data.description
        if goal_data.status is not None:
            goal.status = goal_data.status
        if goal_data.target_date is not None:
            goal.target_date = goal_data.target_date
        if goal_data.priority is not None:
            goal.priority = goal_data.priority

        db.commit()
        db.refresh(goal)

        api_logger.info(f"✅ Goal updated: {goal.title}")
        return goal

    except Exception as e:
        db.rollback()
        api_logger.error(f"❌ Error updating goal {goal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update goal"
        )


@router.delete(
    "/goals/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete goal"
)
async def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """Delete a goal"""
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )

        db.delete(goal)
        db.commit()

        api_logger.info(f"✅ Goal deleted: {goal.title}")
        return None

    except Exception as e:
        db.rollback()
        api_logger.error(f"❌ Error deleting goal {goal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete goal"
        )


@router.post(
    "/goals/{goal_id}/complete",
    response_model=GoalResponse,
    summary="Complete goal"
)
async def complete_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """Mark a goal as completed"""
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )

        goal.status = GoalStatus.COMPLETED
        db.commit()
        db.refresh(goal)

        api_logger.info(f"✅ Goal completed: {goal.title}")
        return goal

    except Exception as e:
        db.rollback()
        api_logger.error(f"❌ Error completing goal {goal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete goal"
        )


@router.get(
    "/goals/stats",
    summary="Get goal statistics"
)
async def get_goal_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get statistics about goals"""
    try:
        query = db.query(Goal)

        if user_id:
            query = query.filter(Goal.user_id == user_id)

        total_goals = query.count()
        active_goals = query.filter(Goal.status == GoalStatus.ACTIVE).count()
        in_progress_goals = query.filter(Goal.status == GoalStatus.IN_PROGRESS).count()
        completed_goals = query.filter(Goal.status == GoalStatus.COMPLETED).count()
        abandoned_goals = query.filter(Goal.status == GoalStatus.ABANDONED).count()

        return {
            "total_goals": total_goals,
            "active_goals": active_goals,
            "in_progress_goals": in_progress_goals,
            "completed_goals": completed_goals,
            "abandoned_goals": abandoned_goals,
            "completion_rate": (completed_goals / total_goals * 100) if total_goals > 0 else 0
        }

    except Exception as e:
        api_logger.error(f"❌ Error getting goal stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get goal statistics"
        )