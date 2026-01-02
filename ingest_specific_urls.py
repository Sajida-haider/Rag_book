"""Script to ingest content from specific URLs into Qdrant database"""
import os
import requests
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import uuid
from typing import List, Dict, Any
import time

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

def extract_content_from_page(html: str, url: str) -> Dict[str, str]:
    """Extract main content from Docusaurus HTML page"""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove common navigation and non-content elements
    for element in soup(['nav', 'header', 'footer', 'aside', 'script', 'style', 'meta', 'link']):
        element.decompose()

    # Remove elements with common class names for navigation, ads, etc.
    import re
    for element in soup.find_all(class_=re.compile(r'nav|menu|sidebar|advertisement|ads|cookie|banner|footer|search|toc')):
        element.decompose()

    # Try to find the main content area
    content_selectors = [
        '[class*="theme-doc-markdown"]',  # Main markdown content area
        '[class*="markdown"]',  # Markdown content
        '[class*="docItemContainer"]',  # Docusaurus doc container
        '[class*="docMainContainer"]',  # Docusaurus main container
        '[class*="docItemCol"]',  # Docusaurus column
        '[class*="docContent"]',  # Docusaurus content
        'article',  # Standard article tag
        'main',     # Main content area
        '.container',  # General container
        '[class*="content"]',  # Content-related
        '[class*="theme"]',  # Theme-related content
    ]

    main_content = None
    for selector in content_selectors:
        elements = soup.select(selector)
        if elements:
            main_content = elements[0]  # Take the first match
            break

    # If no specific selector worked, try to find content by looking for headers and paragraphs
    if not main_content:
        # Look for content by finding the most text-rich area
        all_divs = soup.find_all('div')
        text_rich_divs = [(div, len(div.get_text().strip())) for div in all_divs if len(div.get_text().strip()) > 100]
        text_rich_divs.sort(key=lambda x: x[1], reverse=True)

        if text_rich_divs:
            main_content = text_rich_divs[0][0]  # Take the div with most text
        else:
            main_content = soup.body  # Fallback to body

    if main_content:
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else url.split('/')[-1] or 'Untitled'

        # Extract content text
        content_parts = []

        # Look for all content elements in hierarchical order
        content_elements = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'div', 'span', 'section', 'article', 'pre', 'code'])

        for element in content_elements:
            text = element.get_text().strip()
            if text and len(text) > 5:  # Only include substantial text blocks
                # Preserve heading structure
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    content_parts.append(f"\n{'='*int(element.name[1])} {text} {'='*int(element.name[1])}\n")
                elif element.name == 'li':
                    # Handle list items
                    content_parts.append(f"- {text}")
                elif element.name == 'pre' or element.name == 'code':
                    # Preserve code blocks
                    content_parts.append(f"\n```\n{text}\n```\n")
                else:
                    # Regular text
                    content_parts.append(text)

        content = '\n'.join(content_parts)
    else:
        # Fallback: extract all text from body
        title = url.split('/')[-1] or 'Untitled'
        content = soup.get_text()

    # Clean up the content
    lines = (line.strip() for line in content.splitlines())
    content = '\n'.join(line for line in lines if line)

    return {
        'url': url,
        'title': title,
        'content': content
    }

