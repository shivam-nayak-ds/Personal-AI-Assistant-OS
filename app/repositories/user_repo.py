"""
User Repository for Hermes AI OS

Handles all User-related database queries.
Inherits base CRUD from BaseRepository.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.base_repo import BaseRepository
from app.models.user import User
from app.core.logger import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """
    User-specific DB operations.

    Inherited from BaseRepository:
        create(), get_by_id(), get_all(), update(), delete(), count(), exists()

    User-specific:
        get_by_email(), get_by_username(), get_active_users()
    """

    def __init__(self, db: Session):
        super().__init__(User, db)

    # ─────────────────────────────────────────
    # LOOKUP QUERIES
    # ─────────────────────────────────────────

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email (for login)"""
        return self.db.query(User).filter(
            User.email == email
        ).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username (for login)"""
        return self.db.query(User).filter(
            User.username == username
        ).first()

    def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get user by email OR username (flexible login)"""
        return self.db.query(User).filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()

    def email_exists(self, email: str) -> bool:
        """Check if email already registered"""
        return self.db.query(User).filter(
            User.email == email
        ).first() is not None

    def username_exists(self, username: str) -> bool:
        """Check if username already taken"""
        return self.db.query(User).filter(
            User.username == username
        ).first() is not None

    # ─────────────────────────────────────────
    # STATUS UPDATES
    # ─────────────────────────────────────────

    def activate(self, user_id: int) -> Optional[User]:
        """Activate a user account"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"✅ User {user_id} activated")
        return user

    def deactivate(self, user_id: int) -> Optional[User]:
        """Deactivate a user account"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"🚫 User {user_id} deactivated")
        return user

    def make_admin(self, user_id: int) -> Optional[User]:
        """Grant admin privileges"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.is_admin = True
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"⭐ User {user_id} made admin")
        return user

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users"""
        return self.db.query(User).filter(
            User.is_active == True
        ).offset(skip).limit(limit).all()

    def update_password(self, user_id: int, hashed_password: str) -> Optional[User]:
        """Update user's hashed password"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.hashed_password = hashed_password
        self.db.commit()
        self.db.refresh(user)
        return user
