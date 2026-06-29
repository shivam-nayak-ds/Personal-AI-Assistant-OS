import logging
import sys
from typing import Optional
from app.core.config import settings


def setup_logger(
    name: str,
    level: Optional[int] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup logger with proper configuration"""

    # Use settings level if not specified
    if level is None:
        level = logging.DEBUG if settings.DEBUG else logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(level=logging.DEBUG if settings.DEBUG else logging.INFO)


# Define common loggers
api_logger = setup_logger("api")
db_logger = setup_logger("db")
auth_logger = setup_logger("auth")
rag_logger = setup_logger("rag")
agent_logger = setup_logger("agent")
worker_logger = setup_logger("worker")


# Debug logging levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL