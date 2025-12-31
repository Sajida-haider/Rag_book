"""Test script to verify actual content extraction from a chapter page"""

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
    """Test actual content extraction from a specific chapter page"""

    # Test with one of the module pages
    test_url = "https://rag-book-ten.vercel.app/docs/module-1/chapter-1-ros2-fundamentals"

    print(f"Testing content extraction from: {test_url}")
    print("="*60)

    # Initialize services
    scraper = WebScraperService(delay=0.5)
    extractor = ContentExtractorService()
    cleaner = ContentCleanerService()

    # Fetch the page content (this uses JS rendering if available)
    print("1. Fetching page content with JS rendering...")
    html_content = scraper.fetch_page(test_url)

    if html_content:
        print(f"   Successfully fetched HTML content: {len(html_content)} characters")

        # First, let's manually parse the HTML to see if we can find the content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Look for common Docusaurus content containers
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.main-wrapper',
            '.container',
            '.docPageContainer',
            '.theme-doc',
            '[class*="docItem"]',
            '[class*="docMain"]',
            '[class*="theme"]',
            '[class*="doc"]'
        ]

        print("2. Trying different content selectors...")
        found_content = False
        for selector in content_selectors:
            if selector.startswith('.'):
                elements = soup.select(selector)
            elif selector.startswith('['):
                elements = soup.select(selector)
            else:
                elements = soup.find_all(selector)

            if elements:
                element = elements[0]  # Take the first match
                content = element.get_text().strip()
                if len(content) > 50:  # If we found substantial content
                    print(f"   Found content with selector '{selector}': {len(content)} characters")
                    # Remove or replace problematic Unicode characters for display
                    safe_content = content[:300].encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
                    print(f"   Preview: {safe_content}...")
                    found_content = True
                    break

        if not found_content:
            print("   No substantial content found with common selectors")

        # Extract content from our services
        print("\n3. Extracting content using services...")
        extracted = extractor.extract_all_page_content(html_content, test_url)
        print(f"   Extracted title: {extracted['title']}")
        print(f"   Extracted content length: {len(extracted['content'])} characters")

        if extracted['content'].strip():
            print(f"   Service content preview: {extracted['content'][:500]}...")
        else:
            print("   WARNING: Service extracted content is empty!")

        # Clean the content
        print("4. Cleaning content...")
        cleaned_content, is_valid = cleaner.clean_and_validate(extracted['content'])
        if is_valid:
            print(f"   Cleaned content length: {len(cleaned_content)} characters")
            print(f"   Cleaned content preview: {cleaned_content[:500]}...")
        else:
            print("   WARNING: Content not valid for processing")
    else:
        print("   Failed to fetch content")

if __name__ == "__main__":
    test_content_extraction()