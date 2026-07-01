"""
Task Router for Hermes AI OS

Integrates with TaskService to handle task business logic and DB operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.config import settings
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.goal import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService

router = APIRouter()


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task.
    If associated with a goal, verifies that the goal belongs to the user.
    """
    service = TaskService(db)
    return service.create_task(user_id=current_user.id, data=task_data)


@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="List all tasks"
)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all tasks belonging to the authenticated user"""
    service = TaskService(db)
    return service.get_user_tasks(user_id=current_user.id, skip=skip, limit=limit)


@router.get(
    "/stats",
    summary="Get task statistics"
)
async def get_task_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics about tasks for the authenticated user"""
    service = TaskService(db)
    return service.get_stats(user_id=current_user.id)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID"
)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID"""
    service = TaskService(db)
    return service.get_task(task_id=task_id, user_id=current_user.id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task"
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task details"""
    service = TaskService(db)
    return service.update_task(task_id=task_id, user_id=current_user.id, data=task_data)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task"
)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    service = TaskService(db)
    service.delete_task(task_id=task_id, user_id=current_user.id)
    return None


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Complete task"
)
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a task as completed"""
    service = TaskService(db)
    return service.complete_task(task_id=task_id, user_id=current_user.id)


@router.patch(
    "/{task_id}/uncomplete",
    response_model=TaskResponse,
    summary="Reopen task"
)
async def reopen_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reopen a completed task"""
    service = TaskService(db)
    return service.reopen_task(task_id=task_id, user_id=current_user.id)