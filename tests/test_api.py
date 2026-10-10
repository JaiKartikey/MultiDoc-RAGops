import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.api.main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FastAPI"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_ask_invalid_request():
    # Empty question
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422  # Validation error

    # Missing question
    response = client.post("/ask", json={})
    assert response.status_code == 422

@patch("app.api.main.ask_question")
def test_ask_valid_request(mock_ask_question):
    # Mock the return value of ask_question
    mock_ask_question.return_value = (
        "This is a mocked answer.",
        [{"chunk": "Mocked chunk 1", "score": 0.89}, {"chunk": "Mocked chunk 2", "score": 0.75}],
        0.1,  # retrieval_latency
        0.5   # generation_latency
    )

    response = client.post("/ask", json={"question": "What is the company name?"})
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["question"] == "What is the company name?"
    assert data["answer"] == "This is a mocked answer."
    assert len(data["sources"]) == 2
    assert data["sources"][0]["chunk"] == "Mocked chunk 1"
    assert "latency" in data
    assert "retrieval_latency" in data
    assert "generation_latency" in data
