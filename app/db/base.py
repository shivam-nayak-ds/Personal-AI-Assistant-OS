"""
Base model class for all database models.

All SQLAlchemy models should inherit from this Base class.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create Base class
Base = declarative_base()

# All models will inherit from this Base
# Example usage in models:
"""
from app.db.base import Base
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
"""
