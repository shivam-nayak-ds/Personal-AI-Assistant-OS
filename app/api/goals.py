"""
Goal Router for Hermes AI OS

Integrates with GoalService to handle goal business logic and DB operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from redis import Redis

from app.core.config import settings
from app.core.dependencies import get_db, get_redis, get_current_user
from app.models.user import User
from app.schemas.goal import (
    GoalCreate, GoalUpdate, GoalResponse, GoalWithTasks
)
from app.services.goal_service import GoalService

router = APIRouter()


@router.post(
    "/",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new goal"
)
async def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new goal.
    Validates:
    - Maximum 10 active goals.
    - Target date must be in the future.
    """
    service = GoalService(db)
    # The service automatically validates and creates the goal
    db_goal = service.create_goal(user_id=current_user.id, data=goal_data)

    # Optional: Cache goal in Redis
    try:
        redis.setex(
            f"goal:{db_goal.id}",
            3600,
            f"{db_goal.title}:{db_goal.status}"
        )
    except Exception:
        pass

    return db_goal


@router.get(
    "/",
    response_model=List[GoalResponse],
    summary="List all goals"
)
async def list_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all goals belonging to the authenticated user"""
    service = GoalService(db)
    return service.get_user_goals(user_id=current_user.id, skip=skip, limit=limit)


@router.get(
    "/stats",
    summary="Get goal statistics"
)
async def get_goal_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics about goals for the authenticated user"""
    service = GoalService(db)
    return service.get_stats(user_id=current_user.id)


@router.get(
    "/{goal_id}",
    response_model=GoalWithTasks,
    summary="Get goal by ID"
)
async def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific goal with its tasks"""
    service = GoalService(db)
    goal = service.get_goal(goal_id=goal_id, user_id=current_user.id)
    
    # Map tasks to goal dictionary for GoalWithTasks schema
    goal_dict = {
        "id": goal.id,
        "user_id": goal.user_id,
        "title": goal.title,
        "description": goal.description,
        "status": goal.status,
        "priority": goal.priority,
        "target_date": goal.target_date,
        "created_at": goal.created_at,
        "updated_at": goal.updated_at,
        "tasks": [task for task in goal.tasks]
    }
    return goal_dict


@router.put(
    "/{goal_id}",
    response_model=GoalResponse,
    summary="Update goal"
)
async def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update goal information"""
    service = GoalService(db)
    return service.update_goal(goal_id=goal_id, user_id=current_user.id, data=goal_data)


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete goal"
)
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a goal"""
    service = GoalService(db)
    service.delete_goal(goal_id=goal_id, user_id=current_user.id)
    return None


@router.post(
    "/{goal_id}/complete",
    response_model=GoalResponse,
    summary="Complete goal"
)
async def complete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a goal as completed (requires all tasks to be completed)"""
    service = GoalService(db)
    return service.complete_goal(goal_id=goal_id, user_id=current_user.id)