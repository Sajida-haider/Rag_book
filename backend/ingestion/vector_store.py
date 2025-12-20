import os
import uuid
from typing import List, Dict, Optional
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class QdrantVectorStore:
    """
    Module to store embeddings vectors in Qdrant Cloud
    """

    def __init__(self, collection_name: str = "book_embeddings"):
        # Set up Qdrant connection using environment variables
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if not qdrant_url:
            raise ValueError("QDRANT_URL environment variable is required")

        if qdrant_api_key:
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            # For local Qdrant instances without API key
            self.client = QdrantClient(url=qdrant_url)

        self.collection_name = collection_name

    def create_collection(self, vector_size: int = 1536) -> bool:
        """
        Create Qdrant collection for storing embeddings
        Default vector size is 1536 for OpenAI's text-embedding-ada-002
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection {self.collection_name} already exists")
                return True

            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )

            logger.info(f"Collection {self.collection_name} created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating collection {self.collection_name}: {e}")
            return False

    def store_embeddings(self,
                        embeddings: List[List[float]],
                        contents: List[str],
                        metadata_list: List[Dict],
                        ids: List[str] = None) -> bool:
        """
        Store embedding vectors with unique IDs and metadata in Qdrant
        """
        try:
            if not embeddings or len(embeddings) != len(contents) or len(embeddings) != len(metadata_list):
                logger.error("Mismatch in embeddings, contents, and metadata list lengths")
                return False

            # Generate unique IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(len(embeddings))]

            # Prepare points for upsertion
            points = []
            for i, (embedding, content, metadata) in enumerate(zip(embeddings, contents, metadata_list)):
                point = PointStruct(
                    id=ids[i],
                    vector=embedding,
                    payload={
                        "content": content,
                        "module": metadata.get("module", ""),
                        "chapter": metadata.get("chapter", ""),
                        "file_path": metadata.get("file_path", ""),
                        "relative_path": metadata.get("relative_path", ""),
                        "chunk_id": metadata.get("chunk_id", i),
                        "created_at": metadata.get("created_at", ""),
                        **{k: v for k, v in metadata.items() if k not in ["module", "chapter", "file_path", "relative_path", "chunk_id", "created_at"]}
                    }
                )
                points.append(point)

            # Upsert points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.info(f"Successfully stored {len(points)} embeddings in Qdrant collection {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error storing embeddings in Qdrant: {e}")
            return False

    def store_single_embedding(self,
                             embedding: List[float],
                             content: str,
                             metadata: Dict,
                             id: str = None) -> bool:
        """
        Store a single embedding vector with metadata
        """
        if id is None:
            id = str(uuid.uuid4())

        return self.store_embeddings([embedding], [content], [metadata], [id])

    def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[Dict]:
        """
        Search for similar vectors in the collection
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )

            search_results = []
            for result in results:
                search_results.append({
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "module": result.payload.get("module", ""),
                    "chapter": result.payload.get("chapter", ""),
                    "file_path": result.payload.get("file_path", ""),
                    "score": result.score
                })

            logger.info(f"Found {len(search_results)} similar results")
            return search_results

        except Exception as e:
            logger.error(f"Error searching in Qdrant: {e}")
            return []

    def get_collection_info(self) -> Dict:
        """
        Get information about the collection
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.vectors_count,
                "vector_count": collection_info.vectors_count,
                "segments_count": collection_info.segments_count,
                "status": collection_info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}

    def delete_collection(self) -> bool:
        """
        Delete the collection (useful for reindexing)
        """
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Collection {self.collection_name} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

    def verify_stored_vectors(self, ids: List[str]) -> Dict[str, bool]:
        """
        Verify that specific vectors are stored in Qdrant
        """
        verification_results = {}

        for id in ids:
            try:
                # Try to retrieve the point by ID
                records = self.client.retrieve(
                    collection_name=self.collection_name,
                    ids=[id]
                )
                verification_results[id] = len(records) > 0
            except Exception as e:
                logger.error(f"Error verifying vector with ID {id}: {e}")
                verification_results[id] = False

        success_count = sum(1 for verified in verification_results.values() if verified)
        logger.info(f"Verified {success_count}/{len(ids)} vectors in Qdrant")
        return verification_results


# Example usage
if __name__ == "__main__":
    try:
        # Initialize the vector store
        vector_store = QdrantVectorStore()

        # Create collection
        success = vector_store.create_collection()
        print(f"Collection created: {success}")

        # Example embeddings and metadata (these would come from the embedder)
        sample_embeddings = [
            [0.1, 0.2, 0.3] * 512,  # Simulated embedding vector
            [0.4, 0.5, 0.6] * 512   # Simulated embedding vector
        ]

        sample_contents = [
            "This is the first chunk of content.",
            "This is the second chunk of content."
        ]

        sample_metadata = [
            {
                "module": "introduction",
                "chapter": "getting-started",
                "file_path": "/book/intro/getting-started.md",
                "relative_path": "intro/getting-started.md",
                "chunk_id": 0,
                "created_at": "2025-12-19"
            },
            {
                "module": "advanced",
                "chapter": "deep-dive",
                "file_path": "/book/advanced/deep-dive.md",
                "relative_path": "advanced/deep-dive.md",
                "chunk_id": 1,
                "created_at": "2025-12-19"
            }
        ]

        # Store embeddings
        store_success = vector_store.store_embeddings(sample_embeddings, sample_contents, sample_metadata)
        print(f"Embeddings stored: {store_success}")

        # Get collection info
        info = vector_store.get_collection_info()
        print(f"Collection info: {info}")

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Vector storage requires QDRANT_URL in environment variables")