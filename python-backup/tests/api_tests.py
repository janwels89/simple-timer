import pytest
from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_get_status():
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "enabled" in data
    assert "status" in data

def test_pause_resume():
    response = client.post("/pause_resume")
    assert response.status_code == 200
    assert "enabled" in response.json()

def test_reset():
    response = client.post("/reset")
    assert response.status_code == 200
    assert response.json()["status"] == "reset"

def test_full_reset():
    response = client.post("/full_reset")
    assert response.status_code == 200
    assert response.json()["status"] == "full_reset"

def test_change_mode():
    response = client.post("/mode", json={"direction": 1})
    assert response.status_code == 200
    assert "mode" in response.json()