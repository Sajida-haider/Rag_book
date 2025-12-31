"""Script to reset Qdrant collection with correct vector dimensions"""

import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Qdrant client
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = os.getenv("COLLECTION_NAME", "humanoid_ai_book")

client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
    prefer_grpc=True
)

print(f"Resetting collection: {collection_name}")
print(f"Qdrant URL: {qdrant_url}")

try:
    # Delete existing collection
    try:
        client.delete_collection(collection_name)
        print(f"[SUCCESS] Deleted existing collection '{collection_name}'")
    except Exception as e:
        print(f"[WARNING] Collection '{collection_name}' may not exist yet: {e}")

    # Create collection with correct vector size
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=1024,  # Cohere embeddings are 1024 dimensions
            distance=models.Distance.COSINE
        )
    )

    print(f"[SUCCESS] Created new collection '{collection_name}' with 1024-dimensional vectors")

    # Verify collection info
    collection_info = client.get_collection(collection_name)
    print(f"[SUCCESS] Collection '{collection_name}' now exists with {collection_info.config.params.vectors.size}-dimensional vectors")

except Exception as e:
    print(f"[ERROR] Error resetting collection: {e}")
    print("Possible issues:")
    print("1. Incorrect QDRANT_URL or QDRANT_API_KEY")
    print("2. Network connectivity issues")
    print("3. Insufficient permissions")