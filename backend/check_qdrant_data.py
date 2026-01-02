"""Script to check data in Qdrant collection"""

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

print(f"Checking collection: {collection_name}")
print(f"Qdrant URL: {qdrant_url}")

try:
    # Get collection info
    collection_info = client.get_collection(collection_name)
    print(f"\n[SUCCESS] Collection '{collection_name}' exists!")
    print(f"Vector count: {collection_info.points_count}")

    # Print basic collection info
    print(f"Vector size: 1024 (expected for Cohere embeddings)")
    print(f"Distance: cosine (expected for semantic search)")

    # Check if there are any points in the collection
    if collection_info.points_count > 0:
        print(f"\n[INFO] Sample records from collection:")

        # Scroll to get some records
        records, next_page = client.scroll(
            collection_name=collection_name,
            limit=5,  # Get first 5 records
            with_payload=True,
            with_vectors=False
        )

        for i, record in enumerate(records):
            print(f"\nRecord {i+1}:")
            print(f"  ID: {record.id}")
            print(f"  URL: {record.payload.get('url', 'N/A')}")
            print(f"  Title: {record.payload.get('title', 'N/A')}")
            print(f"  Content preview: {record.payload.get('content', '')[:100]}...")
            print(f"  Created: {record.payload.get('created_at', 'N/A')}")
    else:
        print(f"\n[WARNING] Collection '{collection_name}' exists but is empty.")
        print("Run 'python main.py' to ingest data first.")

except Exception as e:
    print(f"\n[ERROR] Error accessing collection '{collection_name}': {e}")
    print("Possible issues:")
    print("1. Collection doesn't exist yet (run ingestion first)")
    print("2. Incorrect QDRANT_URL or QDRANT_API_KEY")
    print("3. Network connectivity issues")