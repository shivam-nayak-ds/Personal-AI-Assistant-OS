"""
Authentication Tests

Tests:
- Register new user
- Duplicate email/username rejected
- Login with correct credentials
- Login with wrong password → 401
- Access protected route without token → 401
"""

import pytest


# ─────────────────────────────────────────
# REGISTRATION TESTS
# ─────────────────────────────────────────

def test_register_success(client):
    """Valid registration creates user"""
    response = client.post("/api/v1/users/users", json={
        "email": "register@test.com",
        "username": "registeruser",
        "password": "securepass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "register@test.com"
    assert data["username"] == "registeruser"
    assert data["is_active"] is True


def test_register_password_not_in_response(client):
    """Password should NEVER appear in API response"""
    response = client.post("/api/v1/users/users", json={
        "email": "secure@test.com",
        "username": "secureuser",
        "password": "mysecretpassword"
    })
    assert response.status_code == 201
    data = response.json()
    # These must NEVER be exposed
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email_rejected(client):
    """Same email cannot be registered twice"""
    payload = {
        "email": "dup_email@test.com",
        "username": "firstuser",
        "password": "password123"
    }
    # First registration
    client.post("/api/v1/users/users", json=payload)

    # Second registration — same email, different username
    payload["username"] = "seconduser"
    response = client.post("/api/v1/users/users", json=payload)
    assert response.status_code == 400


def test_register_duplicate_username_rejected(client):
    """Same username cannot be registered twice"""
    payload = {
        "email": "first@test.com",
        "username": "duplicateuser",
        "password": "password123"
    }
    client.post("/api/v1/users/users", json=payload)

    # Same username, different email
    payload["email"] = "second@test.com"
    response = client.post("/api/v1/users/users", json=payload)
    assert response.status_code == 400


def test_register_short_password_rejected(client):
    """Password under 8 chars should be rejected"""
    response = client.post("/api/v1/users/users", json={
        "email": "short@test.com",
        "username": "shortpass",
        "password": "123"  # Too short!
    })
    assert response.status_code == 422  # Validation error


# ─────────────────────────────────────────
# LOGIN TESTS
# ─────────────────────────────────────────

def test_login_success_returns_token(client):
    """Valid login returns JWT access token"""
    # Register first
    client.post("/api/v1/users/users", json={
        "email": "logintest@test.com",
        "username": "logintest",
        "password": "loginpass123"
    })
    # Login
    response = client.post("/api/v1/auth/auth/token", json={
        "username": "logintest",
        "password": "loginpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_rejected(client):
    """Wrong password returns 401 Unauthorized"""
    client.post("/api/v1/users/users", json={
        "email": "wrongpass@test.com",
        "username": "wrongpassuser",
        "password": "correctpass123"
    })
    response = client.post("/api/v1/auth/auth/token", json={
        "username": "wrongpassuser",
        "password": "WRONGPASSWORD"
    })
    assert response.status_code == 401


def test_login_nonexistent_user_rejected(client):
    """Login with unknown username returns 401"""
    response = client.post("/api/v1/auth/auth/token", json={
        "username": "nobody_exists",
        "password": "somepassword"
    })
    assert response.status_code == 401


# ─────────────────────────────────────────
# PROTECTED ROUTES
# ─────────────────────────────────────────

def test_protected_route_without_token(client):
    """Accessing protected route without token returns 401"""
    response = client.get("/api/v1/goals/goals")
    assert response.status_code == 401


def test_protected_route_with_invalid_token(client):
    """Fake/expired token returns 401"""
    response = client.get(
        "/api/v1/goals/goals",
        headers={"Authorization": "Bearer fake.invalid.token"}
    )
    assert response.status_code == 401
