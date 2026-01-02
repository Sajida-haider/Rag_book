"""Script to get the full content of Module 4 Chapter 3 from the database"""
import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Qdrant client with the correct credentials
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = os.getenv("COLLECTION_NAME", "humanoid_ai_book")

client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
    prefer_grpc=True
)

print(f"Retrieving full content for Module 4 Chapter 3 from collection: {collection_name}")

# Search for records that match Module 4 Chapter 3
search_results = client.scroll(
    collection_name=collection_name,
    with_payload=True,
    with_vectors=False,
    limit=100
)

print(f"Found {len(search_results[0])} total records in the collection")

# Look specifically for Module 4 Chapter 3 content
module_4_chapter_3_content = None
for record in search_results[0]:
    payload = record.payload
    url = payload.get('url', '')

    if 'module-4' in url.lower() and 'chapter-3' in url.lower():
        print(f"Found Module 4 Chapter 3 record:")
        print(f"  URL: {url}")
        print(f"  Title: {payload.get('title', 'N/A')}")
        print(f"  Content length: {len(payload.get('content', ''))} characters")
        print(f"  Content preview: {payload.get('content', '')[:200]}...")

        module_4_chapter_3_content = payload.get('content', '')
        break

if module_4_chapter_3_content:
    print("\n" + "="*60)
    print("FULL CONTENT FOUND:")
    print("="*60)
    print(module_4_chapter_3_content)
    print("="*60)

    # Extract the first paragraph more carefully
    lines = module_4_chapter_3_content.split('\n')
    first_paragraph = ""

    # Skip initial header lines and find the actual first paragraph
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('Physical AI Humanoid Robotics') and len(line) > 50:
            first_paragraph = line
            break

    print(f"\nACTUAL FIRST PARAGRAPH:")
    print(f"{first_paragraph}")
else:
    print("Module 4 Chapter 3 content not found in the database")

    # Let's try to find any content that might be related to the capstone project
    print("\nLooking for any capstone-related content...")
    for record in search_results[0]:
        payload = record.payload
        content = payload.get('content', '')
        title = payload.get('title', '')
        url = payload.get('url', '')

        if 'capstone' in content.lower() or 'autonomous' in content.lower():
            print(f"Found related content in: {url}")
            print(f"Title: {title}")
            print(f"Content preview: {content[:300]}...")
            print("-" * 40)