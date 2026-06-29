from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.logger import api_logger
from app.models.goal import Goal
from app.models.task import Task
from app.schemas.goal import TaskCreate, TaskUpdate, TaskResponse


router = APIRouter()


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new task

    - **title**: Task title (1-200 characters)
    - **description**: Task description
    - **due_date**: Due date for task completion
    - **goal_id**: Associated goal (optional)
    - **user_id**: User who owns the task
    - **priority**: Priority level (low, medium, high, urgent)
    """
    try:
        # Verify user exists
        from app.models.user import User
        user = db.query(User).filter(User.id == task_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify goal exists if specified
        if task_data.goal_id:
            goal = db.query(Goal).filter(Goal.id == task_data.goal_id).first()
            if not goal:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Goal not found"
                )

        # Create task
        db_task = Task(
            goal_id=task_data.goal_id,
            user_id=task_data.user_id,
            title=task_data.title,
            description=task_data.description,
            completed=False,
            priority=task_data.priority,
            due_date=task_data.due_date
        )

        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        api_logger.info(f"✅ Task created: {task_data.title}")

        return db_task

    except Exception as e:
        db.rollback()
        api_logger.error(f"❌ Error creating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )


@router.get(
    "/tasks",
    response_model=List[TaskResponse],
    summary="List all tasks"
)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    completed: Optional[bool] = None,
    user_id: Optional[int] = None,
    goal_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List tasks with optional filtering"""
    try:
        query = db.query(Task)

        # Apply filters
        if completed is not None:
            query = query.filter(Task.completed == completed)

        if user_id:
            query = query.filter(Task.user_id == user_id)

        if goal_id:
            query = query.filter(Task.goal_id == goal_id)

        # Get results with pagination
        tasks = query.offset(skip).limit(limit).all()
        return tasks

    except Exception as e:
        api_logger.error(f"❌ Error listing tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list tasks"
        )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID"
)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific task"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task

    except Exception as e:
        api_logger.error(f"❌ Error getting task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task"
        )


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update task"
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update task information"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Update fields if provided
        if task_data.title:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.completed is not None:
            task.completed = task_data.completed
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.due_date is not None:
            task.due_date = task_data.due_date

        db.commit()
        db.refresh(task)

        api_logger.info(f"✅ Task updated: {task.title}")
        return task

    except Exception as e:
        db.rollback()
        api_logger.error(f"❌ Error updating task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task"
)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Delete a task"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        db.delete(task)
        db.commit()

        api_logger.info(f"✅ Task deleted: {task.title}")
        return None

    except Exception as e:
        db.rollback()
        api_logger.error(f"❌ Error deleting task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )


@router.post(
    "/tasks/{task_id}/complete",
    response_model=TaskResponse,
    summary="Complete task"
)
async def complete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Mark a task as completed"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        task.completed = True
        db.commit()
        db.refresh(task)

        api_logger.info(f"✅ Task completed: {task.title}")

        # Update goal status if all tasks are completed
        if task.goal_id:
            goal = db.query(Goal).filter(Goal.id == task.goal_id).first()
            if goal:
                all_tasks = db.query(Task).filter(Task.goal_id == task.goal_id).all()
                if all(task.completed for task in all_tasks):
                    goal.status = GoalStatus.COMPLETED
                    db.commit()

        return task

    except Exception as e:
        db.rollback()
        api_logger.error(f"❌ Error completing task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete task"
        )


@router.post(
    "/tasks/{task_id}/uncomplete",
    response_model=TaskResponse,
    summary="Uncomplete task"
)
async def uncomplete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Mark a task as uncompleted"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        task.completed = False
        db.commit()
        db.refresh(task)

        api_logger.info(f"✅ Task uncompleted: {task.title}")
        return task

    except Exception as e:
        db.rollback()
        api_logger.error(f"❌ Error uncompleting task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to uncomplete task"
        )


@router.get(
    "/tasks/stats",
    summary="Get task statistics"
)
async def get_task_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get statistics about tasks"""
    try:
        query = db.query(Task)

        if user_id:
            query = query.filter(Task.user_id == user_id)

        total_tasks = query.count()
        completed_tasks = query.filter(Task.completed == True).count()
        pending_tasks = total_tasks - completed_tasks

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }

    except Exception as e:
        api_logger.error(f"❌ Error getting task stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task statistics"
        )