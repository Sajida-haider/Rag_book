"""Script to retrieve and display existing content from Qdrant database"""
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

def retrieve_existing_content():
    """Retrieve and display all existing content from Qdrant database"""
    print(f"Retrieving all existing content from collection: {collection_name}")

    # Get all records
    all_records = client.scroll(
        collection_name=collection_name,
        with_payload=True,
        with_vectors=False,
        limit=100
    )[0]

    print(f"Found {len(all_records)} total records in the collection")

    # Group records by module
    modules = {
        'Module 1': [],
        'Module 2': [],
        'Module 3': [],
        'Module 4': [],
        'Other': []
    }

    for record in all_records:
        payload = record.payload
        url = payload.get('url', '').lower()

        if 'module-1' in url:
            modules['Module 1'].append((record.id, payload))
        elif 'module-2' in url:
            modules['Module 2'].append((record.id, payload))
        elif 'module-3' in url:
            modules['Module 3'].append((record.id, payload))
        elif 'module-4' in url:
            modules['Module 4'].append((record.id, payload))
        else:
            modules['Other'].append((record.id, payload))

    # Display content by module
    for module_name, records in modules.items():
        if records:  # Only show modules that have records
            print(f"\n{'='*80}")
            print(f"{module_name} CONTENT")
            print(f"{'='*80}")

            for i, (record_id, payload) in enumerate(records, 1):
                print(f"\n{module_name} - Chapter {i}:")
                print(f"  ID: {record_id}")
                print(f"  URL: {payload.get('url', 'N/A')}")
                print(f"  Title: {payload.get('title', 'N/A')}")
                print(f"  Content length: {len(payload.get('content', ''))} characters")

                # Show the actual content
                content = payload.get('content', '')
                print(f"  Content:")
                print(f"  {'-'*60}")
                print(f"  {content}")
                print(f"  {'-'*60}")

    # Summary
    print(f"\n{'='*80}")
    print(f"DATABASE SUMMARY")
    print(f"{'='*80}")
    for module_name, records in modules.items():
        if records:
            print(f"{module_name}: {len(records)} records")

if __name__ == "__main__":
    retrieve_existing_content()