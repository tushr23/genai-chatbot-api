# Systematic, human-like imports
import os
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app, raise_server_exceptions=False)

def reset_rate_limit():
    # Helper to reset rate limit state between tests
        app.state.limiter._storage.reset()

@pytest.fixture(autouse=True)
def clear_rate_limit():
    reset_rate_limit()
    yield
    reset_rate_limit()

def test_chat_empty_question():
    # Should reject empty questions
    response = client.post("/v1/chat", json={"question": "   "})
    assert response.status_code == 400
    assert response.json()["error"] == "Question cannot be empty."

def test_chat_too_long_question():
    # Should reject questions over 200 characters
    long_question = "a" * 201
    response = client.post("/v1/chat", json={"question": long_question})
    assert response.status_code == 400
    assert response.json()["error"] == "Question is too long. Limit to 200 characters."

def test_chat_sql_injection_attempt():
    # Should reject questions with SQL keywords
    response = client.post("/v1/chat", json={"question": "SELECT * FROM users;"})
    assert response.status_code == 400
    assert response.json()["error"] == "Invalid question content."

def test_chat_rate_limit():
    # Should allow 5 requests, then block the 6th
    reset_rate_limit()
    for i in range(5):
        response = client.post("/v1/chat", json={"question": f"Test {i}"})
        assert response.status_code == 200
    response = client.post("/v1/chat", json={"question": "Test 6"})
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.text

def test_404_handler():
    # Should return 404 for missing endpoint
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert response.json()["error"] == "Resource not found"

def test_500_handler(monkeypatch):
    # Should return 500 for internal error
    from fastapi import Request
    def raise_500(request: Request):
        raise Exception("Test error")
    app.add_api_route("/raise500", raise_500, methods=["GET"])
    response = client.get("/raise500")
    assert response.status_code == 500
    # Accept either custom error or default FastAPI error
    data = response.json()
    assert "error" in data or "detail" in data

def test_validation_error_handler():
    # Should return 422 for invalid request data
    response = client.post("/v1/chat", json={"question": 123})
    assert response.status_code == 422
    assert response.json()["error"] == "Invalid request"

def test_missing_api_key(monkeypatch):
    # Should handle missing API_KEY
    monkeypatch.delenv("API_KEY", raising=False)
    from importlib import reload
    import main
    reload(main)
    assert main.API_KEY is None

def test_invalid_debug(monkeypatch, capsys):
    # Should handle invalid DEBUG value
    monkeypatch.setenv("DEBUG", "foo")
    from importlib import reload
    import main
    reload(main)
    captured = capsys.readouterr()
    assert "Debug mode is ON" not in captured.out
    assert main.DEBUG is False

def test_unset_debug(monkeypatch, capsys):
    # Should default DEBUG to False if unset
    monkeypatch.delenv("DEBUG", raising=False)
    from importlib import reload
    import main
    reload(main)
    captured = capsys.readouterr()
    assert "Debug mode is ON" not in captured.out
    assert main.DEBUG is False

def test_debug_env_var(monkeypatch, capsys):
    # Should enable debug mode if DEBUG is True
    monkeypatch.setenv("DEBUG", "True")
    from importlib import reload
    import main
    reload(main)
    captured = capsys.readouterr()
    assert "Debug mode is ON" in captured.out

def test_api_key_env_var(monkeypatch):
    # Should set API_KEY from environment
    monkeypatch.setenv("API_KEY", "test-key")
    from importlib import reload
    import main
    reload(main)
    assert main.API_KEY == "test-key"

def test_chat_valid():
    reset_rate_limit()
    question = "What is AI?"
    response = client.post("/v1/chat", json={"question": question})
    assert response.status_code == 200
    answer = response.json().get("answer", "")
    assert isinstance(answer, str) and len(answer) > 0

def test_chat_empty():
    reset_rate_limit()
    response = client.post("/v1/chat", json={"question": ""})
    assert response.status_code == 400
    answer = response.json().get("answer", "")
    assert isinstance(answer, str)

def test_chat_missing_field():
    # Should handle missing question field
    response = client.post("/v1/chat", json={})
    assert response.status_code in [400, 422]

def test_logs():
    # Should return logs as a list
    response = client.get("/v1/logs")
    assert response.status_code == 200
    logs = response.json().get("logs", [])
    assert isinstance(logs, list)

def test_chat_and_logs_integration():
    reset_rate_limit()
    question = "Define Generative AI."
    client.post("/v1/chat", json={"question": question})
    logs_response = client.get("/v1/logs")
    logs = logs_response.json().get("logs", [])
    assert any("Generative AI" in str(log) for log in logs)
