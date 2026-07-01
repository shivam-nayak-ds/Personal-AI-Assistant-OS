"""
Task CRUD Tests

Tests:
- Create task
- Create task linked to goal
- Complete a task
- Reopen a completed task
- Delete task
- Unauthenticated access rejected
- Task stats
"""


# ─────────────────────────────────────────
# CREATE TESTS
# ─────────────────────────────────────────

def test_create_task_success(client, auth_headers):
    """Valid task creation returns 201"""
    response = client.post("/api/v1/tasks/tasks",
        json={
            "title": "Daily 45 min workout",
            "description": "Go to gym",
            "priority": "high"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Daily 45 min workout"
    assert data["completed"] is False
    assert data["priority"] == "high"
    assert "id" in data


def test_create_task_default_priority(client, auth_headers):
    """Task without priority defaults to medium"""
    response = client.post("/api/v1/tasks/tasks",
        json={"title": "Simple task"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["priority"] == "medium"


def test_create_task_unauthenticated(client):
    """No token = 401"""
    response = client.post("/api/v1/tasks/tasks",
        json={"title": "No auth task"}
    )
    assert response.status_code == 401


def test_create_task_empty_title_rejected(client, auth_headers):
    """Empty title should fail validation"""
    response = client.post("/api/v1/tasks/tasks",
        json={"title": ""},
        headers=auth_headers
    )
    assert response.status_code == 422


# ─────────────────────────────────────────
# READ TESTS
# ─────────────────────────────────────────

def test_get_tasks_returns_list(client, auth_headers):
    """GET /tasks returns a list"""
    response = client.get("/api/v1/tasks/tasks", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_task_by_id(client, auth_headers):
    """Get specific task by ID"""
    create = client.post("/api/v1/tasks/tasks",
        json={"title": "Specific Task"},
        headers=auth_headers
    )
    task_id = create.json()["id"]

    response = client.get(
        f"/api/v1/tasks/tasks/{task_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Task"


def test_get_nonexistent_task_returns_404(client, auth_headers):
    """Non-existent task returns 404"""
    response = client.get(
        "/api/v1/tasks/tasks/99999",
        headers=auth_headers
    )
    assert response.status_code == 404


# ─────────────────────────────────────────
# COMPLETE / REOPEN TESTS
# ─────────────────────────────────────────

def test_complete_task(client, auth_headers):
    """Mark task as completed"""
    create = client.post("/api/v1/tasks/tasks",
        json={"title": "Task to complete"},
        headers=auth_headers
    )
    task_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/tasks/{task_id}/complete",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_complete_task_twice_rejected(client, auth_headers):
    """Completing an already completed task returns 400"""
    create = client.post("/api/v1/tasks/tasks",
        json={"title": "Double complete task"},
        headers=auth_headers
    )
    task_id = create.json()["id"]

    # First complete
    client.patch(
        f"/api/v1/tasks/tasks/{task_id}/complete",
        headers=auth_headers
    )

    # Second complete — should fail
    response = client.patch(
        f"/api/v1/tasks/tasks/{task_id}/complete",
        headers=auth_headers
    )
    assert response.status_code == 400


# ─────────────────────────────────────────
# DELETE TESTS
# ─────────────────────────────────────────

def test_delete_own_task(client, auth_headers):
    """Can delete your own task"""
    create = client.post("/api/v1/tasks/tasks",
        json={"title": "Task to delete"},
        headers=auth_headers
    )
    task_id = create.json()["id"]

    response = client.delete(
        f"/api/v1/tasks/tasks/{task_id}",
        headers=auth_headers
    )
    assert response.status_code in [200, 204]


# ─────────────────────────────────────────
# STATS TESTS
# ─────────────────────────────────────────

def test_task_stats(client, auth_headers):
    """Task stats endpoint returns counts"""
    response = client.get("/api/v1/tasks/tasks/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "completed" in data
    assert "pending" in data
    assert "completion_rate" in data
