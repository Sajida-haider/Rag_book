"""
Comprehensive test suite for RAG functionality
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the backend src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.rag_service import RAGService
from src.services.vector_storage import VectorStorageService, RetrievedContent
from src.services.session_service import SessionService


class TestRAGService:
    """Test the RAG service functionality"""

    @pytest.fixture
    def rag_service(self):
        """Create a RAG service instance for testing"""
        with patch('src.services.vector_storage.QdrantClient'), \
             patch('src.services.rag_service.OpenAI'):
            service = RAGService()
            # Mock the dependencies
            service.vector_storage = Mock(spec=VectorStorageService)
            service.session_service = Mock(spec=SessionService)
            service.openai_client = Mock()
            return service

    @pytest.mark.asyncio
    async def test_process_message_success(self, rag_service):
        """Test successful message processing"""
        # Mock the vector storage search
        mock_content = [RetrievedContent(content="Test content", source="test_source.md", score=0.9)]
        rag_service.vector_storage.search_by_text = AsyncMock(return_value=mock_content)

        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        rag_service.openai_client.chat.completions.create = Mock(return_value=mock_response)

        result = await rag_service.process_message("Test message", "test-session")

        assert "response" in result
        assert "sources" in result
        assert "retrieved_content" in result
        assert result["response"] == "Test response"

    @pytest.mark.asyncio
    async def test_process_message_no_content_found(self, rag_service):
        """Test message processing when no relevant content is found"""
        # Mock empty search results
        rag_service.vector_storage.search_by_text = AsyncMock(return_value=[])

        result = await rag_service.process_message("Test message", "test-session")

        assert "response" in result
        assert result["response"].startswith("I couldn't find specific information")
        assert result["sources"] == []
        assert result["retrieved_content"] == []

    @pytest.mark.asyncio
    async def test_process_message_error_handling(self, rag_service):
        """Test error handling in message processing"""
        # Mock an exception in vector storage
        rag_service.vector_storage.search_by_text = AsyncMock(side_effect=Exception("Test error"))

        result = await rag_service.process_message("Test message", "test-session")

        assert "response" in result
        assert result["response"].startswith("I'm having trouble processing")
        assert result["sources"] == []
        assert result["retrieved_content"] == []


class TestVectorStorageService:
    """Test the vector storage service functionality"""

    @pytest.fixture
    def vector_service(self):
        """Create a vector storage service instance for testing"""
        with patch('src.services.vector_storage.QdrantClient'):
            service = VectorStorageService()
            return service

    @pytest.mark.asyncio
    async def test_search_by_text(self, vector_service):
        """Test searching by text"""
        # This test would require mocking the OpenAI embedding API
        # For now, we'll just ensure the method exists and has the right signature
        assert hasattr(vector_service, 'search_by_text')
        assert asyncio.iscoroutinefunction(vector_service.search_by_text.__func__)


class TestSessionService:
    """Test the session service functionality"""

    @pytest.fixture
    def session_service(self):
        """Create a session service instance for testing"""
        return SessionService()

    def test_create_session(self, session_service):
        """Test creating a new session"""
        session = session_service.create_session()

        assert session.id is not None
        assert session.created_at is not None
        assert session.updated_at is not None
        assert session.messages == []
        assert session.user_id is None

    def test_add_message(self, session_service):
        """Test adding a message to a session"""
        session = session_service.create_session()

        message = session_service.add_message(session.id, "user", "Hello")

        assert message is not None
        assert message.role == "user"
        assert message.content == "Hello"

        # Check that the message was added to the session
        history = session_service.get_session_history(session.id)
        assert len(history) == 1
        assert history[0].content == "Hello"

    def test_get_session_history(self, session_service):
        """Test getting session history"""
        session = session_service.create_session()
        session_service.add_message(session.id, "user", "Hello")
        session_service.add_message(session.id, "assistant", "Hi there!")

        history = session_service.get_session_history(session.id)

        assert len(history) == 2
        assert history[0].role == "user"
        assert history[0].content == "Hello"
        assert history[1].role == "assistant"
        assert history[1].content == "Hi there!"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])