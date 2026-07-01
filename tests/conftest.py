"""
Test Configuration for Hermes AI OS

Sets up:
- SQLite test database (no PostgreSQL needed for tests!)
- FastAPI test client
- Common fixtures (test_user, auth_headers)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.main import app
from app.db.base import Base
from app.core.dependencies import get_db as get_db_dep  # ✅ Import both get_db functions
from app.db.session import get_db as get_db_session      # ✅

# ✅ All models auto-imported via app.models.__init__.py when app.main loads

# ✅ Use SQLite for tests — fast, no setup needed
TEST_DATABASE_URL = "sqlite:///./test_hermes.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create all tables before tests, drop after session"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Fresh DB session for each test"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def client(db):
    """FastAPI test client using test DB"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    # ✅ Override BOTH get_db definitions to completely isolate tests in SQLite
    app.dependency_overrides[get_db_dep] = override_get_db
    app.dependency_overrides[get_db_session] = override_get_db
    
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def registered_user(client):
    """Create and return a test user"""
    response = client.post("/api/v1/users/users", json={
        "email": "fixture@hermes.ai",
        "username": "fixtureuser",
        "password": "fixture_pass123"
    })
    return response.json()


@pytest.fixture()
def auth_headers(client):
    """Register a user, login, and return Bearer token headers"""
    # Register
    client.post("/api/v1/users/users", json={
        "email": "authfix@hermes.ai",
        "username": "authfixuser",
        "password": "authpass123"
    })
    # Login — route is /api/v1/auth + /auth/token = /api/v1/auth/auth/token
    response = client.post("/api/v1/auth/auth/token", json={
        "username": "authfixuser",
        "password": "authpass123"
    })
    token = response.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}
