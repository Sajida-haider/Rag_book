#!/usr/bin/env python3
"""Script to verify that full content is being extracted and stored in Qdrant"""

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

print(f"Checking collection: {collection_name}")
print(f"Qdrant URL: {qdrant_url}")

try:
    # Get collection info
    collection_info = client.get_collection(collection_name)
    print(f"\n[SUCCESS] Collection '{collection_name}' exists!")
    print(f"Vector count: {collection_info.points_count}")

    if collection_info.points_count > 0:
        print(f"\n[INFO] Analyzing content quality in collection:")

        # Scroll to get sample records
        records, next_page = client.scroll(
            collection_name=collection_name,
            limit=10,  # Get first 10 records for analysis
            with_payload=True,
            with_vectors=False
        )

        total_chunks = 0
        total_content_chars = 0
        short_content_count = 0  # Count chunks with less than 200 characters
        long_content_count = 0   # Count chunks with 200+ characters

        for i, record in enumerate(records):
            content = record.payload.get('content', '')
            content_length = len(content)
            total_content_chars += content_length
            total_chunks += 1

            print(f"\nRecord {i+1}:")
            print(f"  URL: {record.payload.get('url', 'N/A')}")
            print(f"  Title: {record.payload.get('title', 'N/A')}")
            print(f"  Content length: {content_length} characters")
            print(f"  Chunk index: {record.payload.get('chunk_index', 'N/A')}")
            print(f"  Total chunks for page: {record.payload.get('total_chunks', 'N/A')}")
            print(f"  Content preview: {content[:150]}...")

            if content_length < 200:
                short_content_count += 1
                print(f"  [SHORT] Content is less than 200 characters")
            else:
                long_content_count += 1
                print(f"  [GOOD] Content has {content_length} characters")

        print(f"\n[ANALYSIS SUMMARY]")
        print(f"Total records analyzed: {total_chunks}")
        print(f"Records with short content (<200 chars): {short_content_count}")
        print(f"Records with good content (≥200 chars): {long_content_count}")
        print(f"Average content length: {total_content_chars // total_chunks if total_chunks > 0 else 0} characters")

        if long_content_count > short_content_count:
            print(f"\n[SUCCESS] Content extraction is working properly!")
            print(f"Majority of records ({long_content_count}/{total_chunks}) have substantial content.")
            print(f"This indicates the JavaScript-aware scraper is successfully extracting full page content.")
        else:
            print(f"\n[CONCERN] Many records have minimal content.")
            print(f"Majority of records ({short_content_count}/{total_chunks}) have minimal content.")
            print(f"This suggests the content extraction still needs improvement.")
    else:
        print(f"\n[WARNING] Collection '{collection_name}' exists but is empty.")
        print("Run 'python main.py' to ingest data first.")

except Exception as e:
    print(f"\n[ERROR] Error accessing collection '{collection_name}': {e}")
    print("Possible issues:")
    print("1. Collection doesn't exist yet (run ingestion first)")
    print("2. Incorrect QDRANT_URL or QDRANT_API_KEY")
    print("3. Network connectivity issues")