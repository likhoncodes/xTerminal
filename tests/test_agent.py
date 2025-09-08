import pytest
import respx
from fastapi.testclient import TestClient
import os

# Set dummy environment variables for testing before importing the app
# This prevents the app from trying to load a real .env file during tests
os.environ['GEMINI_API_URL'] = 'https://fake-gemini-api.com/v1/generate'
os.environ['GEMINI_API_KEY'] = 'fake-api-key'
os.environ['ALLOWED_SHELL_CMDS'] = 'echo,ls'
os.environ['LOG_PATH'] = '/tmp/test_agent.log'

# Now it's safe to import the app
from agent.app import app

# Pytest fixture for the test client
@pytest.fixture
def client():
    # Clear the rate limit counts before each test that uses the client
    # to ensure test isolation.
    from agent.app import request_counts
    request_counts.clear()
    with TestClient(app) as c:
        yield c

# Test for the /health endpoint
def test_health_check(client):
    """Tests if the /health endpoint returns a 200 OK status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

import httpx

# Test for the /chat endpoint with a successful API call
@respx.mock
def test_chat_success(client):
    """Tests the /chat endpoint with a mocked successful Gemini API response."""
    # Mock the external API call
    gemini_route = respx.post(os.environ['GEMINI_API_URL']).mock(
        return_value=httpx.Response(
            200,
            json={
                "candidates": [{
                    "content": {
                        "parts": [{"text": "Hello from Gemini!"}]
                    }
                }]
            }
        )
    )

    # Make the request to our app
    response = client.post("/chat", json={"input": "Hello"})

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"response": "Hello from Gemini!"}
    assert gemini_route.called

# Test for the /chat endpoint when the API returns an error
@respx.mock
def test_chat_api_error(client):
    """Tests the /chat endpoint when the Gemini API returns an error."""
    gemini_route = respx.post(os.environ['GEMINI_API_URL']).mock(
        return_value=httpx.Response(500, json={"error": "Internal Server Error"})
    )

    response = client.post("/chat", json={"input": "This will fail"})

    assert response.status_code == 500
    assert "Gemini API error" in response.json()["detail"]
    assert gemini_route.called

# Test for executing an allowed command
def test_exec_allowed_command(client):
    """Tests executing a command that is on the whitelist."""
    response = client.post("/exec", json={"cmd": "echo hello world"})

    assert response.status_code == 200
    data = response.json()
    assert "hello world" in data["stdout"]
    assert data["returncode"] == 0

# Test for executing a disallowed command
def test_exec_disallowed_command(client):
    """Tests attempting to execute a command that is not on the whitelist."""
    response = client.post("/exec", json={"cmd": "rm -rf /"})

    assert response.status_code == 403
    assert "not allowed" in response.json()["detail"]


# Test for the rate limiter
def test_rate_limiter(client):
    """Tests if the rate limiter blocks excessive requests."""
    # The rate limit is 10 requests per 60 seconds.
    # We'll make 10 successful requests.
    for i in range(10):
        response = client.get("/health")
        assert response.status_code == 200, f"Request {i+1} should have succeeded"

    # The 11th request should fail with a 429 status code.
    response = client.get("/health")
    assert response.status_code == 429
    assert response.json()["detail"] == "Too Many Requests"
