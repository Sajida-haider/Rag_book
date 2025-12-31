"""Test script to demonstrate how content extraction works for your book"""

import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the services to demonstrate the extraction process
from services.web_scraper import WebScraperService
from services.content_extractor import ContentExtractorService
from services.content_cleaner import ContentCleanerService

def test_content_extraction():
    """Test how content is extracted from one of your book pages"""

    # URLs from your book that were successfully extracted
    test_urls = [
        "https://rag-book-ten.vercel.app",
        "https://rag-book-ten.vercel.app/docs/module-1/chapter-1-ros2-fundamentals"
    ]

    # Initialize services
    scraper = WebScraperService(delay=0.5)
    extractor = ContentExtractorService()
    cleaner = ContentCleanerService()

    print("Testing content extraction process...")
    print("="*50)

    for url in test_urls:
        print(f"\nTesting URL: {url}")
        print("-" * 30)

        # Method 1: Try direct HTTP request (this may return 404 for client-side routes)
        print("1. Direct HTTP request:")
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Content length: {len(response.text)} characters")
            else:
                print(f"   Content not accessible via direct HTTP request")
        except Exception as e:
            print(f"   Error: {e}")

        # Method 2: Try with JavaScript rendering (this is what the system actually uses)
        print("\n2. JavaScript rendering (via WebScraperService):")
        html_content = scraper.fetch_page(url)
        if html_content:
            print(f"   Successfully fetched HTML content: {len(html_content)} characters")

            # Extract content from HTML
            extracted = extractor.extract_all_page_content(html_content, url)
            print(f"   Extracted title: {extracted['title']}")
            print(f"   Extracted content length: {len(extracted['content'])} characters")

            # Clean the content
            cleaned_content, is_valid = cleaner.clean_and_validate(extracted['content'])
            if is_valid:
                print(f"   Cleaned content length: {len(cleaned_content)} characters")
                print(f"   Content preview: {cleaned_content[:200]}...")
            else:
                print("   Content not valid for processing")
        else:
            print("   Failed to fetch content via JavaScript rendering")

        print("\n" + "="*50)

if __name__ == "__main__":
    test_content_extraction()