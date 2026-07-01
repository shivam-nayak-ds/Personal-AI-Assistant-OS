"""
User Service for Hermes AI OS

Business logic for user management:
- Register new users
- Profile management
- Password changes
- User stats
"""

from typing import Dict, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repo import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """
    User business logic layer.

    Usage in router:
        service = UserService(db)
        user = service.register(data=user_data)
    """

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    # ─────────────────────────────────────────
    # REGISTER
    # ─────────────────────────────────────────

    def register(self, data: UserCreate) -> User:
        """
        Register a new user.

        Rules:
        - Email must be unique
        - Username must be unique
        - Password gets hashed (never store plain text!)
        """
        # Rule 1: Unique email
        if self.user_repo.email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Try logging in!"
            )

        # Rule 2: Unique username
        if self.user_repo.username_exists(data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken. Try another one!"
            )

        # Rule 3: Hash password — NEVER store plain text
        hashed_password = get_password_hash(data.password)

        user = self.user_repo.create({
            "email": data.email,
            "username": data.username,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_admin": False,
        })

        logger.info(f"👤 New user registered: {data.username}")
        return user

    # ─────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────

    def get_user(self, user_id: int) -> User:
        """Get user by ID"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        """Get user by email or username (for login)"""
        return self.user_repo.get_by_email_or_username(identifier)

    # ─────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────

    def update_profile(self, user_id: int, data: UserUpdate) -> User:
        """
        Update user profile.

        Rules:
        - Can't use someone else's email
        - Can't use someone else's username
        """
        user = self.get_user(user_id)

        # Check email uniqueness (if changing)
        if data.email and data.email != user.email:
            if self.user_repo.email_exists(data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use by another account"
                )

        # Check username uniqueness (if changing)
        if data.username and data.username != user.username:
            if self.user_repo.username_exists(data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        update_data = data.model_dump(exclude_none=True)

        # Hash new password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        updated = self.user_repo.update(user_id, update_data)
        logger.info(f"✏️ User {user_id} profile updated")
        return updated

    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> User:
        """
        Change password securely.

        Rules:
        - Must verify current password first
        - New password gets hashed
        """
        user = self.get_user(user_id)

        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        new_hash = get_password_hash(new_password)
        updated = self.user_repo.update_password(user_id, new_hash)
        logger.info(f"🔑 Password changed for user {user_id}")
        return updated

    # ─────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────

    def delete_account(self, user_id: int) -> bool:
        """Delete user account (cascades to goals, tasks etc.)"""
        self.get_user(user_id)
        result = self.user_repo.delete(user_id)
        logger.info(f"🗑️ User {user_id} account deleted")
        return result

    # ─────────────────────────────────────────
    # STATS
    # ─────────────────────────────────────────

    def get_stats(self, user_id: int) -> Dict:
        """Get user account stats"""
        user = self.get_user(user_id)
        return {
            "user_id": user.id,
            "username": user.username,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "member_since": user.created_at.isoformat() if user.created_at else None,
        }
