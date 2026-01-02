"""
End-to-end test for the RAG chatbot functionality
This test simulates the complete flow from API request to response
"""
import asyncio
import sys
import os

# Add the backend src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.main import ChatRequest
from src.services.rag_service import RAGService
from src.services.vector_storage import VectorStorageService
from src.services.session_service import SessionService


async def test_end_to_end_flow():
    """
    Test the complete end-to-end flow of the RAG chatbot:
    1. Request validation
    2. Session management
    3. Content retrieval
    4. AI response generation
    5. Response formatting
    """
    print("Starting end-to-end test...")

    try:
        # Initialize services (with mocks in a real test)
        from unittest.mock import Mock, AsyncMock, patch

        # Mock external dependencies to avoid actual API calls during testing
        with patch('src.services.vector_storage.QdrantClient'), \
             patch('src.services.rag_service.OpenAI'):

            # Initialize the RAG service
            rag_service = RAGService()

            # Mock the vector storage search to return test data
            mock_content = [
                {
                    "content": "The RAG system combines retrieval and generation for better responses.",
                    "source": "chapter_1_introduction.md",
                    "score": 0.95
                }
            ]
            rag_service.vector_storage.search_by_text = AsyncMock(return_value=mock_content)

            # Mock the OpenAI response
            class MockChoice:
                def __init__(self):
                    self.message = Mock()
                    self.message.content = "The RAG system combines retrieval and generation to provide better responses based on relevant context."

            class MockCompletion:
                def __init__(self):
                    self.choices = [MockChoice()]

            rag_service.openai_client.chat.completions.create = Mock(return_value=MockCompletion())

            # Test the process_message function
            result = await rag_service.process_message(
                message="What is the RAG system?",
                session_id="test-session-e2e"
            )

            # Validate the result
            assert "response" in result
            assert "sources" in result
            assert "retrieved_content" in result

            print("✅ End-to-end test passed!")
            print(f"Response: {result['response'][:100]}...")
            print(f"Sources: {result['sources']}")
            print(f"Retrieved content count: {len(result['retrieved_content'])}")

            # Test with no matching content
            rag_service.vector_storage.search_by_text = AsyncMock(return_value=[])
            result_no_content = await rag_service.process_message(
                message="What is a non-existent concept?",
                session_id="test-session-no-content"
            )

            assert "response" in result_no_content
            assert result_no_content["response"].startswith("I couldn't find specific information")
            assert result_no_content["sources"] == []
            assert result_no_content["retrieved_content"] == []

            print("✅ Test with no content also passed!")

    except Exception as e:
        print(f"❌ End-to-end test failed: {str(e)}")
        raise

    print("✅ All end-to-end tests completed successfully!")


def test_api_request_validation():
    """
    Test the API request validation
    """
    print("\nTesting API request validation...")

    # Test valid request
    valid_request = ChatRequest(message="Hello", session_id="test-session")
    assert valid_request.message == "Hello"
    assert valid_request.session_id == "test-session"
    print("✅ Valid request validation passed!")

    # Test request without session_id (should be handled by API)
    request_no_session = ChatRequest(message="Hello")
    assert request_no_session.message == "Hello"
    assert request_no_session.session_id is None
    print("✅ Request without session_id validation passed!")

    print("✅ All API validation tests passed!")


if __name__ == "__main__":
    print("Running end-to-end tests for RAG chatbot...")

    # Run the tests
    asyncio.run(test_end_to_end_flow())
    test_api_request_validation()

    print("\n🎉 All end-to-end tests completed successfully!")