from fastapi.testclient import TestClient

from ..main import app, tasks

client = TestClient(app)


def setup_function():
    tasks.clear()


def test_home_page_loads():
    response = client.get("/")

    assert response.status_code == 200
    assert "Simple Todo" in response.text


def test_health_check():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] is True


def test_create_and_end_task():
    payload = {
        "title": "Prepare demo",
        "detail": "Create a simple Todo example",
        "due_at": "2026-05-22T10:00:00",
        "checklist": [{"text": "Create API"}, {"text": "Add UI"}],
    }

    create_response = client.post("/api/tasks", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Prepare demo"
    assert created["done"] is False
    assert len(created["checklist"]) == 2

    list_response = client.get("/api/tasks")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    end_response = client.patch(f"/api/tasks/{created['id']}/end")
    assert end_response.status_code == 200
    assert end_response.json()["done"] is True
