"""Script to check all Module 4 related records in the database"""
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

print(f"Retrieving all Module 4 related records from collection: {collection_name}")

# Get all records
all_records = client.scroll(
    collection_name=collection_name,
    with_payload=True,
    with_vectors=False,
    limit=100
)[0]

print(f"Found {len(all_records)} total records in the collection")

# Look for all Module 4 related content
module_4_records = []
for i, record in enumerate(all_records):
    payload = record.payload
    url = payload.get('url', '')

    if 'module-4' in url.lower():
        module_4_records.append({
            'id': record.id,
            'payload': payload,
            'index': i
        })
        print(f"\nModule 4 Record {len(module_4_records)}:")
        print(f"  ID: {record.id}")
        print(f"  URL: {url}")
        print(f"  Title: {payload.get('title', 'N/A')}")
        print(f"  Section: {payload.get('section', 'N/A')}")
        print(f"  Chunk Index: {payload.get('chunk_index', 'N/A')}")
        print(f"  Total Chunks: {payload.get('total_chunks', 'N/A')}")
        print(f"  Content length: {len(payload.get('content', ''))} characters")
        print(f"  Content preview: {payload.get('content', '')[:200]}...")

if module_4_records:
    print(f"\nFound {len(module_4_records)} Module 4 records total")

    # Sort by chunk index if available
    module_4_records.sort(key=lambda x: int(x['payload'].get('chunk_index', 0)) if x['payload'].get('chunk_index') else 0)

    print("\n" + "="*80)
    print("COMBINED MODULE 4 CONTENT:")
    print("="*80)

    combined_content = ""
    for record_info in module_4_records:
        payload = record_info['payload']
        content = payload.get('content', '')
        chunk_idx = payload.get('chunk_index', 'N/A')
        total_chunks = payload.get('total_chunks', 'N/A')

        print(f"\nChunk {chunk_idx}/{total_chunks}:")
        print(f"URL: {payload.get('url', 'N/A')}")
        print("-" * 40)
        print(content)
        print("-" * 40)

        combined_content += content + "\n\n"

    print(f"\nCOMBINED CONTENT LENGTH: {len(combined_content)} characters")

    # Look for the specific content the user mentioned
    if 'Vision-Language-Action' in combined_content or 'VLA' in combined_content:
        print("\n" + "="*60)
        print("FOUND THE CONTENT THE USER MENTIONED!")
        print("="*60)

        # Extract the overview paragraph
        lines = combined_content.split('\n')
        for i, line in enumerate(lines):
            if 'Overview' in line or ('vision' in line.lower() and 'language' in line.lower() and 'action' in line.lower()):
                # Get this line and the next few lines
                overview_paragraph = ""
                for j in range(i, min(i+5, len(lines))):
                    if lines[j].strip():
                        overview_paragraph += lines[j].strip() + " "
                print(f"Overview section: {overview_paragraph.strip()}")
                break
else:
    print("No Module 4 records found in the database")