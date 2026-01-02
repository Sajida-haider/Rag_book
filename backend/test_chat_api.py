"""
Test file to validate the API contract implementation for the RAG chatbot backend.
"""
import pytest
import asyncio
from httpx import AsyncClient
import sys
import os

# Add the backend src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health endpoint"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_chat_endpoint_basic():
    """Test the basic functionality of the chat endpoint"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/chat", json={
            "message": "Hello, how are you?",
            "session_id": "test-session-123"
        })
    assert response.status_code == 200
    data = response.json()

    # Validate response structure based on API contract
    assert "response" in data
    assert "sources" in data
    assert "session_id" in data
    assert "retrieved_content" in data

    # Validate types
    assert isinstance(data["response"], str)
    assert isinstance(data["sources"], list)
    assert isinstance(data["session_id"], str)
    assert isinstance(data["retrieved_content"], list)


@pytest.mark.asyncio
async def test_chat_endpoint_without_session_id():
    """Test the chat endpoint without providing session_id"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/chat", json={
            "message": "Hello, how are you?"
        })
    assert response.status_code == 200
    data = response.json()

    # Should generate a session ID if not provided
    assert "response" in data
    assert "session_id" in data
    assert data["session_id"] is not None  # Should be generated


@pytest.mark.asyncio
async def test_chat_endpoint_empty_message():
    """Test the chat endpoint with an empty message"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/chat", json={
            "message": "",
            "session_id": "test-session-456"
        })
    assert response.status_code == 400  # Should return bad request


@pytest.mark.asyncio
async def test_chat_endpoint_missing_message():
    """Test the chat endpoint without a message field"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/chat", json={
            "session_id": "test-session-789"
        })
    assert response.status_code == 422  # Should return validation error


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])