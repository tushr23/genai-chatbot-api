
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# Test /chat endpoint with valid question
def test_chat_valid():
    question = "What is AI?"
    response = client.post("/chat", json={"question": question})
    assert response.status_code == 200
    answer = response.json().get("answer", "")
    assert isinstance(answer, str) and len(answer) > 0


# Test /chat endpoint with empty question
def test_chat_empty():
    response = client.post("/chat", json={"question": ""})
    assert response.status_code == 200
    answer = response.json().get("answer", "")
    assert isinstance(answer, str)


# Test /chat endpoint with missing question field
def test_chat_missing_field():
    response = client.post("/chat", json={})
    assert response.status_code in [400, 422]


# Test /logs endpoint
def test_logs():
    response = client.get("/logs")
    assert response.status_code == 200
    logs = response.json().get("logs", [])
    assert isinstance(logs, list)


# Test /chat and /logs integration
def test_chat_and_logs_integration():
    question = "Define Generative AI."
    client.post("/chat", json={"question": question})
    logs_response = client.get("/logs")
    logs = logs_response.json().get("logs", [])
    assert any("Generative AI" in str(log) for log in logs)
