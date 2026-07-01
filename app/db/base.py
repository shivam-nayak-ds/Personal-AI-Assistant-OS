"""
Base model class for all database models.

All SQLAlchemy models should inherit from this Base class.
IMPORTANT: All models must be imported before calling Base.metadata.create_all()
so SQLAlchemy can resolve all relationships.
"""

from sqlalchemy.orm import declarative_base

# Create Base class — all models inherit from this
Base = declarative_base()

# NOTE: Models are imported in app/db/session.py's init_db()
# and in tests/conftest.py — NOT here to avoid circular imports
