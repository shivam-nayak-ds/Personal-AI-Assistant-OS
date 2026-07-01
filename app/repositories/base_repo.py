"""
Base Repository for Hermes AI OS

Generic CRUD operations that all repositories inherit.
This avoids repeating create/read/update/delete in every repo.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from app.db.base import Base
from app.core.logger import get_logger

logger = get_logger(__name__)

# Generic type — works for User, Goal, Task etc.
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository with standard CRUD operations.

    Usage:
        class GoalRepository(BaseRepository[Goal]):
            def __init__(self, db: Session):
                super().__init__(Goal, db)
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    # ─────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────

    def create(self, data: Dict[str, Any]) -> ModelType:
        """Create a new record"""
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        logger.debug(f"Created {self.model.__name__} id={obj.id}")
        return obj

    # ─────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get single record by ID"""
        return self.db.query(self.model).filter(
            self.model.id == id
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def count(self) -> int:
        """Count total records"""
        return self.db.query(self.model).count()

    def exists(self, id: int) -> bool:
        """Check if record exists"""
        return self.db.query(self.model).filter(
            self.model.id == id
        ).first() is not None

    # ─────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────

    def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """Update record fields"""
        obj = self.get_by_id(id)
        if not obj:
            return None

        for field, value in data.items():
            if value is not None and hasattr(obj, field):
                setattr(obj, field, value)

        self.db.commit()
        self.db.refresh(obj)
        logger.debug(f"Updated {self.model.__name__} id={id}")
        return obj

    # ─────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────

    def delete(self, id: int) -> bool:
        """Delete a record by ID"""
        obj = self.get_by_id(id)
        if not obj:
            return False

        self.db.delete(obj)
        self.db.commit()
        logger.debug(f"Deleted {self.model.__name__} id={id}")
        return True
