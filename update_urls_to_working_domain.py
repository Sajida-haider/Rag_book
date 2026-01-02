"""Script to update URLs in Qdrant database to use the working domain"""
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

def update_urls_to_working_domain():
    """Update URLs in the database to use the working domain"""
    print(f"Updating URLs in collection: {collection_name}")

    # Get all records
    all_records = client.scroll(
        collection_name=collection_name,
        with_payload=True,
        with_vectors=False,
        limit=100
    )[0]

    print(f"Found {len(all_records)} total records in the collection")

    updated_count = 0
    for record in all_records:
        old_payload = record.payload
        old_url = old_payload.get('url', '')

        # Check if the URL contains the old domain that needs to be updated
        if 'mybook-h81fpl8zu-sajida-haiders-projects.vercel.app' in old_url:
            # Replace with the working domain
            new_url = old_url.replace(
                'mybook-h81fpl8zu-sajida-haiders-projects.vercel.app',
                'mybook-murex.vercel.app'
            )

            # Update the payload
            new_payload = old_payload.copy()
            new_payload['url'] = new_url

            # Update the record in Qdrant
            client.set_payload(
                collection_name=collection_name,
                points=[record.id],
                payload=new_payload
            )

            print(f"Updated URL: {old_url}")
            print(f"  -> New URL: {new_url}")
            updated_count += 1

        elif 'my-book-efxlpl0go-sajida-haiders-projects.vercel.app' in old_url:
            # Replace with the working domain
            new_url = old_url.replace(
                'my-book-efxlpl0go-sajida-haiders-projects.vercel.app',
                'mybook-murex.vercel.app'
            )

            # Update the payload
            new_payload = old_payload.copy()
            new_payload['url'] = new_url

            # Update the record in Qdrant
            client.set_payload(
                collection_name=collection_name,
                points=[record.id],
                payload=new_payload
            )

            print(f"Updated URL: {old_url}")
            print(f"  -> New URL: {new_url}")
            updated_count += 1

        elif 'rag-book-ten.vercel.app' in old_url:
            # Replace with the working domain
            new_url = old_url.replace(
                'rag-book-ten.vercel.app',
                'mybook-murex.vercel.app'
            )

            # Update the payload
            new_payload = old_payload.copy()
            new_payload['url'] = new_url

            # Update the record in Qdrant
            client.set_payload(
                collection_name=collection_name,
                points=[record.id],
                payload=new_payload
            )

            print(f"Updated URL: {old_url}")
            print(f"  -> New URL: {new_url}")
            updated_count += 1
        else:
            print(f"No update needed: {old_url}")

    print(f"\nSuccessfully updated {updated_count} records")

    # Verify the updates by checking a few records
    print(f"\nVerifying updates...")
    sample_records = client.scroll(
        collection_name=collection_name,
        with_payload=True,
        with_vectors=False,
        limit=5
    )[0]

    print(f"Sample updated records:")
    for i, record in enumerate(sample_records):
        payload = record.payload
        print(f"{i+1}. URL: {payload.get('url', 'N/A')}")
        print(f"   Title: {payload.get('title', 'N/A')}")
        print(f"   Content preview: {payload.get('content', '')[:100]}...")

if __name__ == "__main__":
    update_urls_to_working_domain()