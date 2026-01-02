#!/usr/bin/env python3
"""Test script to verify the JavaScript-aware web scraper works properly"""

import sys
import os

# Add the backend directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Desktop', 'book_ragbot', 'backend'))

def test_scraper():
    try:
        from services.web_scraper import WebScraperService

        print("Testing WebScraperService with JavaScript rendering...")

        # Test with a Docusaurus site (using a placeholder URL since we don't know the exact one)
        # We'll use a common Docusaurus pattern for testing
        test_urls = [
            "https://rag-book.vercel.app/docs/introduction",  # Example Docusaurus URL
            "https://docusaurus.io/docs",  # Docusaurus documentation
            "https://create-react-app.dev/docs/getting-started"  # Another React-based site
        ]

        scraper = WebScraperService(delay=0.5, use_js_rendering=True)

        for url in test_urls:
            print(f"\nTesting URL: {url}")
            result = scraper.extract_content(url)

            if result:
                print(f"✓ Success! Title: {result['title'][:50]}...")
                print(f"Content length: {len(result['content'])} characters")
                print(f"Content preview: {result['content'][:200]}...")
            else:
                print(f"✗ Failed to extract content from {url}")

            # Small delay between requests
            import time
            time.sleep(1)

    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you have the required dependencies installed.")
        print("You may need to install Playwright: pip install playwright")
        print("Then run: playwright install")
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_dependencies():
    """Test if required dependencies are available"""
    print("Testing dependencies...")

    try:
        import requests
        print("✓ requests is available")
    except ImportError:
        print("✗ requests is not available")

    try:
        import bs4
        print("✓ beautifulsoup4 is available")
    except ImportError:
        print("✗ beautifulsoup4 is not available")

    try:
        from playwright.sync_api import sync_playwright
        print("✓ playwright is available")
    except ImportError:
        print("✗ playwright is not available - this is required for JavaScript rendering")

    # Check if browsers are installed for Playwright
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
            print("✓ Playwright browsers are installed")
    except Exception as e:
        print(f"✗ Playwright browsers not installed: {e}")
        print("Please run: playwright install")

if __name__ == "__main__":
    print("Testing JavaScript-aware web scraper...")
    test_dependencies()
    print("\n" + "="*50)
    test_scraper()