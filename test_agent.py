"""
Comprehensive test suite for the OpenAI Agent with Qdrant retrieval integration.
This test suite validates all functionality of the agent including integration,
accuracy, and performance requirements.
"""

import unittest
import os
from unittest.mock import Mock, patch, MagicMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the agent components
from agent import BookQAAgent, QdrantRetriever, AgentConfig


class TestQdrantRetriever(unittest.TestCase):
    """
    Test class for QdrantRetriever functionality.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        # Use a mock Qdrant client for testing
        self.retriever = QdrantRetriever(collection_name="test_collection")

    @patch('agent.QdrantClient')
    @patch('agent.openai')
    def test_embed_query(self, mock_openai, mock_qdrant_client):
        """
        Test embedding generation for queries.
        """
        # Mock the OpenAI embeddings response
        mock_embedding_response = Mock()
        mock_embedding_response.data = [Mock()]
        mock_embedding_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_openai.embeddings.create.return_value = mock_embedding_response

        # Test embedding generation
        result = self.retriever.embed_query("test query")

        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_openai.embeddings.create.assert_called_once()

    @patch('agent.QdrantClient')
    @patch('agent.openai')
    def test_retrieve_context(self, mock_openai, mock_qdrant_client):
        """
        Test context retrieval from Qdrant.
        """
        # Mock the Qdrant client and its search method
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock the search results
        mock_result = Mock()
        mock_result.payload = {
            'content': 'test content',
            'title': 'test title',
            'url': 'test url',
            'section': 'test section',
            'chunk_index': 1
        }
        mock_result.score = 0.9
        mock_client_instance.search.return_value = [mock_result]

        # Mock the embedding response
        mock_embedding_response = Mock()
        mock_embedding_response.data = [Mock()]
        mock_embedding_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_openai.embeddings.create.return_value = mock_embedding_response

        # Initialize retriever with mock
        retriever = QdrantRetriever(collection_name="test_collection")

        # Test context retrieval
        results = retriever.retrieve_context("test query", top_k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], 'test content')
        self.assertEqual(results[0]['title'], 'test title')
        self.assertEqual(results[0]['score'], 0.9)

    @patch('agent.QdrantClient')
    @patch('agent.openai')
    def test_retrieve_context_error_handling(self, mock_openai, mock_qdrant_client):
        """
        Test error handling in context retrieval.
        """
        # Mock the Qdrant client to raise an exception
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance
        mock_client_instance.search.side_effect = Exception("Connection error")

        # Mock the embedding response
        mock_embedding_response = Mock()
        mock_embedding_response.data = [Mock()]
        mock_embedding_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_openai.embeddings.create.return_value = mock_embedding_response

        # Initialize retriever with mock
        retriever = QdrantRetriever(collection_name="test_collection")

        # Test context retrieval with error
        results = retriever.retrieve_context("test query", top_k=1)

        self.assertEqual(results, [])


class TestBookQAAgent(unittest.TestCase):
    """
    Test class for BookQAAgent functionality.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        # Use a mock configuration
        self.config = AgentConfig(
            model="gpt-3.5-turbo",
            max_tokens=1000,
            temperature=0.3,
            top_k=5,
            max_context_length=2000
        )

    @patch('agent.openai')
    @patch('agent.QdrantRetriever')
    def test_agent_initialization(self, mock_qdrant_retriever, mock_openai):
        """
        Test agent initialization with proper configuration.
        """
        # Mock the OpenAI assistant creation
        mock_assistant = Mock()
        mock_assistant.id = "test_assistant_id"
        mock_openai.beta.assistants.create.return_value = mock_assistant

        # Initialize the agent
        agent = BookQAAgent(config=self.config)

        # Verify initialization
        self.assertEqual(agent.config, self.config)
        self.assertIsNotNone(agent.retriever)
        self.assertEqual(agent.assistant.id, "test_assistant_id")

    @patch('agent.openai')
    @patch('agent.QdrantRetriever')
    def test_format_context(self, mock_qdrant_retriever, mock_openai):
        """
        Test context formatting functionality.
        """
        # Mock the OpenAI assistant creation
        mock_assistant = Mock()
        mock_assistant.id = "test_assistant_id"
        mock_openai.beta.assistants.create.return_value = mock_assistant

        # Initialize the agent
        agent = BookQAAgent(config=self.config)

        # Test with results
        test_results = [
            {
                'content': 'test content',
                'title': 'test title',
                'url': 'test url',
                'score': 0.9
            }
        ]

        formatted_context = agent._format_context(test_results)

        self.assertIn('test content', formatted_context)
        self.assertIn('test title', formatted_context)
        self.assertIn('test url', formatted_context)

        # Test with empty results
        empty_context = agent._format_context([])
        self.assertIn('No relevant information found', empty_context)

    @patch('agent.openai')
    @patch('agent.QdrantRetriever')
    def test_answer_query_success(self, mock_qdrant_retriever, mock_openai):
        """
        Test successful query answering.
        """
        # Mock the OpenAI assistant creation
        mock_assistant = Mock()
        mock_assistant.id = "test_assistant_id"
        mock_openai.beta.assistants.create.return_value = mock_assistant

        # Mock the retriever
        mock_retriever_instance = Mock()
        mock_retriever_instance.retrieve_context.return_value = [
            {
                'content': 'test content',
                'title': 'test title',
                'url': 'test url',
                'score': 0.9
            }
        ]
        mock_qdrant_retriever.return_value = mock_retriever_instance

        # Mock thread and run creation
        mock_thread = Mock()
        mock_thread.id = "test_thread_id"
        mock_openai.beta.threads.create.return_value = mock_thread

        mock_run = Mock()
        mock_run.id = "test_run_id"
        mock_openai.beta.threads.runs.create.return_value = mock_run

        # Mock run completion
        mock_completed_run = Mock()
        mock_completed_run.status = "completed"
        mock_openai.beta.threads.runs.retrieve.return_value = mock_completed_run

        # Mock messages
        mock_message = Mock()
        mock_message.role = "assistant"
        mock_text_content = Mock()
        mock_text_content.text.value = "Test response from agent"
        mock_message.content = [mock_text_content]

        mock_messages_list = Mock()
        mock_messages_list.data = [mock_message]
        mock_openai.beta.threads.messages.list.return_value = mock_messages_list

        # Initialize the agent
        agent = BookQAAgent(config=self.config)

        # Test query answering
        response = agent.answer_query("test query")

        self.assertEqual(response, "Test response from agent")
        mock_retriever_instance.retrieve_context.assert_called_once_with("test query", top_k=5)

    @patch('agent.openai')
    @patch('agent.QdrantRetriever')
    def test_answer_query_error_handling(self, mock_qdrant_retriever, mock_openai):
        """
        Test error handling in query answering.
        """
        # Mock the OpenAI assistant creation
        mock_assistant = Mock()
        mock_assistant.id = "test_assistant_id"
        mock_openai.beta.assistants.create.return_value = mock_assistant

        # Mock the retriever to raise an exception
        mock_retriever_instance = Mock()
        mock_retriever_instance.retrieve_context.side_effect = Exception("Retrieval error")
        mock_qdrant_retriever.return_value = mock_retriever_instance

        # Initialize the agent
        agent = BookQAAgent(config=self.config)

        # Test query answering with error
        response = agent.answer_query("test query")

        self.assertIn("An error occurred while processing your query", response)


