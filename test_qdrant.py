import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ragbot_backend'))

from dotenv import load_dotenv
load_dotenv()

import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

# Load configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "PUT_YOUR_COHERE_KEY_HERE")
QDRANT_URL = os.getenv("QDRANT_URL", "PUT_YOUR_QDRANT_URL_HERE")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "PUT_YOUR_QDRANT_API_KEY_HERE")
COLLECTION_NAME = "Rag_embeding"

# Connect to Qdrant
if not QDRANT_URL.startswith(('http://', 'https://')):
    qdrant_url = f"https://{QDRANT_URL}"
else:
    qdrant_url = QDRANT_URL

qdrant = QdrantClient(
    url=qdrant_url,
    api_key=QDRANT_API_KEY,
    https=True
)

# Check collection info
try:
    collection_info = qdrant.get_collection(COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' exists")
    print(f"Points count: {collection_info.points_count}")
    print(f"Vectors count: {collection_info.vectors_count}")

    # Try to get some points to see if there's content
    if collection_info.points_count > 0:
        # Get a few points to see what's in there
        points = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            limit=3
        )
        print(f"Sample points: {len(points[0])}")
        for i, point in enumerate(points[0]):
            print(f"Point {i+1}:")
            print(f"  ID: {point.id}")
            print(f"  Payload keys: {list(point.payload.keys())}")
            if 'text' in point.payload:
                print(f"  Text preview: {point.payload['text'][:100]}...")
            if 'url' in point.payload:
                print(f"  URL: {point.payload['url']}")
            print()
    else:
        print("No points in the collection")

except Exception as e:
    print(f"Error accessing Qdrant: {e}")