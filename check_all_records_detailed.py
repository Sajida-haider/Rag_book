"""Script to check all records in the database for detailed content"""
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

print(f"Retrieving ALL records from collection: {collection_name}")

# Get all records
all_records = client.scroll(
    collection_name=collection_name,
    with_payload=True,
    with_vectors=False,
    limit=100
)[0]

print(f"Found {len(all_records)} total records in the collection")

# Look for any record that contains the specific content mentioned by the user
found_detailed_content = False
for i, record in enumerate(all_records):
    payload = record.payload
    url = payload.get('url', '')
    content = payload.get('content', '')
    title = payload.get('title', 'N/A')

    print(f"\nRecord {i+1}:")
    print(f"  URL: {url}")
    print(f"  Title: {title}")
    print(f"  Content length: {len(content)} characters")

    # Check if this record contains the detailed content mentioned by the user
    if 'Vision-Language-Action' in content or 'VLA' in content or ('overview' in content.lower() and 'capstone' in content.lower()):
        print(f"  *** FOUND DETAILED CONTENT! ***")
        print(f"  Content preview: {content[:500]}...")
        found_detailed_content = True

        # Extract the overview paragraph
        lines = content.split('\n')
        for line in lines:
            if 'Overview' in line or ('vision' in line.lower() and 'language' in line.lower() and 'action' in line.lower()):
                print(f"\nMATCHING PARAGRAPH FOUND:")
                print(f"{line.strip()}")
                break

        # Look for the specific text the user mentioned
        if 'Vision-Language-Action (VLA)' in content or 'capstone' in content.lower():
            # Find the overview section
            content_parts = content.split('\n')
            for part in content_parts:
                if len(part.strip()) > 50:  # Look for substantial paragraphs
                    if 'overview' in part.lower() or 'vision-language-action' in part.lower() or 'capstone' in part.lower():
                        print(f"\nDETAILED OVERVIEW FOUND:")
                        print(f"{part.strip()}")
                        break
    else:
        print(f"  Content preview: {content[:200]}...")

if not found_detailed_content:
    print(f"\n" + "="*80)
    print("SEARCHING FOR THE SPECIFIC CONTENT MENTIONED BY THE USER")
    print("="*80)
    print("The content you mentioned:")
    print("'Overview: This capstone chapter integrates all the concepts from the Vision-Language-Action (VLA) module into a comprehensive autonomous humanoid system. We'll explore how perception, planning, and navigation work together to enable full robot task execution in simulation environments. This project demonstrates the complete pipeline from voice command to robot action, showcasing how the individual components combine to create sophisticated autonomous behavior.'")
    print("\nThis specific detailed content does not appear to be stored in the current database.")
    print("The database only contains truncated headers/titles for each chapter.")

    # Check if we can access the actual deployed content
    print(f"\nTrying to access the actual content from the deployed URL...")
    import requests
    try:
        response = requests.get("http://mybook-h81fpl8zu-sajida-haiders-projects.vercel.app/docs/module-4/chapter-3-capstone-autonomous-humanoid")
        if response.status_code == 200:
            print("Successfully accessed the deployed page")
            # Try to extract content from the HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            print(f"Extracted text length: {len(text)} characters")
            # Look for the overview section in the extracted text
            if 'Vision-Language-Action' in text or 'VLA' in text or 'capstone' in text.lower():
                print("Found content with VLA/capstone references in the deployed page")
            else:
                print("The detailed content may not be available at the deployed URL either")
        else:
            print(f"Could not access the deployed page, status code: {response.status_code}")
    except Exception as e:
        print(f"Error accessing deployed page: {e}")