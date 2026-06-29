"""
Structured logging configuration with JSON output and file rotation.

Features:
- JSON structured logging for production
- Console logging for development
- Log rotation (10MB per file, 5 backup files)
- Request ID tracking
- Different log levels per module
- Integration with FastAPI
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Any, Dict
import json
from datetime import datetime

from app.core.config import get_settings

settings = get_settings()


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        # Add any custom extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info", "request_id", "user_id", "duration_ms"
            ]:
                log_data[key] = value
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output in development."""
    
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging() -> logging.Logger:
    """
    Setup application logging.
    
    Returns:
        logging.Logger: Configured root logger
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    if settings.LOG_FORMAT == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        if settings.DEBUG:
            # Colored format for development
            console_formatter = ColoredFormatter(
                "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        else:
            # Plain format for production console
            console_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        console_handler.setFormatter(console_formatter)
    
    logger.addHandler(console_handler)
    
    # File handler with rotation (only if LOG_FILE is specified)
    if settings.LOG_FILE:
        log_file_path = Path(settings.LOG_FILE)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            filename=settings.LOG_FILE,
            maxBytes=int(settings.LOG_ROTATION.replace("MB", "")) * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    # Set log levels for specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logger.info(
        "Logging configured",
        extra={
            "environment": settings.ENVIRONMENT,
            "log_format": settings.LOG_FORMAT,
            "log_file": settings.LOG_FILE,
            "debug": settings.DEBUG
        }
    )
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        logging.Logger: Configured logger
    """
    return logging.getLogger(name)


# Convenience function for adding request context to logs
def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    request_id: str | None = None,
    user_id: str | None = None,
    **kwargs
) -> None:
    """
    Log message with request context.
    
    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        request_id: Optional request ID
        user_id: Optional user ID
        **kwargs: Additional fields to log
    """
    extra = {}
    if request_id:
        extra["request_id"] = request_id
    if user_id:
        extra["user_id"] = user_id
    extra.update(kwargs)
    
    log_func = getattr(logger, level.lower())
    log_func(message, extra=extra)


# Initialize logging on module import
logger = setup_logging()


# Example usage:
"""
from app.core.logger import get_logger, log_with_context

logger = get_logger(__name__)

# Simple logging
logger.info("User logged in")
logger.error("Database connection failed", exc_info=True)

# With context
log_with_context(
    logger,
    "info",
    "Processing request",
    request_id="req-123",
    user_id="user-456",
    duration_ms=123.45
)
"""
