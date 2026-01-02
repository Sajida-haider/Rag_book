"""Service for storing embeddings in Qdrant vector database"""

import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import sys
import os
# Add the backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from models import VectorRecord, Embedding, Metadata

# Load environment variables
load_dotenv()

class VectorStorageService:
    def __init__(self):
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        collection_name = os.getenv("COLLECTION_NAME", "humanoid_ai_book")

        if not qdrant_url:
            raise ValueError("QDRANT_URL environment variable is required")
        if not qdrant_api_key:
            raise ValueError("QDRANT_API_KEY environment variable is required")

        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            prefer_grpc=True
        )
        self.collection_name = collection_name
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create the collection if it doesn't exist"""
        try:
            # Check if collection exists
            collection_info = self.client.get_collection(self.collection_name)
            # Access the vector size properly - Qdrant API may return this differently
            # The configuration structure may be different than expected
            print(f"Collection {self.collection_name} already exists.")

            # For now, just use the existing collection and let the embedding service handle vector size
            # In a real scenario, we'd need to ensure the vector size matches
        except:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1024,  # Cohere multilingual-v3.0 embeddings are 1024 dimensions
                    distance=models.Distance.COSINE
                )
            )

    def store_embedding(self, record: VectorRecord) -> bool:
        """Store a single vector record in Qdrant"""
        try:
            # Check if vector already exists
            if self.vector_exists(record.id):
                print(f"Vector {record.id} already exists, skipping...")
                return True  # Return True as it's effectively already stored

            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=record.id,
                        vector=record.vector,
                        payload=record.payload
                    )
                ]
            )
            return True
        except Exception as e:
            print(f"Error storing embedding: {e}")
            return False

    def store_embeddings_batch(self, records: List[VectorRecord]) -> bool:
        """Store multiple vector records in Qdrant"""
        if not records:
            return True

        try:
            # Filter out records that already exist
            records_to_store = []
            for record in records:
                if not self.vector_exists(record.id):
                    records_to_store.append(record)
                else:
                    print(f"Vector {record.id} already exists, skipping...")

            if not records_to_store:
                print("All vectors already exist, no new vectors to store.")
                return True

            points = []
            for record in records_to_store:
                points.append(
                    models.PointStruct(
                        id=record.id,
                        vector=record.vector,
                        payload=record.payload
                    )
                )

            # Process in smaller batches to avoid memory issues with large datasets
            batch_size = 100  # Adjust as needed
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )

            print(f"Stored {len(records_to_store)} new vectors out of {len(records)} total records.")
            return True
        except Exception as e:
            print(f"Error storing embeddings batch: {e}")
            return False

    def search_similar(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors in the collection"""
        try:
            from qdrant_client.http import models
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

            return [
                {
                    "payload": result.payload,
                    "score": result.score,
                    "id": result.id
                }
                for result in results.points
            ]
        except Exception as e:
            print(f"Error searching similar vectors: {e}")
            return []

    def vector_exists(self, vector_id: str) -> bool:
        """Check if a vector with the given ID already exists in the collection"""
        try:
            # Try to retrieve the point by ID
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[vector_id]
            )
            return len(result) > 0
        except Exception as e:
            # If it's a UUID format error, it means the ID doesn't exist in the collection
            error_msg = str(e).lower()
            if "uuid" in error_msg or "parse" in error_msg or "invalid" in error_msg:
                # This is likely an invalid UUID format, so the vector doesn't exist
                return False
            print(f"Error checking if vector exists: {e}")
            return False

    def get_all_records(self) -> List[VectorRecord]:
        """Retrieve all records from the collection"""
        try:
            results = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000  # Adjust as needed
            )

            records = []
            for point in results[0]:  # results is (points, next_page_offset)
                records.append(
                    VectorRecord(
                        id=point.id,
                        payload=point.payload,
                        vector=point.vector,
                        created_at=point.payload.get("created_at")  # This may need adjustment
                    )
                )

            return records
        except Exception as e:
            print(f"Error retrieving records: {e}")
            return []