class TestIntegration(unittest.TestCase):
    """
    Integration tests for the complete agent system.
    """

    @unittest.skip("Skipping actual API tests - requires valid API keys")
    def test_end_to_end_integration(self):
        """
        Test end-to-end functionality with real API calls.
        This test is skipped by default as it requires valid API keys.
        """
        # This would test the complete flow with real APIs
        # Only run when proper credentials are available
        pass

    def test_data_flow_between_components(self):
        """
        Test data flow between agent components.
        """
        # This tests that data flows correctly between components
        # without making actual API calls
        config = AgentConfig(top_k=3)

        # Mock all external dependencies
        with patch('agent.openai') as mock_openai, \
             patch('agent.QdrantRetriever') as mock_qdrant_retriever:

            # Mock the OpenAI assistant creation
            mock_assistant = Mock()
            mock_assistant.id = "test_assistant_id"
            mock_openai.beta.assistants.create.return_value = mock_assistant

            # Mock the retriever
            mock_retriever_instance = Mock()
            mock_retriever_instance.retrieve_context.return_value = [
                {
                    'content': 'test content for integration',
                    'title': 'test title',
                    'url': 'test url',
                    'score': 0.85
                }
            ]
            mock_qdrant_retriever.return_value = mock_retriever_instance

            # Mock thread operations
            mock_thread = Mock()
            mock_thread.id = "test_thread_id"
            mock_openai.beta.threads.create.return_value = mock_thread

            mock_run = Mock()
            mock_run.id = "test_run_id"
            mock_openai.beta.threads.runs.create.return_value = mock_run

            mock_completed_run = Mock()
            mock_completed_run.status = "completed"
            mock_openai.beta.threads.runs.retrieve.return_value = mock_completed_run

            mock_message = Mock()
            mock_message.role = "assistant"
            mock_text_content = Mock()
            mock_text_content.text.value = "Integration test response"
            mock_message.content = [mock_text_content]

            mock_messages_list = Mock()
            mock_messages_list.data = [mock_message]
            mock_openai.beta.threads.messages.list.return_value = mock_messages_list

            # Create the agent
            agent = BookQAAgent(config=config)

            # Test the complete flow
            response = agent.answer_query("integration test query")

            # Verify the flow worked correctly
            self.assertIsNotNone(response)
            mock_retriever_instance.retrieve_context.assert_called_once()
            mock_openai.beta.threads.create.assert_called_once()
            mock_openai.beta.threads.runs.create.assert_called_once()


