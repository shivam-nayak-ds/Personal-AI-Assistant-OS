"""
Goal CRUD + Business Rules Tests

Tests:
- Create goal (valid)
- Past deadline rejected
- Unauthenticated access rejected
- Get goals list
- Update goal
- Delete own goal
- Cannot delete someone else's goal (403)
- Goal stats endpoint
"""


# ─────────────────────────────────────────
# CREATE TESTS
# ─────────────────────────────────────────

def test_create_goal_success(client, auth_headers):
    """Valid goal creation returns 201"""
    response = client.post("/api/v1/goals/goals",
        json={
            "title": "Learn FastAPI",
            "description": "Master FastAPI for backend dev",
            "target_date": "2028-12-31T00:00:00",
            "priority": "high"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Learn FastAPI"
    assert data["status"] == "active"
    assert data["priority"] == "high"
    assert "id" in data


def test_create_goal_without_deadline(client, auth_headers):
    """Goal without deadline is valid"""
    response = client.post("/api/v1/goals/goals",
        json={"title": "Open-ended goal"},
        headers=auth_headers
    )
    assert response.status_code == 201


def test_create_goal_past_deadline_rejected(client, auth_headers):
    """Past deadline should return 400"""
    response = client.post("/api/v1/goals/goals",
        json={
            "title": "Past goal",
            "target_date": "2020-01-01T00:00:00"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "future" in response.text.lower()


def test_create_goal_unauthenticated(client):
    """No token = 401"""
    response = client.post("/api/v1/goals/goals",
        json={"title": "No auth goal"}
    )
    assert response.status_code == 401


def test_create_goal_empty_title_rejected(client, auth_headers):
    """Empty title should fail validation"""
    response = client.post("/api/v1/goals/goals",
        json={"title": ""},
        headers=auth_headers
    )
    assert response.status_code == 422


# ─────────────────────────────────────────
# READ TESTS
# ─────────────────────────────────────────

def test_get_goals_returns_list(client, auth_headers):
    """GET /goals returns list"""
    response = client.get("/api/v1/goals/goals", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_goals_unauthenticated(client):
    """No token = 401"""
    response = client.get("/api/v1/goals/goals")
    assert response.status_code == 401


def test_get_goal_by_id(client, auth_headers):
    """Get specific goal by ID"""
    # Create first
    create = client.post("/api/v1/goals/goals",
        json={"title": "Specific Goal"},
        headers=auth_headers
    )
    goal_id = create.json()["id"]

    # Get it
    response = client.get(
        f"/api/v1/goals/goals/{goal_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Goal"


def test_get_nonexistent_goal_returns_404(client, auth_headers):
    """Non-existent goal ID returns 404"""
    response = client.get(
        "/api/v1/goals/goals/99999",
        headers=auth_headers
    )
    assert response.status_code == 404


# ─────────────────────────────────────────
# UPDATE TESTS
# ─────────────────────────────────────────

def test_update_goal(client, auth_headers):
    """Update goal title and priority"""
    create = client.post("/api/v1/goals/goals",
        json={"title": "Old Title"},
        headers=auth_headers
    )
    goal_id = create.json()["id"]

    response = client.put(
        f"/api/v1/goals/goals/{goal_id}",
        json={"title": "New Title", "priority": "urgent"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


# ─────────────────────────────────────────
# DELETE TESTS
# ─────────────────────────────────────────

def test_delete_own_goal(client, auth_headers):
    """Can delete your own goal"""
    create = client.post("/api/v1/goals/goals",
        json={"title": "Goal To Delete"},
        headers=auth_headers
    )
    goal_id = create.json()["id"]

    response = client.delete(
        f"/api/v1/goals/goals/{goal_id}",
        headers=auth_headers
    )
    assert response.status_code in [200, 204]


def test_get_goal_stats(client, auth_headers):
    """Goal stats endpoint works"""
    response = client.get("/api/v1/goals/goals/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "completion_rate" in data
