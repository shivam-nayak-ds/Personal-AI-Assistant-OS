"""
Security utilities for authentication and authorization.

Features:
- JWT token generation and validation
- Password hashing with bcrypt
- API key validation
- Token refresh mechanism
- CORS configuration
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security_scheme = HTTPBearer()


# ============== Password Hashing ==============

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
    
    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============== JWT Token Management ==============

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in token (e.g., {"sub": user_id})
        expires_delta: Optional custom expiration time
    
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    logger.info(
        "Access token created",
        extra={"user_id": data.get("sub"), "expires_at": expire.isoformat()}
    )
    
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Data to encode in token
        expires_delta: Optional custom expiration time
    
    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_REFRESH_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dict: Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return payload
    
    except JWTError as e:
        logger.warning(f"JWT decode failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_refresh_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT refresh token.
    
    Args:
        token: JWT refresh token string
    
    Returns:
        Dict: Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_REFRESH_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Verify token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return payload
    
    except JWTError as e:
        logger.warning(f"Refresh token decode failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


def get_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        str: User ID
    
    Raises:
        HTTPException: If token is invalid
    """
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return user_id


# ============== API Key Validation ==============

def validate_api_key(api_key: str) -> bool:
    """
    Validate API key against configured key.
    
    Args:
        api_key: API key from request
    
    Returns:
        bool: True if valid
    """
    return api_key == settings.API_KEY


def verify_api_key(api_key: str) -> None:
    """
    Verify API key or raise exception.
    
    Args:
        api_key: API key from request
    
    Raises:
        HTTPException: If API key is invalid
    """
    if not validate_api_key(api_key):
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )


# ============== Token Dependencies ==============

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = security_scheme
) -> str:
    """
    Dependency to get current user ID from JWT token.
    
    Usage in FastAPI route:
        @app.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user_id)):
            return {"user_id": user_id}
    
    Args:
        credentials: HTTP Bearer credentials
    
    Returns:
        str: Current user ID
    
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    return get_user_id_from_token(token)


# ============== CORS Configuration ==============

def get_cors_config() -> Dict[str, Any]:
    """
    Get CORS configuration for FastAPI.
    
    Returns:
        Dict: CORS configuration
    """
    return {
        "allow_origins": settings.ALLOWED_ORIGINS,
        "allow_credentials": settings.ALLOW_CREDENTIALS,
        "allow_methods": settings.ALLOW_METHODS.split(","),
        "allow_headers": settings.ALLOW_HEADERS.split(","),
    }


# ============== Encryption Utilities ==============

def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data (placeholder).
    
    TODO: Implement proper encryption using cryptography library
    
    Args:
        data: Plain text data
    
    Returns:
        str: Encrypted data
    """
    # TODO: Use Fernet symmetric encryption
    from base64 import b64encode
    return b64encode(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data (placeholder).
    
    TODO: Implement proper decryption using cryptography library
    
    Args:
        encrypted_data: Encrypted data
    
    Returns:
        str: Decrypted plain text
    """
    # TODO: Use Fernet symmetric encryption
    from base64 import b64decode
    return b64decode(encrypted_data.encode()).decode()


# Example usage:
"""
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_id
)
from fastapi import Depends

# Hash password during registration
hashed = hash_password("user_password")

# Verify password during login
is_valid = verify_password("user_password", hashed)

# Create token after successful login
token = create_access_token(data={"sub": user.id})

# Protected route
@app.get("/me")
async def get_me(user_id: str = Depends(get_current_user_id)):
    return {"user_id": user_id}
"""
