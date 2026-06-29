from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import redis

from app.core.config import settings
from app.core.dependencies import get_db, get_redis
from app.core.logger import auth_logger
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_current_active_user
)
from app.models.user import User
from app.schemas.user import UserLogin, UserResponse, Token, TokenData


router = APIRouter()


@router.post(
    "/auth/token",
    response_model=Token,
    summary="Login user and get access token"
)
async def login_for_access_token(
    request: Request,
    form_data: UserLogin,
    db: Session = Depends(get_db),
    redis: redis = Depends(get_redis)
):
    """
    Authenticate user and return JWT tokens

    - **username** or **email**: User's username or email
    - **password**: User's password

    Returns access token (short-lived) and refresh token (long-lived)
    """
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == form_data.username) |
        (User.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        auth_logger.warning(f"❌ Failed login attempt for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.username, "type": "refresh"}
    )

    # Store refresh token in Redis (optional, for additional security)
    try:
        redis.setex(
            f"refresh_token:{user.username}",
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            refresh_token
        )
    except Exception as e:
        auth_logger.error(f"Error storing refresh token: {str(e)}")

    auth_logger.info(f"✅ User logged in: {user.username}")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post(
    "/auth/refresh",
    response_model=Token,
    summary="Refresh access token"
)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
    redis: redis = Depends(get_redis)
):
    """
    Refresh expired access token using refresh token

    - **refresh_token**: Long-lived refresh token
    """
    try:
        # Verify refresh token (simplified, in production use JWT verification)
        payload = redis.get(f"refresh_token:{refresh_token}")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Get user
        data = payload if isinstance(payload, dict) else {"sub": payload}
        username = data.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        new_refresh_token = create_refresh_token(
            data={"sub": user.username, "type": "refresh"}
        )

        # Update stored refresh token
        redis.setex(
            f"refresh_token:{user.username}",
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            new_refresh_token
        )

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    except Exception as e:
        auth_logger.error(f"❌ Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token"
        )


@router.post(
    "/auth/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user"
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    redis: redis = Depends(get_redis)
):
    """
    Logout user (invalidate refresh token)
    """
    try:
        # Remove refresh token from Redis
        redis.delete(f"refresh_token:{current_user.username}")

        auth_logger.info(f"✅ User logged out: {current_user.username}")
        return {"message": "Successfully logged out"}

    except Exception as e:
        auth_logger.error(f"❌ Error logging out: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
async def register(
    user_data: UserLogin,
    db: Session = Depends(get_db),
    redis: redis = Depends(get_redis)
):
    """
    Register a new user account

    - **username**: User's username
    - **email**: User's email
    - **password**: User's password

    Returns the created user (password not included)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.username) |
        (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )

    # Create user
    try:
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        auth_logger.info(f"✅ New user registered: {new_user.username}")

        # Create access token
        access_token = create_access_token(
            data={"sub": new_user.username},
            expires_delta=timedelta(minutes=30)
        )

        return {
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at
        }

    except Exception as e:
        db.rollback()
        auth_logger.error(f"❌ Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.get(
    "/auth/me",
    response_model=UserResponse,
    summary="Get current user profile"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get the current authenticated user's profile"""
    return current_user


@router.post(
    "/auth/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change user password"
)
async def change_password(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change the current user's password

    Note: This is a simplified version - in production you'd need a password field in the request
    """
    # For now, just return success as password change requires password field in request
    auth_logger.info(f"✅ Password change requested for: {current_user.username}")
    return {"message": "Password change endpoint - implement password field in request"