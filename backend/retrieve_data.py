"""
Module for retrieving stored embeddings and metadata from Qdrant vector database.
This module implements the functionality to connect to Qdrant and retrieve all stored embeddings and metadata.
"""

import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance, CollectionStatus
from qdrant_client.http import models
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantDataRetriever:
    """
    A class to handle Qdrant data retrieval operations.
    """

    def __init__(self, collection_name: str = "documents"):
        """
        Initialize the QdrantDataRetriever with connection parameters.

        Args:
            collection_name (str): Name of the collection to retrieve from
        """
        # Use environment variables for cloud Qdrant configuration
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("COLLECTION_NAME", collection_name)

        # Initialize Qdrant client for cloud instance
        try:
            if self.qdrant_url and self.qdrant_api_key:
                self.client = QdrantClient(
                    url=self.qdrant_url,
                    api_key=self.qdrant_api_key,
                    prefer_grpc=True
                )
                logger.info(f"Connected to Qdrant cloud at {self.qdrant_url}")
            else:
                # Fallback to local instance if cloud config not available
                host = os.getenv("QDRANT_HOST", "localhost")
                port = int(os.getenv("QDRANT_PORT", 6333))
                self.client = QdrantClient(host=host, port=port)
                logger.info(f"Connected to Qdrant at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise

    def check_collection_exists(self) -> bool:
        """
        Check if the specified collection exists in Qdrant.

        Returns:
            bool: True if collection exists, False otherwise
        """
        try:
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]
            return self.collection_name in collection_names
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            return False

    def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the collection.

        Returns:
            Dict[str, Any]: Collection information or None if error
        """
        try:
            if not self.check_collection_exists():
                logger.warning(f"Collection {self.collection_name} does not exist")
                return None

            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None

    def retrieve_all_embeddings(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve all embeddings and metadata from the Qdrant collection.

        Args:
            limit (int, optional): Maximum number of points to retrieve

        Returns:
            List[Dict[str, Any]]: List of points with embeddings and metadata
        """
        try:
            if not self.check_collection_exists():
                logger.error(f"Collection {self.collection_name} does not exist")
                return []

            # Get all points from the collection
            points = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=True
            )

            # Process the results
            retrieved_data = []
            for point in points[0]:  # points[0] contains the list of points
                data = {
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload,
                    "collection": self.collection_name
                }
                retrieved_data.append(data)

            logger.info(f"Retrieved {len(retrieved_data)} embeddings from Qdrant")
            return retrieved_data

        except Exception as e:
            logger.error(f"Error retrieving embeddings: {e}")
            return []

    def retrieve_embeddings_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve specific embeddings by their IDs.

        Args:
            ids (List[str]): List of point IDs to retrieve

        Returns:
            List[Dict[str, Any]]: List of points with embeddings and metadata
        """
        try:
            if not self.check_collection_exists():
                logger.error(f"Collection {self.collection_name} does not exist")
                return []

            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=ids,
                with_payload=True,
                with_vectors=True
            )

            retrieved_data = []
            for point in points:
                data = {
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload,
                    "collection": self.collection_name
                }
                retrieved_data.append(data)

            logger.info(f"Retrieved {len(retrieved_data)} embeddings by IDs")
            return retrieved_data

        except Exception as e:
            logger.error(f"Error retrieving embeddings by IDs: {e}")
            return []

    def get_all_metadata(self) -> List[Dict[str, Any]]:
        """
        Retrieve all metadata without the embeddings (vectors).

        Returns:
            List[Dict[str, Any]]: List of metadata without vectors
        """
        try:
            if not self.check_collection_exists():
                logger.error(f"Collection {self.collection_name} does not exist")
                return []

            points = self.client.scroll(
                collection_name=self.collection_name,
                with_payload=True,
                with_vectors=False
            )

            metadata_list = []
            for point in points[0]:  # points[0] contains the list of points
                metadata = {
                    "id": point.id,
                    "payload": point.payload,
                    "collection": self.collection_name
                }
                metadata_list.append(metadata)

            logger.info(f"Retrieved {len(metadata_list)} metadata entries from Qdrant")
            return metadata_list

        except Exception as e:
            logger.error(f"Error retrieving metadata: {e}")
            return []

    def search_by_content(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar content using vector similarity.

        Args:
            query_vector (List[float]): The vector to search for similarity
            top_k (int): Number of top results to return

        Returns:
            List[Dict[str, Any]]: List of similar points with embeddings and metadata
        """
        try:
            if not self.check_collection_exists():
                logger.error(f"Collection {self.collection_name} does not exist")
                return []

            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True,
                with_vectors=True
            )

            results = []
            for result in search_results:
                data = {
                    "id": result.id,
                    "vector": result.vector,
                    "payload": result.payload,
                    "score": result.score,
                    "collection": self.collection_name
                }
                results.append(data)

            logger.info(f"Found {len(results)} similar results")
            return results

        except Exception as e:
            logger.error(f"Error searching by content: {e}")
            return []


def main():
    """
    Main function to demonstrate the Qdrant data retrieval functionality.
    """
    try:
        # Initialize the retriever with the correct collection name
        retriever = QdrantDataRetriever(collection_name="humanoid_ai_book")

        # Check if collection exists
        if not retriever.check_collection_exists():
            logger.error(f"Collection '{retriever.collection_name}' does not exist in Qdrant")
            return

        # Get collection info
        collection_info = retriever.get_collection_info()
        if collection_info:
            logger.info(f"Collection Info: {collection_info}")

        # Retrieve all embeddings
        all_embeddings = retriever.retrieve_all_embeddings(limit=5)  # Limit for demo
        logger.info(f"Total embeddings retrieved: {len(all_embeddings)}")

        # Retrieve all metadata
        all_metadata = retriever.get_all_metadata()
        logger.info(f"Total metadata entries retrieved: {len(all_metadata)}")

        # Print first few entries as example
        if all_embeddings:
            logger.info("Sample embedding entry:")
            logger.info(f"ID: {all_embeddings[0]['id']}")
            logger.info(f"Payload keys: {list(all_embeddings[0]['payload'].keys())}")
            logger.info(f"Vector length: {len(all_embeddings[0]['vector'])}")

        return {
            "embeddings_count": len(all_embeddings),
            "metadata_count": len(all_metadata),
            "collection_info": collection_info
        }

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return None


if __name__ == "__main__":
    main()