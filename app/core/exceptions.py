"""
Custom exception classes and HTTP exception handlers.

Features:
- Domain-specific exceptions
- Standardized error responses
- FastAPI exception handlers
- Error logging
- User-friendly error messages
"""

from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logger import get_logger

logger = get_logger(__name__)


# ============== Base Exception ==============

class HermesException(Exception):
    """Base exception for all Hermes AI OS exceptions."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ============== Authentication & Authorization ==============

class AuthenticationError(HermesException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(HermesException):
    """Raised when user is not authorized to perform action."""
    
    def __init__(self, message: str = "Not authorized", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid or expired."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message=message)


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message=message)


# ============== Resource Exceptions ==============

class ResourceNotFoundError(HermesException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, resource_id: Any):
        message = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "id": str(resource_id)}
        )


class ResourceAlreadyExistsError(HermesException):
    """Raised when trying to create a resource that already exists."""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' already exists"
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details={"resource": resource, "identifier": identifier}
        )


class ResourceUpdateError(HermesException):
    """Raised when resource update fails."""
    
    def __init__(self, resource: str, resource_id: Any, reason: str):
        message = f"Failed to update {resource} '{resource_id}': {reason}"
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"resource": resource, "id": str(resource_id), "reason": reason}
        )


class ResourceDeleteError(HermesException):
    """Raised when resource deletion fails."""
    
    def __init__(self, resource: str, resource_id: Any, reason: str):
        message = f"Failed to delete {resource} '{resource_id}': {reason}"
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"resource": resource, "id": str(resource_id), "reason": reason}
        )


# ============== Database Exceptions ==============

class DatabaseError(HermesException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""
    
    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message=message)


# ============== Validation Exceptions ==============

class ValidationError(HermesException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class InvalidInputError(ValidationError):
    """Raised when input data is invalid."""
    
    def __init__(self, field: str, reason: str):
        message = f"Invalid value for field '{field}': {reason}"
        super().__init__(message=message, field=field)


class MissingFieldError(ValidationError):
    """Raised when required field is missing."""
    
    def __init__(self, field: str):
        message = f"Required field '{field}' is missing"
        super().__init__(message=message, field=field)


# ============== External Service Exceptions ==============

class ExternalServiceError(HermesException):
    """Raised when external service call fails."""
    
    def __init__(self, service: str, message: str, details: Optional[Dict] = None):
        full_message = f"{service} service error: {message}"
        super().__init__(
            message=full_message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details or {"service": service}
        )


class LLMProviderError(ExternalServiceError):
    """Raised when LLM provider API fails."""
    
    def __init__(self, provider: str, message: str):
        super().__init__(service=f"LLM ({provider})", message=message)


class VectorDatabaseError(ExternalServiceError):
    """Raised when vector database operation fails."""
    
    def __init__(self, message: str):
        super().__init__(service="Vector Database", message=message)


class SearchServiceError(ExternalServiceError):
    """Raised when search service fails."""
    
    def __init__(self, message: str):
        super().__init__(service="Search", message=message)


# ============== Rate Limiting ==============

class RateLimitError(HermesException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


# ============== File Upload Exceptions ==============

class FileUploadError(HermesException):
    """Raised when file upload fails."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class FileSizeLimitError(FileUploadError):
    """Raised when uploaded file exceeds size limit."""
    
    def __init__(self, max_size_mb: int):
        message = f"File size exceeds maximum allowed size of {max_size_mb}MB"
        super().__init__(message=message, details={"max_size_mb": max_size_mb})


class InvalidFileTypeError(FileUploadError):
    """Raised when uploaded file type is not allowed."""
    
    def __init__(self, file_type: str, allowed_types: list):
        message = f"File type '{file_type}' is not allowed. Allowed types: {', '.join(allowed_types)}"
        super().__init__(
            message=message,
            details={"file_type": file_type, "allowed_types": allowed_types}
        )


# ============== Business Logic Exceptions ==============

class TaskError(HermesException):
    """Raised when task operation fails."""
    
    def __init__(self, message: str, task_id: Optional[str] = None):
        details = {"task_id": task_id} if task_id else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class GoalError(HermesException):
    """Raised when goal operation fails."""
    
    def __init__(self, message: str, goal_id: Optional[str] = None):
        details = {"goal_id": goal_id} if goal_id else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class MemoryError(HermesException):
    """Raised when memory operation fails."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


# ============== Exception Handlers ==============

async def hermes_exception_handler(request: Request, exc: HermesException) -> JSONResponse:
    """
    Handler for custom Hermes exceptions.
    
    Args:
        request: FastAPI request
        exc: Hermes exception
    
    Returns:
        JSONResponse: Standardized error response
    """
    logger.error(
        f"HermesException: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "details": exc.details
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler for standard HTTP exceptions.
    
    Args:
        request: FastAPI request
        exc: HTTP exception
    
    Returns:
        JSONResponse: Standardized error response
    """
    logger.warning(
        f"HTTPException: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.detail,
                "type": "HTTPException"
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for request validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation error
    
    Returns:
        JSONResponse: Standardized validation error response
    """
    logger.warning(
        f"ValidationError: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "message": "Validation error",
                "type": "ValidationError",
                "details": exc.errors()
            }
        }
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unhandled exceptions.
    
    Args:
        request: FastAPI request
        exc: Unhandled exception
    
    Returns:
        JSONResponse: Generic error response
    """
    logger.critical(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "message": "Internal server error",
                "type": "InternalServerError"
            }
        }
    )


# Function to register all exception handlers
def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(HermesException, hermes_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    
    logger.info("Exception handlers registered")


# Example usage:
"""
from app.core.exceptions import ResourceNotFoundError, InvalidInputError

# In service layer
user = db.query(User).filter(User.id == user_id).first()
if not user:
    raise ResourceNotFoundError("User", user_id)

# In validation
if age < 0:
    raise InvalidInputError("age", "must be positive")

# In FastAPI app
from app.core.exceptions import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
"""
