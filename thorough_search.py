"""Script to do a more thorough search of the Qdrant database for detailed content"""
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

print(f"Doing a thorough search of collection: {collection_name}")

# Get all records
all_records = client.scroll(
    collection_name=collection_name,
    with_payload=True,
    with_vectors=False,
    limit=100
)[0]

print(f"Found {len(all_records)} total records in the collection")

# Look for any record that might contain detailed content with keywords from the overview
keywords = ['vision-language-action', 'vla', 'capstone', 'overview', 'perception', 'planning', 'navigation', 'simulation', 'autonomous']

found_records = []
for i, record in enumerate(all_records):
    payload = record.payload
    content = payload.get('content', '').lower()
    url = payload.get('url', '')
    title = payload.get('title', '')

    # Check if this record contains any of our keywords
    has_keywords = any(keyword in content for keyword in keywords)

    print(f"\nRecord {i+1}:")
    print(f"  URL: {url}")
    print(f"  Title: {title}")
    print(f"  Content length: {len(payload.get('content', ''))} characters")

    if has_keywords:
        print(f"  *** CONTAINS KEYWORDS! ***")
        print(f"  Content preview: {payload.get('content', '')[:500]}...")
        found_records.append({
            'record': record,
            'index': i+1
        })
    else:
        print(f"  Content preview: {content[:200]}...")

print(f"\n" + "="*80)
print(f"SUMMARY:")
print(f"Total records searched: {len(all_records)}")
print(f"Records containing relevant keywords: {len(found_records)}")

if found_records:
    print("\nRecords with relevant content:")
    for found in found_records:
        payload = found['record'].payload
        print(f"  - Record {found['index']}")
        print(f"    URL: {payload.get('url', 'N/A')}")
        print(f"    Content: {payload.get('content', '')[:300]}...")
else:
    print("\nNo records found containing the keywords.")

    # Let's try another approach - look for any record with substantial content
    print(f"\nLooking for any record with substantial content (>200 characters)...")
    substantial_records = []
    for i, record in enumerate(all_records):
        payload = record.payload
        content = payload.get('content', '')
        if len(content) > 200:  # Look for records with more than 200 characters
            substantial_records.append({
                'record': record,
                'index': i+1,
                'length': len(content)
            })

    print(f"Found {len(substantial_records)} records with substantial content:")
    for sub_rec in substantial_records:
        payload = sub_rec['record'].payload
        print(f"  - Record {sub_rec['index']} ({sub_rec['length']} chars)")
        print(f"    URL: {payload.get('url', 'N/A')}")
        print(f"    Title: {payload.get('title', 'N/A')}")
        print(f"    Content preview: {payload.get('content', '')[:300]}...")
        print()