"""Simple test to verify content extraction"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the services to demonstrate the extraction process
from services.web_scraper import WebScraperService
from services.content_extractor import ContentExtractorService

def test_content_extraction():
    """Test actual content extraction from a specific chapter page"""

    # Test with one of the module pages
    test_url = "https://rag-book-ten.vercel.app/docs/module-1/chapter-1-ros2-fundamentals"

    print(f"Testing content extraction from: {test_url}")
    print("="*60)

    # Initialize services
    scraper = WebScraperService(delay=0.5)
    extractor = ContentExtractorService()

    # Fetch the page content (this uses JS rendering if available)
    print("1. Fetching page content with JS rendering...")
    html_content = scraper.fetch_page(test_url)

    if html_content:
        print(f"   Successfully fetched HTML content: {len(html_content)} characters")

        # Extract content from our services
        print("2. Extracting content using services...")
        extracted = extractor.extract_all_page_content(html_content, test_url)
        print(f"   Extracted title: {extracted['title']}")
        print(f"   Extracted content length: {len(extracted['content'])} characters")

        if len(extracted['content']) > 50:
            print(f"   SUCCESS: Content extraction is working! Got {len(extracted['content'])} characters")
        else:
            print(f"   ISSUE: Content extraction still not working - only got {len(extracted['content'])} characters")
    else:
        print("   Failed to fetch content")

if __name__ == "__main__":
    test_content_extraction()