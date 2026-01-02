"""Script to check the actual URLs stored in the Qdrant database"""
import os
from qdrant_client import QdrantClient
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

print(f"Checking URLs in collection: {collection_name}")
print(f"Qdrant URL: {qdrant_url}")

# Get a few sample records to check the URLs
print("Retrieving sample records from collection...")
sample_records = client.scroll(
    collection_name=collection_name,
    with_payload=True,
    with_vectors=False,
    limit=10
)[0]

print(f"Found {len(sample_records)} total records in the collection")
print("\nSample URLs from the database:")
for i, record in enumerate(sample_records):
    payload = record.payload
    url = payload.get('url', 'N/A')
    title = payload.get('title', 'N/A')
    print(f"{i+1}. URL: {url}")
    print(f"   Title: {title}")
    print()