"""
Test script for Qdrant data retrieval functionality.
This script tests the retrieve_data.py module to ensure it can connect to Qdrant
and retrieve embeddings and metadata correctly.
"""

import unittest
import os
from unittest.mock import Mock, patch
from backend.retrieve_data import QdrantDataRetriever


class TestQdrantDataRetriever(unittest.TestCase):
    """
    Test class for QdrantDataRetriever functionality.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        # Use a mock Qdrant client for testing
        self.retriever = QdrantDataRetriever(host="localhost", port=6333, collection_name="test_collection")

    @patch('backend.retrieve_data.QdrantClient')
    def test_initialization(self, mock_client):
        """
        Test initialization of QdrantDataRetriever.
        """
        # Mock the client connection
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        # Initialize retriever with mock
        retriever = QdrantDataRetriever(host="localhost", port=6333, collection_name="test_collection")

        # Verify client was initialized
        self.assertIsNotNone(retriever)
        self.assertEqual(retriever.collection_name, "test_collection")

    @patch('backend.retrieve_data.QdrantClient')
    def test_check_collection_exists(self, mock_client):
        """
        Test checking if a collection exists.
        """
        # Mock the client and its methods
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        # Mock collections response
        mock_collection = Mock()
        mock_collection.name = "test_collection"
        mock_collections = Mock()
        mock_collections.collections = [mock_collection]
        mock_client_instance.get_collections.return_value = mock_collections

        # Initialize retriever with mock
        retriever = QdrantDataRetriever(host="localhost", port=6333, collection_name="test_collection")

        # Test collection exists
        result = retriever.check_collection_exists()
        self.assertTrue(result)

    @patch('backend.retrieve_data.QdrantClient')
    def test_get_collection_info(self, mock_client):
        """
        Test getting collection information.
        """
        # Mock the client and its methods
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        # Mock collection response
        mock_collection = Mock()
        mock_collection.name = "test_collection"
        mock_collection.config = Mock()
        mock_collection.config.params = Mock()
        mock_collection.config.params.vectors = Mock()
        mock_collection.config.params.vectors.size = 1536
        mock_collection.config.params.vectors.distance = "Cosine"
        mock_collection.points_count = 100
        mock_collection.status = "green"

        mock_client_instance.get_collection.return_value = mock_collection
        mock_client_instance.get_collections.return_value = Mock(collections=[mock_collection])

        # Initialize retriever with mock
        retriever = QdrantDataRetriever(host="localhost", port=6333, collection_name="test_collection")

        # Test getting collection info
        result = retriever.get_collection_info()
        self.assertIsNotNone(result)
        self.assertEqual(result["vector_size"], 1536)
        self.assertEqual(result["count"], 100)

    @patch('backend.retrieve_data.QdrantClient')
    def test_retrieve_all_embeddings(self, mock_client):
        """
        Test retrieving all embeddings from Qdrant.
        """
        # Mock the client and its methods
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        # Mock point response
        mock_point = Mock()
        mock_point.id = "test_id_1"
        mock_point.vector = [0.1, 0.2, 0.3]
        mock_point.payload = {"text": "test content", "source": "test_source"}

        # Mock scroll response (returns tuple of points and next_page)
        mock_client_instance.scroll.return_value = ([mock_point], None)
        mock_client_instance.get_collections.return_value = Mock(collections=[Mock(name="test_collection")])

        # Initialize retriever with mock
        retriever = QdrantDataRetriever(host="localhost", port=6333, collection_name="test_collection")

        # Test retrieving embeddings
        result = retriever.retrieve_all_embeddings()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test_id_1")
        self.assertEqual(result[0]["payload"]["text"], "test content")

    @patch('backend.retrieve_data.QdrantClient')
    def test_retrieve_embeddings_by_ids(self, mock_client):
        """
        Test retrieving embeddings by specific IDs.
        """
        # Mock the client and its methods
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        # Mock point response
        mock_point = Mock()
        mock_point.id = "test_id_1"
        mock_point.vector = [0.1, 0.2, 0.3]
        mock_point.payload = {"text": "test content", "source": "test_source"}

        mock_client_instance.retrieve.return_value = [mock_point]
        mock_client_instance.get_collections.return_value = Mock(collections=[Mock(name="test_collection")])

        # Initialize retriever with mock
        retriever = QdrantDataRetriever(host="localhost", port=6333, collection_name="test_collection")

        # Test retrieving embeddings by IDs
        result = retriever.retrieve_embeddings_by_ids(["test_id_1"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test_id_1")

    @patch('backend.retrieve_data.QdrantClient')
    def test_get_all_metadata(self, mock_client):
        """
        Test retrieving all metadata without embeddings.
        """
        # Mock the client and its methods
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        # Mock point response
        mock_point = Mock()
        mock_point.id = "test_id_1"
        mock_point.payload = {"text": "test content", "source": "test_source"}

        # Mock scroll response (returns tuple of points and next_page)
        mock_client_instance.scroll.return_value = ([mock_point], None)
        mock_client_instance.get_collections.return_value = Mock(collections=[Mock(name="test_collection")])

        # Initialize retriever with mock
        retriever = QdrantDataRetriever(host="localhost", port=6333, collection_name="test_collection")

        # Test retrieving metadata
        result = retriever.get_all_metadata()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test_id_1")
        self.assertEqual(result[0]["payload"]["text"], "test content")

    @patch('backend.retrieve_data.QdrantClient')
    def test_search_by_content(self, mock_client):
        """
        Test searching for similar content using vector similarity.
        """
        # Mock the client and its methods
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        # Mock search result
        mock_result = Mock()
        mock_result.id = "test_id_1"
        mock_result.vector = [0.1, 0.2, 0.3]
        mock_result.payload = {"text": "similar content", "source": "test_source"}
        mock_result.score = 0.95

        mock_client_instance.search.return_value = [mock_result]
        mock_client_instance.get_collections.return_value = Mock(collections=[Mock(name="test_collection")])

        # Initialize retriever with mock
        retriever = QdrantDataRetriever(host="localhost", port=6333, collection_name="test_collection")

        # Test searching by content
        result = retriever.search_by_content([0.1, 0.2, 0.3])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test_id_1")
        self.assertEqual(result[0]["score"], 0.95)


def test_connection_to_qdrant():
    """
    Test actual connection to Qdrant (if available).
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Try to connect to Qdrant with default settings
        retriever = QdrantDataRetriever()

        # Check if collection exists
        if retriever.check_collection_exists():
            logger.info("Successfully connected to Qdrant and found collection")

            # Get collection info
            info = retriever.get_collection_info()
            if info:
                logger.info(f"Collection info: {info}")

            # Try to retrieve some data
            embeddings = retriever.retrieve_all_embeddings(limit=5)
            logger.info(f"Retrieved {len(embeddings)} sample embeddings")

            return True
        else:
            logger.warning("Collection does not exist, but connection was successful")
            return True

    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return False


def run_tests():
    """
    Run all tests.
    """
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Test actual connection if Qdrant is available
    print("\nTesting actual connection to Qdrant (if available)...")
    connection_result = test_connection_to_qdrant()
    print(f"Connection test result: {'PASS' if connection_result else 'FAIL'}")


if __name__ == "__main__":
    run_tests()