def ingest_specific_urls():
    """Ingest content from the specific URLs provided"""
    urls_to_ingest = [
        # Module 1
        "https://rag-book-ten.vercel.app/docs/module-1/chapter-1-ros2-fundamentals",
        "https://rag-book-ten.vercel.app/docs/module-1/chapter-2-python-agents-ros2",
        "https://rag-book-ten.vercel.app/docs/module-1/chapter-3-urdf-humanoid-models",
        # Module 2
        "https://rag-book-ten.vercel.app/docs/module-2/chapter-1-physics-simulation-gazebo",
        "https://rag-book-ten.vercel.app/docs/module-2/chapter-2-high-fidelity-unity",
        "https://rag-book-ten.vercel.app/docs/module-2/chapter-3-sensor-simulation",
        # Module 3
        "https://rag-book-ten.vercel.app/docs/module-3/chapter-1-nvidia-isaac-sim",
        "https://rag-book-ten.vercel.app/docs/module-3/chapter-2-isaac-ros-perception",
        "https://rag-book-ten.vercel.app/docs/module-3/chapter-3-nav2-navigation",
        # Module 4
        "https://rag-book-ten.vercel.app/docs/module-4/chapter-1-voice-to-action",
        "https://rag-book-ten.vercel.app/docs/module-4/chapter-2-cognitive-planning-with-llms",
        "https://rag-book-ten.vercel.app/docs/module-4/chapter-3-capstone-autonomous-humanoid"
    ]

    print(f"Ingesting content from {len(urls_to_ingest)} specific URLs into collection: {collection_name}")

    successful_ingests = 0
    failed_ingests = 0

    for i, url in enumerate(urls_to_ingest):
        print(f"\nProcessing URL {i+1}/{len(urls_to_ingest)}: {url}")

        try:
            # Fetch the page content
            response = requests.get(url)
            if response.status_code == 200:
                # Extract content from the HTML
                extracted = extract_content_from_page(response.text, url)

                print(f"  Title: {extracted['title']}")
                print(f"  Content length: {len(extracted['content'])} characters")

                # Check if content already exists in the database based on URL
                search_results = client.scroll(
                    collection_name=collection_name,
                    scroll_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="url",
                                match=models.MatchValue(value=extracted['url'])
                            )
                        ]
                    ),
                    limit=1
                )

                if search_results[0]:  # If content already exists
                    print(f"  Content already exists in database, skipping...")
                    continue
                else:
                    # Create a unique ID for this record
                    record_id = str(uuid.uuid4())

                    # Create the payload
                    payload = {
                        'url': extracted['url'],
                        'title': extracted['title'],
                        'content': extracted['content'],
                        'section': extracted['url'].split('/')[-1],  # Extract section from URL
                        'created_at': str(uuid.uuid4()),  # Using UUID as timestamp substitute
                        'chunk_index': 0,
                        'total_chunks': 1
                    }

                    # Create a simple embedding (using length as a placeholder)
                    # In a real implementation, you would use a proper embedding model
                    embedding = [0.0] * 1024  # Placeholder embedding

                    # Store in Qdrant
                    client.upsert(
                        collection_name=collection_name,
                        points=[
                            models.PointStruct(
                                id=record_id,
                                vector=embedding,
                                payload=payload
                            )
                        ]
                    )

                    print(f"  Successfully stored with ID: {record_id}")
                    successful_ingests += 1
            else:
                print(f"  Failed to fetch page: {response.status_code}")
                failed_ingests += 1

        except Exception as e:
            print(f"  Error processing {url}: {e}")
            failed_ingests += 1

        # Add a small delay to be respectful to the server
        time.sleep(1)

    # Verify what we've stored
    print(f"\n{'='*60}")
    print(f"INGESTION SUMMARY")
    print(f"{'='*60}")
    print(f"Successful: {successful_ingests}")
    print(f"Failed: {failed_ingests}")
    print(f"Total processed: {len(urls_to_ingest)}")

    # Count total records in the database
    all_records = client.scroll(
        collection_name=collection_name,
        with_payload=True,
        limit=1000
    )
    total_records = len(all_records[0])
    print(f"Total records in database: {total_records}")

    # Count records by module
    module_counts = {}
    for record in all_records[0]:
        payload = record.payload
        url = payload.get('url', '')
        if 'module-1' in url:
            module_counts['Module 1'] = module_counts.get('Module 1', 0) + 1
        elif 'module-2' in url:
            module_counts['Module 2'] = module_counts.get('Module 2', 0) + 1
        elif 'module-3' in url:
            module_counts['Module 3'] = module_counts.get('Module 3', 0) + 1
        elif 'module-4' in url:
            module_counts['Module 4'] = module_counts.get('Module 4', 0) + 1

    print(f"\nRecords by module:")
    for module, count in module_counts.items():
        print(f"  {module}: {count} records")

if __name__ == "__main__":
    ingest_specific_urls()