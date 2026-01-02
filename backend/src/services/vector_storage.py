from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
import logging
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetrievedContent(BaseModel):
    content: str
    source: str
    score: float

class VectorStorageService:
    """
    Service for interacting with Qdrant vector database to store and retrieve embeddings
    """

    def __init__(self):
        # Initialize Qdrant client with environment variables
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "book_embeddings")

        if not self.qdrant_url:
            raise ValueError("QDRANT_URL environment variable is required")

        # Initialize Qdrant client
        if self.qdrant_api_key:
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
                prefer_grpc=False  # Using HTTP instead of gRPC for simplicity
            )
        else:
            self.client = QdrantClient(url=self.qdrant_url)

        logger.info(f"Connected to Qdrant at {self.qdrant_url}, collection: {self.collection_name}")

    async def search_similar(self, query_vector: List[float], limit: int = 5) -> List[RetrievedContent]:
        """
        Search for similar content in the vector database based on the query vector

        Args:
            query_vector: The vector representation of the query
            limit: Maximum number of results to return

        Returns:
            List of retrieved content with scores and sources
        """
        try:
            # Perform vector similarity search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True
            )

            # Format results as RetrievedContent objects
            results = []
            for hit in search_results:
                payload = hit.payload
                results.append(RetrievedContent(
                    content=payload.get("content", ""),
                    source=payload.get("source", ""),
                    score=hit.score
                ))

            logger.info(f"Found {len(results)} similar items for query")
            return results

        except Exception as e:
            logger.error(f"Error searching in Qdrant: {str(e)}")
            raise

    async def search_by_text(self, query_text: str, limit: int = 5) -> List[RetrievedContent]:
        """
        Search for similar content using text query (requires embedding generation)

        Args:
            query_text: The text query to search for
            limit: Maximum number of results to return

        Returns:
            List of retrieved content with scores and sources
        """
        try:
            # In a real implementation, we would generate embeddings for the query text
            # For now, we'll use a placeholder - in practice you'd use an embedding model
            # like OpenAI's embeddings API or a local model
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Generate embedding for the query text
            response = client.embeddings.create(
                input=query_text,
                model="text-embedding-ada-002"  # Using OpenAI's embedding model
            )

            query_vector = response.data[0].embedding

            # Search using the generated vector
            return await self.search_similar(query_vector, limit)

        except Exception as e:
            logger.error(f"Error searching by text in Qdrant: {str(e)}")
            raise

    def collection_exists(self) -> bool:
        """
        Check if the specified collection exists in Qdrant

        Returns:
            True if collection exists, False otherwise
        """
        try:
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]
            return self.collection_name in collection_names
        except Exception as e:
            logger.error(f"Error checking if collection exists: {str(e)}")
            return False

    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection

        Returns:
            Dictionary with collection information
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.vectors_count,
                "vectors_count": collection_info.config.params.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}