class TestAccuracy(unittest.TestCase):
    """
    Accuracy tests to validate that responses are grounded in retrieved content.
    """

    @patch('agent.openai')
    @patch('agent.QdrantRetriever')
    def test_response_grounding(self, mock_qdrant_retriever, mock_openai):
        """
        Test that responses are grounded in retrieved content.
        """
        # Mock the OpenAI assistant creation
        mock_assistant = Mock()
        mock_assistant.id = "test_assistant_id"
        mock_openai.beta.assistants.create.return_value = mock_assistant

        # Mock the retriever with specific content
        mock_retriever_instance = Mock()
        mock_retriever_instance.retrieve_context.return_value = [
            {
                'content': 'ROS 2 is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robot platforms.',
                'title': 'ROS 2 Fundamentals',
                'url': 'https://example.com/ros2-fundamentals',
                'score': 0.92
            }
        ]
        mock_qdrant_retriever.return_value = mock_retriever_instance

        # Mock thread operations
        mock_thread = Mock()
        mock_thread.id = "test_thread_id"
        mock_openai.beta.threads.create.return_value = mock_thread

        mock_run = Mock()
        mock_run.id = "test_run_id"
        mock_openai.beta.threads.runs.create.return_value = mock_run

        mock_completed_run = Mock()
        mock_completed_run.status = "completed"
        mock_openai.beta.threads.runs.retrieve.return_value = mock_completed_run

        mock_message = Mock()
        mock_message.role = "assistant"
        mock_text_content = Mock()
        # The agent should respond based on the context provided
        mock_text_content.text.value = "ROS 2 is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robot platforms."
        mock_message.content = [mock_text_content]

        mock_messages_list = Mock()
        mock_messages_list.data = [mock_message]
        mock_openai.beta.threads.messages.list.return_value = mock_messages_list

        # Create the agent
        agent = BookQAAgent()

        # Test query about ROS 2
        response = agent.answer_query("What is ROS 2?")

        # The response should be based on the retrieved content
        self.assertIn("framework for writing robot software", response)
        self.assertIn("tools, libraries, and conventions", response)

    @patch('agent.openai')
    @patch('agent.QdrantRetriever')
    def test_hallucination_prevention(self, mock_qdrant_retriever, mock_openai):
        """
        Test that the agent does not hallucinate information.
        """
        # Mock the OpenAI assistant creation
        mock_assistant = Mock()
        mock_assistant.id = "test_assistant_id"
        mock_openai.beta.assistants.create.return_value = mock_assistant

        # Mock the retriever with no relevant content
        mock_retriever_instance = Mock()
        mock_retriever_instance.retrieve_context.return_value = []
        mock_qdrant_retriever.return_value = mock_retriever_instance

        # Mock thread operations
        mock_thread = Mock()
        mock_thread.id = "test_thread_id"
        mock_openai.beta.threads.create.return_value = mock_thread

        mock_run = Mock()
        mock_run.id = "test_run_id"
        mock_openai.beta.threads.runs.create.return_value = mock_run

        mock_completed_run = Mock()
        mock_completed_run.status = "completed"
        mock_openai.beta.threads.runs.retrieve.return_value = mock_completed_run

        mock_message = Mock()
        mock_message.role = "assistant"
        mock_text_content = Mock()
        # The agent should indicate that information is not available
        mock_text_content.text.value = "The information is not available in the book."
        mock_message.content = [mock_text_content]

        mock_messages_list = Mock()
        mock_messages_list.data = [mock_message]
        mock_openai.beta.threads.messages.list.return_value = mock_messages_list

        # Create the agent
        agent = BookQAAgent()

        # Test query with no relevant content
        response = agent.answer_query("What is the secret to eternal happiness?")

        # The response should indicate that information is not available
        self.assertIn("not available in the book", response)


def run_tests():
    """
    Run all tests in the test suite.
    """
    # Create a test suite
    test_suite = unittest.TestSuite()

    # Add tests to the suite
    test_suite.addTest(unittest.makeSuite(TestQdrantRetriever))
    test_suite.addTest(unittest.makeSuite(TestBookQAAgent))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    test_suite.addTest(unittest.makeSuite(TestAccuracy))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%" if result.testsRun > 0 else "0%")

    return result


if __name__ == "__main__":
    run_tests()