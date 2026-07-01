"""
Health Endpoint Tests

Tests:
- GET /          → Welcome message
- GET /health    → Server status
- GET /health/db → DB status
- GET /info      → App info
- GET /docs      → Swagger UI
"""


def test_root_returns_welcome(client):
    """Root endpoint returns welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Hermes" in data["message"]


def test_health_returns_healthy(client):
    """Health check returns healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "healthy"
    assert "version" in data


def test_info_endpoint(client):
    """Info endpoint returns app metadata"""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "features" in data
    assert data["app"]["name"] == "Hermes AI OS"


def test_docs_accessible_in_debug(client):
    """Swagger docs should load in DEBUG mode"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_accessible_in_debug(client):
    """ReDoc documentation should load in DEBUG mode"""
    response = client.get("/redoc")
    assert response.status_code == 200


def test_unknown_endpoint_returns_404(client):
    """Unknown routes return 404"""
    response = client.get("/this-does-not-exist")
    assert response.status_code == 404
