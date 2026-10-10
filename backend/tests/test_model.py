"""Tests for the model endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_model_status_not_loaded():
    """Test model status when no model is loaded."""
    response = client.get("/api/v1/model/status")
    assert response.status_code == 200
    data = response.json()
    assert data["model_loaded"] is False
    assert data["message"] == "Model is not loaded"


def test_model_load_endpoint():
    """Test model load endpoint with non-existent file."""
    response = client.post("/api/v1/model/load", json={"model_path": "nonexistent.pkl"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


if __name__ == "__main__":
    test_model_status_not_loaded()
    test_model_load_endpoint()
    print("Model endpoint tests passed!")