from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert "Daily Operations Assistant" in response.text
